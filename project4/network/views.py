import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, models
from django.db.models import Count, Q, Value, F, Case, When
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import User, Post, Comment, Reaction, ViewedPost


#def index(request):
#    return render(request, "network/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/auth/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/auth/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/auth/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/auth/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/auth/register.html")

class HomePage(LoginRequiredMixin, TemplateView):
    template_name = "network/home_page/index.html"
    login_url = "register"

class ProfileMain(LoginRequiredMixin, TemplateView):
    template_name = "network/profile_page/profile.html"
    login_url = "register"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile_user"] = self.kwargs["pk"]
        return context

class ProfileDetail(LoginRequiredMixin, DetailView):
    template_name = "network/components/profile_details.html"
    context_object_name = "UserDetail"
    model = User

class ListFollowing(LoginRequiredMixin, ListView):
    model = User
    context_object_name = "following_list"

class ModifyFollowing(LoginRequiredMixin, UpdateView):
    model = User

    def follow(self, id):
        if self.object.following.get(pk=id):
            return
        user = get_object_or_404(User, pk=id)
        self.object.following.add(user)

    def unfollow(self, id):
        if self.object.following.get(pk=id):
            self.object.following.remove(pk=id)

class ListPosts(ListView):
    template_name = "network/components/short_post_block.html"
    queryset = Post.objects.annotate(
        likes=Count('reactions', filter=Q(reactions__status='L'), distinct=True),
        dislikes=Count('reactions', filter=Q(reactions__status='D'), distinct=True)
        ).order_by('-created_on')
    context_object_name = "post_list"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["scope"] = self.kwargs["scope"]
        context["limit"] = self.kwargs["limit"]
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        limit = self.kwargs["limit"]

        queryset = queryset.annotate(own = Case(
            When(created_by=self.request.user, then=Value("true", output_field=models.TextField())),
            default=Value("false", output_field=models.TextField()),
            ))

        if self.kwargs["scope"] == "popular":
            result = queryset.annotate(views_num=Count('viewers')).order_by('-views_num')
            if limit and isinstance(limit, int):
                return result[:limit]
            return result[:5]
        elif self.kwargs["scope"] == "recently-viewed":
            sorted_posts = queryset.filter(viewers__username=self.request.user.username).order_by("-viewedpost__viewed_on")
            distinct_posts = []
            i =  0
            if limit and isinstance(limit, int):
                j = limit - 1
            else:
                j = 4
            for post in sorted_posts:
                if post.id not in distinct_posts:
                    distinct_posts.append(post)
                    i += 1
                    if i > j:
                        break
            return distinct_posts
        elif self.kwargs["scope"] == "own-posts":
            result = queryset.filter(created_by=self.request.user)
            if limit and isinstance(limit, int):
                return result[:limit]
            return result[:5]
        else:
            self.template_name = "network/components/post_list.html"
            if limit and isinstance(limit, int):
                return queryset[:limit]
            return queryset


class ShowPost(DetailView):
    template_name = "network/components/post_view.html"
    model = Post

    def get_object(self, queryset=None):
        """
        Return the object the view is displaying.
        Require `self.queryset` and a `pk` or `slug` argument in the URLconf.
        Subclasses can override this to return any object.
        """
        # Use a custom queryset if provided; this is required for subclasses
        # like DateDetailView
        if queryset is None:
            queryset = self.get_queryset()

        # Next, try looking up by primary key.
        pk = self.kwargs.get(self.pk_url_kwarg)
        slug = self.kwargs.get(self.slug_url_kwarg)
        if pk is not None:
            queryset = queryset.filter(pk=pk)

        # Next, try looking up by slug.
        if slug is not None and (pk is None or self.query_pk_and_slug):
            slug_field = self.get_slug_field()
            queryset = queryset.filter(**{slug_field: slug})

        # If none of those are defined, it's an error.
        if pk is None and slug is None:
            raise AttributeError(
                "Generic detail view %s must be called with either an object "
                "pk or a slug in the URLconf." % self.__class__.__name__
            )

        try:
            # annotate queryset with reactions count and own attribute
            queryset = queryset.annotate(
                likes=Count('reactions', filter=Q(reactions__status='L'), distinct=True),
                dislikes=Count('reactions', filter=Q(reactions__status='D'), distinct=True),
                own = Case(
                    When(created_by=self.request.user, then=Value("true", output_field=models.TextField())),
                    default=Value("false", output_field=models.TextField()),
                    )
                )
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(
                _("No %(verbose_name)s found matching the query")
                % {"verbose_name": queryset.model._meta.verbose_name}
            )
        return obj

class CreatePost(CreateView):
    template_name = "network/components/post_form.html"
    model = Post

class DeletePost(DeleteView):
    model = Post

class CreateReaction(CreateView):
    model = Reaction

class CommentDetails(DetailView):
    model = Comment

class ListComments(ListView):
    template_name = "network/components/comment_list.html"
    queryset = Comment.objects.all()
    context_object_name = "comment_list"
    pagination = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        post_pk = self.kwargs["post_pk"]
        return queryset.filter(post__pk=post_pk).order_by("-created_on")

class CreateComment(CreateView):
    model = Comment

class ModifyComment(UpdateView):
    model = Comment

class DeleteComment(DeleteView):
    model = Comment
