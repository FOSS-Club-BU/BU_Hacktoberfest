from django.contrib import admin
from .models import User, Repository, PullRequest, Issue
from django.contrib import admin

# Register your models here.

class PullRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'repository', 'pr_id',"points", 'title', 'url', 'state', 'created_at', 'closed_at', 'merged_at', 'additions', 'deletions', 'changed_files', 'is_competition_repo')

    @admin.action(description='Mark as competition repo')
    def mark_as_competition_repo(self, request, queryset):
        queryset.update(is_competition_repo=True)
    
    @admin.action(description='Mark as not competition repo')
    def mark_as_not_competition_repo(self, request, queryset):
        queryset.update(is_competition_repo=False)



class UserAdmin(admin.ModelAdmin): 
    list_display = ('username','first_name', 'last_name', 'get_profile_username', 'points')

class RepositoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'difficulty' ,'club', 'tech_stack')

admin.site.register(User, UserAdmin)
admin.site.register(Repository, RepositoryAdmin)
admin.site.register(PullRequest, PullRequestAdmin)
admin.site.register(Issue)



