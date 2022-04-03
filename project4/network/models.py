from django.contrib.auth.models import AbstractUser
from django.db import models
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify


def get_avatar_upload_path(instance, filename):
	user_id = instance.pk
	slug = slugify(user_id)
	return "avatars/%s-%s" % (slug, filename)

class User(AbstractUser):
    following = models.ManyToManyField(
        "self", verbose_name="Users the user follows", 
        related_name="follower", blank=True
        )
    avatar = models.ImageField(
        verbose_name="User's avatar", upload_to=get_avatar_upload_path, 
        blank=True, null=True
        )
    about = models.TextField(verbose_name="About user", max_length=500, blank=True, null=True)
    _last_seen = models.ManyToManyField(
        'Post', related_name="viewers", 
        blank=True, through='ViewedPost',
        through_fields=('viewer', 'viewed_post')
        )

    def follow(self, id):
        if self.following.get(pk=id):
            return
        user = get_object_or_404(User, pk=id)
        self.following.add(user)

    def unfollow(self, id):
        if self.following.get(pk=id):
            self.following.remove(pk=id)

    @property
    def last_seen(self):
        return self._last_seen.all()

    @last_seen.setter
    def last_seen(self, post):
        if self._last_seen.count() > 10:
            oldest = self._last_seen.all().order_by('-viewedpost_set__viewed_on')[0]
            self._last_seen.remove(oldest)
        self._last_seen.add(post)

class Post():
    title = models.CharField(verbose_name="Title", max_length=100, blank=False, null=False)
    body = models.TextField(verbose_name="Text of the message", max_length=500, blank=False, null=False)

    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, related_name="created_posts", 
        blank=True, null=True,
        on_delete=models.CASCADE
        )

    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, related_name="edited_posts", 
        blank=True, null=True
        )

class ViewedPost():
    viewer = models.ForeignKey(User, on_delete=models.CASCADE)
    viewed_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    viewed_on = models.DateTimeField(auto_now_add=True)

class Comment():
    post = models.ForeignKey(Post, related_name="comments")
    body = models.TextField(
        verbose_name="Text of the comment", max_length=500, 
        blank=False, null=False
        )
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, related_name="created_comments", 
        blank=True, null=True,
        on_delete=models.CASCADE
        )

    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, related_name="edited_comments", 
        blank=True, null=True
        )

class Attitude():
    
    ATTITUDE_CHOICES = [
        ('L', 'Like'),
        ('D', 'Dislike'),
    ]

    post = models.ForeignKey(Post, related_name="attitudes")
    user = models.ForeignKey(User, related_name="reactions")
    status = models.CharField(max_length=1, choices=ATTITUDE_CHOICES)

    created_on = models.DateTimeField(auto_now_add=True)

