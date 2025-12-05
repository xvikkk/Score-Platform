from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# 用户资料模型
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username

class UGCItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ugc_items')
    image = models.ImageField(upload_to='ugc_images/')
    content = models.TextField()
    post_time = models.DateTimeField(auto_now_add=True)
    
    # 添加缓存字段
    cached_top = models.FloatField(default=0)
    cached_hot = models.FloatField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    @property
    def scored(self):
        if self.ratings.count() > 0:
            return self.ratings.aggregate(models.Avg('score'))['score__avg']
        return 0

    @property
    def rating_count(self):
        return self.ratings.count()
    
    @property
    def discussion_count(self):
        return self.discussions.count()

    @property
    def top(self):
        if self.last_updated > timezone.now() - timezone.timedelta(hours=1):
            return self.cached_top
        
        p = self.rating_count / (self.rating_count + self.discussion_count) if (self.rating_count + self.discussion_count) > 0 else 0
        q = 1 - p
        top_value = self.scored * p + self.discussion_count * q
        
        self.cached_top = top_value
        self.save(update_fields=['cached_top', 'last_updated'])
        
        return top_value
    
    @property
    def hot(self):
        if self.last_updated > timezone.now() - timezone.timedelta(hours=1):
            return self.cached_hot
        
        top_value = self.top
        now = timezone.now()
        
        rating_times = self.ratings.all().values_list('rating_time', flat=True)
        recent_rating_time = max(rating_times) if rating_times else now

        discussion_times = self.discussions.all().values_list('comment_time', flat=True)
        recent_discussion_time = max(discussion_times) if discussion_times else now

        recent_time = min(recent_rating_time, recent_discussion_time)

        time_diff = now - recent_time
        hours_passed = time_diff.total_seconds() / 3600
        decay_factor = 0.9 ** hours_passed
        hot_value = top_value * decay_factor
        
        self.cached_hot = hot_value
        self.save(update_fields=['cached_hot', 'last_updated'])
        
        return hot_value
    
# 评分模型
class Rating(models.Model):
    ugc_item = models.ForeignKey(UGCItem, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    score = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1到5分
    rating_time = models.DateTimeField(auto_now_add=True)

    # 确保每个用户对每个UGC项只能评分一次
    class Meta:
        unique_together = ('ugc_item', 'user')

    def __str__(self):
        return f"{self.user.username} rated {self.ugc_item.id} - {self.score}"
    
# 讨论模型
class Discussion(models.Model):
    ugc_item = models.ForeignKey(UGCItem, on_delete=models.CASCADE, related_name='discussions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discussions')
    content = models.TextField()
    comment_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.comment_time}"