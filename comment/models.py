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
    comment_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    # related_name 区分外键 用related_name命别名
    root = models.ForeignKey('self', related_name='root_comment', null=True, on_delete=models.DO_NOTHING)
    parent = models.ForeignKey('self', related_name='parent_comment', null=True, on_delete=models.DO_NOTHING)
    reply_to = models.ForeignKey(User, related_name='reply_to', null=True, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['comment_time']