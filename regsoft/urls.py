"""regsoft URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from . import views
urlpatterns = [
    url(r'^$', views.index),
    url(r'^signin/', views.signin),
    url(r'^postsign/', views.postsign),
    url(r'^admin/', admin.site.urls),
    url(r'^logout/', views.logout, name='log'), # onclick redirects to url with name = 'log'
    url(r'^signup/', views.signup, name='signup'),
    url(r'^postsignup/', views.postsignup, name='postsignup'),
    url(r'^create/', views.create, name='create'),
    url(r'^check/', views.check, name='check'),    
    url(r'^postrating/', views.postrating, name='postrating')

]
