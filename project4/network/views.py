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
from .forms import AvatarUploadForm


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

class FollowingPage(LoginRequiredMixin, TemplateView):
    template_name = "network/following_page/following.html"
    login_url = "register"

class ProfileMain(LoginRequiredMixin, TemplateView):
    template_name = "network/profile_page/profile.html"
    login_url = "register"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile_user"] = self.kwargs["pk"]
        return context

class ProfileDetail(LoginRequiredMixin, DetailView):
    template_name = "network/profile_page/components/profile_details.html"
    login_url = "register"
    context_object_name = "UserDetail"
    model = User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object = self.get_object()
        context["following_count"] = object.following.count()
        context["followers_count"] = User.objects.filter(following__id=self.kwargs["pk"]).count()
        context["follow_status"] = True if object in User.objects.get(pk=self.request.user.id).following.all() else False
        return context


def upload_avatar(request, pk):
    # view to render and edit profile avatar picture
    user = get_object_or_404(User, pk=pk)
    original_form = AvatarUploadForm(initial={'id': user.pk, 'avatar': user.avatar})
    if request.method == "POST":
        form = AvatarUploadForm(request.POST, request.FILES)
        if form.is_valid():
            user.avatar = form.cleaned_data["avatar"]
            user.save()
            new_form = AvatarUploadForm(initial={'id': user.pk, 'avatar': user.avatar})
            return render(request, "network/profile_page/components/avatar_form_view.html", {
                "message": "Avatar was successfully updated.",
                "form": new_form
            })
        else:
            return render(request, "network/profile_page/components/avatar_form_view.html", {
                "message": "File upload error.",
                "form": original_form
            })
    return render(request, "network/profile_page/components/avatar_form_view.html", {
        "form": original_form
    })

class ListUsers(LoginRequiredMixin, ListView):
    template_name = "network/components/user_list.html"
    login_url = "register"
    model = User
    context_object_name = "users"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["type"] = self.kwargs["type"]
        context["limit"] = self.kwargs["limit"]
        context["target_user"] = self.kwargs["pk"]
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        limit = self.kwargs["limit"]

        if self.kwargs["type"] == "followers":
            result = queryset.filter(following__id=self.kwargs["pk"])
            if limit and isinstance(limit, int):
                return result[:limit]
            return result
        elif self.kwargs["type"] == "following":
            result = User.objects.get(id=self.kwargs["pk"])
            result = result.following.all()
            if limit and isinstance(limit, int):
                return result[:limit]
            return result

class ListPosts(LoginRequiredMixin, ListView):
    template_name = "network/components/short_post_block.html"
    login_url = "register"
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
        if context["scope"] == "popular":
            context["title"] = ""
        elif context["scope"] == "recently-viewed":
            context["title"] = "Recently viewed posts"
        elif context["scope"] == "own-posts":
            context["title"] = "Your posts"
        elif context["scope"][:4] == "user":
            context["title"] = "User's posts"
        elif context["scope"] == "following":
            context["title"] = "All following users' posts"
        elif context["scope"] == "strip":
            context["title"] = "All published posts"
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
            sorted_posts = queryset.filter(
                                    viewers_list__username=self.request.user.username
                                ).order_by("-viewedpost__viewed_on")
            distinct_posts = []
            i =  0
            if limit and isinstance(limit, int):
                j = limit - 1
            else:
                j = 4
            for post in sorted_posts:
                if post not in distinct_posts:
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
        elif self.kwargs["scope"][:4] == "user":
            result = queryset.filter(created_by__id=int(self.kwargs["scope"][5:]))
            if limit and isinstance(limit, int):
                return result[:limit]
            return result[:5]
        elif self.kwargs["scope"] == "following":
            self.template_name = "network/home_page/components/post_list.html"
            following = User.objects.get(pk=self.request.user.pk).following.all()
            queryset = queryset.filter(created_by__in=following)
            if limit and isinstance(limit, int):
                return queryset[:limit]
            return queryset
        elif self.kwargs["scope"][:9] == "following" and len(self.kwargs["scope"]) > 9:
            self.template_name = "network/home_page/components/post_list.html"
            id = self.kwargs["scope"][10:]
            queryset = queryset.filter(created_by__id=id)
            if limit and isinstance(limit, int):
                return queryset[:limit]
            return queryset
        else:
            self.template_name = "network/home_page/components/post_list.html"
            if limit and isinstance(limit, int):
                return queryset[:limit]
            return queryset

class ShowPost(LoginRequiredMixin, DetailView):
    template_name = "network/components/post_view.html"
    login_url = "register"
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

class ListComments(LoginRequiredMixin, ListView):
    template_name = "network/components/comment_list.html"
    login_url = "register"
    queryset = Comment.objects.all()
    context_object_name = "comment_list"
    pagination = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        post_pk = self.kwargs["post_pk"]
        return queryset.filter(post__pk=post_pk).order_by("-created_on")
