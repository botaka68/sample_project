from django.contrib import admin
from django.urls import path, include
from iocs import views as iocs_views


urlpatterns = [
    # Django admin
    path('coolcatadmin/', admin.site.urls),

    # User management
    path('accounts/', include('django.contrib.auth.urls')),

    # Local apps
    path('accounts/', include('accounts.urls')),
    path('upload/', iocs_views.upload, name='upload'),
    path('submit/', iocs_views.submit, name='submit'),
    path('summary/', iocs_views.summary, name='summary'),
    path('success/', iocs_views.success, name='success'),
    path('error/', iocs_views.error, name='error'),
 
    path('', include('pages.urls')),
]




admin.site.site_title = "ArtiCAT Admin"
admin.site.index_title = "ArtiCAT Admin"
admin.site.site_header = "ArtiCAT Admin"
