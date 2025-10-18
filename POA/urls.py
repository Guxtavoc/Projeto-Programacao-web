
from django.contrib import admin
from django.urls import path
from POA import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.visualizarHome, name = "Home"),
]
