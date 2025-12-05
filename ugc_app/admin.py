from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, UGCItem, Rating, Discussion

# 内联显示用户资料
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = '用户资料'

# 自定义用户管理
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)

# 评分内联显示
class RatingInline(admin.TabularInline):
    model = Rating
    extra = 0
    readonly_fields = ('rating_time',)
    fields = ('user', 'score', 'rating_time')

# 讨论内联显示
class DiscussionInline(admin.TabularInline):
    model = Discussion
    extra = 0
    readonly_fields = ('comment_time',)
    fields = ('user', 'content', 'comment_time')

# 内容管理
@admin.register(UGCItem)
class UGCItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content_preview', 'post_time', 'scored_display', 'rating_count', 'discussion_count', 'hot_display')
    list_filter = ('post_time', 'user')
    search_fields = ('content', 'user__username')
    readonly_fields = ('post_time', 'scored_display', 'rating_count', 'discussion_count', 'top_display', 'hot_display')
    inlines = [RatingInline, DiscussionInline]
    date_hierarchy = 'post_time'
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'image', 'content', 'post_time')
        }),
        ('统计信息', {
            'fields': ('scored_display', 'rating_count', 'discussion_count', 'top_display', 'hot_display'),
            'classes': ('collapse',)
        }),
    )
    
    def content_preview(self, obj):
        """内容预览"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '内容预览'
    
    def scored_display(self, obj):
        """显示平均评分"""
        return f"{obj.scored:.1f}"
    scored_display.short_description = '平均评分'
    
    def hot_display(self, obj):
        """显示热度"""
        return f"{obj.hot:.2f}"
    hot_display.short_description = '热度'
    
    def top_display(self, obj):
        """显示历史热度"""
        return f"{obj.top:.2f}"
    top_display.short_description = '历史热度'

# 评分管理
@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'ugc_item_preview', 'user', 'score', 'rating_time')
    list_filter = ('score', 'rating_time')
    search_fields = ('ugc_item__content', 'user__username')
    readonly_fields = ('rating_time',)
    date_hierarchy = 'rating_time'
    
    def ugc_item_preview(self, obj):
        """UGC内容预览"""
        content = obj.ugc_item.content
        return content[:30] + '...' if len(content) > 30 else content
    ugc_item_preview.short_description = 'UGC内容'

# 讨论管理
@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    list_display = ('id', 'ugc_item_preview', 'user', 'content_preview', 'comment_time')
    list_filter = ('comment_time',)
    search_fields = ('content', 'ugc_item__content', 'user__username')
    readonly_fields = ('comment_time',)
    date_hierarchy = 'comment_time'
    
    def ugc_item_preview(self, obj):
        """UGC内容预览"""
        content = obj.ugc_item.content
        return content[:30] + '...' if len(content) > 30 else content
    ugc_item_preview.short_description = 'UGC内容'
    
    def content_preview(self, obj):
        """评论内容预览"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '评论内容'

# 用户资料管理
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio_preview', 'profile_photo_display')
    search_fields = ('user__username', 'bio')
    
    def bio_preview(self, obj):
        """个人简介预览"""
        if obj.bio:
            return obj.bio[:50] + '...' if len(obj.bio) > 50 else obj.bio
        return '无'
    bio_preview.short_description = '个人简介'
    
    def profile_photo_display(self, obj):
        """显示是否有头像"""
        return "✅" if obj.profile_photo else "❌"
    profile_photo_display.short_description = '头像'

# 重新注册User模型
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# 自定义管理站点标题
admin.site.site_header = 'UGC平台管理系统'
admin.site.site_title = 'UGC平台管理'
admin.site.index_title = '站点管理'