import json
from logging import raiseExceptions

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Q
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

from .models import Post, Reaction, User, ViewedPost, Comment

@csrf_exempt
@login_required
def create_post(request):
    if request.method == "POST":
        data = json.loads(request.body)
        text = data["text"]
        if text is not None and text != "" and len(text) >= 3 and len(text) <= 500:
            try:
                post = Post.objects.create(text=text, created_by=request.user)
                post.save()
            except:
                return JsonResponse({"error": "Post wasn't added."}, status=400)
        else:
            return JsonResponse({"validationError": "Invalid post length."}, status=400)

        return JsonResponse({"message": "Post was added successfully."}, status=201)
    
    return JsonResponse({"error": "POST request required."}, status=400)

@csrf_exempt
def mark_post_viewed(request, pk):
    if request.method == "PUT" and request.user.is_authenticated:
        data = json.loads(request.body)
        req_type = data["type"]
        if req_type == "viewed":
            try:
                post = Post.objects.get(id=pk)
                user = User.objects.get(username=request.user.username)
                if post.created_by == user:
                    return JsonResponse({"error": "Post cannot be marked as viewed because viewer is author of post."}, status=400)
                viewed_post = ViewedPost(viewer=user, viewed_post=post)
                viewed_post.save()
            except:
                return JsonResponse({"error": "Error mark the post as viewed."}, status=400)
            return JsonResponse({"message": "Post was marked as viewed."}, status=201)
    return JsonResponse({"error": "POST request method is required. Error mark the post as viewed."}, status=400)

@csrf_exempt
def post_reaction(request, type, pk):
    if request.method == "POST" and request.user.is_authenticated:
        choice = "D"
        if type == "like":
            choice = "L"
        try:
            post = get_object_or_404(Post, pk=pk)
            if not Reaction.objects.filter(post = post, user = request.user) and post.created_by != request.user:
                reaction = Reaction.objects.create(
                    post = get_object_or_404(Post, pk=pk),
                    user = request.user,
                    status = choice
                )
                reaction.save()
        except:
            return JsonResponse({"error": "Error reacting on post."}, status=400)
        post = Post.objects.annotate(
                        reacts=Count('reactions', filter=Q(reactions__status=choice), distinct=True)
                    ).get(pk=pk)
        return JsonResponse({
                "message": "Post was reacted.",
                "count": post.reacts
            }, status=201)
    return JsonResponse({"error": "POST request method is required. Error reacting on post."}, status=400)

@csrf_exempt
def update_post(request, pk):
    if request.method == "PUT":
        data = json.loads(request.body)
        text = data["postText"] 
        if request.user.is_authenticated:
            try:
                post = Post.objects.get(pk=pk)
                init_text = post.text
            except:
                return JsonResponse({"error": "Post not found.", "text": init_text}, status=404)
            if post.created_by != request.user:
                return JsonResponse({"error": "Not authorized.", "text": init_text}, status=401)
            if len(text) > 500:
                text = text[:500]
            try:
                post.text = text
                post.updated_by = request.user
                post.save()
            except:
                return JsonResponse({"error": "Not authorized.", "text": init_text}, status=401)
            return JsonResponse({"message": "Post was successfully updated.", "text": text}, status=200)
        return JsonResponse({"error": "Not authorized.", "text": text}, status=401)
    return JsonResponse({"error": "PUT request method is required.", "text": ""}, status=400)

@csrf_exempt
def create_comment(request, post_pk):
    if request.method == "POST":
        if request.user.is_authenticated:
            comment_text = json.loads(request.body)
            try:
                post = get_object_or_404(Post, pk=post_pk)
            except:
                return JsonResponse({"error": "Post not found."}, status=404)
            if not comment_text or len(comment_text) == 0 or len(comment_text) > 500:
                return JsonResponse({"error": "Invalid comment length."}, status=400)
            try:
                new_comment = Comment.objects.create(
                    body = comment_text,
                    post = post,
                    created_by = request.user
                )
                new_comment.save()
            except:
                return JsonResponse({"error": "Error adding comment."}, status=400)
            return JsonResponse({"message": "Comment was successfulyy added."}, status=200)
        return JsonResponse({"error": "Not authorized."}, status=401)
    return JsonResponse({"error": "POST request method is required."}, status=400)

@csrf_exempt
def update_profile_about(request, pk):
    if request.method == "PUT":
        data = json.loads(request.body)
        text = data["aboutText"] 
        if request.user.is_authenticated:
            try:
                user = User.objects.get(pk=pk)
                init_text = user.about
            except:
                return JsonResponse({"error": "Invalid user.", "text": init_text}, status=404)
            if user != request.user:
                return JsonResponse({"error": "Not authorized.", "text": init_text}, status=401)
            if len(text) > 500:
                text = text[:500]
            try:
                user.about = text
                user.save()
            except:
                return JsonResponse({"error": "Not authorized.", "text": init_text}, status=401)
            return JsonResponse({"message": "Profile About info was successfully updated.", "text": text}, status=200)
        return JsonResponse({"error": "Not authorized.", "text": text}, status=401)
    return JsonResponse({"error": "PUT request method is required.", "text": ""}, status=400)

@csrf_exempt
def switch_following_status(request, pk):
    if request.method == "PUT":
        if request.user.is_authenticated:
            try:
                user = User.objects.get(pk=pk)
            except:
                return JsonResponse({"error": "Invalid user."}, status=404)
            if user == request.user:
                return JsonResponse({"error": "Cannot follow itself."}, status=400)
            if user in request.user.following.all():
                request.user.following.remove(user)
                message = f"Stopped follow user {user.username}."
                action = "unfollow"
            else:
                request.user.following.add(user)
                message = f"Started follow user {user.username}."
                action = "follow"
            try:
                request.user.save()
            except:
                return JsonResponse({"error": "Internal server error."}, status=400)
            return JsonResponse({"message": message, "action": action}, status=200)
        return JsonResponse({"error": "Not authorized."}, status=401)
    return JsonResponse({"error": "PUT request method is required."}, status=400)

@csrf_exempt
def get_followers_counts(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except:
        return JsonResponse({"error": "Invalid user."}, status=404)
    
    followers = User.objects.filter(following__id=pk).count()

    return JsonResponse({"message": followers}, status=200)
