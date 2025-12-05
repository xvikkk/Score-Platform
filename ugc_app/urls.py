# urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # 首页
    path('', views.IndexView.as_view(), name='index'),
    # 注册
    path('register/', views.RegisterView.as_view(), name='register'),
    # 登录与登出
    path('login/', auth_views.LoginView.as_view(template_name='ugc_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='ugc_app/logout.html'), name='logout'),
    # 个人主页
    path('personal/<str:username>/', views.PersonalView.as_view(), name='personal'),
    # 上传内容
    path('upload/', views.UploadView.as_view(), name='upload'),
    # 搜索
    path('search/', views.SearchView.as_view(), name='search'),
    # UGC内容详情
    path('ugc/<int:ugc_id>/', views.UGCDetailView.as_view(), name='ugc_detail'),
    path('ugc/<int:ugc_id>/rate/', views.RateUGCView.as_view(), name='rate_ugc'),
    path('ugc/<int:ugc_id>/discussion/', views.AddDiscussionView.as_view(), name='add_discussion'),
]