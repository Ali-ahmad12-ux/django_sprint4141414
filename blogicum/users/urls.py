from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),

    path('profile/', views.profile_view, name='my_profile'),
    path('profile/<str:username>/', views.user_profile, name='profile'),

    path('login/',
         auth_views.LoginView.as_view(
             template_name='registration/login.html'
         ),
         name='login'),
    path('logout/',
         auth_views.LogoutView.as_view(
             template_name='registration/logged_out.html'
         ),
         name='logout'),
    path('password_change/',
         auth_views.PasswordChangeView.as_view(
             template_name='registration/password_change_form.html'
         ),
         name='password_change'),
    path('password_change/done/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='registration/password_change_done.html'
         ),
         name='password_change_done'),
]
