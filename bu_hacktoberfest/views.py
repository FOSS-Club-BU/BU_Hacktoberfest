
from django.shortcuts import render

def home(request):
    return render(request, 'index.html')

def login(request):
    return render(request, 'login.html')


def faq_view(request):
    faqs = [
        {
            "question": "What is Hacktoberfest?",
            "answer": "Hacktoberfest is an annual event in October where developers contribute to open-source projects on GitHub, learning and engaging with the community."
        },
        {
            "question": "What is BU Hacktoberfest?",
            "answer": "BU Hacktoberfest is a month-long event at Bennett University where students can participate in Hacktoberfest, learn about open-source, and win prizes."
        },
        {
            "question": "How do I participate?",
            "answer": "Sign up on the website, link your GitHub account, and start contributing to open-source projects on GitHub."
        },
        {
            "question": "In which repos can I contribute to?",
            "answer": "You can contribute to any repositries listed on https://hacktoberfest.fossbu.co/repositories/ ."
        },
        {
            "question": "Will these PRs count towards the global Hacktoberfest?",
            "answer": "Yes, PRs made to the repositories containing the `Hacktoberfest` label will count towards the global Hacktoberfest event."
        },
        {
            "question": "How do I top the leaderboard?",
            "answer": "Contribute to as many repositories as you can, and make high-quality PRs. The more points you earn, the higher you will be on the leaderboard."
        },
        {
            "question": "Will each PR count as one point?",
            "answer": "Not necessarily. PRs can have different point values based on the difficulty of the task. Some PRs may be worth more points than others. You can check the issue labels for the point value."
        },
        {
            "question": "How do I earn points?",
            "answer": "You can earn points by making PRs to the repositories listed on the website. The points are based on the difficulty of the task and the quality of the PR."
        }
    ]

    return render(request, 'faq.html', {'faqs': faqs})
