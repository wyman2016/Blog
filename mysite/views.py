import datetime
from django.urls import reverse

from django.contrib import auth
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Sum
from django.shortcuts import render, redirect

from mysite.form import LoginForm, RegistForm
from read_record.utils import get_seven_days_read_data, get_today_hot_data, get_yesterday_hot_data
from django.contrib.contenttypes.models import ContentType
from blog.models import Blog
from django.core.cache import cache
from . import form

def home(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    dates, read_nums = get_seven_days_read_data(blog_content_type)
    today_hot_datas = get_today_hot_data(blog_content_type)
    yesterday_hot_datas = get_yesterday_hot_data(blog_content_type)

    # 获取7天数据缓存,如果获取不到,那么读取缓存
    seven_hot_datas = cache.get('hot_blogs_7_days')
    if seven_hot_datas is None:
        seven_hot_datas = get_7_days_hot_blogs()
        cache.set('hot_blogs_7_days', seven_hot_datas, 3600)
        print('uer cache 用的计算')
    else:
        print('uer cache 用的缓存')

    context = {}
    context['dates'] = dates
    context['read_nums'] = read_nums
    context['today_hot_datas'] = today_hot_datas
    context['yesterday_hot_datas'] = yesterday_hot_datas
    context['hot_blogs_7_days'] = seven_hot_datas
    return render(request, 'home.html', context)


def login(request):
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        # 进行django-form验证,验证通过后,通过auth登陆
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            auth.login(request, user)
        return redirect(request.GET.get('form', reverse('home')))
    else:
        # 失败返回form,里面包含了一些djangfo-form表单所需要的失败信息,比如提示
        login_form = LoginForm()

    context = {}
    context['login_form'] = login_form
    return render(request, 'login.html', context)

def register(request):
    if request.method == 'POST':
        regist_form = RegistForm(request.POST)
        # 进行django-form验证,验证通过后,通过auth存储新用户数据
        if regist_form.is_valid():
            username = regist_form.cleaned_data['username']
            password = regist_form.cleaned_data['password']
            email = regist_form.cleaned_data['email']
            user = User.objects.create_superuser(username=username, email=email, password=password)
            user.save()
            # 存储完用户数据后,登陆
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)
            # reverse('home'): 如果没有form参数,默认返回首页
            return redirect(request.GET.get('form', reverse('home')))
    else:
        # 失败返回form,里面包含了一些djangfo-form表单所需要的失败信息,比如提示
        regist_form = RegistForm()

    context = {}
    context['regist_form'] = regist_form
    return render(request, 'register.html', context)



def get_7_days_hot_blogs():
    today = timezone.now().date()

    date = today - datetime.timedelta(days=7)
    # values: 提取相关属性
    # annotate: 统计同一条blog下面所有不同日期read_details的和
    blogs = Blog.objects \
        .filter(read_details__date__lt=today, read_details__date__gte=date) \
        .values('id', 'title') \
        .annotate(read_num_sum=Sum('read_details__read_num')) \
        .order_by('-read_num_sum')
    return blogs[:3]
