from django.shortcuts import render
from django.views.generic import View
# Create your views here.

def login(request):
    method=request.method
    if method=="POST":
        USER_INPUT = []
        user  = request.POST.get('user',None)
        email = request.POST.get('email',None)
        temp = {'user':user,'email':email}
        USER_INPUT.append(temp)
        return render(request,'login.html',{'data':USER_INPUT})
    else:
        return render(request,'python_weixin/login.html')

