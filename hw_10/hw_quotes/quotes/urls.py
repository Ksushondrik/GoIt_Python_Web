from django.urls import path

from . import views

app_name = 'quotes'

urlpatterns = [
    path('', views.main, name="root"),
    path('<int:page>', views.main, name='root_paginate'),
    path('author/<str:author_name>/', views.author_detail, name='author_detail'),
    path('tag/<str:tag_name>/', views.tag_detail, name='tag_detail'),
    path('add_author/', views.add_author, name='add_author'),
    path('add_quote/', views.add_quote, name='add_quote'),
]
