from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Count
from django.views.generic import CreateView
from blog.models import Post

User = get_user_model()


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/registration_form.html'  # ✅ التغيير هنا
    success_url = reverse_lazy('blog:index')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


@login_required
def profile_view(request):
    posts = Post.objects.filter(author=request.user).order_by('-pub_date')
    return render(request, 'users/profile.html', {
        'profile_user': request.user,
        'posts': posts
    })


def profile(request, username):
    try:
        profile_user = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(request, 'pages/404.html', status=404)

    if request.user == profile_user:
        posts = Post.objects.filter(author=profile_user)
    else:
        posts = Post.objects.filter(
            author=profile_user,
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )

    posts = posts.select_related('author', 'category', 'location')
    posts = posts.prefetch_related('comments')
    posts = posts.annotate(comment_count=Count('comments'))
    posts = posts.order_by('-pub_date')

    return render(request, 'users/profile.html', {
        'profile_user': profile_user,
        'posts': posts
    })


def user_profile(request, username):
    return profile(request, username)
