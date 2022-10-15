from django.urls import path
from . import views

urlpatterns = [
    path('complete/', views.complete, name='complete_profile'),
    path('user/<str:username>/', views.profile, name='user_profile'),
    path('user/linkedin_id/edit/', views.edit_linkedin_id, name='edit_linkedin_id'),
    path('user/details/edit/', views.edit_profile, name='edit_profile'),
    path('rankings/', views.rankings, name='rankings'),
]
