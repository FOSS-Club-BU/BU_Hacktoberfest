from django.contrib import admin
from .models import User, Repository, PullRequest, Issue
# Register your models here.

class PullRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'repository', 'pr_id',"points", 'title', 'url', 'state', 'created_at', 'closed_at', 'merged_at', 'additions', 'deletions', 'changed_files', 'is_competition_repo')

admin.site.register(User)
admin.site.register(Repository)
admin.site.register(PullRequest, PullRequestAdmin)
admin.site.register(Issue)



