from django.shortcuts import render, HttpResponseRedirect, reverse, HttpResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
import requests
from project.models import Issue, Project, PullRequest, IssueAssignmentRequest, ActiveIssue
from project.views import parse_level
from .forms import UserProfileForm
from .models import UserProfile
from home.helpers import EmailThread_to_admin
from helper import complete_profile_required, check_issue_time_limit
from project.forms import PRJudgeForm, PRSubmissionForm, CreateIssueForm
from django.contrib import messages
import json
import re
from itertools import chain

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
            accepted_assignment_requests_for_mentor = assignment_requests_for_mentor.filter(state=1)
            rejected_assignment_requests_for_mentor = assignment_requests_for_mentor.filter(state=2)
            pending_assignment_requests_for_mentor = assignment_requests_for_mentor.filter(state=3)\
                                                                                   .order_by("requested_at")
            assignment_requests_for_mentor = chain(pending_assignment_requests_for_mentor,
                                                   accepted_assignment_requests_for_mentor,
                                                   rejected_assignment_requests_for_mentor)

            pr_requests_for_mentor = PullRequest.objects.filter(issue__mentor=user)
            accepted_pr_requests_for_mentor = pr_requests_for_mentor.filter(state=1)
            rejected_pr_requests_for_mentor = pr_requests_for_mentor.filter(state=2)
            pending_pr_requests_for_mentor = pr_requests_for_mentor.filter(state=3).order_by("submitted_at")
            pr_requests_for_mentor = chain(pending_pr_requests_for_mentor,
                                           accepted_pr_requests_for_mentor, rejected_pr_requests_for_mentor)

            pr_form = PRSubmissionForm()
            judge_form = PRJudgeForm()

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
                "judge_form": judge_form,
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
    if request.method == "POST":
        if form.is_valid():
            # TODO:ISSUE Backend Check on Registration Number
            existing_profile = form.save(commit=False)
            existing_profile.linkedin_id = request.POST['linkedin_id']
            regex = (r"^https?://((www|\w\w)\.)?linkedin.com/((in/[^/]+/?)|(pub/[^/]+/((\w|\d)+/?){3}))$")
            if re.fullmatch(regex, existing_profile.linkedin_id):
                existing_profile.is_complete = True
                existing_profile.save()
                return HttpResponseRedirect(reverse('user_profile', kwargs={'username': request.user.username}))
            else:
                context = {
                    'form': form,
                }
                existing_profile.is_complete = False
                messages.add_message(request, messages.ERROR, "Enter valid LinkedIn id")
                return render(request, 'user_profile/complete_profile.html', context=context)


@complete_profile_required
def edit_linkedin_id(request):
    try:
        if request.method == "POST":
            body = json.loads(request.body)
            if 'linkedin_id' not in body:
                return HttpResponse(status=400)

            existing_profile = UserProfile.objects.get(user=request.user)
            new_linkedin_id = body['linkedin_id']
            regex = (r"^https?://((www|\w\w)\.)?linkedin.com/((in/[^/]+/?)|(pub/[^/]+/((\w|\d)+/?){3}))$")
            if re.fullmatch(regex, new_linkedin_id):
                existing_profile.linkedin_id = new_linkedin_id
                existing_profile.save()
                return HttpResponse(status=200)
            else:
                return HttpResponse(status=400)
        else:
            return HttpResponse(status=400)
    except Exception:
        return HttpResponse(status=400)


@complete_profile_required
def edit_profile(request):
    try:
        if request.method == "POST":
            body = json.loads(request.body)

            if 'profile_regno' not in body:
                return HttpResponse(status=400)
            new_regno = body['profile_regno']

            if 'profile_name' not in body:
                return HttpResponse(status=400)
            new_name = body['profile_name']

            if 'profile_course' not in body:
                return HttpResponse(status=400)
            new_course = body['profile_course']

            if 'profile_year' not in body:
                return HttpResponse(status=400)
            new_year = body['profile_year']

            user = request.user
            template_path = "user_profile/mail_template_request_profile_edit.html"
            email_context = {
                'username': user.username,
                'protocol': request.build_absolute_uri().split('://')[0],
                'host': request.get_host(),
                'subject': f"Request for Profile Edit by {user.username}",
                'new_regno': new_regno,
                'new_name': new_name,
                'new_course': new_course,
                'new_year': new_year,
            }
            EmailThread_to_admin(template_path, email_context).start()

            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400)
    except Exception:
        return HttpResponse(status=400)


@login_required
def rankings(request):
    contributors = UserProfile.objects.filter(role=UserProfile.STUDENT).order_by('-total_points')
    context = {
        'contributors': contributors,
    }
    # TODO:ISSUE: Display number of Issues solved as well in the Rankings
    return render(request, 'user_profile/rankings.html', context=context)


@login_required
def create_issue(request):
    if request.method == 'POST':
        level = {
            '0': 'free',
            '1': 'easy',
            '2': 'medium',
            '3': 'hard',
            '4': 'very_easy'
        }
        form = CreateIssueForm(request.POST)
        project_id = form['project'].value()
        level_id = form['level'].value()
        mentor_id = form['mentor'].value()
        points = form['points'].value()
        is_restricted_str = form['is_restricted'].value()
        default_points = parse_level(level.get(level_id))
        title = form['title'].value()
        description = form['description'].value()

        is_default_points_used = False
        if points == '0':
            is_default_points_used = True
            points = str(default_points[1])
        is_restricted = False
        if is_restricted_str == '1':
            is_restricted = True

        project = Project.objects.get(id=project_id)
        level = level.get(level_id)
        mentor = User.objects.get(id=mentor_id).username
        url = project.api_url

        labels = [mentor, level]

        if not is_default_points_used:
            labels.append(points)

        if is_restricted:
            labels.append('restricted')

        url += '/issues'

        issue_detail = {
            'title': title,
            'body': description,
            'labels': labels
        }
        social = request.user.social_auth.get(provider='github')
        headers = {
            "Authorization": "token {}".format(social.extra_data['access_token']),
        }
        r = requests.post(url, data=json.dumps(issue_detail), headers=headers)
        response_data = r.json()
        # print(r)
        if r.status_code == 201:
            print('Successfully created Issue "%s"' % title)
            Issue.objects.create(
                title='' + response_data['title'],
                api_url='' + response_data['repository_url'],
                html_url='' + response_data['url'],
                project=project,
                mentor=User.objects.get(id=mentor_id),
                level=level_id,
                points=points,
                state=1,
                description=description,
                is_restricted=is_restricted
            )
            msg="Successfully created Issue: {}".format(title)
            messages.success(request, msg)
            return HttpResponseRedirect(reverse('user_profile', kwargs={'username': request.user.username}))
        else:
            print('Could not create Issue "%s"' % title)
            print('Response:', r.content)
            messages.error(request, "Error while creating the issue!!")
            return HttpResponseRedirect(reverse('user_profile', kwargs={'username': request.user.username}))
    elif request.method == 'GET':
        if request.user.userprofile.role == UserProfile.STUDENT:
            messages.error(request, "Student cannot create an issue!!")
            return HttpResponseRedirect(reverse('user_profile', kwargs={'username': request.user.username}))
        form = CreateIssueForm()
        return render(request, 'user_profile/create_issue.html', context={'form': form})
