from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import subprocess
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

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



@csrf_exempt
def sync_databases_view(request):
    if request.method == 'POST':
        try:
            # Ejecutar el script de sincronización
            subprocess.run(['python', 'core/sync_db.py'], check=True)
            return JsonResponse({'status': 'success', 'message': 'Sincronización completada con éxito.'})
        except subprocess.CalledProcessError as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})