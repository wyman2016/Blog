import datetime
from django.utils import timezone

from django.contrib.contenttypes.models import ContentType
from .models import ReadNum, ReadDetail
from django.db.models import Sum


# 用来管理阅读次数存储过程
def read_statistics_one_read(request, obj):
    ct = ContentType.objects.get_for_model(obj)
    key = "%s_%s_read" % (ct.model, obj.pk)

    if not request.COOKIES.get(key):
        # 计数+1  get_or_create 返回的是一个元祖
        readnum, created = ReadNum.objects.get_or_create(content_type=ct, object_id=obj.pk)
        readnum.read_num += 1
        readnum.save()

        # 当天阅读数计数+1
        readnum_detail, created = ReadDetail.objects.get_or_create(content_type=ct, object_id=obj.pk,
                                                                   date=timezone.now().date())
        readnum_detail.read_num += 1
        readnum_detail.save()

    return key


def get_seven_days_read_data(content_type):
    today = timezone.now().date()
    read_nums = []
    dates = []
    for i in range(6, -1, -1):
        date = today - datetime.timedelta(days=i)
        dates.append(date.strftime('%m/%d'))
        read_details = ReadDetail.objects.filter(content_type=content_type, date=date)
        read_sums = read_details.aggregate(read_num_sum=Sum('read_num'))
        read_nums.append(read_sums['read_num_sum'] or 0)
    return dates, read_nums


def get_today_hot_data(content_type):
    today = timezone.now().date()
    # 获取今日阅读统计数量
    read_details = ReadDetail.objects.filter(content_type=content_type, date=today).order_by('-read_num')
    return read_details[:3]


def get_yesterday_hot_data(content_type):
    today = timezone.now().date()
    yesterday = today - datetime.timedelta(days=1)
    # 获取今日阅读统计数量
    read_details = ReadDetail.objects.filter(content_type=content_type, date=yesterday).order_by('-read_num')
    return read_details[:3]


