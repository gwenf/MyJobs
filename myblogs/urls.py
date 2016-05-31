from django.conf.urls import patterns, url, include

from myblogs import views

urlpatterns = patterns(
    '',
    url(r'^new$', views.create_blog_entry, name='create_blog_entry'),
    url(r'^rss$', views.BlogFeed(), name='blog_rss_feed'),
    url(r'^', views.view_blog, name='view_blog'),
)
