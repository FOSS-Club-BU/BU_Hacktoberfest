from django.contrib import admin
from .models import User, Repository, PullRequest, Issue, BlackListedRepository, HacktoberfestStats, DailyStats, TopContributor, TopRepository, StarredRepository

@admin.register(HacktoberfestStats)
class HacktoberfestStatsAdmin(admin.ModelAdmin):
    list_display = ('generated_at', 'total_participants', 'total_prs', 'total_merged_prs', 'completion_rate')
    readonly_fields = ('generated_at',)

@admin.register(DailyStats)
class DailyStatsAdmin(admin.ModelAdmin):
    list_display = ('date', 'pr_count', 'active_users', 'points_awarded')
    ordering = ('-date',)

@admin.register(TopContributor)
class TopContributorAdmin(admin.ModelAdmin):
    list_display = ('rank', 'user', 'points', 'merged_prs')
    ordering = ('rank',)

@admin.register(TopRepository)
class TopRepositoryAdmin(admin.ModelAdmin):
    list_display = ('repository', 'total_prs', 'merged_prs', 'unique_contributors')
    ordering = ('-merged_prs',)

@admin.register(StarredRepository)
class StarredRepositoryAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'stars', 'total_prs', 'merged_prs', 'last_updated')
    ordering = ('-stars',)
    readonly_fields = ('last_updated',)

class PullRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'repository', 'pr_id', "points", 'title', 'url', 'state', 'created_at', 'closed_at', 'merged_at', 'additions', 'deletions', 'changed_files', 'is_competition_repo')

    @admin.action(description='Mark as competition repo')
    def mark_as_competition_repo(self, request, queryset):
        queryset.update(is_competition_repo=True)
    
    @admin.action(description='Mark as not competition repo')
    def mark_as_not_competition_repo(self, request, queryset):
        queryset.update(is_competition_repo=False)

class UserAdmin(admin.ModelAdmin): 
    list_display = ('username', 'first_name', 'last_name', 'get_profile_username', 'points')

class RepositoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'difficulty', 'club', 'tech_stack')

class BlackListedRepositoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'url')

admin.site.register(User, UserAdmin)
admin.site.register(Repository, RepositoryAdmin)
admin.site.register(PullRequest, PullRequestAdmin)
admin.site.register(BlackListedRepository, BlackListedRepositoryAdmin)
admin.site.register(Issue)