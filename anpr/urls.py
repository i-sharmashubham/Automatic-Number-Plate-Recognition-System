"""anpr URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('logout', views.logout, name='logout'),
    path('register', views.register, name='register'),
    path('viewchallan', views.viewchallan, name='viewchallan'),
    path('challandetails', views.challandetails, name='challandetails'),
    path('makepayment', views.makepayment, name='makepayment'),
    path('error', views.error, name='error'),
    path('paymemtstatus', views.paymemtstatus, name='paymemtstatus'),
    path('paymenthistory', views.paymenthistory, name='paymenthistory'),
    path('paymentdetails', views.paymentdetails, name='paymentdetails'),
    path('createchallan', views.createchallan, name='createchallan'),
    path('verification/', include('verify_email.urls')),
    path('subscribe', views.subscribe, name='subscribe'),
    path('unsubscribe', views.unsubscribe, name='unsubscribe'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
