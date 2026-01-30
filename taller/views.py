from django.contrib import messages
from django.contrib.auth import forms as auth_forms
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from django.utils import timezone

from .forms import AvanceForm, CitaForm, OrdenServicioForm, CostosForm, FotoOrdenForm
from .models import Avance, Cita, OrdenServicio, FotoOrden


def index(request: HttpRequest) -> HttpResponse:
    return render(request, 'taller/index.html')


def folio_lookup(request: HttpRequest) -> HttpResponse:
    folio = (request.GET.get('folio') or '').strip().upper()
    if not folio:
        return render(request, 'taller/seguimiento.html')
    return redirect('seguimiento_detalle', folio=folio)


def seguimiento_detalle(request: HttpRequest, folio: str) -> HttpResponse:
    orden = get_object_or_404(OrdenServicio, folio=folio.upper())
    avances = orden.avances.all()
    fotos = orden.fotos.all()
    
    # Definir pasos para el tracker visual
    # choices es una lista de tuplas (valor, etiqueta)
    pasos_visuales = []
    target_steps = [
        OrdenServicio.Estatus.EN_RECEPCION,
        OrdenServicio.Estatus.EN_PREPARACION,
        OrdenServicio.Estatus.EN_PROCESO,
        OrdenServicio.Estatus.PREPARANDO_ENTREGA,
        OrdenServicio.Estatus.TRABAJO_TERMINADO,
    ]
    
    # Creamos un dict para buscar labels rápido
    labels_map = dict(OrdenServicio.Estatus.choices)
    
    for step in target_steps:
        pasos_visuales.append({
            'value': step,
            'label': labels_map[step]
        })
    
    # Mapeo de orden para saber qué índice tiene el estatus actual
    orden_estatus = target_steps
    
    try:
        idx_actual = orden_estatus.index(orden.estatus)
    except ValueError:
        idx_actual = 0
        
    return render(request, 'taller/seguimiento_detalle.html', {
        'orden': orden, 
        'avances': avances,
        'fotos': fotos,
        'pasos': pasos_visuales,
        'idx_actual': idx_actual
    })


class SuperuserLoginView(LoginView):
    template_name = 'taller/login.html'
    authentication_form = auth_forms.AuthenticationForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_superuser:
            form.add_error(None, 'Solo el superuser puede iniciar sesión.')
            return self.form_invalid(form)
        return super().form_valid(form)


def _superuser_required(user) -> bool:
    return user.is_authenticated and user.is_superuser


@user_passes_test(_superuser_required)
def dashboard(request: HttpRequest) -> HttpResponse:
    q = (request.GET.get('q') or '').strip()
    qs = OrdenServicio.objects.all().order_by('-actualizado_en')
    if q:
        qs = qs.filter(
            Q(folio__icontains=q)
            | Q(vehiculo_marca__icontains=q)
            | Q(vehiculo_modelo__icontains=q)
            | Q(vehiculo_matricula__icontains=q)
            | Q(estatus__icontains=q)
            | Q(cliente_nombre__icontains=q)
        )
    
    activas = qs.exclude(estatus=OrdenServicio.Estatus.TRABAJO_TERMINADO)
    entregadas = qs.filter(estatus=OrdenServicio.Estatus.TRABAJO_TERMINADO)
    
    # Citas
    citas_proximas = Cita.objects.filter(fecha__gte=timezone.now(), completada=False).order_by('fecha')
    
    return render(request, 'taller/dashboard.html', {
        'activas': activas, 
        'entregadas': entregadas, 
        'citas_proximas': citas_proximas,
        'q': q
    })


@user_passes_test(_superuser_required)
def orden_nueva(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = OrdenServicioForm(request.POST)
        if form.is_valid():
            orden = form.save()
            messages.success(request, f'Orden creada. Folio: {orden.folio}')
            return redirect('orden_detalle', pk=orden.pk)
    else:
        form = OrdenServicioForm()
    return render(request, 'taller/orden_form.html', {'form': form, 'titulo': 'Nueva orden'})


@user_passes_test(_superuser_required)
def orden_editar(request: HttpRequest, pk: int) -> HttpResponse:
    orden = get_object_or_404(OrdenServicio, pk=pk)
    if request.method == 'POST':
        form = OrdenServicioForm(request.POST, instance=orden)
        if form.is_valid():
            orden = form.save()
            messages.success(request, f'Orden {orden.folio} actualizada.')
            return redirect('dashboard')
    else:
        form = OrdenServicioForm(instance=orden)
    return render(request, 'taller/orden_form.html', {'form': form, 'orden': orden, 'titulo': 'Editar orden'})


@user_passes_test(_superuser_required)
def orden_detalle(request: HttpRequest, pk: int) -> HttpResponse:
    orden = get_object_or_404(OrdenServicio, pk=pk)
    
    form = AvanceForm(initial={'estatus': orden.estatus}, orden=orden)
    costos_form = CostosForm(instance=orden)
    fotos_form = FotoOrdenForm(orden=orden)

    if request.method == 'POST':
        if 'submit_avance' in request.POST:
            form = AvanceForm(request.POST, orden=orden)
            if form.is_valid():
                avance: Avance = form.save(commit=False)
                avance.orden = orden
                avance.save()
                orden.estatus = avance.estatus
                orden.save(update_fields=['estatus', 'actualizado_en'])
                messages.success(request, 'Avance registrado.')
                return redirect('orden_detalle', pk=orden.pk)
        
        elif 'submit_costos' in request.POST:
            costos_form = CostosForm(request.POST, instance=orden)
            if costos_form.is_valid():
                costos_form.save()
                messages.success(request, 'Costos actualizados.')
                return redirect('orden_detalle', pk=orden.pk)

        elif 'submit_fotos' in request.POST:
            fotos_form = FotoOrdenForm(request.POST, orden=orden)
            if fotos_form.is_valid():
                fotos_form.save()
                messages.success(request, 'Galería actualizada correctamente.')
                return redirect('orden_detalle', pk=orden.pk)

    avances = orden.avances.all()
    fotos = orden.fotos.all()
    
    return render(
        request,
        'taller/orden_detalle.html',
        {
            'orden': orden, 
            'form': form, 
            'costos_form': costos_form,
            'fotos_form': fotos_form,
            'avances': avances, 
            'fotos': fotos,
            'cliente_url': _cliente_url(request, orden)
        },
    )


def _cliente_url(request: HttpRequest, orden: OrdenServicio) -> str:
    path = reverse('seguimiento_detalle', kwargs={'folio': orden.folio})
    return request.build_absolute_uri(path)


@user_passes_test(_superuser_required)
def cita_nueva(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cita agendada.')
            return redirect('dashboard')
    else:
        form = CitaForm()
    return render(request, 'taller/cita_form.html', {'form': form, 'titulo': 'Nueva cita'})


@user_passes_test(_superuser_required)
def cita_editar(request: HttpRequest, pk: int) -> HttpResponse:
    cita = get_object_or_404(Cita, pk=pk)
    if request.method == 'POST':
        form = CitaForm(request.POST, instance=cita)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cita actualizada.')
            return redirect('dashboard')
    else:
        form = CitaForm(instance=cita)
    return render(request, 'taller/cita_form.html', {'form': form, 'titulo': 'Editar cita', 'cita': cita})


@user_passes_test(_superuser_required)
def cita_eliminar(request: HttpRequest, pk: int) -> HttpResponse:
    cita = get_object_or_404(Cita, pk=pk)
    if request.method == 'POST':
        cita.delete()
        messages.success(request, 'Cita eliminada.')
        return redirect('dashboard')
    return render(request, 'taller/cita_confirmar_eliminar.html', {'cita': cita})
