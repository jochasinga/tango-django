from django.conf.urls import patterns, url
from rango import views

# empty string (regex '^$')
urlpatterns = patterns('', 
    # Map path '/' to index view, with optional name first page.
    # http://localhost:PORT/rango/ => index.html
    url(r'^$', views.index, name='first page'),

    # http://localhost:PORT/rango/index => index.html
    url(r'^index', views.index, name='first page'),
    
    # http://localhost:PORT/rango/myass => index.html
    url(r'^myass', views.index, name='first page'),

    # Map path '/about/' to about view, which will dispatch about template
    url(r'^about/', views.about, name='about'),

    # Map path '/add_category/' to add_category view
    url(r'^add_category/$', views.add_category, name='add_category'),

    # map path '/category/any_category_name_here/' to category view 
    url(r'^category/(?P<category_name_url>\w+)/$', views.category, name='category'),

    url(r'^category/(?P<category_name_url>\w+)/add_page/$', views.add_page, name='add page'),

)


                       
