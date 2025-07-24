from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import register

urlpatterns = [
    #path('signup/', SignupPageView.as_view(), name='signup'),
    path('register/', register, name='signup'),

]
