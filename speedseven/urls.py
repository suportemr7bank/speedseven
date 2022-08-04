"""speedseven URL Configuration

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
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.decorators import login_required
from django_select2.views import AutoResponseView

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from clients.views import clients
from core.views.core import TinyMceUploadView, TinyMceDocView
from investment.views.operations import ReceiptsView


admin.site.site_url = '/adm/inicio/'


urlpatterns = [
    path('adm/', include('core.urls')),
    path('adm/', include('emailtemplates.urls')),
    path('adm/', include('products.urls')),
    path('adm/', include('investorprofile.urls')),
    path('adm/', include('investment.urls_adm')),
    path('adm/api/', include('accounts.urls_api')),
    path('adm/usuarios/convites/', include('accounts.urls_invitation')),

    path('admin/', admin.site.urls),
    path('contas/', include('accounts.urls_account')),
    path('cliente/', include('clients.urls')),
    path('', include('website.urls')),
    path('media/private/uploads/<path:file_name>/',
         clients.ClientDocsView.as_view(), name='document_download'),

    path('media/private/receipts/<path:file_name>/',
         ReceiptsView.as_view(), name='receipts_download'),

    path('api/', include('core.urls_api')),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/v1/', include('clients.api.urls')),

    path("select2/", include(([path("fields/auto.json", login_required(
        AutoResponseView.as_view()), name="auto-json")], 'django_select2'))),

    path(settings.TINYMCE_URL, TinyMceUploadView.as_view(),
         name='upload_tinymce_image'),

    path(settings.TINYMCE_URL+'<str:file_name>',
         TinyMceDocView.as_view(), name='tinymce_doc_image'),

]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL + 'public',
                          document_root=settings.MEDIA_ROOT / 'public')
