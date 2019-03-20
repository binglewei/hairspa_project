from django.shortcuts import render
from django.views.generic import View
# Create your views here.

from django.shortcuts import *
from response import JSONResponse
import hashlib
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
    signature=request.GET.get("signature",None)
    timestamp=request.GET.get("timestamp",None)
    nonce=request.GET.get("nonce",None)
    echostr=request.GET.get("echostr",None)
    token="binglewei"
    # 字典序排序
    list = [token, timestamp, nonce]
    list.sort()
    sha1 = hashlib.sha1()
    map(sha1.update, list)
    hashcode = sha1.hexdigest()
    # sha1加密算法

    # 如果是来自微信的请求，则回复echostr
    if hashcode == signature:
        return echostr
    sorted_x = sorted(respones_param.iteritems(), key=lambda param: param[0])
    str_data=""
    for tuple in sorted_x:
        str_data += str(tuple[0]) + str(tuple[1])
    return JSONResponse(respones_param)