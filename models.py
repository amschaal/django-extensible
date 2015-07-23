from django.db import models
from uuid import uuid4
from django.db.models import Q
from jsonfield import JSONField

def generate_pk():
    return str(uuid4())[:15]

class ModelType(models.Model):
    content_type = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    description = models.TextField()
#     plugins = models.ManyToManyField(Plugin,null=True,blank=True, through='ModelTypePlugins')
    fields = JSONField(null=True,blank=True)
    def __unicode__(self):
        return "%s: %s" % (self.content_type, self.name)



class ExtensibleModel(models.Model):
    type = models.ForeignKey(ModelType, null=True, blank=True)
    #@deprecated: will use json, eventually will use native jsonb field with Django 1.9
    data = JSONField(null=True,blank=True,default={})
    class Meta:
        abstract = True

