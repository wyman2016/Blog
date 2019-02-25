from django.db import models
from blog.models import Blog
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User

# Create your models here.
class Comment(models.Model):

    # contentType关联
    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # comment相关
    text = models.TextField(default='')
    comment_time = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        ordering = ['-comment_time']