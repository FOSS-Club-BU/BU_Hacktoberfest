# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from allauth.socialaccount.models import SocialAccount

class User(AbstractUser):
    github_username = models.CharField(max_length=39, blank=True)
    total_commits = models.IntegerField(default=0)
    total_prs = models.IntegerField(default=0)
    total_issues = models.IntegerField(default=0)
    total_lines_added = models.IntegerField(default=0)
    total_lines_deleted = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    last_updated = models.DateTimeField(null=True, blank=True)

    def total_merged_prs(self):
        return self.pull_requests.filter(state='merged').count()
    
    def total_closed_issues(self):
        return self.issues.filter(state='closed').count()
    
    def total_open_issues(self):
        return self.issues.filter(state='open').count()
    
    def total_open_prs(self):
        return self.pull_requests.filter(state='open').count()
    
    def total_closed_prs(self):
        return self.pull_requests.filter(state='closed').count()
    
    def total_merged_prs(self):
        return self.pull_requests.filter(state='merged').count()
    
    def get_profile_username(self):
        # get github username from social account
        social_account = SocialAccount.objects.get(user=self, provider='github')
        return social_account.extra_data.get('login')
    
    # change string representation of the model
    def __str__(self):
        return self.first_name if self.first_name else self.username


class Repository(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    name = models.CharField(max_length=100)
    url = models.URLField()
    is_active = models.BooleanField(default=True)  
    description = models.TextField(null=True, blank=True)
    maintainer_username = models.CharField(max_length=39, null=True, blank=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    tech_stack = models.TextField(null=True, blank=True) 
    club = models.CharField(max_length=50, null=True, blank=True)
    usernames_not_eligible = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
    
    # Return the tech stack as a list
    def get_tech_stack(self):
        return [tech.strip() for tech in self.tech_stack.split(',') if tech.strip()]

    # plural name for admin panel
    class Meta:
        verbose_name_plural = 'Repositories'


class PullRequest(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pull_requests')
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='pull_requests', null=True, blank=True)  # Optional for global PRs
    pr_id = models.IntegerField()
    title = models.CharField(max_length=255)
    url = models.URLField()
    state = models.CharField(max_length=20)
    points = models.IntegerField(default=1)
    created_at = models.DateTimeField()
    closed_at = models.DateTimeField(null=True, blank=True)
    merged_at = models.DateTimeField(null=True, blank=True)
    additions = models.IntegerField()
    deletions = models.IntegerField()
    changed_files = models.IntegerField()
    is_competition_repo = models.BooleanField(default=False)  # Flag for competition-specific PRs



class Issue(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='issues')
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='issues', null=True, blank=True)  # Optional for global issues
    issue_id = models.IntegerField()
    title = models.CharField(max_length=255)
    url = models.URLField()
    state = models.CharField(max_length=20)
    created_at = models.DateTimeField()
    closed_at = models.DateTimeField(null=True, blank=True)
    comments = models.IntegerField()
    is_competition_repo = models.BooleanField(default=False)  # Flag for competition-specific issues

class Commit(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commits')
    sha = models.CharField(max_length=40)
    message = models.TextField()
    url = models.URLField()
    created_at = models.DateTimeField()
    additions = models.IntegerField()
    deletions = models.IntegerField()
    repository_name = models.CharField(max_length=100)


class BlackListedRepository(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField()

    class Meta:
        verbose_name_plural = 'Blacklisted Repositories'