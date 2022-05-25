from django.urls import path

from . import views

app_name = 'trailcondition'
urlpatterns = [
    path('', views.index, name='index'),
    path('result/', views.result, name='result'),
    path('about/', views.about, name='about'),
    path('trainer/', views.trainer, name='trainer'),
    path('trainerfinish/', views.trainerfinish, name='trainerfinish')
]