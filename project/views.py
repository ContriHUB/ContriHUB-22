from django.shortcuts import HttpResponseRedirect, reverse
from contrihub.settings import AVAILABLE_PROJECTS, LABEL_MENTOR, LABEL_LEVEL, LABEL_POINTS, DEPENDABOT_LOGIN, \
    LABEL_RESTRICTED, DEFAULT_FREE_POINTS, DEFAULT_VERY_EASY_POINTS, DEFAULT_EASY_POINTS, DEFAULT_MEDIUM_POINTS, \
    DEFAULT_HARD_POINTS
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
from .models import Project, Issue
from helper import safe_hit_url, SUCCESS, complete_profile_required
from config import api_endpoint, html_endpoint

User = get_user_model()


@user_passes_test(lambda u: u.userprofile.role == u.userprofile.ADMIN)
@complete_profile_required
def populate_projects(request):
    """
    Used to Populate Projects in Local Database. Creates entries based on project names present in AVAILABLE_PROJECTS
    config variable in settings.py
    :param request:
    :return:
    """
    api_uri = api_endpoint['contrihub_api_1']
    html_uri = html_endpoint['contrihub_html']
    # print(AVAILABLE_PROJECTS)
    for project_name in AVAILABLE_PROJECTS:
        project_qs = Project.objects.filter(name=project_name)
        if not project_qs:
            api_url = f"{api_uri}{project_name}"
            html_url = f"{html_uri}{project_name}"
            Project.objects.create(
                name=project_name,
                api_url=api_url,
                html_url=html_url
            )

    return HttpResponseRedirect(reverse('home'))


@user_passes_test(lambda u: u.userprofile.role == u.userprofile.ADMIN)
@complete_profile_required
def populate_issues(request):
    """
    Used to Populate Issues in Local Database. It fetches Issues from Github using Github API.
    :param request:
    :return:
    """
    project_qs = Project.objects.all()

    social = request.user.social_auth.get(provider='github')
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {social.extra_data['access_token']}",  # Authentication
    }

    uri = api_endpoint['contrihub_api_2']

    for project in project_qs:
        url = f"{uri}{project.name}/issues"
        response = safe_hit_url(url=url, headers=headers)
        if response['status'] == SUCCESS:
            issues = response['data']
            for issue in issues:
                # print(issue)
                # TODO: Can be given as ISSUE
                try:
                    if issue['user']['login'] == DEPENDABOT_LOGIN:  # Ignoring issues created by Dependabot
                        continue
                except:
                    continue
                finally:
                    print('error')
                if issue.get('pull_request') is not None:  # this issue is actually a PR.
                    # Source: https://docs.github.com/en/rest/reference/issues#list-repository-issues
                    print("This issue is a actually a PR")
                    continue
                title, number, state = issue['title'], issue['number'], issue['state']
                mentor_name, level, points, is_restricted = parse_labels(labels=issue['labels'])
                # print("Fsf ",mentor_name)
                api_url, html_url = issue['url'], issue['html_url']
                issue_qs = Issue.objects.filter(number=number, project=project)

                if issue_qs:  # Update if already present
                    db_issue = issue_qs.first()
                    db_issue.title = title
                    db_issue.level = level
                    db_issue.points = points
                    db_issue.is_restricted = is_restricted
                    if state == "closed":
                        db_issue.state = db_issue.CLOSED
                    else:
                        db_issue.state = db_issue.OPEN

                else:  # Else Create New
                    db_issue = Issue(
                        number=number,
                        title=title,
                        api_url=api_url,
                        html_url=html_url,
                        project=project,
                        level=level,
                        points=points,
                        is_restricted=is_restricted
                    )

                print(db_issue)
                try:
                    mentor = User.objects.get(username=mentor_name)
                    db_issue.mentor = mentor
                except User.DoesNotExist:
                    pass

                db_issue.save()

    return HttpResponseRedirect(reverse('home'))


def parse_labels(labels):
    mentor, level, points, is_restricted = None, Issue.EASY, 0, False
    for label in labels:

        if str(label["description"]).lower() == LABEL_MENTOR:  # Parsing Mentor
            # print("dfs ",label["name"])
            mentor = parse_mentor(label["name"])

        if str(label["description"]).lower() == LABEL_LEVEL:  # Parsing Level
            level, points = parse_level(label["name"])  # Fetching Level and it's default point

        if str(label["description"]).lower() == LABEL_POINTS:  # Parsing Points
            points = parse_points(label["name"])  # Consider Custom points if provided

        if str(label["name"]).lower() == LABEL_RESTRICTED:  # Parsing Is Restricted
            is_restricted = True

    return mentor, level, points, is_restricted


def parse_level(level):
    level = str(level).lower()
    levels_read = (Issue.FREE_READ, Issue.VERY_EASY_READ, Issue.EASY_READ, Issue.MEDIUM_READ, Issue.HARD_READ)
    levels = (Issue.FREE, Issue.VERY_EASY, Issue.EASY, Issue.MEDIUM, Issue.HARD)
    default_points = (
        DEFAULT_FREE_POINTS, DEFAULT_VERY_EASY_POINTS, DEFAULT_EASY_POINTS, DEFAULT_MEDIUM_POINTS, DEFAULT_HARD_POINTS
    )

    for lev, read, pts in zip(levels, levels_read, default_points):
        if level == str(read).lower():
            return lev, pts

    return Issue.EASY, DEFAULT_EASY_POINTS  # Default FallBack


def parse_mentor(mentor):
    return str(mentor)


def parse_points(points):
    points = str(points)

    if points.isnumeric():
        return int(float(points))

    return 0  # Default FallBack
