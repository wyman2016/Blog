from django.shortcuts import render, redirect
from .models import Comment
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse


def update_comment(request):
    # 获取跳转过来的网页地址 reverse: 将name反转成地址
    referer = request.META.get('HTTP_REFERER', reverse('home'))
    if not request.user.is_authenticated:
        return render(request, 'error.html', {'message': '用户未登录', 'redirect_to': referer})

    text = request.POST.get('text', '').strip()

    # 如果评论为空
    if text == '':
        return render(request, 'error.html', {'message': '评论内容为空', 'redirect_to': referer})

    # 获取contenttype
    # 不直接用Blog,是因为可能评论的对象不止是Blog,方便扩展
    try:
        content_type = request.POST.get('content_type', '')
        object_id = int(request.POST.get('object_id', ''))
        model_class = ContentType.objects.get(model=content_type).model_class()
        model_object = model_class.objects.get(pk=object_id)
    except Exception as e:
        return render(request, 'error.html', {'message': '评论对象不存在', 'redirect_to': referer})

    comment = Comment()
    comment.user = request.user
    comment.text = text
    comment.content_object = model_object
    comment.save()
    return redirect(referer)
