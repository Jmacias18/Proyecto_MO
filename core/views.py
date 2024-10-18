from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

@method_decorator(login_required, name='dispatch')
class HomePageView(TemplateView):
    template_name = "core/home.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Sana Premium Foods"
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name,{'title': 'Captura de Horas de Mano de Obra'})

class SamplePageView(TemplateView):
    template_name = "core/sample.html"

