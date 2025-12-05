# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
import asyncio
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from .models import UserProfile, UGCItem, Rating, Discussion
from .forms import UserRegistrationForm, UGCItemForm, RatingForm, DiscussionForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

class IndexView(ListView):
    """首页视图，显示所有UGC内容"""
    model = UGCItem
    template_name = 'ugc_app/index.html'
    context_object_name = 'ugc_items'
    paginate_by = 10
    
    def get_queryset(self):
        # 获取排序参数
        sort_by = self.request.GET.get('sort', 'time')
        
        if sort_by == 'hot':
            return sorted(UGCItem.objects.all(), key=lambda x: x.hot, reverse=True)
        elif sort_by == 'top':
            return sorted(UGCItem.objects.all(), key=lambda x: x.top, reverse=True)
        else:
            return UGCItem.objects.all().order_by('-post_time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_sort'] = self.request.GET.get('sort', 'time')
        return context

class RegisterView(CreateView):
    """用户注册视图"""
    form_class = UserRegistrationForm
    template_name = 'ugc_app/register.html'
    success_url = reverse_lazy('index')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # 自动登录用户
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(self.request, user)
        
        messages.success(self.request, f'账号 {username} 创建成功！')
        return response

class PersonalView(LoginRequiredMixin, DetailView):
    """个人主页视图"""
    model = User
    template_name = 'ugc_app/personal.html'
    context_object_name = 'profile_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context['user_profile'] = UserProfile.objects.get(user=user)
        context['ugc_items'] = UGCItem.objects.filter(user=user).order_by('-post_time')
        return context

class UploadView(LoginRequiredMixin, CreateView):
    """上传内容视图"""
    model = UGCItem
    form_class = UGCItemForm
    template_name = 'ugc_app/upload.html'
    success_url = reverse_lazy('index')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, '内容上传成功！')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('personal', kwargs={'username': self.request.user.username})

class SearchView(ListView):
    """搜索视图"""
    model = UGCItem
    template_name = 'ugc_app/search.html'
    context_object_name = 'ugc_items'
    paginate_by = 5
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        sort_by = self.request.GET.get('sort', 'time')
        
        if query:
            ugc_items = UGCItem.objects.filter(
                Q(content__icontains=query)
            )
            
            # 根据排序参数进行排序
            if sort_by == 'hot':
                return sorted(ugc_items, key=lambda x: x.hot, reverse=True)
            elif sort_by == 'top':
                return sorted(ugc_items, key=lambda x: x.top, reverse=True)
            else:
                return ugc_items.order_by('-post_time')
        return UGCItem.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['current_sort'] = self.request.GET.get('sort', 'time')
        return context

class RateUGCView(LoginRequiredMixin, CreateView):
    """评分UGC内容视图"""
    model = Rating
    form_class = RatingForm
    template_name = 'ugc_app/rate.html'
    
    def get_success_url(self):
        return reverse_lazy('index')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ugc_item'] = get_object_or_404(UGCItem, id=self.kwargs['ugc_id'])
        return context
    
    def form_valid(self, form):
        ugc_item = get_object_or_404(UGCItem, id=self.kwargs['ugc_id'])
        score = form.cleaned_data['score']
        
        # 检查用户是否已经评分过
        rating, created = Rating.objects.get_or_create(
            ugc_item=ugc_item,
            user=self.request.user,
            defaults={'score': score}
        )
        
        if not created:
            # 如果已经评分过，更新评分
            rating.score = score
            rating.save()
            messages.info(self.request, '评分已更新！')
        else:
            messages.success(self.request, '评分成功！')
        
        return super().form_valid(form)

class AddDiscussionView(LoginRequiredMixin, CreateView):
    """添加评论视图"""
    model = Discussion
    form_class = DiscussionForm
    template_name = 'ugc_app/discussion.html'
    
    def get_success_url(self):
        return reverse_lazy('index')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ugc_item'] = get_object_or_404(UGCItem, id=self.kwargs['ugc_id'])
        return context
    
    def form_valid(self, form):
        ugc_item = get_object_or_404(UGCItem, id=self.kwargs['ugc_id'])
        form.instance.ugc_item = ugc_item
        form.instance.user = self.request.user
        messages.success(self.request, '评论发布成功！')
        return super().form_valid(form)

class UGCDetailView(DetailView):
    """UGC内容详情页视图"""
    model = UGCItem
    template_name = 'ugc_app/ugc_detail.html'
    context_object_name = 'ugc_item'
    pk_url_kwarg = 'ugc_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ugc_item = self.get_object()
        context['ratings'] = ugc_item.ratings.all()
        context['discussions'] = ugc_item.discussions.all().order_by('-comment_time')
        
        # 检查当前用户是否已评分
        user_rating = None
        if self.request.user.is_authenticated:
            try:
                user_rating = Rating.objects.get(ugc_item=ugc_item, user=self.request.user)
            except Rating.DoesNotExist:
                pass
        
        context['user_rating'] = user_rating
        return context