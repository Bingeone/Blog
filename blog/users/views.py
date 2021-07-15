from django.shortcuts import render

# Create your views here.
from django.views import View


# 定义注册页面
class RegisterView(View):

    def get(self, request):
        return render(request, 'register.html')
