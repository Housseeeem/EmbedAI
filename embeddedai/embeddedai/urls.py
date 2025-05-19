"""
URL configuration for embeddedai project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path
from codeanalyzer import views
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path
from codeanalyzer import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
from django.urls import path, include
from codeanalyzer import views
from accounts import views as accounts_views  # 🆕
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', accounts_views.login_view, name='home'),  # 🆕 Homepage is login page now
    path('upload/', views.upload_code, name='upload_code'),  # Upload after login
    path('history/', views.analysis_history, name='history'),
    path('export_pdf/<int:analysis_id>/', views.export_pdf, name='export_pdf'),
    path('ide/', views.ide_view, name='ide'),
    path('analyze_code_online/', views.analyze_code_online, name='analyze_code_online'),
    path('accounts/', include('accounts.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)