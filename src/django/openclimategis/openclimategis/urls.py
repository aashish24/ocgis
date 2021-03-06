from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^subset$','cdata.views.get_data'),
    url(r'^inspect$','cdata.views.display_inspect'),
    url(r'^shp/(?P<key>.*)$','cdata.views.get_shp'),
    # Examples:
    # url(r'^$', 'ocgis.views.home', name='home'),
    # url(r'^ocgis/', include('ocgis.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
