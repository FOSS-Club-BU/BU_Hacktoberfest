from django.contrib.auth.models import AbstractUser
from django.db import models
from allauth.socialaccount.models import SocialAccount

class HacktoberfestStats(models.Model):
    generated_at = models.DateTimeField(auto_now_add=True)
    total_participants = models.IntegerField()
    total_prs = models.IntegerField()
    total_merged_prs = models.IntegerField()
    total_repositories = models.IntegerField()
    average_points = models.FloatField()
    completion_rate = models.FloatField()
    
    class Meta:
        verbose_name = 'Hacktoberfest Statistics'
        verbose_name_plural = 'Hacktoberfest Statistics'

class StarredRepository(models.Model):
    name = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    url = models.URLField()
    stars = models.IntegerField()
    stars_text = models.CharField(max_length=20, default='0')
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Starred Repository'
        verbose_name_plural = 'Starred Repositories'
        ordering = ['-stars']

    def __str__(self):
        return f"{self.full_name} ({self.stars} stars)"

    @property
    def total_prs(self):
        return PullRequest.objects.filter(url__startswith=self.url).count()

    @property
    def merged_prs(self):
        return PullRequest.objects.filter(url__startswith=self.url, state='merged').count()

class DailyStats(models.Model):
    date = models.DateField()
    pr_count = models.IntegerField()
    active_users = models.IntegerField()
    points_awarded = models.IntegerField()

    class Meta:
        verbose_name = 'Daily Statistics'
        verbose_name_plural = 'Daily Statistics'

class TopContributor(models.Model):
    stats = models.ForeignKey(HacktoberfestStats, on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    points = models.IntegerField()
    merged_prs = models.IntegerField()
    rank = models.IntegerField()

class TopRepository(models.Model):
    stats = models.ForeignKey(HacktoberfestStats, on_delete=models.CASCADE)
    repository = models.ForeignKey('Repository', on_delete=models.CASCADE)
    total_prs = models.IntegerField()
    merged_prs = models.IntegerField()
    unique_contributors = models.IntegerField()

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
        social_account = SocialAccount.objects.get(user=self, provider='github')
        return social_account.extra_data.get('login')
    
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
    
    def get_tech_stack(self):
        return [tech.strip() for tech in self.tech_stack.split(',') if tech.strip()]

    class Meta:
        verbose_name_plural = 'Repositories'

class PullRequest(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pull_requests')
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='pull_requests', null=True, blank=True)
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
    is_competition_repo = models.BooleanField(default=False)

class Issue(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='issues')
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='issues', null=True, blank=True)
    issue_id = models.IntegerField()
    title = models.CharField(max_length=255)
    url = models.URLField()
    state = models.CharField(max_length=20)
    created_at = models.DateTimeField()
    closed_at = models.DateTimeField(null=True, blank=True)
    comments = models.IntegerField()
    is_competition_repo = models.BooleanField(default=False)

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