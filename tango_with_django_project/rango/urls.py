from django.conf.urls import patterns, url
from rango import views

# empty string (regex '^$')
urlpatterns = patterns('', 
    url(r'^$', views.index, name='first page'),
    url(r'^about/', views.about, name='about'),
    url(r'^category/(?P<category_name_url>\w+)/$', views.category, name='category'),
)
                       
