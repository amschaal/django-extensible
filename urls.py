from django.conf.urls import url
import views


urlpatterns = [
#     url(r'^designer/$', 'django_json_forms.views.designer', name='designer'),
#     url(r'^test/$', 'django_json_forms.views.test', name='test_json_form'),
#     url(r'^$', 'django_json_forms.views.forms', name='forms'),
#     url(r'^forms/(?P<pk>\d+)/$', 'django_json_forms.views.form', name='form'),
    url(r'^model_type/(?P<pk>\d+)/update/$', views.update_model_type, name='update_model_type'),
    url(r'^model_type/create/$',views.create_modeltype,name="create_modeltype"),
#     url(r'^forms/(?P<pk>\d+)/designer/$', 'django_json_forms.views.form_designer', name='form_designer'),
#     url(r'^forms/(?P<pk>\d+)/responses/$', 'django_json_forms.views.responses', name='responses'),
#     url(r'^responses/(?P<pk>\d+)/view/$', 'django_json_forms.views.response', name='response'),
#     url(r'^responses/(?P<pk>\d+)/download/$', 'django_json_forms.views.download_response_file', name='download_response_file'),
    
]

