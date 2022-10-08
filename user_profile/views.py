from django.shortcuts import render, HttpResponseRedirect, reverse, HttpResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from project.models import Issue, PullRequest, IssueAssignmentRequest, ActiveIssue
from .forms import UserProfileForm
from .models import UserProfile
from helper import complete_profile_required, check_issue_time_limit
from project.forms import PRSubmissionForm
import json

User = get_user_model()

# TODO:ISSUE: Implement feature where User can see how many Issues they have solved Level Wise
# TODO:ISSUE: Implement feature where user can follow/unfollow other users
# TODO:ISSUE: Implement feature to activities of followed users


@complete_profile_required
@check_issue_time_limit
def profile(request, username):
    """
    View which returns User Profile based on username.
    :param request:
    :param username:
    :return:
    """
    user = request.user
    native_profile_qs = UserProfile.objects.filter(user__username=username)
    if native_profile_qs:  # Checking if profile exists

        native_profile = native_profile_qs.first()

        if username == user.username:
            # TODO: ISSUE Fetch User's Avatar's URL from Github API and display it in profile
            pr_requests_by_student = PullRequest.objects.filter(contributor=user)
            assignment_requests_by_student = IssueAssignmentRequest.objects.filter(requester=user)
            active_issues = ActiveIssue.objects.filter(contributor=user)

            mentored_issues = Issue.objects.filter(mentor=user)
            assignment_requests_for_mentor = IssueAssignmentRequest.objects.filter(issue__mentor=user)
            pr_requests_for_mentor = PullRequest.objects.filter(issue__mentor=user)

            pr_form = PRSubmissionForm()

            context = {
                "student_years": UserProfile.YEARS,
                "student_courses": UserProfile.COURSES,
                "mentored_issues": mentored_issues,
                "pr_requests_by_student": pr_requests_by_student,
                "pr_requests_for_mentor": pr_requests_for_mentor,
                "active_issues": active_issues,
                "assignment_requests_by_student": assignment_requests_by_student,
                "assignment_requests_for_mentor": assignment_requests_for_mentor,
                'pr_form': pr_form,
                "native_profile": native_profile
            }
            return render(request, 'user_profile/profile.html', context=context)
        else:
            context = {
                "native_profile": native_profile
            }
            return render(request, 'user_profile/profile.html', context=context)
    return HttpResponse("Profile not found!")


@login_required
def complete(request):
    """
    For Completing User Profile after First Login.
    :param request:
    :return:
    """
    existing_profile = UserProfile.objects.get(user=request.user)
    if request.method == "GET":
        form = UserProfileForm(instance=existing_profile)
        context = {
            'form': form
        }
        return render(request, 'user_profile/complete_profile.html', context=context)

    form = UserProfileForm(request.POST, instance=existing_profile)
    if form.is_valid():
        # TODO:ISSUE Backend Check on Registration Number
        existing_profile = form.save(commit=False)
        existing_profile.is_complete = True
        existing_profile.save()
    return HttpResponseRedirect(reverse('user_profile', kwargs={'username': request.user.username}))

# TODO:ISSUE Edit Profile Functionality
@complete_profile_required
def edit_linkedin_id(request):
    try:
        if request.method == "POST":
            body = json.loads(request.body)
            if 'linkedin_id' not in body:
                return HttpResponse(status=400)
            
            existing_profile = UserProfile.objects.get(user=request.user)
            new_linkedin_id = body['linkedin_id']
            existing_profile.linkedin_id = new_linkedin_id
            existing_profile.save()

            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400)
    except Exception as e:
        print(e)
        return HttpResponse(status=400)

@login_required
def rankings(request):
    contributors = UserProfile.objects.filter(role=UserProfile.STUDENT).order_by('-total_points')
    context = {
        'contributors': contributors,
    }
    # TODO:ISSUE: Display number of Issues solved as well in the Rankings
    return render(request, 'user_profile/rankings.html', context=context)
