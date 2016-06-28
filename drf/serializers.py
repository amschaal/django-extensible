#Takes a list of fields, for dynamic nested serializers.  Used by ExtensibleSerializer. 
from rest_framework import serializers
from rest_framework.fields import DictField

from extensible.drf.fields import ModelRelatedField, DRFFieldHandler, JSONField
from extensible.models import ModelType




class ModelTypeSerializer(serializers.ModelSerializer):
    content_type__model = serializers.CharField(source='content_type.model',read_only=True)
    fields = JSONField()
    class Meta:
        model = ModelType
class FlatModelTypeSerializer(serializers.ModelSerializer):
    fields = JSONField()
    class Meta:
        model = ModelType

class DataSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields',[])
        read_only = kwargs.pop('read_only',False)
#         if self.model_type:
#             serializer_fields = self.get_model_type_fields(self.model_type)
        for key,field in fields.iteritems():
            if read_only:
                field.required = False
            self.fields[key] = field
            
        super(DataSerializer, self).__init__(*args,**kwargs)
        for key, field in self.fields.iteritems():
            if hasattr(field, 'source'):
                field.source = None

class ExtensibleSerializer(serializers.ModelSerializer):
    type = ModelRelatedField(model=ModelType,serializer=FlatModelTypeSerializer,required=False,allow_null=True)
    data = DictField(default={},required=False)
    def __init__(self, *args, **kwargs):
        self.model_type_fields = {} #Cache model type fields used by DataSerializer, keyed by instance.type_id
        self.model_type = kwargs.pop('model_type',None)
        super(ExtensibleSerializer, self).__init__(*args,**kwargs)
        if self.model_type:
            self.fields['data'] = DataSerializer(fields=self.get_model_type_fields(self.model_type))
        
    def update(self, instance, validated_data):
        self.fields['data'] = DictField() #hacky, figure out how to serialize to nested DataSerializer
        validated_data['data'] = {key:str(value) for key,value in validated_data.get('data',{}).items()} #HStore only takes strings
        return super(ExtensibleSerializer, self).update(instance,validated_data)
    def create(self, validated_data):
        self.fields['data'] = DictField() #hacky, figure out how to serialize to nested DataSerializer
        validated_data['data'] = {key:str(value) for key,value in validated_data.get('data',{}).items()} #HStore only takes strings
        return super(ExtensibleSerializer, self).create(validated_data)
    def to_representation(self, instance ):
        rep = super(ExtensibleSerializer, self).to_representation(instance)
        if hasattr(instance, 'type_id'):
            if instance.type:
                rep['data'] = DataSerializer(instance.data,fields=self.get_model_type_fields(instance.type_id),read_only=True).data
        return rep
    def get_model_type_fields(self,model_type):
        if not self.model_type_fields.has_key(str(model_type)):
            self.model_type_fields[str(model_type)] = DRFFieldHandler(ModelType.objects.get(id=model_type).fields).get_fields()
        return self.model_type_fields[str(model_type)]