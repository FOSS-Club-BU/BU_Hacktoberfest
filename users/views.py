from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse

from django.contrib.auth.decorators import login_required
from .models import User
from .models import Repository, PullRequest, Issue, Commit
from .tasks import update_user_contributions, update_user_contributions, update_all_user_contributions
import os
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

def github_required(request):
    print(request.user.socialaccount_set)


@login_required
def profile(request):
    github_required(request)
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

# @login_required
# def update_user_contributions_view(request):
#     user = request.user
#     update_user_contributions(user)
#     return JsonResponse({'status': 'success'})

# @login_required
# def update_all_user_contributions_view(request):
#     update_all_user_contributions()
#     return JsonResponse({'status': 'success'})

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

# @login_required
# def pr_detail_view(request, id):
#     pr = get_object_or_404(PullRequest, id=id, user=request.user)
#     context = {
#         'pr': pr
#     }
#     return render(request, 'users/pr_detail.html', context)


def leaderboard_view(request):
    leaderboard_users = User.objects.filter(is_staff=False).order_by('-points')[:10]  # Top 10 users

    context = {
        'leaderboard_users': leaderboard_users
    }
    return render(request, 'leaderboard.html', context)


@csrf_exempt
def update_all(request):
    # have a secret key for this POST endpoint
    if request.POST.get('API_KEY') != os.getenv('API_KEY'):
        return JsonResponse({'status': 'error', 'message': 'Invalid secret key'})
    update_all_user_contributions()
    return JsonResponse({'status': 'success'})


def redirect_view(request):
    return redirect('profile')

def repositories_view(request):
    repositories = Repository.objects.filter(is_active=True)  # Fetch active repositories
    context = {
        'repositories': repositories
    }
    return render(request, 'repositories.html', context)