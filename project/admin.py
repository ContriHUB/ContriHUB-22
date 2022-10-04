from django.contrib import admin
from .models import Project, Issue, PullRequest, IssueAssignmentRequest, ActiveIssue

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'domain', 'html_url')

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('title', 'number', 'project', 'mentor', 'level', 'points', 'state')

@admin.register(PullRequest)
class PullRequestAdmin(admin.ModelAdmin):
    list_display = ('contributor', 'pr_link', 'state', 'bonus', 'penalty', 'submitted_at')

@admin.register(IssueAssignmentRequest)
class IssueAssignmentRequestAdmin(admin.ModelAdmin):
    list_display = ('requester', 'issue', 'state')

@admin.register(ActiveIssue)
class ActiveIssueAdmin(admin.ModelAdmin):
    list_display = ('contributor', 'issue', 'assigned_at')



