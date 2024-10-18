# usuarios/views.py
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

def staff_required(user):
    return user.is_staff

@method_decorator([login_required, user_passes_test(staff_required)], name='dispatch')
class UserListView(ListView):
    model = User
    template_name = 'usuarios/user_list.html'
    context_object_name = 'users'

@method_decorator([login_required, user_passes_test(staff_required)], name='dispatch')
class UserCreateView(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'usuarios/user_form.html'
    success_url = reverse_lazy('usuarios:user_list')

@method_decorator([login_required, user_passes_test(staff_required)], name='dispatch')
class UserUpdateView(UpdateView):
    model = User
    form_class = UserChangeForm
    template_name = 'usuarios/user_form.html'
    success_url = reverse_lazy('usuarios:user_list')

@method_decorator([login_required, user_passes_test(staff_required)], name='dispatch')
class UserDeleteView(DeleteView):
    model = User
    template_name = 'usuarios/user_confirm_delete.html'
    success_url = reverse_lazy('usuarios:user_list')