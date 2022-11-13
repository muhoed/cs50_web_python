from time import strftime
from django.contrib.auth.models import AbstractUser
from django.db import models
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
    viewed_posts = models.ManyToManyField(
        'Post', related_name="viewers", 
        blank=True, through='ViewedPost',
        through_fields=('viewer', 'viewed_post')
        )

    @property
    def last_seen(self):
        return ViewedPost.objects.filter(viewer=self).order_by('-viewed_on').first().viewed_post

    def __str__(self):
        return f"{self.username}"

class Post(models.Model):
    text = models.TextField(verbose_name="Text of the message", max_length=500, blank=False, null=False)

    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, related_name="created_posts", 
        blank=True, null=True,
        on_delete=models.CASCADE
        )

    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, related_name="edited_posts", 
        blank=True, null=True,
        on_delete=models.DO_NOTHING
        )

    def __str__(self):
        return f"Post by {self.created_by}. Published on {self.created_on.strftime('%Y-%m-%d')}"

class ViewedPost(models.Model):
    viewer = models.ForeignKey(User, on_delete=models.CASCADE)
    viewed_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    viewed_on = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    body = models.TextField(
        verbose_name="Text of the comment", max_length=500, 
        blank=False, null=False
        )
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, related_name="created_comments", 
        blank=False, null=False,
        on_delete=models.CASCADE
        )

    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, related_name="edited_comments", 
        blank=True, null=True,
        on_delete=models.DO_NOTHING
        )

    def __str__(self):
        return f"{str(self.created_by)} comments to post '{self.post.title.capitalize()}' on {self.created_on.strftime('%Y-%m-%d')}"

class Reaction(models.Model):
    
    ATTITUDE_CHOICES = [
        ('L', 'Like'),
        ('D', 'Dislike'),
    ]

    post = models.ForeignKey(Post, related_name="reactions", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="reactions", on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=ATTITUDE_CHOICES)

    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reaction of {str(self.user)} to post {self.post.title}"

