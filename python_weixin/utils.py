# -*- coding: utf-8 -*-
import hashlib
from celery import task 
import json,logging, copy
from django.utils.encoding import force_unicode
from django.db.models.base import ModelBase
from dateutil import rrule   
import datetime ,time
import requests
import re ,os,django
import zipfile
from celery import Celery

from django.core.mail import send_mail,EmailMessage

from django.contrib.auth.models import *
from django.utils.timezone import localtime
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
class LazyJSONEncoder(json.JSONEncoder):
    """ a JSONEncoder subclass that handle querysets and models objects.
    Add how handle your type of object here to use when when dump json"""
    def default(self,o):
        # this handles querysets and other iterable types
        try:
            iterable = iter(o)
        except TypeError:
            pass
        else:
            return list(iterable)
 
        # this handlers Models
        try:
            isinstance(o.__class__,ModelBase)
        except Exception:
            pass
        else:
            return force_unicode(o)
 
        return super(LazyJSONEncoder,self).default(obj)
 
def serialize_to_json(obj,*args,**kwargs):
    """ A wrapper for json.dumps with defaults as:
 
    ensure_ascii=False
    cls=LazyJSONEncoder
 
    All arguments can be added via kwargs
    """
    kwargs['ensure_ascii'] = kwargs.get('ensure_ascii',False)
    kwargs['cls'] = kwargs.get('cls',LazyJSONEncoder)
 
 
    return json.dumps(obj,*args,**kwargs)

def qdct_as_kwargs(qdct):
    kwargs={}
    for k,v in qdct.items():
        kwargs[str(k)]=v
    return kwargs
    
def workdays(start, end, holidays=0, days_off=None):  
    if days_off is None:  
        days_off = []              # 默认：周六和周日  
    workdays = [x for x in range(7) if x not in days_off]  
    days = rrule.rrule(rrule.DAILY, dtstart=start, until=end,  
                                byweekday=workdays)  
    return days.count( ) - holidays 

def checkname(name):
    user_list = []
    name_list = name.split(';')
    for name in name_list:   
        if not name:continue
        if transform_first_name(name):
            user_list.append(transform_first_name(name))
        elif Group_to_UserName(name):
            user_list.append(Group_to_UserName(name))
        else:
            return 0,name
    return 1,disrepeat((';').join(user_list))
def read_holidays(start, end, holidays_file=BASE_DIR+r'/clientmanage_v2/holidays'):  
      # 返回在开始和结束日期之间的假期列表  
      try:  
            holidays_file = open(holidays_file)  
      except IOError, err:  
            print 'cannot read holidays (%r):' % (holidays_file,), err  
            return [  ]  
      holidays = [  ]  
      for line in holidays_file:  
            # 跳过空行和注释  
            if line.isspace( ) or line.startswith('#'):  
                  continue  
            # 试图解析格式：YYYY-M-D  
            try:  
                  y, m, d = [int(x.strip( )) for x in line.split('-')]  
                  date = datetime.date(y, m, d)  
            except ValueError:  
                  # 检测无效行并继续  
                  print "Invalid line %r in holidays file %r" % (  
                          line, holidays_file)  
                  continue  
            if start<=date<=end:  
                  holidays.append(date)  
      holidays_file.close( )  
      return holidays
      
def Group_to_UserName(group):

    user_list = []
    group_list = group.split(';')
    for group in group_list:
        try:
            group = Group.objects.get(name=group)
            users = group.user_set.all()
            for one in users:
                user_list.append(one.first_name)
        except:
            continue
    return disrepeat((';').join(user_list))
    
@task 
def rtx(userName,title,content,is_cc = True):

    url = 'http://officeApi.kugou.net/sendRtxByPost'
    appId = 15
    appKey = 'UEtAz8URLwyUnTWm'
    userName = transform_englishname(userName)
    if not userName:return
    if is_cc:
        userName += ";huanxiongli;"
    payload = dict((['appId', appId],['appKey', appKey],
        ['userName', userName],['title', title],['content', content],))
    r = requests.post(url=url, data=payload)


def msg(to,content):

    url = 'http://officeApi.kugou.net/sendMsgByPost'
    to = to
    content = content
    payload = dict((['to', to],['content', content],))

    r = requests.post(url=url, data=payload)

def timestamp_to_ms():
    str_time = time.time()
    return str_time
def trans_mail(userName):
    mail_to = []
    if userName:
        mail_to = []
        for ele in get_user_by_name(userName):
            mail_to.append(ele.email)
        return mail_to
    else:
        return ''
@task
def mail(userName,subject,content,sender=None,attach_filepath=None,html=None,cc=None):
    mail_to = []
    mail_cc = []
    if userName:
        
        mail_to = trans_mail(userName)
    if cc:
        mail_cc = trans_mail(cc)
    if sender:
        sender = User.objects.get(first_name=sender)
        sender_email = "%s <%s>" % (sender.last_name, sender.email)

    else:
        sender_email = "%s <%s>" % ('MTP', 'mtp@kugou.net')
    email = EmailMessage(subject, content, sender_email,mail_to,cc = mail_cc)
    if html:
        email.content_subtype = "html"
    if attach_filepath:
        email.attach_file(attach_filepath)
    email.send()
    

    
def disrepeat(userName):
    if userName:
        userName = userName.strip()
        user_temp_list = userName.split(';')
        user_distinct_list = []
        for temp_list in user_temp_list:
            if temp_list not in user_distinct_list:
                user_distinct_list.append(temp_list)
        new_list = [ x for x in user_distinct_list if x != '' ]#
        userName = (';').join(new_list)
        return userName
    else:
        return '' 
def transform_englishname(s):
    if s:
        name_list = []
        for ele in get_user_by_name(s):
            name_list.append(ele.username)
        return (';').join(name_list)
    else:
        return ''
def transform_chinesename(s):
    if s:
        name_list = []
        for ele in get_user_by_name(s):
            name_list.append(ele.last_name)
        return (';').join(name_list)
    else:
        return ''

def transform_chinesename_2(s):
    if s:
        name_list = []
        import re
        patt = re.compile(r"\((.*?)\)", re.I | re.X)
        name_list = patt.findall(s)
        return (';').join(name_list)
    else:
        return ''
def get_user_by_name(name):
    if not name:return ''
    name = name.strip().split(';')
    name_list = []
    for ele in name:
        if not ele :continue
        try:
            user = User.objects.get(first_name=ele)
        except:
            try:
                user = User.objects.get(last_name = ele)
            except:
                try:
                    user = User.objects.get(username=ele)
                except:
                    continue
        if user in name_list:continue
        name_list.append(user)
    return name_list
def transform_first_name(s):
    if s:
        name_list = []
        for ele in get_user_by_name(s):
            name_list.append(ele.first_name)
        return (';').join(name_list)
    else:
        return '' 
    
def timestamp_to_date(timestr):
    y, m, d = [int(x.strip( )) for x in timestr.split('-')]
    date =  datetime.date(y, m, d)
    return date
    
def timestamp_to_time():
    str_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    return str_time
    
def timestamp_time_str():
    str_time = time.strftime('%Y-%m-%d-%H:%M:%S',time.localtime(time.time()))
    return str_time
def diff(start = None,end = None):
    if start:
        start = timestamp_to_date(start)
    else:
        start = timestamp_to_date(timestamp())
    if end:
        end = timestamp_to_date(end)
    else:
        end = timestamp_to_date(timestamp())
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    holidays_file = BASE_DIR+r'/clientmanage_v2/holidays'
    if start<=end:
        holidays = read_holidays(start,end,holidays_file)
        diff = workdays(start,end,len(holidays))
    else:
        holidays = read_holidays(end,start,holidays_file)
        diff = workdays(end,start,len(holidays))
        diff = -diff
    return diff
def isholiday(str_time = None):#str_time格式 '%Y-%m-%d'
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    holidays_file = BASE_DIR+r'/clientmanage_v2/holidays'
    str_time = timestamp() if not str_time else str_time
    try:
        holidays_file = open(holidays_file)  

                # 跳过空行和注释
    except IOError, err:
        print 'cannot read holidays (%r):' % (holidays_file,), err
        return False    
    for line in holidays_file:  
        if line.isspace( ) or line.startswith('#'):  
              continue  
        else:
            if str_time in line.strip('\n'):
                return True
    return False   
def workday_n_later(n, str_time = None):#str_time格式 '%Y-%m-%d'
    day = datetime.datetime.strptime(str_time, '%Y-%m-%d') \
            if str_time else datetime.date.today()
    while n>0:
        day = day + datetime.timedelta(days=1)
        if not isholiday(day.strftime('%Y-%m-%d')):
            n -= 1
    return day
def workday_distance(start, end):
    '''
    与diff不同的
    start=end时候，不返回1，返回0
    '''
    diff_distance = diff(start, end)
    if diff_distance > 0:
        return diff_distance - 1
    elif diff_distance == 0:
        return diff_distance
    else:
        return diff_distance + 1

def timestamp():
    str_time = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    return str_time
    
def date_diff(date):
    str_time = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    return str_time <= date   
def blue(str):
    star_str = '<font  color="blue">'
    end_str = '</font>'
    return star_str + ' ' + str + ' '+ end_str


def red(str):
    star_str = '<font  color="red">'
    end_str = '</font>'
    return star_str + ' ' + str + ' ' + end_str


def zip_dir(dirname,zipfilename):
    filelist = []
    if os.path.isfile(dirname):
        filelist.append(dirname)
    else :
        for root, dirs, files in os.walk(dirname):
            for name in files:
                filelist.append(os.path.join(root, name))
         
    zf = zipfile.ZipFile(zipfilename, "w", zipfile.zlib.DEFLATED)
    for tar in filelist:
        arcname = tar[len(dirname):]
        #print arcname
        zf.write(tar,arcname)
    zf.close()
   
def last_name_to_id(userName):
    id_list = []
    if userName:
        name_list = []
        for ele in get_user_by_name(userName):
            name_list.append(str(ele.id))
        return (';').join(name_list)
    else:
        return ''

def save_to_database(base_str):
    new_str = base_str.replace('\n','<br>') if base_str else ''
    return new_str
def readout_from_database(base_str):
    new_str = base_str.replace('\n','/@').replace('<br>','/@').replace('\\','/!').replace('&','/~').replace("'","\\'").replace("\'","%%").replace(">","/,").replace("<","/:").replace('"','@')
    return new_str 


def get_start_and_end_date_by_week(year, week, wanted='tuple'):
    d = datetime.date(year,1,1)
    d = d - datetime.timedelta(d.weekday()) - datetime.timedelta(days=1)
    dlt = datetime.timedelta(days = (week-0)*7)
    start, end = d+dlt, d+dlt+datetime.timedelta(days=6)
    return start, end
def get_start_and_end_date_by_month(year, month):
    import calendar,datetime
    FORMAT = "%d-%02d-%02d"
    d = calendar.monthrange(year, month)
    start_date = FORMAT % (year, month, 1)
    end_date = FORMAT % (year, month, d[1])
    return  start_date, end_date
    
def get_start_and_end_date_by_quarter(year,quarter):
    start_date = datetime.date(year,3*quarter-2,1)
    if quarter & 2 == 0 :end = 31
    else:end = 30
    end_date = datetime.date(year,3*quarter,end)
    return str(start_date)[0:10],str(end_date)[0:10]
    
def get_start_and_end_date_by_half_year(year,half):
    if half == 1:
        start_date = datetime.date(year,1,1)
        end_date = datetime.date(year,6,30)
    elif half == 2:
        start_date = datetime.date(year,7,1)
        end_date = datetime.date(year,12,31)
    return str(start_date)[0:10],str(end_date)[0:10]   
def get_start_and_end_date_by_year(year):
    start_date = datetime.date(year,1,1)
    end_date = datetime.date(year,12,31)
    return str(start_date)[0:10],str(end_date)[0:10]
    
def get_month_end(x, n=0):
    '''
    获取月末
    n表示几个月后
    '''
    # 找到n个月后的同一天
    while n>0:
        try:
            x = x.replace(month=x.month+1)
        except ValueError:
            if x.month == 12:
                x = x.replace(year=x.year+1, month=1)
            else:
                # next month is too short to have "same date"
                # pick your own heuristic, or re-raise the exception:
                # 以n月后的第一天代替
                x = x.replace(month=x.month+1, day=1)
        n -= 1

    if x.month == 12:
        return x.replace(day=31)
    return x.replace(month=x.month+1, day=1) - datetime.timedelta(days=1)
    
def get_day_end(x, n=0):
    '''
    获取日最后一秒
    n表示几日之后
    '''
    y = x + datetime.timedelta(days=n+1)
    y = y.replace(hour = 0, minute = 0, second = 0)
    z = y - datetime.timedelta(seconds = 1)
    return z

def get_day_start(x, n=0):
    y = x + datetime.timedelta(days=n)
    y = y.replace(hour = 0, minute = 0, second = 0)
    return y

def add_months(d, x):
    newmonth = ((( d.month - 1) + x ) % 12 ) + 1
    newyear  = d.year + ((( d.month - 1) + x ) / 12 ) 
    return datetime.date( newyear, newmonth, d.day)

def md5(str):
    m = hashlib.md5()
    m.update(str)
    return m.hexdigest()