from django.contrib import admin
from django.urls import path
from core.views import (
    register_view, login_view, logout_view,
    admin_panel, create_test, take_test,
    users_list, results_list, stats_view, create_admin
)

urlpatterns = [
    path('', login_view, name='home'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),

    path('admin/', admin.site.urls),
    path('admin-panel/', admin_panel, name='admin_panel'),
    path('create-admin/', create_admin, name='create_admin'),

    path('create/', create_test, name='create_test'),
    path('test/', take_test, name='take_test'),

    path('users/', users_list, name='users_list'),
    path('results/', results_list, name='results_list'),
    path('stats/', stats_view, name='stats_view'),
]
