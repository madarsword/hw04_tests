from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .forms import PostForm
from .models import Post, Group, User
from .utils import paginate_page


def index(request):
    posts = Post.objects.select_related('group', 'author').all()
    page_obj = paginate_page(request, posts)
    template = 'posts/index.html'
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('group')
    page_obj = paginate_page(request, posts)
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('author')
    page_obj = paginate_page(request, posts)
    context = {
        'author': author,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None)
    context = {'form': form}
    if form.is_valid():
        temp_post = form.save(commit=False)
        temp_post.author = request.user
        temp_post.save()
        return redirect(
            'posts:profile', temp_post.author
        )
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {'form': form, 'is_edit': True, 'post': post}
    return render(request, template, context)
