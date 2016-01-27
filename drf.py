from rest_framework.fields import CharField, IntegerField, FloatField,\
    ChoiceField, NullBooleanField, DictField
class DRFFieldHandler():
    def __init__(self, fields, initial={}):
        self.serializer_fields = {}
        self.initial=initial
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
        options['max_length'] = int(field.get("max_length", "500") )
        return CharField(**options)
    
#     def create_field_for_file(self, field, options):
#         return forms.FileField(**options)
    
    def create_field_for_textarea(self, field, options):
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
        options['choices']  = [ (c['value'], c['name'] ) for c in field['choices'] ]
        return ChoiceField(  **options)

    def create_field_for_checkbox(self, field, options):
        return NullBooleanField(**options)