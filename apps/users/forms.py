import re
from django import forms
from django_redis import get_redis_connection

from users.models import Users


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
            return forms.ValidationError

        if Users.objects.filter(mobile=mobile).exists():
            return forms.ValidationError("手机号已存在")

        return mobile

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        password = cleaned_data.get('password', None)
        password_repeat = cleaned_data.get('password_repeat', None)
        mobile = cleaned_data.get('mobile', None)
        sms_text = cleaned_data.get('sms_text')

        if password != password_repeat:
            raise forms.ValidationError

        conn = get_redis_connection('verify_codes')
        sms_key = f'sms_{mobile}'
        sms_value = conn.get(sms_key)

        if (not sms_value) or (sms_text != sms_value.decode('utf8')):
            return forms.ValidationError("短信验证码错误")

