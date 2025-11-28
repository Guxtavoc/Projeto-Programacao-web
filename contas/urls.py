from django.urls import path
from . import views   # importa o módulo views certo

urlpatterns = [
    path('login/', views.login_view, name='contas_login'),
    path('logout/', views.logout_view, name='contas_logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path("criar_usuario/", views.criar_usuario, name="criar_usuario"),
]
