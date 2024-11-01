from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Count, Prefetch, Max, Q, Min, Avg, Sum
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.decorators import login_required
from .models import User, Repository, PullRequest, Issue, Commit
from .models import User, Repository, PullRequest, HacktoberfestStats, DailyStats, TopContributor, TopRepository, StarredRepository
from .tasks import update_user_contributions, update_all_user_contributions
import os
from django.db.models.functions import TruncDate
from django.views.decorators.csrf import csrf_exempt
import requests

def update_starred_repositories():
    temp_l = []
    for pr in PullRequest.objects.filter(is_competition_repo=True, state='merged'):
        repo_url = pr.url.split('/pull')[0]
        print(repo_url)
        try:
            if repo_url in temp_l:
                continue
            response = requests.get(
                f"https://api.github.com/repos/{repo_url.replace('https://github.com/','')}", 
                headers={
                    'Authorization': f"token {os.getenv('GITHUB_API_TOKEN')}",
                    'Accept': 'application/vnd.github.v3+json'
                }
            )
            print(repo_url + " " + str(response.status_code))
            if response.status_code == 200:
                repo_data = response.json()
                print(repo_data['stargazers_count'])
                if repo_data['stargazers_count'] >= 200:
                    repo, created = StarredRepository.objects.update_or_create(
                        url=repo_url,
                        defaults={
                            'name': repo_data['name'],
                            'full_name': repo_data['full_name'],
                            'stars': repo_data['stargazers_count'],
                            'stars_text': f"{repo_data['stargazers_count']/1000:.1f}k"
                        }
                    )
                    repo.update_pr_counts()
            temp_l.append(repo_url)
        except Exception as e:
            print(f"Error fetching repo data: {e}")

def github_required(request):
    print(request.user.socialaccount_set)

def event_ended_view(request):
    return render(request, 'event_ended.html')

def assign_pull_request_to_top_repo(pr):
    repository = Repository.objects.filter(url__startswith=pr.url.split('/pull')[0]).first()
    pr.repository = repository
    pr.save()

def generate_stats():
    # Calculate basic stats
    stats = HacktoberfestStats.objects.create(
        total_participants=User.objects.count(),
        total_prs=PullRequest.objects.count(),
        total_prs_in_competition_repos=PullRequest.objects.filter(is_competition_repo=True).count(),
        total_merged_prs=PullRequest.objects.filter(state='merged').count(),
        total_merged_prs_in_competition_repos=PullRequest.objects.filter(state='merged', is_competition_repo=True).count(),
        total_repositories=Repository.objects.count(),
        average_points=User.objects.aggregate(avg_points=Avg('points'))['avg_points'] or 0,
        completion_rate=PullRequest.objects.filter(state='merged').count() / PullRequest.objects.count() * 100 if PullRequest.objects.count() > 0 else 0
    )

    # Calculate most active day
    most_active_day = DailyStats.objects.order_by('-pr_count').first()
    if most_active_day:
        stats.most_active_day = most_active_day.date
        stats.save()

    # Top contributors
    top_users = User.objects.annotate(
        merged_prs=Count('pull_requests', filter=Q(pull_requests__state='merged'))
    ).order_by('-points')[:10]

    for rank, user in enumerate(top_users, 1):
        TopContributor.objects.create(
            stats=stats,
            user=user,
            points=user.points,
            merged_prs=user.merged_prs,
            rank=rank
        )

    # Repository stats
    hacktoberfest_repos = Repository.objects.filter(is_active=True).annotate(
        total_prs=Count('pull_requests', distinct=True),
        merged_prs=Count('pull_requests', filter=Q(pull_requests__state='merged'), distinct=True),
        unique_contributors=Count('pull_requests__user', distinct=True)
    ).order_by('-merged_prs')

    for repo in hacktoberfest_repos:
        TopRepository.objects.create(
            stats=stats,
            repository=repo,
            total_prs=repo.total_prs,
            merged_prs=repo.merged_prs,
            unique_contributors=repo.unique_contributors
        )

    # Daily stats
    daily_prs = PullRequest.objects.annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        pr_count=Count('id'),
        active_users=Count('user', distinct=True),
        points_awarded=Sum('points')
    ).order_by('date')

    for day in daily_prs:
        DailyStats.objects.create(**day)

    return stats

def stats_view(request):
    stats = HacktoberfestStats.objects.last()
    if not stats:
        stats = generate_stats()

    hacktoberfest_repos = Repository.objects.filter(is_active=True).annotate(
        total_prs=Count('pull_requests', distinct=True),
        merged_prs=Count('pull_requests', filter=Q(pull_requests__state='merged'), distinct=True),
        unique_contributors=Count('pull_requests__user', distinct=True)
    ).order_by('-merged_prs')

    starred_repos = StarredRepository.objects.all().order_by('-stars')
    daily_stats = DailyStats.objects.all().distinct('date').order_by('date')
    top_contributors = TopContributor.objects.filter(stats=stats).order_by('rank')

    return render(request, 'stats.html', {
        'stats': stats,
        'daily_stats': daily_stats,
        'top_contributors': top_contributors,
        'hacktoberfest_repos': hacktoberfest_repos,
        'starred_repos': starred_repos
    })

@login_required
def profile(request):
    user = request.user
    no_of_prs = PullRequest.objects.filter(user=user).count()
    no_of_issues = Issue.objects.filter(user=user).count()
    no_of_commits = Commit.objects.filter(user=user).count()
    context = {
        'user': user.first_name,
        'no_of_prs': no_of_prs,
        'no_of_issues': no_of_issues,
        'no_of_commits': no_of_commits
    }
    return JsonResponse(context)

@login_required
def profile_view(request):
    if not request.user.socialaccount_set.filter(provider='github').exists():
        return redirect('welcome')
    user = request.user
    total_commits = user.commits.count()
    total_prs = user.pull_requests.count()
    total_merged_prs = user.pull_requests.filter(state='merged').count()
    total_issues = user.issues.count()
    total_closed_issues = user.issues.filter(state='closed').count()
    total_open_issues = user.issues.filter(state='open').count()
    recent_prs = user.pull_requests.filter(is_competition_repo=True).order_by('-created_at')
    recent_commits = user.commits.order_by('-created_at')[:10]
    recent_issues = user.issues.order_by('-created_at')[:10]
    context = {
        'user': user,
        'total_commits': total_commits,
        'total_prs': total_prs,
        'total_merged_prs': total_merged_prs,
        'total_issues': total_issues,
        'total_closed_issues': total_closed_issues,
        'total_open_issues': total_open_issues,
        'recent_prs': recent_prs,
        'recent_commits': recent_commits,
        'recent_issues': recent_issues,
    }
    return render(request, 'users/profile.html', context)

@login_required
def welcome_view(request):
    if request.user.socialaccount_set.filter(provider='github').exists():
        return redirect('profile')
    return render(request, 'welcome.html')

LEADERBOARD_REVEALED = os.getenv('LEADERBOARD_REVEALED', False)

def leaderboard_view(request):
    if LEADERBOARD_REVEALED or request.user.is_staff:
        return render(request, 'leaderboard.html')
    else:
        return render(request, 'leaderboard_not_available.html', {
            'reveal_date': "8th October, 2024"
        })

def leaderboard_api_view(request):
    if LEADERBOARD_REVEALED or request.user.is_staff:
        social_accounts = SocialAccount.objects.filter(provider='github')

        users_query = (
            User.objects.filter(socialaccount__provider='github')
            .prefetch_related(Prefetch('socialaccount_set', queryset=social_accounts, to_attr='social_data'))
            .annotate(
                total_merged_prs=Count('pull_requests', filter=Q(pull_requests__state='merged')),
                last_merged_pr=Max('pull_requests__closed_at', filter=Q(pull_requests__state='merged'))
            )
            .order_by('-points', 'last_merged_pr')
        )
        
        data = {
            'users': [{
                'rank': (i + 1),
                'first_name': user.first_name,
                'last_name': user.last_name,
                'github_username': user.social_data[0].extra_data.get('login') if user.social_data else '',
                'points': user.points,
                'total_merged_prs': user.total_merged_prs,
                'id': user.username
            } for i, user in enumerate(users_query)]
        }

        return JsonResponse(data, safe=False)
    
    else:
        return JsonResponse({'message': 'Leaderboard not available yet'}, status=403)

@csrf_exempt
def update_all(request):
    if request.POST.get('API_KEY') != os.getenv('API_KEY'):
        return JsonResponse({'status': 'error', 'message': 'Invalid secret key'})
    update_all_user_contributions()
    update_starred_repositories()
    return JsonResponse({'status': 'success'})

def redirect_view(request):
    return redirect('profile')

def repositories_view(request):
    repositories = Repository.objects.filter(is_active=True)
    context = {
        'repositories': repositories
    }
    return render(request, 'repositories.html', context)

def public_profile_view(request, username):
    user = get_object_or_404(User, username=username)
    pull_requests = PullRequest.objects.filter(user=user).order_by('-created_at')
    data = {
        'name': f"{user.first_name} {user.last_name}",
        'github_username': user.get_profile_username(),  
        'points': user.points,
        'total_merged_prs': user.total_merged_prs,
        'profile_pic': "https://avatars.githubusercontent.com/"+user.get_profile_username(),
        'github_link': f"https://github.com/{user.get_profile_username()}",
        'pull_requests': pull_requests
    }
    return render(request, 'users/public_profile.html', {'user_data': data})