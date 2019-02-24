import datetime

from django.utils import timezone
from django.db.models import Sum
from django.shortcuts import render_to_response
from read_record.utils import get_seven_days_read_data, get_today_hot_data, get_yesterday_hot_data
from django.contrib.contenttypes.models import ContentType
from blog.models import Blog


def home(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    dates, read_nums = get_seven_days_read_data(blog_content_type)
    today_hot_datas = get_today_hot_data(blog_content_type)
    yesterday_hot_datas = get_yesterday_hot_data(blog_content_type)
    context = {}
    context['dates'] = dates
    context['read_nums'] = read_nums
    context['today_hot_datas'] = today_hot_datas
    context['yesterday_hot_datas'] = yesterday_hot_datas
    context['hot_blogs_7_days'] = get_7_days_hot_blogs()
    return render_to_response('home.html',  context)

def get_7_days_hot_blogs():
    today = timezone.now().date()

    date = today - datetime.timedelta(days=7)
    blogs = Blog.objects\
                .filter(read_details__date__lt=today, read_details__date__gte=date) \
                .values('id', 'title') \
                .annotate(read_num_sum=Sum('read_details__read_num')) \
                .order_by('-read_num_sum')
    print(blogs)
    return blogs[:7]



