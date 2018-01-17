from django.conf.urls import url
# from .views import *
from . import views

app_name = 'app'

urlpatterns = [
	url(r'^$', views.index , name='index'),
	url(r'^search_author', views.search_author, name='search_author'),
	url(r'^search_publisher', views.search_publisher, name='search_publisher'),
	url(r'^search_doi', views.search_doi, name='search_doi'),
	url(r'^search_funder', views.search_funder, name='search_funder'),
	url(r'^search_keyword', views.search_keyword, name='search_keyword'),
	url(r'^post_dryad', views.post_dryad, name='post_dryad'),
	url(r'^post_crossref', views.post_crossref, name='post_crossref'),
	url(r'^searchByPublisher', views.searchByPublisher, name='searchByPublisher'),
	url(r'^searchByAuthor', views.searchByAuthor, name='searchByAuthor'),
	url(r'^searchByDOI', views.searchByDOI, name='searchByDOI'),
 	url(r'^searchByFunder', views.searchByFunder, name='searchByFunder'),
 	url(r'^searchByTitle', views.searchByTitle, name='searchByTitle'),
	url(r'^post_zenodo', views.post_zenodo, name='post_zenodo'),
]
