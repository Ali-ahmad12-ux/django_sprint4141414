from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('registration/', views.RegistrationView.as_view(), name='registration'),
    path('register/', views.RegistrationView.as_view(), name='register'),  # أضف هذا
]
