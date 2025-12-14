import os
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from .models import Category, Comment, Post
from .forms import CommentForm, PostForm

os.environ['DJANGO_SETTINGS_MODULE'] = 'blogicum.settings'
User = get_user_model()


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'posts'
    paginate_by = 10
    ordering = '-pub_date'

    def get_queryset(self):
        public_condition = Q(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )
        
        queryset = Post.objects.select_related(
            'author', 'category', 'location'
        ).prefetch_related('comments')
        
        if self.request.user.is_authenticated:
            queryset = queryset.filter(
                Q(author=self.request.user) | public_condition
            )
        else:
            queryset = queryset.filter(public_condition)
        
        queryset = queryset.annotate(comment_count=Count('comments'))
        return queryset.order_by('-pub_date')


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        queryset = super().get_queryset()
        post_id = self.kwargs.get('pk')
        
        if self.request.user.is_authenticated:
            user_posts = queryset.filter(
                Q(pk=post_id) & Q(author=self.request.user)
            )
            if user_posts.exists():
                return user_posts
        
        return queryset.filter(
            pk=post_id,
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all().order_by('created_at')
        context['form'] = CommentForm()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('users:profile', args=[self.request.user.username])


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        return redirect('blog:detail', pk=self.kwargs['pk'])
    
    def get_success_url(self):
        return reverse('blog:detail', kwargs={'pk': self.object.pk})


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/confirm_delete.html'
    success_url = reverse_lazy('blog:index')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class CategoryPostsView(ListView):
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        
        queryset = Post.objects.filter(
            category=self.category,
            is_published=True,
            pub_date__lte=timezone.now()
        ).select_related(
            'author', 'category', 'location'
        ).prefetch_related('comments')
        
        queryset = queryset.annotate(comment_count=Count('comments'))
        return queryset.order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


@login_required
def comment_create(request, post_id):
    post = get_object_or_404(
        Post, 
        pk=post_id,
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    )
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('blog:detail', pk=post_id)
    else:
        form = CommentForm()
    
    return render(request, 'blog/comment_form.html', {
        'form': form,
        'post': post
    })


@login_required
def comment_edit(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    
    if comment.author != request.user:
        return redirect('blog:detail', pk=post_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:detail', pk=post_id)
    else:
        form = CommentForm(instance=comment)
    
    return render(request, 'blog/comment_form.html', {
        'form': form,
        'comment': comment,
        'post': comment.post
    })


@login_required
def comment_delete(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    
    if comment.author != request.user:
        return redirect('blog:detail', pk=post_id)
    
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:detail', pk=post_id)
    
    return render(request, 'blog/comment_confirm_delete.html', {
        'comment': comment,
        'post': comment.post
    })
