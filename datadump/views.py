from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Comment
from taggit.models import Tag
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.template.defaultfilters import slugify
from .forms import CreatePost
from django.db.models.signals import pre_save
from django.contrib.auth.decorators import login_required


def post_list(request, tag_slug=None):
    object_list = Post.objects.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 5)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    context = {
        'page': page,
        'posts': posts,
        'tag': tag,
    }
    return render(request, 'datadump/post/list.html', context)


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    comments = post.comments.filter(active=True)
    if request.method == 'POST':
        if request.user.is_authenticated:
            name = request.user.username
            email = request.user.email
            comment = request.POST.get('comment')
            c = Comment(post=post, name=name, email=email, body=comment)
            c.save()
        else:
            name = request.POST.get('name')
            email = request.POST.get('email')
            comment = request.POST.get('comment')
            c = Comment(post=post, name=name, email=email, body=comment)
            c.save()
    context = {
        'post': post,
        'comments': comments
    }
    return render(request, 'datadump/post/detail.html', context)


@login_required
def create_post(request):
    if request.method == 'POST':
        create_form = CreatePost(request.POST)
        if create_form.is_valid():
            def pre_save_post_receiver(sender, instance, *args, **kwargs):
                instance.slug = slugify(instance.title)
                instance.author = request.user
                instance.status = "published"
            pre_save.connect(pre_save_post_receiver, sender=Post)
            create_form.save()
            return redirect('/datadump')
    else:
        create_form = CreatePost()

    context = {
        'create_form': create_form,
    }
    return render(request, 'datadump/post/create_post.html', context)

