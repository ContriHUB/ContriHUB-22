from django.shortcuts import render, HttpResponseRedirect, reverse, HttpResponse, redirect
from django.core.mail import send_mail, BadHeaderError

from home.helpers import EmailThread
from django.core import mail
from project.models import Project, Issue, IssueAssignmentRequest, Like
from project.models import ActiveIssue, PullRequest, Domain, SubDomain, Dislike

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from helper import complete_profile_required, check_issue_time_limit
from project.forms import PRSubmissionForm, PRJudgeForm
from django.utils import timezone
from django.contrib import messages


# TODO:ISSUE: Replace each HttpResponse with a HTML page
# TODO:ISSUE: Create a URL to view each Issue on a separate Page with all its information.
# TODO:ISSUE: Create a URL to view each PR on a separate Page with all its information.
# TODO:ISSUE: Create a URL to view each Issue Assignment Request on a separate Page with all its information.
# TODO:ISSUE: Make a Custom Http404 Page
# TODO:ISSUE: Up-vote Down-vote Issue Feature
from user_profile.models import UserProfile
from .forms import ContactForm


@complete_profile_required
def home(request):
    global issues_qs, domain, subdomain
    project_qs = Project.objects.all()
    issues_qs = Issue.objects.all()
    domains_qs = Domain.objects.all()
    subdomains_qs = SubDomain.objects.all()
    domain = 'All'
    subdomain = 'All'
    context = {
        'projects': project_qs,
        'issues': issues_qs,
        'domains': domains_qs,
        'subdomains': subdomains_qs,
        'curr_domain': domain,
        'curr_subdomain': subdomain
    }
    return render(request, 'home/index.html', context=context)


@complete_profile_required
def filter_by_domain(request, domain_pk):
    global issues_qs, domain, subdomain
    subdomain = 'All'
    domain = Domain.objects.get(pk=domain_pk)
    project_qs = Project.objects.all()
    issues_qs = Issue.objects.filter(project__domain=domain)
    domains_qs = Domain.objects.all()
    subdomains_qs = SubDomain.objects.all()
    context = {
        'projects': project_qs,
        'issues': issues_qs,
        'domains': domains_qs,
        'subdomains': subdomains_qs,
        'curr_domain': domain,
        'curr_subdomain': subdomain
    }
    return render(request, 'home/index.html', context=context)


@complete_profile_required
def filter_by_subdomain(request, subdomain_pk):
    global issues_qs, domain, subdomain
    subdomain = SubDomain.objects.get(pk=subdomain_pk)
    project_qs = Project.objects.all()
    if domain != 'All':
        issues_qs = Issue.objects.filter(project__domain=domain)
    issues_qs = issues_qs.filter(project__subdomain=subdomain)
    domains_qs = Domain.objects.all()
    subdomains_qs = SubDomain.objects.all()
    context = {
        'projects': project_qs,
        'issues': issues_qs,
        'domains': domains_qs,
        'subdomains': subdomains_qs,
        'curr_domain': domain,
        'curr_subdomain': subdomain
    }
    return render(request, 'home/index.html', context=context)


def authorize(request):
    """
    Used for rendering authorize.html which is responsible for both LogIn and SignUp
    :param request:
    :return:
    """
    return render(request, 'home/authorize.html', {})


@login_required
def logout_(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))


@login_required
@complete_profile_required
@check_issue_time_limit
def request_issue_assignment(request, issue_pk):
    issue = Issue.objects.get(pk=issue_pk)
    requester = request.user
    if issue.is_assignable(requester=requester):

        IssueAssignmentRequest.objects.create(issue=issue, requester=requester)
        message = f"Assignment Request for Issue <a href={issue.html_url}>#{issue.number}</a> of " \
                  f"<a href={issue.project.html_url}>{issue.project.name}</a> submitted successfully. "

        template_path = "home/mail_template_request_issue_assignment.html"
        email_context = {
            'mentor': issue.mentor,
            'user': requester,
            'url': issue.html_url,
            'protocol': request.build_absolute_uri().split('://')[0],
            'host': request.get_host(),
            'subject': "Request for Issue Assignment under ContriHUB-22.",
            'issue': issue,
            'action': '',
            'receiver': issue.mentor,
        }
        try:
            EmailThread(template_path, email_context).start()
            # TODO:ISSUE: Create Html Template for HttpResponses in home/views.py
            return HttpResponse(f"Issue Requested Successfully. Email Request Sent to the Mentor(\
                                {issue.mentor.username}). Keep your eye out on your profile.")
        except mail.BadHeaderError:
            linkedin_id = UserProfile.objects.get(user=issue.mentor).linkedin_id
            return HttpResponse(f"Issue Requested Successfully, but there was some problem sending email to the\
                                mentor("f"{issue.mentor.username}). For quick response from mentor try contacting\
                                him/her on Linkedin({linkedin_id})")

    message = f"Assignment Request for <a href={issue.html_url}>Issue #{issue.number}</a> of <a href=\
              {issue.project.html_url}>" f"{issue.project.name}</a> cannot be made by you currently."
    return HttpResponse(message)


@login_required
def accept_issue_request(request, issue_req_pk):
    user = request.user
    issue_request = IssueAssignmentRequest.objects.get(pk=issue_req_pk)
    issue = issue_request.issue
    requester = issue_request.requester
    if issue_request.is_acceptable(mentor=user):
        ActiveIssue.objects.create(issue=issue, contributor=requester)
        issue_request.state = IssueAssignmentRequest.ACCEPTED
        issue_request.save()
        # TODO:ISSUE Send Email to Student that their request is accepted
        message = f"Issue <a href={issue.html_url}>#{issue.number}</a> of Project <a href={issue.project.html_url}>" \
                  f"{issue.project.name}</a> successfully assigned to {requester}"
        return HttpResponse(message)
    else:
        message = "This Issue Cannot be accepted by you! Probably it's already Accepted/Rejected."
        return HttpResponse(message)


def reject_issue_request(request, issue_req_pk):
    # TODO: ISSUE: [Ask Mentor for Clarification]: Implement Reject Issue Request with proper error handling
    # user = request.user
    issue_request = IssueAssignmentRequest.objects.get(pk=issue_req_pk)
    issue = issue_request.issue
    requester = issue_request.requester
    issue_request.state = IssueAssignmentRequest.REJECTED
    issue_request.save()
    message = f"Issue <a href={issue.html_url}>#{issue.number}</a> of Project <a href={issue.project.html_url}>" \
              f"{issue.project.name}</a> is rejected for {requester}"
    return HttpResponse(message)


@login_required
@complete_profile_required
@check_issue_time_limit
def submit_pr_request(request, active_issue_pk):
    if request.method == 'GET':
        contributor = request.user
        active_issue_qs = ActiveIssue.objects.filter(pk=active_issue_pk, contributor=contributor)
        if active_issue_qs:
            active_issue = active_issue_qs[0]
            issue = active_issue.issue
            pr_qs = PullRequest.objects.filter(issue_id=issue.pk, contributor=contributor)
            if pr_qs:
                # If resubmitting PR request for Active Issue
                form = PRSubmissionForm(request.GET, instance=pr_qs.first())
            else:
                form = PRSubmissionForm(request.GET)

            if active_issue.can_raise_pr(contributor=contributor) and form.is_valid():
                pr = form.save(commit=False)
                pr.issue = issue
                pr.contributor = request.user
                pr.state = PullRequest.PENDING_VERIFICATION
                pr.submitted_at = timezone.now()
                pr.save()

                # TODO:ISSUE Create Check on URL in backend so that it is a Valid Github PR URL.

                template_path = "home/mail_template_submit_pr_request.html"
                email_context = {
                    'mentor': issue.mentor,
                    'user': contributor,
                    'url': pr.pr_link,
                    'protocol': request.build_absolute_uri().split('://')[0],
                    'host': request.get_host(),
                    'issue': issue,
                    'action': '',
                    'subject': "Request for Approval of PR on an issue under ContriHUB-22.",
                    'receiver': issue.mentor,
                }
                try:
                    EmailThread(template_path, email_context).start()
                    message = f"Email Request Sent to the Mentor({issue.mentor.username}). PR Verification Request\
                              Successfully Submitted for <a href={issue.html_url}>Issue #" f"{issue.number}\
                              </a> of Project <a href={issue.project.html_url}>{issue.project.name}</a>"
                except mail.BadHeaderError:
                    ms_teams_id = UserProfile.objects.get(user=issue.mentor).ms_teams_id
                    message = f"PR Verification Request Successfully Submitted for <a href={issue.html_url}>Issue #" \
                              f"{issue.number}</a> of Project <a href={issue.project.html_url}>{issue.project.name}\
                              </a>. But there was some problem sending email to the mentor({issue.mentor.username})\
                              . For quick response from mentor try contacting him/her on MS-Teams({ms_teams_id})"
                return HttpResponse(message)
            else:
                message = f"This request cannot be full-filled. Probably you already submitted PR verification\
                          request " f"for <a href={issue.html_url}>Issue #{issue.number}</a> of Project <a href=" \
                          f"{issue.project.html_url}>{issue.project.name}</a>"
            return HttpResponse(message)

    message = "This request cannot be full-filled."
    return HttpResponse(message)


# TODO:ISSUE: Implement Functionality for mentor to assign bonus/peanlty points while accepting/rejecting the \
# issue.A form will be needed.

# TODO:ISSUE: Send an Email to Contributor Notifying that their PR is accepted/rejected.

# TODO:ISSUE: Implement a feature such that mentor is able to leave remarks about PR before Accepting/Rejecting\
#  (Some fields in Model need to be added/updated).

@login_required
@complete_profile_required
def judge_pr(request, pk):
    if request.method == 'GET':
        mentor = request.user
        pr_qs = PullRequest.objects.filter(pk=pk)
        if pr_qs:
            pr = pr_qs.first()
            issue = pr.issue

            if mentor.username == issue.mentor.username:
                contributor = pr.contributor

                pr = PullRequest.objects.get(issue=issue, contributor=contributor)
                form = PRJudgeForm(request.GET)
                if pr.state == PullRequest.PENDING_VERIFICATION and form.is_valid() and "accept" in request.GET:
                    bonus = form.cleaned_data['bonus']
                    penalty = form.cleaned_data['penalty']
                    remark = form.cleaned_data['remark']
                    pr.accept(bonus=bonus, penalty=penalty, remark=remark)
                    message = f"Successfully accepted <a href={pr.pr_link}>PR</a> of Issue <a href={issue.html_url}>" \
                        f"{issue.number}</a> of Project <a href={issue.project.html_url}>{issue.project.name}</a>"
                    template_path = "home/mail_template_pr_action.html"
                    email_context = {
                        'mentor': issue.mentor,
                        'user': contributor,
                        'url': pr.pr_link,
                        'protocol': request.build_absolute_uri().split('://')[0],
                        'host': request.get_host(),
                        'issue': issue,
                        'action': 'accepted',
                        'subject': "PR Accepted under ContriHUB-22.",
                        'receiver': contributor,
                    }
                    try:
                        EmailThread(template_path, email_context).start()
                        return HttpResponse(f"PR Accepted Successfully. Email sent to the contributor(\
                                            {contributor}).")
                    except mail.BadHeaderError:
                        return HttpResponse(f"PR Accepted Successfully, but there was some problem sending email \
                                            to the contributor("f"{contributor}).")
                elif pr.state == PullRequest.PENDING_VERIFICATION and form.is_valid() and "reject" in request.GET:
                    bonus = form.cleaned_data['bonus']
                    penalty = form.cleaned_data['penalty']
                    remark = form.cleaned_data['remark']
                    pr.reject(bonus=bonus, penalty=penalty, remark=remark)
                    message = f"Successfully rejected <a href={pr.pr_link}>PR</a> of Issue <a href={issue.html_url}>" \
                        f"{issue.number}</a> of Project <a href={issue.project.html_url}>{issue.project.name}</a>"
                    template_path = "home/mail_template_pr_action.html"
                    email_context = {
                        'mentor': issue.mentor,
                        'user': contributor,
                        'url': pr.pr_link,
                        'protocol': request.build_absolute_uri().split('://')[0],
                        'host': request.get_host(),
                        'issue': issue,
                        'action': 'rejected',
                        'subject': "PR Rejected under ContriHUB-22.",
                        'receiver': contributor,
                    }
                    try:
                        EmailThread(template_path, email_context).start()
                        return HttpResponse(f"PR rejected successfully. Email sent to the contributor(\
                                            {contributor}).")
                    except mail.BadHeaderError:
                        return HttpResponse(f"PR rejected successfully, but there was some problem sending email \
                                            to the contributor("f"{contributor}).")
                else:
                    message = "This PR Verification Request is already Accepted/Rejected. Probably in the FrontEnd You\
                                still see the " "Accept/Reject Button, because showing ACCEPTED/REJECTED status in\
                                frontend is an ISSUE."
            else:
                message = f"You are not mentor of Issue <a href={issue.html_url}>{issue.number}</a> of Project \
                     <a href="f"{issue.project.html_url}>{issue.project.name}</a>"
        else:
            message = "This PR is probably already Accepted. Probably in the FrontEnd You still see the " \
                    "Accept/Reject Button, because showing ACCEPTED/REJECTED status in frontend is an ISSUE."
        return HttpResponse(message)


@login_required
def contact_form(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        user = form['name'].value()
        email = form['email'].value()
        body = form['body'].value()
        subject = form['subject'].value()
        message = 'Name: {}\nEmail: {}\n\n{}'.format(user, email, body)
        try:
            send_mail(subject, message, '', ['contrihub.avishkar@gmail.com'])
        except BadHeaderError:
            return HttpResponse('Mail could not be sent. Try again later!!')
        messages.success(request, "Message sent successfully")
        return redirect('home')
    elif request.method == 'GET':
        form = ContactForm()
        return render(request, 'home/contact_form.html', context={'form': form})


@login_required
def likes(request, issue_pk):
    user = request.user.userprofile
    issue = Issue.objects.get(pk=issue_pk)
    current_likes = Issue.objects.get(pk=issue_pk).likes
    current_dislikes = Issue.objects.get(pk=issue_pk).dislikes
    liked = Like.objects.filter(user=user, issue=issue)
    disliked = Dislike.objects.filter(user=user, issue=issue)
    if not liked and not disliked:

        liked = Like.objects.create(user=user, issue=issue)
        current_likes = current_likes + 1

    elif not liked and disliked:

        liked = Like.objects.create(user=user, issue=issue)
        disliked = Dislike.objects.filter(user=user, issue=issue).delete()
        current_likes = current_likes + 1
        current_dislikes = current_dislikes - 1

    else:

        liked = Like.objects.filter(user=user, issue=issue).delete()
        current_likes = current_likes - 1

    Issue.objects.filter(pk=issue_pk).update(likes=current_likes)
    Issue.objects.filter(pk=issue_pk).update(dislikes=current_dislikes)
    return redirect('/')


@login_required
def dislikes(request, issue_pk):
    user = request.user.userprofile
    issue = Issue.objects.get(pk=issue_pk)
    current_likes = Issue.objects.get(pk=issue_pk).likes
    current_dislikes = Issue.objects.get(pk=issue_pk).dislikes
    liked = Like.objects.filter(user=user, issue=issue)
    disliked = Dislike.objects.filter(user=user, issue=issue)
    if not disliked and not liked:

        disliked = Dislike.objects.create(user=user, issue=issue)
        current_dislikes = current_dislikes + 1

    elif not disliked and liked:

        disliked = Dislike.objects.create(user=user, issue=issue)
        liked = Like.objects.filter(user=user, issue=issue).delete()
        current_likes = current_likes - 1
        current_dislikes = current_dislikes + 1

    else:

        disliked = Dislike.objects.filter(user=user, issue=issue).delete()
        current_dislikes = current_dislikes - 1

    Issue.objects.filter(pk=issue_pk).update(likes=current_likes)
    Issue.objects.filter(pk=issue_pk).update(dislikes=current_dislikes)
    return redirect('/')
