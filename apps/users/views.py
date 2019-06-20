import json

from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django_redis import get_redis_connection
from django.contrib.auth import login
# Create your views here.

from utils.json_func import to_json_data
from utils.res_code import Code, error_map
from . import forms
from users.models import Users



class RegisterView(View):

    """
    /users/register/
    用户注册
    """
    def get(self, request):
        return render(request, 'users/register.html')

    def post(self, request):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))
        form = forms.RegisterForm(dict_data)
        if form.is_valid():
            username = form.cleaned_data.get('username', None)
            password = form.cleaned_data.get('password', None)
            mobile = form.cleaned_data.get('mobile', None)

            user = Users.objects.create_user(username=username, password=password, mobile=mobile)
            login(request, user)
            return to_json_data(errmsg="注册成功")

        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)

            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)


class LoginView(View):
    """
    /users/login/
    用户登录视图
    """
    def get(self, request):
        return render(request, 'users/login.html')

    def post(self, request):
        # 获取前端传来的数据
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        dict_data = json.loads(json_data.decode('utf-8'))
        # 将request传递给form表单
        form = forms.LoginForm(data=dict_data, request=request)
        # form验证的时候已经用login（）方法登录了
        if form.is_valid():
            return to_json_data(errmsg='登陆成功')
        else:
            err_msg_list = []
            for item in forms.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串
            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)










