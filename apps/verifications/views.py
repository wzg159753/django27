import logging

from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from django_redis import get_redis_connection

from utils.captcha.captcha import captcha
from . import constants
from utils.json_func import to_json_data
from users.models import Users
# Create your views here.

logger = logging.getLogger('django')


class ImageCodeView(View):
    """
    图片验证码
    /image_codes/<uuid:image_code>/
    """
    def get(self, request, image_code_id):
        # 接入图片验证码接口
        text, image_bytes = captcha.generate_captcha()
        connect = get_redis_connection('verify_codes')
        img_key = f'img_{image_code_id}'
        logger.info(f'图片验证码：{text}')
        connect.setex(img_key, constants.IMAGE_CODE_REDIS_EXPIRES, text)
        return HttpResponse(content=image_bytes, content_type='image/jpg')


class CheckUserNameView(View):
    """
    验证用户名
    /usernames/(?P<username>\w{5,9})/
    """
    def get(self, request, username):
        count = Users.objects.filter(username=username).count()
        data = {
            'username': username,
            'count': count
        }
        return to_json_data(data=data)

class CheckMobileView(View):
    """
    验证手机号
    /mobiles/(?P<mobile>1[3-9]\d{9})/
    """
    def get(self, request, mobile):
        count = Users.objects.filter(mobile=mobile).count()
        data = {
            'mobile': mobile,
            'count': count
        }
        return to_json_data(data=data)