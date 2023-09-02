from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse

# Create your views here.
class IndexVIew(View):
    def get(self, request):
        return render(request, 'index.html')

