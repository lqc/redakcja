from django.conf.urls.defaults import *

urlpatterns = patterns('wiki.views',
    url(r'^$', 
        'document_list', name='wiki_doclist'),
    url(r'^gallery/(?P<directory>[^/]+)$', 
        'document_gallery', name="wiki_gallery"),
    url(r'^(?P<name>[^/]+)/history$', 
        'document_history', name="wiki_history"),
    url(r'^(?P<name>[^/]+)/text$', 
        'document_text', name="wiki_text"),
    url(r'^(?P<name>[^/]+)/publish/(?P<version>\d+)$', 
        'document_publish', name="wiki_publish"),
    url(r'^(?P<name>[^/]+)/diff/(?P<revA>\d+)/(?P<revB>\d+)$', 
        'document_diff', name="wiki_diff"),    
    url(r'^(?P<name>[^/]+)$', 
        'document_detail', name="wiki_details"),        
    
)   
