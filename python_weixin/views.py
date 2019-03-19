from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.views.generic import View
# Create your views here.
# from  templates import *
class login(View):
    def get(self,request):
        return render(request,'login.html')
    def post(self,request):
        USER_INPUT = []
        user  = request.POST.get('user',None)
        email = request.POST.get('email',None)
        temp = {'user':user,'email':email}
        USER_INPUT.append(temp)
        return render(request,'login.html',{'data':USER_INPUT})