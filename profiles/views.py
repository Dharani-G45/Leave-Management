from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Profile

@login_required
def profile_page(request):
    try:
        user_profile = request.user.profile
    except Profile.DoesNotExist:
        user_profile = None

    context = {
        'profile': user_profile,
        'user': request.user
    }
    return render(request, 'profiles/profile.html', context)