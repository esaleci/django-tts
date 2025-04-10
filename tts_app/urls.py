from django.urls import path
from . import views

app_name = 'tts_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('convert/', views.convert_text, name='convert'),
    path('history/', views.history, name='history'),
]