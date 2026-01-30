from django import forms

from .models import Avance, Cita, OrdenServicio, FotoOrden


class OrdenServicioForm(forms.ModelForm):
    testigos = forms.MultipleChoiceField(
        choices=OrdenServicio.TESTIGOS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Testigos Encendidos"
    )

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
            'testigos',
            'estatus',
            'costo_total',
            'monto_pagado',
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
            'costo_total': forms.NumberInput(),
            'monto_pagado': forms.NumberInput(),
            'notas': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure initial data for JSONField is correctly handled if it's a list
        if self.instance and self.instance.pk and self.instance.testigos:
            self.initial['testigos'] = self.instance.testigos
            
        base = 'w-full rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-3 text-white placeholder-zinc-500 shadow-sm transition focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500'
        for name, field in self.fields.items():
            if name != 'testigos': # Skip styling for checkbox container here, handle in template or separate logic
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
            'nota': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Descripción del avance (Requerido para actualizar estatus)'}),
        }

    def __init__(self, *args, orden=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.orden = orden
        # Make nota required as per user request
        self.fields['nota'].required = True
        
        base = 'w-full rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-3 text-white placeholder-zinc-500 shadow-sm transition focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500'
        for field in self.fields.values():
            field.widget.attrs['class'] = base

    def clean_estatus(self):
        estatus = self.cleaned_data.get('estatus')
        if self.orden and estatus == self.orden.estatus:
            raise forms.ValidationError("No puedes guardar el mismo estatus consecutivamente. Actualiza el estatus o cancela la operación.")
        return estatus

class FotoOrdenForm(forms.Form):
    def __init__(self, *args, orden=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.orden = orden
        
        existing_photos = {}
        unnumbered_photos = []
        
        if orden:
            # Fetch all photos ordered by ID for stability
            all_photos = orden.fotos.all().order_by('id')
            
            for foto in all_photos:
                if foto.numero:
                    existing_photos[foto.numero] = foto.url
                else:
                    unnumbered_photos.append(foto)

        # Map labels to fields
        labels = {
            1: 'Parte Frontal',
            2: 'Parte Trasera',
            3: 'Lateral Izquierdo',
            5: 'Lateral Derecho',
            6: 'Cofre',
            7: 'Techo',
            8: 'Interior Delantero',
            9: 'Interior Trasero',
            10: 'Tablero'
        }

        # Create 10 URL fields dynamically
        for i in range(1, 11):
            field_name = f'foto_{i}'
            initial_val = ''
            
            if i in existing_photos:
                initial_val = existing_photos[i]
            elif unnumbered_photos:
                # Assign unnumbered photo to this slot and fix DB
                foto = unnumbered_photos.pop(0)
                initial_val = foto.url
                
                # Self-healing: Assign number to avoid duplicates on save
                foto.numero = i
                foto.save()
            
            self.fields[field_name] = forms.URLField(
                required=False,
                initial=initial_val,
                widget=forms.URLInput(attrs={
                    'placeholder': 'https://...',
                    'class': 'w-full rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-3 text-white placeholder-zinc-500 shadow-sm transition focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500'
                }),
                label=labels.get(i, f"Foto {i}")
            )

    def save(self):
        if not self.orden:
            return
            
        for i in range(1, 11):
            url = self.cleaned_data.get(f'foto_{i}')
            
            # Find existing photo at this position
            foto_obj = self.orden.fotos.filter(numero=i).first()
            
            if url:
                if foto_obj:
                    if foto_obj.url != url:
                        foto_obj.url = url
                        foto_obj.save()
                else:
                    FotoOrden.objects.create(orden=self.orden, numero=i, url=url)
            else:
                # If field is empty but object exists, delete it (user cleared the field)
                if foto_obj:
                    foto_obj.delete()

    def clean(self):
        cleaned_data = super().clean()
        # Basic validation if needed
        return cleaned_data


class CostosForm(forms.ModelForm):
    class Meta:
        model = OrdenServicio
        fields = ['costo_total', 'monto_pagado']
        widgets = {
            'costo_total': forms.NumberInput(),
            'monto_pagado': forms.NumberInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base = 'w-full rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-3 text-white placeholder-zinc-500 shadow-sm transition focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500'
        for field in self.fields.values():
            field.widget.attrs['class'] = base

