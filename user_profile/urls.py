from django.urls import path
from . import views

urlpatterns = [
    path('complete/', views.complete, name='complete_profile'),
    path('user/<str:username>/', views.profile, name='user_profile'),
    path('user/edit/linkedin_id/', views.edit_linkedin_id, name='edit_linkedin_id'),
    path('rankings/', views.rankings, name='rankings'),
]
