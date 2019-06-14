from django import forms
from django.core.validators import RegexValidator
from django_redis import get_redis_connection

from users.models import Users


mobile_validator = RegexValidator(r"^1[3-9]\d{9}$", "手机号码格式不正确")


class CheckImgCodeForm(forms.Form):
    mobile = forms.CharField(max_length=11, min_length=11, validators=[mobile_validator, ],
                             error_messages={"min_length": "手机号长度有误", "max_length": "手机号长度有误",
                                             "required": "手机号不能为空"})
    image_code_id = forms.UUIDField(error_messages={"required": "图片UUID不能为空"})
    text = forms.CharField(max_length=4, min_length=4,
                           error_messages={"min_length": "图片验证码长度有误", "max_length": "图片验证码长度有误",
                                           "required": "图片验证码不能为空"})


    def clean(self):
        cleaned_data = super().clean()
        mobile = cleaned_data.get('mobile', None)
        image_code_id = cleaned_data.get('image_code_id', None)
        text = cleaned_data.get('text', None)

        if Users.objects.filter(mobile=mobile).exists():
            raise ValueError('手机号已存在')

        img_code_key = f'img_{image_code_id}'
        conn = get_redis_connection('verify_codes')
        img_text_bytes = conn.get(img_code_key)
        result = img_text_bytes.decode('utf-8') if img_text_bytes else None

        if (not result) or (result != text):
            raise ValueError('图片验证失败')

        sms_flag_key = f'sms_flag_{mobile}'
        if conn.get(sms_flag_key):
            raise ValueError('用户操作过快，请稍后操作')

