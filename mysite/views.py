import datetime

from django.contrib import auth
from django.utils import timezone
from django.db.models import Sum
from django.shortcuts import render, redirect
from read_record.utils import get_seven_days_read_data, get_today_hot_data, get_yesterday_hot_data
from django.contrib.contenttypes.models import ContentType
from blog.models import Blog
from django.core.cache import cache


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
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')

    user = auth.authenticate(request, username=username, password=password)
    if user is not None:
        auth.login(request, user)
        return redirect('/')
    else:
        return render(request, 'error.html', {'message':'用户名或密码不正确'})

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
