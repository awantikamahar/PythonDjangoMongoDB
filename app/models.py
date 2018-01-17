from django.db import models

# Create your models here.
from mongoengine import *
# from djangotoolbox.fields import ListField

class Post(Document):
	title = StringField()
	creator = ListField()
	description = StringField()
	date = ListField()
	types = StringField()
	identifier = ListField()
	relation = ListField()
	publisher = StringField()
	reference = StringField()
	subjects = ListField()

class Cross(Document):
	reference_count = StringField()
	publisher = StringField()
	funder = ListField()
	doi = StringField()
	title = StringField()
	reference = ListField()
	author = ListField()
	issn = ListField()
	date_time = StringField()


class Zen(Document):
	title = StringField()
	creator = StringField()
	conceptdoi = StringField()
	doi = StringField()
	related_identifiers = ListField()
	date = StringField()
	links = ListField()

class Dry(Document):
	title = StringField()
	creator = ListField()
	description = StringField()
	date = ListField()
	doi = StringField()
	types = StringField()
	identifier = ListField()
	relation = ListField()
	publisher = StringField()
	reference = StringField()
	subjects = ListField()