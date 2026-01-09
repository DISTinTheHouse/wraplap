from django.db import models
from django.utils.crypto import get_random_string


class OrdenServicio(models.Model):
    class Servicio(models.TextChoices):
        WRAP = 'WRAP', 'Wrap'
        PPF = 'PPF', 'PPF'
        WRAP_Y_PPF = 'WRAP_PPF', 'Wrap + PPF'

    class Estatus(models.TextChoices):
        RECIBIDO = 'RECIBIDO', 'Recibido'
        PREPARACION = 'PREPARACION', 'Preparación'
        EN_PROCESO = 'EN_PROCESO', 'En proceso'
        CONTROL_CALIDAD = 'CONTROL_CALIDAD', 'Control de calidad'
        LISTO = 'LISTO', 'Listo'
        ENTREGADO = 'ENTREGADO', 'Entregado'

    folio = models.CharField(max_length=12, unique=True, blank=True, db_index=True)
    cliente_nombre = models.CharField(max_length=200)
    vehiculo_marca = models.CharField(max_length=80)
    vehiculo_modelo = models.CharField(max_length=80)
    vehiculo_matricula = models.CharField(max_length=20, blank=True)
    vehiculo_anio = models.PositiveIntegerField()
    vehiculo_color = models.CharField(max_length=80)
    servicio = models.CharField(max_length=12, choices=Servicio.choices, default=Servicio.WRAP)
    estatus = models.CharField(max_length=20, choices=Estatus.choices, default=Estatus.RECIBIDO)
    notas = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.folio} - {self.vehiculo_marca} {self.vehiculo_modelo}'

    def _generar_folio_unico(self) -> str:
        while True:
            candidato = get_random_string(10, allowed_chars='ABCDEFGHJKLMNPQRSTUVWXYZ23456789')
            if not OrdenServicio.objects.filter(folio=candidato).exists():
                return candidato

    def save(self, *args, **kwargs):
        if not self.folio:
            self.folio = self._generar_folio_unico()
        return super().save(*args, **kwargs)


class Avance(models.Model):
    orden = models.ForeignKey(OrdenServicio, on_delete=models.CASCADE, related_name='avances')
    estatus = models.CharField(max_length=20, choices=OrdenServicio.Estatus.choices)
    nota = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado_en']

    def __str__(self) -> str:
        return f'{self.orden.folio} - {self.estatus}'


class Cita(models.Model):
    class Tipo(models.TextChoices):
        SERVICIO = 'SERVICIO', 'Nuevo servicio'
        PROSPECTO = 'PROSPECTO', 'Prospecto'

    cliente_nombre = models.CharField(max_length=200)
    cliente_contacto = models.CharField(max_length=100, blank=True, help_text='Teléfono o email')
    fecha = models.DateTimeField()
    tipo = models.CharField(max_length=20, choices=Tipo.choices, default=Tipo.PROSPECTO)
    notas = models.TextField(blank=True)
    completada = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['fecha']

    def __str__(self) -> str:
        return f'{self.fecha} - {self.cliente_nombre}'
