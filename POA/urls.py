from django.contrib import admin
from django.urls import path, include
from django.urls import path
from contas.views import dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name="home"),
    path('', include('contas.urls')),
    path('academico/', include('academico.urls')),
]
