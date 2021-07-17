# -*- coding: utf-8 -*-
# @time :2021/7/15 11:58
from django.urls import path

from .views import RegisterView, ImageCodeView, SmsCodeView

# users子应用视图路由的配置

urlpatterns = [
    # path的第一个路由,及视图函数
    path('register/',RegisterView.as_view(),name='register'),

    # 图片验证码路由
    path('imagecode/',ImageCodeView.as_view(),name='imagecode'),
    # 短信发送
    path('smscode/',SmsCodeView.as_view(),name='smscode'),
]