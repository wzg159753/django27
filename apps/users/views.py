from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
# Create your views here.

class RegisterView(View):

    def get(self, request):

        return render(request, 'users/register.html')



class ImageCodeView(View):

    def get(self, request, image_code_id):
        # 接入图片验证码接口
        text, image_bytes = None
        connect = get_redis_connect('veriftions')
        img_key = f'img_{image_code_id}'
        connect.setex(img_key, 300, text)
        return HttpResponse(content=image_bytes, content_type='image/jpg')
