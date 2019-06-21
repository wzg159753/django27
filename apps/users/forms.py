import re
from django import forms
from django.contrib.auth import login
from django.db.models import Q
from django_redis import get_redis_connection

from users.models import Users
from users import constants


class RegisterForm(forms.Form):
    """
    用户注册表单验证
    """
    username = forms.CharField(label='用户名', max_length=20, min_length=5,
                               error_messages={"min_length": "用户名长度要大于5", "max_length": "用户名长度要小于20",
                                               "required": "用户名不能为空"}
                               )
    password = forms.CharField(label='密码', max_length=20, min_length=6,
                               error_messages={"min_length": "密码长度要大于6", "max_length": "密码长度要小于20",
                                               "required": "密码不能为空"}
                               )
    password_repeat = forms.CharField(label='确认密码', max_length=20, min_length=6,
                                      error_messages={"min_length": "密码长度要大于6", "max_length": "密码长度要小于20",
                                                      "required": "密码不能为空"}
                                      )
    mobile = forms.CharField(label='手机号', max_length=11, min_length=11,
                             error_messages={"min_length": "手机号长度有误", "max_length": "手机号长度有误",
                                             "required": "手机号不能为空"})

    sms_code = forms.CharField(label='短信验证码', max_length=6, min_length=6,
                               error_messages={"min_length": "短信验证码长度有误", "max_length": "短信验证码长度有误",
                                               "required": "短信验证码不能为空"})

    def clean_username(self):
        username = self.cleaned_data.get('username', '')
        if Users.objects.filter(username=username).exists():
            raise forms.ValidationError("用户名已存在")
        return username

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile', '')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return forms.ValidationError("手机号格式错误")

        if Users.objects.filter(mobile=mobile).exists():
            return forms.ValidationError("手机号已存在")

        return mobile

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password', None)
        password_repeat = cleaned_data.get('password_repeat', None)
        mobile = cleaned_data.get('mobile', None)
        sms_text = cleaned_data.get('sms_code')

        if password != password_repeat:
            raise forms.ValidationError("两次输入密码不一致")

        conn = get_redis_connection('verify_codes')
        sms_key = f'sms_{mobile}'
        sms_value = conn.get(sms_key)

        if (not sms_value) or (sms_text != sms_value.decode('utf8')):
            raise forms.ValidationError("短信验证码错误")


class LoginForm(forms.Form):
    """
        登录表单验证
        """
    # 因为可以传用户名和手机号进行登录，所以不需要设置其他属性
    user_account = forms.CharField()
    password = forms.CharField(label='密码', max_length=20, min_length=6, required=True,
                               error_messages={"min_length": "密码长度要大于6", "max_length": "密码长度要小于20",
                                               "required": "密码不能为空"})
    # 是否记住登录
    remember_me = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        # 注意这里一定要pop取值，自己测试用get会报错
        self.request = kwargs.pop('request', None)  # 获取view中实例化传来的request
        super(LoginForm, self).__init__(*args, **kwargs)  # 复用父类方法

    def clean_user_account(self):
        # 获取用户名或手机号
        user_account = self.cleaned_data.get('user_account')
        if not user_account:
            raise forms.ValidationError('用户名为空!')
        # 如果不是手机号 并且用户名小于5或大于20
        if not re.match(r"^1[3-9]\d{9}$", user_account) and ((len(user_account) < 5) or (len(user_account) > 20)):
            raise forms.ValidationError('用户名或手机号格式错误')

        return user_account

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        user_account = cleaned_data.get('user_account', None)
        password = cleaned_data.get('password')
        remember_me = cleaned_data.get('remember_me')

        # models的Q方法是进行or（或）查询，
        user_query = Users.objects.filter(Q(username=user_account) | Q(mobile=user_account))
        # 如果存在这个queryset（对象集合）
        if user_query:
            # 取集合中的对象
            user = user_query.first()
            # 用form的内置方法判断密码是否一致
            if user.check_password(password):
                # 判断是否点击前端 记住我
                if remember_me:
                    # 如果有点击，则设置 session过期时间为五天
                    self.request.session.set_expiry(constants.USER_SESSION_EXPIRES)
                else:
                    # 如果没点击则设置过期时间为关闭浏览器
                    self.request.session.set_expiry(0)

                # 登录 django内置登录 自动设置一条session 为user
                login(self.request, user)
            else:
                raise forms.ValidationError('密码错误')

        else:
            raise forms.ValidationError('用户名不存在')