from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView
from blog.models import Post

User = get_user_model()


# 1. تسجيل مستخدم جديد
class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/registration.html'
    success_url = reverse_lazy('blog:index')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


# 2. صفحة الملف الشخصي (للمستخدم الحالي)
@login_required
def profile_view(request):
    # عرض جميع منشورات المستخدم الحالي (بما فيها غير المنشورة)
    posts = Post.objects.filter(author=request.user).order_by('-pub_date')
    return render(request, 'users/profile.html', {
        'profile_user': request.user,
        'posts': posts
    })


# 3. عرض ملف أي مستخدم (هذه هي الدالة التي تطلبها الاختبارات)
def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    
    # إذا كان المستخدم الحالي هو صاحب الصفحة، يرى جميع منشوراته
    if request.user == profile_user:
        posts = Post.objects.filter(author=profile_user)
    else:
        # الزوار يرون فقط المنشورات المنشورة
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
