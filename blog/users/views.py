from django.shortcuts import render

# Create your views here.
from django.views import View
from django.http.response import HttpResponseBadRequest
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from django.http import HttpResponse
from django.http.response import JsonResponse
from utils.response_code import RETCODE
from random import randint
from libs.yuntongxun.sms import CCP

import logging

logger = logging.getLogger('django')


# 定义注册页面
class RegisterView(View):

    def get(self, request):
        return render(request, 'register.html')


class ImageCodeView(View):

    def get(self, request):
        """
        1、接受前端传递过来的uuid
        2、判断uuid是否获取到
        3、通过调用captcha 来生成图片验证码（图片的二进制和图片内容）
        4、将图片内容保存到redis中
            uuid作为一个key，图片内容作为一个value ，同时需要设置图片的时效
        5、返回图片二进制
        :param request:
        :return:
        """
        pass
        # 1、接受前端传递过来的uuid
        uuid = request.GET.get('uuid')
        # 2、判断uuid是否获取到
        if uuid is None:
            return HttpResponseBadRequest("没有传递uuid")
        # 3、通过调用captcha 来生成图片验证码（图片的二进制和图片内容）
        text, image = captcha.generate_captcha()
        # 4、将图片内容保存到redis中
        redis_conn = get_redis_connection("default")
        # key, 设置uuid
        # seconds, 设置时效300
        # value, text
        #     uuid作为一个key，图片内容作为一个value ，同时需要设置图片的时效
        redis_conn.setex('img:%s' % uuid, 300, text)
        # 5、返回图片二进制
        return HttpResponse(image, content_type='image/jpeg')


class SmsCodeView(View):

    def get(self, request):
        """
        1、接受参数
        2、参数的验证
            2.1验证参数是否齐全
            2.2图片验证码的验证
                连接redis，获取redis的中的图片验证码
                判断图片验证码是否存在
                如果图片验证码未过期，我们获取到之后就可以删除图片验证码
                比对图片验证码
        3、生成短息验证码
        4、保存短息验证码到redis中
        5、返回响应
        :param request:
        :return:
        """
        # 1、接受参数
        mobile = request.GET.get('mobile')
        image_code = request.GET.get('image_code')
        uuid = request.GET.get('uuid')
        # 2、参数的验证
        #     2.1验证参数是否齐全
        if not all([mobile, image_code, uuid]):
            return JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '缺少必要的参数'})
        #     2.2图片验证码的验证
        #         连接redis，获取redis的中的图片验证码
        redis_conn = get_redis_connection('default')
        redis_image_code = redis_conn.get('img:%s' % uuid)
        #         判断图片验证码是否存在
        if redis_image_code is None:
            return JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图片验证码过期'})
        #         如果图片验证码未过期，我们获取到之后就可以删除图片验证码
        try:
            redis_conn.delete('img:%s' % uuid)
        except Exception as e:
            logger.error(e)
        #         比对图片验证码,大小写的问题，redis的数据bytes类型
        if redis_image_code.decode().lower() != image_code.lower():
            return JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图片验证码有误'})

        # 3、生成短息验证码
        sms_code = '%06d' % randint(0, 999999)
        # 方便后期比对方便，将短信息验证码记录到日志中
        logger.info(sms_code)
        # 4、保存短息验证码到redis中
        redis_conn.setex('sms:%s' % mobile, 300, sms_code)
        # 5、发短信
        # 参数1： 测试手机号
        # 参数2： 列表
        # 1 短信验证码 2 有效期
        # 参数3： 免费开发测试使用的模板ID为1
        CCP().send_template_sms(mobile, [sms_code, 5], 1)
        # 6、返回响应
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '短信发送成功'})
