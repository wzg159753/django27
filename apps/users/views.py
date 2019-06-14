from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django_redis import get_redis_connection
# Create your views here.



class RegisterView(View):

    def get(self, request):
        return render(request, 'users/register.html')




