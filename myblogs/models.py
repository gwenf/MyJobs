from datetime import datetime
from django.db import models
from ckeditor.fields import RichTextField

# Create your models here.

class BlogEntry(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField(max_length=1000)
    published_on = models.DateTimeField(default=datetime.now, null=True)
    last_edited = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey('myjobs.User')
    site = models.ForeignKey('seo.SeoSite')
    tags = models.ManyToManyField('mypartners.Tag', null=True)
    # TODO: comments
