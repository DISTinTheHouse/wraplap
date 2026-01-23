from django.contrib import admin

from .models import Avance, OrdenServicio


@admin.register(OrdenServicio)
class OrdenServicioAdmin(admin.ModelAdmin):
    list_display = ('folio', 'cliente_nombre', 'vehiculo_marca', 'vehiculo_modelo', 'servicio', 'estatus', 'saldo_pendiente', 'actualizado_en')
    list_filter = ('servicio', 'estatus')
    search_fields = ('folio', 'cliente_nombre', 'vehiculo_marca', 'vehiculo_modelo')
    readonly_fields = ('folio', 'creado_en', 'actualizado_en', 'saldo_pendiente')


@admin.register(Avance)
class AvanceAdmin(admin.ModelAdmin):
    list_display = ('orden', 'estatus', 'creado_en')
    list_filter = ('estatus',)
    search_fields = ('orden__folio', 'orden__cliente_nombre')
