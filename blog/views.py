from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.urls import reverse_lazy
from django.db.models import Count
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm

User = get_user_model()


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10
    context_object_name = 'posts'

    def get_queryset(self):
        queryset = Post.objects.select_related(
            'author', 'category', 'location'
        ).filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')
        return queryset


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        queryset = Post.objects.select_related(
            'author', 'category', 'location'
        )
        post = get_object_or_404(queryset, pk=self.kwargs['pk'])
        if self.request.user.is_authenticated and self.request.user == post.author:
            return queryset
        if (not post.is_published or not post.category.is_published 
                or post.pub_date > timezone.now()):
            raise Http404("Пост не найден")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Пост успешно создан!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def form_valid(self, form):
        messages.success(self.request, 'Пост успешно обновлен!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:detail', kwargs={'pk': self.object.pk})


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/delete.html'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def get_success_url(self):
        messages.success(self.request, 'Пост успешно удален!')
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class CategoryPostsView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = 10
    context_object_name = 'posts'

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        category = get_object_or_404(Category, slug=category_slug)
        if not category.is_published:
            raise Http404("Категория не найдена")
        queryset = Post.objects.select_related(
            'author', 'category', 'location'
        ).filter(
            category=category,
            is_published=True,
            pub_date__lte=timezone.now()
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs['category_slug']
        context['category'] = get_object_or_404(Category, slug=category_slug)
        return context


class ProfileView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = 10
    context_object_name = 'posts'

    def get_queryset(self):
        username = self.kwargs['username']
        user = get_object_or_404(User, username=username)
        if self.request.user == user:
            queryset = Post.objects.filter(
                author=user
            ).select_related(
                'category', 'location'
            ).annotate(
                comment_count=Count('comments')
            ).order_by('-pub_date')
        else:
            queryset = Post.objects.filter(
                author=user,
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now()
            ).select_related(
                'category', 'location'
            ).annotate(
                comment_count=Count('comments')
            ).order_by('-pub_date')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.kwargs['username']
        context['profile_user'] = get_object_or_404(User, username=username)
        return context


class ProfileEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = UserChangeForm
    template_name = 'blog/edit_profile.html'

    def get_object(self):
        username = self.kwargs['username']
        return get_object_or_404(User, username=username)

    def test_func(self):
        return self.request.user.username == self.kwargs['username']

    def get_success_url(self):
        messages.success(self.request, 'Профиль успешно обновлен!')
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


@login_required
def comment_create(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Комментарий добавлен!')
    return redirect('blog:detail', pk=post_id)


@login_required
def comment_edit(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if comment.author != request.user:
        raise PermissionDenied
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Комментарий обновлен!')
            return redirect('blog:detail', pk=post_id)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'blog/edit_comment.html', {
        'form': form,
        'comment': comment,
        'post': comment.post
    })


@login_required
def comment_delete(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if comment.author != request.user:
        raise PermissionDenied
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Комментарий удален!')
        return redirect('blog:detail', pk=post_id)
    return render(request, 'blog/delete_comment.html', {
        'comment': comment,
        'post': comment.post
    })
