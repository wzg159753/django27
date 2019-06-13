from django.shortcuts import render
from django.http import HttpResponse
from django.views import View

# Create your views here.

class NewsIndexView(View):
    """
    首页
    """
    def get(self, request):
        return render(request, 'news/index.html')