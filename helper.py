import requests
import json

from django.http import HttpResponse
from django.shortcuts import HttpResponseRedirect, reverse
from django.utils import timezone
from project.models import ActiveIssue

SUCCESS, FAILED = 1, 2


def safe_hit_url(url, payload=None, headers=None, timeout=10):
    """
        Function to safely HIT an API with all exceptions being handled.
    """
    org = "Github"
    try:
        r = requests.get(url, params=payload, headers=headers, timeout=timeout)
        print(f"\n\nHeaders are: {r.request.headers}")

        try:
            response_data = r.json()
            return {
                "status": SUCCESS,
                "data": response_data
            }
        except json.decoder.JSONDecodeError:
            error_str = f"Internal Server Error: Could not fetch data. Probably {org} Server is down. Try again!"
            return {
                "status": FAILED,
                "message": error_str,
            }
    except requests.exceptions.ConnectTimeout:
        error_str = f"ConnectTimeout: Could not connect to {org} server. Check your Internet Connection and Try Again!"
        return {
            "status": FAILED,
            "message": error_str,
        }
    except requests.exceptions.ReadTimeout:
        error_str = f"ReadTimeout: Connected to {org} server but it took too long to respond. Try Again!"
        return {
            "status": FAILED,
            "message": error_str,
        }
    except requests.exceptions.ConnectionError:
        error_str = f"ConnectTimeout: Could not connect to {org} server. Check your Internet Connection and Try Again!"
        return {
            "status": FAILED,
            "message": error_str,
        }


def complete_profile_required(func):
    """
    A decorator which checks if the profile is complete or not.
    In case the profile is not complete, user is directed to Complete Profile Page.
    :param func:
    :return:
    """
    def wrapper(*args, **kwargs):
        request = args[0]
        user = request.user
        if user.is_authenticated and (not user.userprofile.is_complete):
            return HttpResponseRedirect(reverse('complete_profile'))
        return func(*args, **kwargs)

    return wrapper


def check_issue_time_limit(func):
    """
    A decorator which checks if the issue time limit is complete or not.
    :param func:
    :return:
    """
    def wrapper(*args, **kwargs):
        request = args[0]
        user = request.user
        issue_pk = kwargs.get('issue_pk')
        if issue_pk is None:
            active_issue_pk = kwargs.get('active_issue_pk')
            username = kwargs.get('username')
            if active_issue_pk is None:
                if username is None:
                    return HttpResponse(
                        "Now, this is something which is unhandled. Copy the URL and Report to the Team "
                        "Now.")
                else:
                    if username == user.username:  # Visiting own profile
                        active_issue_qs = ActiveIssue.objects.filter(contributor=user)
                        for active_issue in active_issue_qs:
                            if is_deadline_passed(active_issue):  # Deadline Crossed
                                active_issue.delete()
                    return func(*args, **kwargs)
            else:
                active_issue_qs = ActiveIssue.objects.filter(pk=active_issue_pk, contributor=user)
                if active_issue_qs:
                    active_issue = active_issue_qs[0]
                    if is_deadline_passed(active_issue):  # Deadline Crossed
                        active_issue.delete()
                        # TODO: ISSUE: set a message i.e. "Dead Crossed" here and redirect to user profile and show \
                        # this
                        #  message
                        return HttpResponse("Deadline Crossed")
                    else:
                        return func(*args, **kwargs)
                else:
                    # TODO: ISSUE: Redirect to 404 page
                    return HttpResponse("That's a 404")
        else:
            # Some operation regarding this issue is taking place
            active_issue_qs = ActiveIssue.objects.filter(issue=issue_pk)
            for active_issue in active_issue_qs:
                if is_deadline_passed(active_issue):  # Deadline
                    active_issue.delete()
            return func(*args, **kwargs)

    return wrapper


def is_deadline_passed(active_issue):
    current_time = timezone.now()
    deadline = active_issue.assigned_at + timezone.timedelta(days=active_issue.issue.get_issue_days_limit())
    time_delta = (deadline - current_time)
    total_seconds = time_delta.total_seconds()
    if total_seconds <= 0:  # Deadline Crossed
        return True
    return False
