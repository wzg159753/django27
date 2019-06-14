import json
import logging
import random
import string

from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from django_redis import get_redis_connection

from utils.captcha.captcha import captcha
from utils.res_code import Code, error_map
from . import constants
from utils.json_func import to_json_data
from users.models import Users
from utils.yuntongxun.sms import CCP
from . import forms
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


class SmsCodeView(View):
    """
    发送短信验证码
    /sms_codes/
    """
    def post(self, request):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
            # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))
        form = forms.CheckImgCodeForm(dict_data)

        if form.is_valid():
            mobile = form.cleaned_data.get('mobile', None)

            sms_num = ''.join([random.choice(string.digits) for _ in range(constants.SMS_CODE_NUMS)])

            sms_key = f'sms_{mobile}'
            sms_flag_key = f'sms_flag_{mobile}'
            try:
                conn = get_redis_connection(alias='verify_codes')
                pipline = conn.pipeline()
                pipline.setex(sms_key, constants.SMS_CODE_REDIS_EXPIRES, sms_num)
                pipline.setex(sms_flag_key, constants.SEND_SMS_CODE_INTERVAL, 1)
                pipline.execute()

                logger.info(f'短信验证码:{sms_num}')
                return to_json_data(errno=Code.OK, errmsg="短信验证码发送成功")

            except Exception as e:
                logger.error(f'验证码保存失败:{e}')
                return to_json_data(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR])

            # try:
            #     result = CCP().send_template_sms(mobile,
            #                                      [sms_num, constants.SMS_CODE_REDIS_EXPIRES],
            #                                      constants.SMS_CODE_TEMP_ID)
            # except Exception as e:
            #     logger.error("发送验证码短信[异常][ mobile: %s, message: %s ]" % (mobile, e))
            #     return to_json_data(errno=Code.SMSERROR, errmsg=error_map[Code.SMSERROR])
            # else:
            #     if result == 0:
            #         logger.info("发送验证码短信[正常][ mobile: %s sms_code: %s]" % (mobile, sms_num))
            #         return to_json_data(errno=Code.OK, errmsg="短信验证码发送成功")
            #     else:
            #         logger.warning("发送验证码短信[失败][ mobile: %s ]" % mobile)
            #         return to_json_data(errno=Code.SMSFAIL, errmsg=error_map[Code.SMSFAIL])

        else:
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
                # print(item[0].get('message'))   # for test
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串

            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)



