from django import forms

from .models import Avance, Cita, OrdenServicio


class OrdenServicioForm(forms.ModelForm):
    class Meta:
        model = OrdenServicio
        fields = [
            'cliente_nombre',
            'vehiculo_marca',
            'vehiculo_modelo',
            'vehiculo_matricula',
            'vehiculo_anio',
            'vehiculo_color',
            'servicio',
            'estatus',
            'notas',
        ]
        widgets = {
            'cliente_nombre': forms.TextInput(),
            'vehiculo_marca': forms.TextInput(),
            'vehiculo_modelo': forms.TextInput(),
            'vehiculo_matricula': forms.TextInput(),
            'vehiculo_anio': forms.NumberInput(),
            'vehiculo_color': forms.TextInput(),
            'servicio': forms.Select(),
            'estatus': forms.Select(),
            'notas': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base = 'w-full rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-3 text-white placeholder-zinc-500 shadow-sm transition focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500'
        for field in self.fields.values():
            field.widget.attrs['class'] = base


class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['cliente_nombre', 'cliente_contacto', 'fecha', 'tipo', 'notas']
        widgets = {
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notas': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base = 'w-full rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-3 text-white placeholder-zinc-500 shadow-sm transition focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500'
        for field in self.fields.values():
            field.widget.attrs['class'] = base


class AvanceForm(forms.ModelForm):
    class Meta:
        model = Avance
        fields = ['estatus', 'nota']
        widgets = {
            'estatus': forms.Select(),
            'nota': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base = 'w-full rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-3 text-white placeholder-zinc-500 shadow-sm transition focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500'
        for field in self.fields.values():
            field.widget.attrs['class'] = base
