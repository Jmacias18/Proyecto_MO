# procesos/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Procesos
from .forms import ProcesosForm
from django.contrib import messages

class ProcesosListView(ListView):
    model = Procesos
    template_name = 'procesos/procesos_list.html'
    context_object_name = 'procesos'

class ProcesosCreateView(CreateView):
    model = Procesos
    form_class = ProcesosForm
    template_name = 'procesos/procesos_form.html'
    success_url = reverse_lazy('procesos:procesos_list')

class ProcesosUpdateView(UpdateView):
    model = Procesos
    form_class = ProcesosForm
    template_name = 'procesos/procesos_form.html'
    success_url = reverse_lazy('procesos:procesos_list')

def activar_desactivar_proceso(request, pk):
    proceso = get_object_or_404(Procesos, pk=pk)
    proceso.estado_pro = not proceso.estado_pro
    proceso.save()
    return redirect('procesos:procesos_list')
