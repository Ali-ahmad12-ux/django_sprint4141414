from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='detail'),
    path('posts/create/', views.PostCreateView.as_view(), name='create'),
    path('posts/<int:pk>/edit/', views.PostUpdateView.as_view(), name='edit'),
    path('posts/<int:pk>/delete/', views.PostDeleteView.as_view(), name='delete'),
    path('category/<slug:category_slug>/', views.CategoryPostsView.as_view(), name='category'),
    path('profile/<str:username>/', views.ProfileView.as_view(), name='profile'),
    path('profile/<str:username>/edit/', views.ProfileEditView.as_view(), name='edit_profile'),
    
    # التعليقات
    path('posts/<int:post_id>/comment/', views.comment_create, name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/', views.comment_edit, name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/', views.comment_delete, name='delete_comment'),
]
