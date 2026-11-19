
"""
URL configuration for student_management project.
"""

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from registration.views import StaffLoginView

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # Existing Home pages
    path('', include('home.urls')),

    # Module 08 - Staff Login
    path(
        'login/',
        StaffLoginView.as_view(),
        name='login'
    ),

    # Module 08 - Staff Logout
    path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),

    # Existing Registration pages
    path('registration/', include('registration.urls')),
]
