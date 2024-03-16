from . import views
from django.contrib.auth.views import LogoutView, LoginView
from django.urls import path


urlpatterns = [
    path('accounts/login/', LoginView.as_view(template_name='page-signin.html', redirect_authenticated_user=True), name='login'),
    path('logout', LogoutView.as_view(template_name='page-signin.html'), name='logout'),
    path('', views.home_view, name=''),
    path("candidate-data", views.candidate_data_view, name="candidate-data"),
    path("register", views.register_view, name="register"),
     path('dashboard-power-bi/', views.dashboard_power_bi, name='dashboard_power_bi'),
]
