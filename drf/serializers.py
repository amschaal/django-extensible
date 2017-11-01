#Takes a list of fields, for dynamic nested serializers.  Used by ExtensibleSerializer. 
from rest_framework import serializers
from rest_framework.fields import DictField

from extensible.drf.fields import ModelRelatedField, DRFFieldHandler, JSONField
from extensible.models import ModelType
from rest_framework.utils import model_meta




class ModelTypeSerializer(serializers.ModelSerializer):
    content_type__model = serializers.CharField(source='content_type.model',read_only=True)
    fields = JSONField()
    class Meta:
        model = ModelType
        fields = '__all__'
class FlatModelTypeSerializer(serializers.ModelSerializer):
    fields = JSONField()
    class Meta:
        model = ModelType
        fields = '__all__'

class DataSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields',{})
        read_only = kwargs.get('read_only',False)
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
    data = DataSerializer() #placeholder, overwritten in __init__
    def __init__(self, *args, **kwargs):
        self.model_type_fields = {} #Cache model type fields used by DataSerializer, keyed by instance.type_id
        self.model_type = kwargs.pop('model_type',None)
        super(ExtensibleSerializer, self).__init__(*args,**kwargs)
        if self.model_type:
            self.fields['data'] = DataSerializer(fields=self.get_model_type_fields(self.model_type))
        
    def update(self, instance, validated_data):
        #This is the same implementation as in ModelSerializer, but minus the assertion about nested writes!
        info = model_meta.get_field_info(instance)
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                field = getattr(instance, attr)
                field.set(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance
#         self.fields['data'] = DictField() #hacky, figure out how to serialize to nested DataSerializer
#         validated_data['data'] = {key:str(value) for key,value in validated_data.get('data',{}).items()} #HStore only takes strings
#         return super(ExtensibleSerializer, self).update(instance,validated_data)
    def create(self, validated_data):
        #This is the same implementation as in ModelSerializer, but minus the assertion about nested writes!
        ModelClass = self.Meta.model
        info = model_meta.get_field_info(ModelClass)
        many_to_many = {}
        for field_name, relation_info in info.relations.items():
            if relation_info.to_many and (field_name in validated_data):
                many_to_many[field_name] = validated_data.pop(field_name)
        instance = ModelClass.objects.create(**validated_data)
        # Save many-to-many relationships after the instance is created.
        if many_to_many:
            for field_name, value in many_to_many.items():
                field = getattr(instance, field_name)
                field.set(value)
        return instance
#         self.fields['data'] = DictField() #hacky, figure out how to serialize to nested DataSerializer
#         validated_data['data'] = {key:str(value) for key,value in validated_data.get('data',{}).items()} #HStore only takes strings
#         return super(ExtensibleSerializer, self).create(validated_data)
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