from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('authorize/', views.authorize, name='authorize'),
    path('logout/', views.logout_, name='logout'),
    path('request_issue_assignment/<int:issue_pk>/', views.request_issue_assignment, name='request_issue_assignment'),
    path('accept_issue_request/<int:issue_req_pk>/', views.accept_issue_request, name='accept_issue_request'),
    path('reject_issue_request/<int:issue_req_pk>/', views.reject_issue_request, name='reject_issue_request'),
    path('submit_pr_request/<int:active_issue_pk>/', views.submit_pr_request, name='submit_pr_request'),
    path('accept_pr/<int:pk>/', views.accept_pr, name='accept_pr'),
    path('reject_pr/<int:pk>/', views.reject_pr, name='reject_pr'),
    path('filter_by_domain/<int:domain_pk>/', views.filter_by_domain, name='filter_by_domain'),
    path('filter_by_subdomain/<int:subdomain_pk>/', views.filter_by_subdomain, name='filter_by_subdomain'),
]
