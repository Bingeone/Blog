# -*- coding: utf-8 -*-
# @time :2021/7/15 11:58
from django.urls import path
from .views import RegisterView

# users子应用视图路由的配置

urlpatterns = [
    # path的第一个路由,及视图函数
    path('register/',RegisterView.as_view(),name='register'),


]