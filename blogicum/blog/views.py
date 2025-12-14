import os
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from .models import Category, Comment, Post
from .forms import CommentForm, PostForm


# تعيين إعدادات Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'blogicum.settings'
User = get_user_model()


# 1. الصفحة الرئيسية - عرض جميع المنشورات
class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'posts'
    paginate_by = 10
    ordering = '-pub_date'

    def get_queryset(self):
        queryset = Post.objects.select_related(
            'author', 'category', 'location'
        ).prefetch_related(
            'comments'
        ).annotate(
            comment_count=Count('comments')
        )

        # المنطق لعرض المنشورات
        if self.request.user.is_authenticated:
            user_posts = queryset.filter(author=self.request.user)
            public_posts = queryset.filter(
                is_published=True,
                pub_date__lte=timezone.now(),
                category__is_published=True
            ).exclude(author=self.request.user)
            queryset = user_posts.union(public_posts)
        else:
            queryset = queryset.filter(
                is_published=True,
                pub_date__lte=timezone.now(),
                category__is_published=True
            )
        return queryset


# 2. عرض تفاصيل منشور واحد
class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        queryset = super().get_queryset()
        post_id = self.kwargs.get('pk')
        post = get_object_or_404(Post, pk=post_id)

        if (self.request.user.is_authenticated
                and self.request.user == post.author):
            return queryset.filter(pk=post_id)
        else:
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


# 3. إنشاء منشور جديد
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('users:profile', args=[self.request.user.username])


# 4. تعديل منشور
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        return redirect('blog:detail', pk=self.kwargs['pk'])


# 5. حذف منشور
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/confirm_delete.html'
    success_url = reverse_lazy('blog:index')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


# 6. عرض منشورات فئة معينة
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
        return Post.objects.filter(
            category=self.category,
            is_published=True,
            pub_date__lte=timezone.now()
        ).select_related(
            'author', 'category', 'location'
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


# 7. إنشاء تعليق جديد
class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:detail', kwargs={'pk': self.kwargs['post_id']})


# 8. تعديل تعليق
class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment_form.html'

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def get_success_url(self):
        return reverse('blog:detail', kwargs={'pk': self.object.post.pk})


# 9. حذف تعليق
class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment_confirm_delete.html'

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def get_success_url(self):
        return reverse('blog:detail', kwargs={'pk': self.object.post.pk})


# 10. دالة لعرض صفحة المستخدم (Profile)
def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=profile_user).order_by('-pub_date')

    return render(request, 'users/profile.html', {
        'profile_user': profile_user,
        'posts': posts
    })
