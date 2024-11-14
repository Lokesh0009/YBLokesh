from django.urls import path
from portfolio.views import *

urlpatterns = [
    path('', welcomePage_view, name="welcomePage"),
    path('blog', blog_list, name='blog_list'),
    path('blog/create/new/', blog_create, name='blog_create'),
    path('blog/details/<str:id>/', blog_detail, name='blog_detail'),
    path('blog/delete/<str:post_id>/', delete_post, name='delete_post'),
    # path('remove-tag/<int:tag_id>/', remove_tag, name='remove_tag'),
    path('track_analytics/', track_analytics, name = 'track_analytics')
]