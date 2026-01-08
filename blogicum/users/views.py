from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model

User = get_user_model()

class RegistrationView(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'registration/registration.html'
    success_url = reverse_lazy('blog:index')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response
