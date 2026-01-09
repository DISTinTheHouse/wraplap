from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import OrdenServicio


class OrdenServicioTests(TestCase):
    def test_crea_folio_unico(self):
        orden = OrdenServicio.objects.create(
            cliente_nombre='Cliente',
            vehiculo_marca='Ferrari',
            vehiculo_modelo='Roma',
            vehiculo_anio=2024,
            vehiculo_color='Rojo',
            servicio=OrdenServicio.Servicio.WRAP,
            estatus=OrdenServicio.Estatus.RECIBIDO,
        )
        self.assertTrue(orden.folio)

    def test_seguimiento_por_folio(self):
        orden = OrdenServicio.objects.create(
            cliente_nombre='Cliente',
            vehiculo_marca='Lamborghini',
            vehiculo_modelo='Huracan',
            vehiculo_anio=2023,
            vehiculo_color='Negro',
        )
        res = self.client.get(reverse('seguimiento_detalle', kwargs={'folio': orden.folio}))
        self.assertEqual(res.status_code, 200)


class DashboardAuthTests(TestCase):
    def test_dashboard_requiere_superuser(self):
        res = self.client.get(reverse('dashboard'))
        self.assertEqual(res.status_code, 302)

    def test_login_rechaza_usuario_no_superuser(self):
        User = get_user_model()
        User.objects.create_user(username='normal', password='pass12345')
        res = self.client.post(reverse('login'), {'username': 'normal', 'password': 'pass12345'})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Solo el superuser puede iniciar sesión.')
