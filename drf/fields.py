from rest_framework.fields import CharField, IntegerField, FloatField,\
    ChoiceField, NullBooleanField, DictField
from rest_framework import serializers
class DRFFieldHandler():
    def __init__(self, fields, initial={}):
        self.serializer_fields = {}
        self.initial=initial
        if fields:
            for field in fields:
                options = self.get_options(field)
                f = getattr(self, "create_field_for_"+field['type'] )(field, options)
                self.serializer_fields[field['name']] = f
    def get_fields(self):
        return self.serializer_fields
    
#     def get_dict_field(self):
#         return DictField(**self.serializer_fields)

    def get_options(self, field):
        options = {}
        options['label'] = field.get("label", field['name'])
        options['help_text'] = field.get("help_text", None)
        options['required'] = bool(field.get("required", 0) )
        if self.initial.has_key(field['name']):
            options['initial']=self.initial[field['name']]
        return options

    def create_field_for_text(self, field, options):
        options['allow_blank'] = bool(field.get("allow_blank", 1) )
        options['max_length'] = int(field.get("max_length", "500") )
        return CharField(**options)
    
#     def create_field_for_file(self, field, options):
#         return forms.FileField(**options)
    
    def create_field_for_textarea(self, field, options):
        options['allow_blank'] = bool(field.get("allow_blank", 1) )
        options['max_length'] = int(field.get("max_length", "9999") )
        return CharField(**options)

    def create_field_for_integer(self, field, options):
        options['max_value'] = int(field.get("max_value", "999999999") )
        options['min_value'] = int(field.get("min_value", "-999999999") )
        return IntegerField(**options)
    
    def create_field_for_float(self, field, options):
        options['max_value'] = int(field.get("max_value", "999999999") )
        options['min_value'] = int(field.get("min_value", "-999999999") )
        return FloatField(**options)

    def create_field_for_radio(self, field, options):
        options['choices'] = [ (c['value'], c['name'] ) for c in field['choices'] ]
        return ChoiceField(**options)

    def create_field_for_select(self, field, options):
        options['choices']  = [ (c.get('value',c.get('name')), c.get('name',c.get('value')) ) for c in field['choices'] ]
        return ChoiceField(  **options)

    def create_field_for_checkbox(self, field, options):
        return NullBooleanField(**options)
    
#Allows Creation/Updating of related model fields with OBJECT instead of just id
class ModelRelatedField(serializers.RelatedField):
    model = None
    pk = 'id'
    serializer = None
    def __init__(self, **kwargs):
        self.model = kwargs.pop('model', self.model)
        self.pk = kwargs.pop('pk', self.pk)
        self.serializer = kwargs.pop('serializer', self.serializer)
        assert self.model is not None, (
            'Must set model for ModelRelatedField'
        )
        assert self.serializer is not None, (
            'Must set serializer for ModelRelatedField'
        )
        self.queryset = kwargs.pop('queryset', self.model.objects.all())
        super(ModelRelatedField, self).__init__(**kwargs)
    def to_internal_value(self, data):
        if isinstance(data, int):
            kwargs = {self.pk:data}
            return self.model.objects.get(**kwargs)
        if data.get(self.pk,None):
            return self.model.objects.get(id=data['id'])
        return None
    def to_representation(self, value):
        return self.serializer(value).data
    
class JSONField(serializers.Field):
    def to_internal_value(self,value):
        import json
        if not isinstance(value, str) or value is None:
            return value
        value = json.loads(value)#JSONField(value)
        return value
    def to_representation(self, value):
        return value
        import json
        return json.dumps(value)