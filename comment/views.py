from django.shortcuts import render
from .models import Comment


# Create your views here.
from django.urls import reverse


def update_comment(request):
    referer = request.META.get('HTTP_REFERER', reverse('home'))


    comment = Comment()
    comment.user = request.user
    comment.text = request.GET('text' ,'')
    pass