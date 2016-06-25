from django.db import models
from uuid import uuid4
from django.db.models import Q
from jsonfield import JSONField
import copy
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import HStoreField

def generate_pk():
    return str(uuid4())[:15]
# ContentType
class ModelType(models.Model):
#     content_type = models.CharField(max_length=100)
    content_type = models.ForeignKey(ContentType)
    name = models.CharField(max_length=100)
    description = models.TextField()
#     plugins = models.ManyToManyField(Plugin,null=True,blank=True, through='ModelTypePlugins')
    fields = JSONField(null=True,blank=True)
    def __unicode__(self):
        return "%s: %s" % (self.content_type, self.name)
    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('model_type', kwargs={'pk':self.id})



class ExtensibleModel(models.Model):
    type = models.ForeignKey(ModelType, null=True, blank=True, on_delete=models.PROTECT)
    #@deprecated: will use json, eventually will use native jsonb field with Django 1.9
    data = HStoreField(null=True,blank=True,default=dict)#JSONField(null=True,blank=True,default=dict)
    def fields(self):
        return self._meta.get_all_field_names()
    def data_fields(self):
        if not self.type:
            return []
        if not self.type.fields:
            return []
        fields = copy.deepcopy(self.type.fields)
        for field in fields:
            value = self.data.get(field['name'],None)
            field.update({'value':value})
        return fields
    class Meta:
        abstract = True

