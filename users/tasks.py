import requests
from datetime import datetime
from django.utils import timezone
# from celery import shared_task
from .models import User, PullRequest, Issue, Repository, BlackListedRepository
# import allauth
from allauth.socialaccount.models import SocialLogin, SocialToken, SocialApp
from allauth.socialaccount.models import SocialAccount


GITHUB_API_URL = 'https://api.github.com'
START_DATE = datetime(2024, 10, 1)  # Start tracking from October 1, 2024
END_DATE = datetime(2024, 10, 31)   # End tracking on October 31, 2024

def get_headers(user):
    print(SocialToken.objects.get(
            account__user=user, account__provider='github'
        ).token)
    return {
        'Authorization': f"token {SocialToken.objects.get(account__user=user, account__provider='github').token}",
        'Accept': 'application/vnd.github.v3+json'
    }

def update_points(user, points):
    user.points = points
    user.save()


# @shared_task
def update_all_user_contributions():
    users = User.objects.all()
    for user in users:
        print(f'Processing user {user}')
        try:
            github_account = SocialAccount.objects.get(user=user, provider='github')
            update_user_contributions(user)
        except SocialAccount.DoesNotExist:
            print(f'User {user} does not have a linked GitHub account')

def update_user_contributions(user):

    update_global_pull_requests(user)
    # update_global_issues(user)

    user.last_updated = timezone.now()
    user.save()


def update_global_pull_requests(user):
    LABEL_POINTS = {
        'BU_Hacktoberfest:1': 1,
        'BU_Hacktoberfest:2': 2,
        'BU_Hacktoberfest:3': 3,
    }
    active_urls = Repository.objects.filter(is_active=True).values_list('url', flat=True)
    active_urls = list(active_urls)

    blacklisted_repos = BlackListedRepository.objects.all().values_list('url', flat=True)

    response = requests.get(f'{GITHUB_API_URL}/search/issues?q=author:{user.socialaccount_set.get(provider="github").extra_data["login"]}+type:pr&sort=created&per_page=100', headers=get_headers(user))
    
    if response.status_code == 200:
        prs = response.json()['items']
        total_points = 0

        for pr_data in prs:
            print(f'Processing PR {pr_data["html_url"]}')
            pr_state = pr_data['state']
            if pr_state == 'closed' and pr_data['pull_request'].get('merged_at'):
                pr_state = 'merged'
            
            created_at = datetime.strptime(pr_data['created_at'], r"%Y-%m-%dT%H:%M:%SZ")
            
            if START_DATE <= created_at <= END_DATE:
                repo_url = pr_data['html_url'].split('/pull')[0]
                is_competition_repo = repo_url in active_urls
                if not is_competition_repo:
                    if repo_url in blacklisted_repos:
                        is_competition_repo = False
                    else:
                        response = requests.get(f"{GITHUB_API_URL}/repos/{repo_url.replace('https://github.com/','')}", headers=get_headers(user))
                        # print(response)
                        if response.status_code == 200:
                            repo_data = response.json()
                            print("Stars count: ", repo_data['stargazers_count'])
                            if repo_data['stargazers_count'] > 200:
                                is_competition_repo = True
                        else:
                            print(f'Failed to fetch repo data for {repo_url}: {response.json()}')

                else:
                    repo = Repository.objects.get(url=repo_url)
                    if repo.usernames_not_eligible:
                        if user.get_profile_username() in repo.usernames_not_eligible.split(','):
                            is_competition_repo = False

                # Default points
                points = 1 if is_competition_repo else 0
                labels = [label['name'] for label in pr_data['labels']]

                for label in labels:
                    if label in LABEL_POINTS:
                        points = LABEL_POINTS[label]
                        break

                if pr_state == 'merged' and is_competition_repo:
                    total_points += points

                PullRequest.objects.update_or_create(
                    user=user,
                    url=pr_data['html_url'],
                    defaults={
                        'title': pr_data['title'],
                        'pr_id': pr_data['number'],
                        'state': pr_state,
                        'created_at': pr_data['created_at'],
                        'merged_at': pr_data.get('merged_at'),
                        'closed_at': pr_data.get('closed_at'),
                        'additions': pr_data.get('additions', 0),
                        'deletions': pr_data.get('deletions', 0),
                        'points': points,
                        'changed_files': pr_data.get('changed_files', 0),
                        'is_competition_repo': is_competition_repo 
                    }
                )

                
        update_points(user, total_points)

    else:
        print(f'Failed to fetch PRs for user {user}: {response.json()}')

def update_global_issues(user):
    response = requests.get(f'{GITHUB_API_URL}/search/issues?q=author:{user.github_username}+type:issue', headers=get_headers(user))
    if response.status_code == 200:
        issues = response.json()['items']
        for issue_data in issues:
            Issue.objects.update_or_create(
                user=user,
                issue_id=issue_data['number'],
                defaults={
                    'title': issue_data['title'],
                    'url': issue_data['html_url'],  
                    'state': issue_data['state'],
                    'created_at': issue_data['created_at'],
                    'closed_at': issue_data.get('closed_at'),
                    'comments': issue_data['comments'],
                    'is_competition_repo': False  # Mark this as a global issue
                }
            )
