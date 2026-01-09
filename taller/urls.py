from django.contrib.auth import views as auth_views
from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('seguimiento/', views.folio_lookup, name='folio_lookup'),
    path('seguimiento/<str:folio>/', views.seguimiento_detalle, name='seguimiento_detalle'),
    path('login/', views.SuperuserLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/nuevo/', views.orden_nueva, name='orden_nueva'),
    path('dashboard/<int:pk>/', views.orden_detalle, name='orden_detalle'),
    path('dashboard/<int:pk>/editar/', views.orden_editar, name='orden_editar'),
    path('dashboard/citas/nueva/', views.cita_nueva, name='cita_nueva'),
    path('dashboard/citas/<int:pk>/editar/', views.cita_editar, name='cita_editar'),
    path('dashboard/citas/<int:pk>/eliminar/', views.cita_eliminar, name='cita_eliminar'),
]

