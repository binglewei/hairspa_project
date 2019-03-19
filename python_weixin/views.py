from django.shortcuts import render
from django.views.generic import View
# Create your views here.

from django.shortcuts import *
from response import JSONResponse
def login(request):
    method=request.method
    print  "method====",method
    print  "request.mate====",request.META
    if method=="POST":
        USER_INPUT = []
        user  = request.POST.get('user',None)
        email = request.POST.get('email',None)
        temp = {'user':user,'email':email}
        USER_INPUT.append(temp)
        return render(request,'python_weixin/login.html',{'data':USER_INPUT})
    else:
        return render(request,'python_weixin/login.html')

def checkSignature(request):
    respones_param={}
    params=request.GET.items()
    for i in params:
        key=i[0]
        values=i[1]
        respones_param[key]=values
    return JSONResponse(respones_param)