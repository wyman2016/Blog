from django.shortcuts import render, get_object_or_404

from comment.forms import CommentForm
from .models import Blog, BlogType
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models.aggregates import Count
from read_record.utils import read_statistics_one_read
from comment.models import Comment
from django.contrib.contenttypes.models import ContentType

padding_num = 2 #前后显示多少个页码

def blog_list(request):
    blogs_all_list = Blog.objects.all()
    context = blog_parm_caculate({'blogs_all_list':blogs_all_list,'request':request} )
    return render(request, 'blog/blog_list.html', context)


def blog_detail(request, blog_pk):

    blog = get_object_or_404(Blog, pk=blog_pk)
    # 获取content_type
    blog_content_type = ContentType.objects.get_for_model(blog)
    context = {}
    context['previous_blog'] = Blog.objects.filter(create_time__gt=blog.create_time).last()
    context['next_blog'] = Blog.objects.filter(create_time__lt=blog.create_time).first()
    context['blog'] = blog
    read_cookie_key = read_statistics_one_read(request, blog)
    respose = render(request, 'blog/blog_detail.html', context)
    # 只读次数存储到cookies,阅读标记
    respose.set_cookie(read_cookie_key, 'true')
    return respose


def blog_with_type(request, blog_type_pk):
    blog_type = get_object_or_404(BlogType, pk=blog_type_pk)
    blogs_all_list = Blog.objects.filter(blog_type=blog_type)
    context = blog_parm_caculate({'blogs_all_list':blogs_all_list,'request':request} )
    blog_type = get_object_or_404(BlogType, pk=blog_type_pk)
    context['blog_type'] = BlogType.objects.all()
    return render(request, 'blog/blog_with_type.html', context)

def blog_with_date(request, year, month):
    #通过年月筛选
    blogs_all_list = Blog.objects.filter(create_time__year=year, create_time__month=month)
    context = blog_parm_caculate({'blogs_all_list':blogs_all_list,'request':request} )

    context['blog_with_date_des'] = '%s年%s月' % (year,month)
    context['blog_date'] = Blog.objects.dates('create_time', 'month', order="DESC")
    return render(request, 'blog/blog_with_date.html', context)

def blog_parm_caculate(map):
    request = map['request']
    blogs_all_list = map['blogs_all_list']
    paginator = Paginator(map['blogs_all_list'], settings.EACH_PAGE_BLOGS_NUMBER) #pagesize:10
    page_number = request.GET.get('page', 1) #获取页码
    page_of_blogs = paginator.get_page(page_number) #得到博客
    current_page_num = page_of_blogs.number
    page_range = []

    #如果前面没有两个页码,那么久省略
    for index in range(padding_num*2+1):
        page_num_temp = current_page_num - padding_num + index
        if (page_num_temp) >= 1 and page_num_temp <= paginator.num_pages:
            page_range.append(current_page_num - padding_num + index)
        
    #添加第一页省略号,如果元素齐全后,还有多余
    if current_page_num - padding_num > 1:
        if current_page_num - padding_num != padding_num:
            page_range.insert(0,'..')
        page_range.insert(0,1)

    #添加最后一页省略号,如果元素齐全后,还有多余
    if paginator.num_pages - current_page_num > 2:
        if paginator.num_pages - current_page_num != padding_num + 1:
            page_range.append('..')
        page_range.append(paginator.num_pages)
    

     #获取日期归档对应的博客数量
    blog_dates_dic = {}
    blog_dates = Blog.objects.dates('create_time', 'month', order="DESC") 
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(create_time__year=blog_date.year,
                                         create_time__month=blog_date.month).count()
        blog_dates_dic[blog_date] = blog_count

    context = {}
    context['blogs'] = blogs_all_list
    context['page_range'] = page_range
    #获取博客类型下,blog的数量
    context['blog_types'] = BlogType.objects.annotate(type_blog_num = Count('blog'))
    context['blog_dates'] = blog_dates_dic
    context['page_of_blogs'] = page_of_blogs
    #返回值
    return context