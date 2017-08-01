from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import logout
from django.views.generic import TemplateView

from . import views

admin.autodiscover()


urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^card/$', views.CardView.as_view(), name='card'),
    url(r'^card/(?P<pk>[^/]+)/$', views.CardDetailView.as_view(), name='card-detail'),
    url(r'^api/', include('idm_card.api_urls', 'api')),
    url(r'^admin/', admin.site.urls),
    url(r'^oidc/', include('oidc_auth.urls')),
    url(r'^logout/$', logout, name='logout'),
]

handler_403 = TemplateView(template_name='403.html')
handler_404 = TemplateView(template_name='404.html')