# blogapp/admin.py

from django.contrib import admin
from .models import Blog, Category, Tag
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from accountuser.models import UserProfile
from community.models import Comment, Question, Answer
from paper.models import Paper
from payment.models import Invoice

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profiles'

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'avatar', 'cover_photo', 'job', 'location', 'education', 'birth_date', 'bio', 'interests', 'website', 'twitter', 'instagram', 'facebook', 'created_at', 'role')
    search_fields = ('user_username', 'job', 'location', 'education', 'bio', 'interests', 'website', 'twitter', 'instagram', 'facebook')

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

# unregister old user admin
admin.site.unregister(User)

# register new user admin
admin.site.register(User, UserAdmin)

class BlogAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "is_home", "publish_date", "slug", "selected_categories",)
    list_editable = ("is_active", "is_home")
    search_fields = ("title", "description",)
    readonly_fields = ("slug", "publish_date",)
    list_filter = ("is_active", "is_home", "categories")
    
    def selected_categories(self, obj):
        html = "<ul>"
        
        for category in obj.categories.all():
            html += "<li>" + category.name + "</li>"
        
        html += "</ul>"
        
        return mark_safe(html)
    
class PaperAdmin(admin.ModelAdmin):
    list_display = ("title", "publish_date", "file")
    search_fields = ("title",)
    readonly_fields = ("publish_date",)
    
admin.site.register(Invoice)
admin.site.register(Paper, PaperAdmin)
admin.site.register(Blog, BlogAdmin)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Comment)
admin.site.register(Question)
admin.site.register(Answer)