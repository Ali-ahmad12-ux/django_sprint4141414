from django.contrib import admin
from .models import Category, Location, Post, Comment

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'created_at')
    list_filter = ('is_published',)
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'created_at')
    list_filter = ('is_published',)
    search_fields = ('name',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'is_published', 'pub_date', 'created_at')
    list_filter = ('is_published', 'category', 'author')
    search_fields = ('title', 'text', 'author__username')
    readonly_fields = ('created_at',)
    filter_horizontal = ()
    fieldsets = (
        (None, {
            'fields': ('title', 'text', 'author', 'image')
        }),
        ('Дата и место', {
            'fields': ('pub_date', 'category', 'location')
        }),
        ('Публикация', {
            'fields': ('is_published', 'created_at')
        }),
    )

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_at', 'text_preview')
    list_filter = ('created_at', 'author')
    search_fields = ('text', 'author__username', 'post__title')
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Текст'
