from django.urls import path, include
from profiles.views import logout, login, register, create_profile, member_profile, delete, verification_message

urlpatterns = [
    path('logout/', logout, name='logout'),
    path('login/', login, name='login'), 
    path('register/', register, name='register'),
    path('create-profile/', create_profile, name='create_profile'),
    path('delete/', delete, name="delete"),
    path('verification-message/', verification_message, name="verification_message"),
    path('member/<int:id>/', member_profile, name='member_profile'),
    path('password-reset/', include('profiles.url_reset')),
]