from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('start/', views.start, name='start'),
    path('pause/', views.pause, name='pause'),
    path('resume/', views.resume, name='resume'),
    path('stop/', views.stop, name='stop'),
    path('remove/', views.remove, name='remove'),
    path('es/', views.es, name='es'),
    path('ds/', views.ds, name='ds'),
    path('list/', views.list, name='list'),
    path('pss/', views.pss, name='pss'),
    path('view/', views.report, name='view'),
    path('spstart/', views.spstart, name='spstart')

    ]