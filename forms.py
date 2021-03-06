from django import forms
from crispy_forms.helper import FormHelper
from models import ModelType
import json
from django.contrib.contenttypes.models import ContentType
from extensible.models import ExtensibleModel




class JSONForm(forms.Form):
    def __init__(self,*args,**kwargs):
        try:
            fields = json.loads(kwargs.pop('fields','[]'))
        except:
            fields = kwargs.pop('fields',[])
        super(JSONForm, self).__init__(*args, **kwargs)
        fh = FieldHandler(fields)
        self.fields = fh.formfields
        

class FieldHandler():
    def __init__(self, fields, initial={}):
        self.formfields = {}
        self.initial = initial
        for field in fields:
            options = self.get_options(field)
            f = getattr(self, "create_field_for_"+field['type'] )(field, options)
            self.formfields[field['name']] = f

    def get_options(self, field):
        options = {}
        options['label'] = field.get("label", field['name'])
        options['help_text'] = field.get("help_text", None)
        options['required'] = bool(field.get("required", 0) )
        if self.initial.has_key(field['name']):
            options['initial']=self.initial[field['name']]
        return options

    def create_field_for_text(self, field, options):
        options['max_length'] = int(field.get("max_length", "100") )
        return forms.CharField(**options)
    
    def create_field_for_file(self, field, options):
        return forms.FileField(**options)
    
    def create_field_for_textarea(self, field, options):
        options['max_length'] = int(field.get("max_value", "9999") )
        return forms.CharField(widget=forms.Textarea, **options)

    def create_field_for_integer(self, field, options):
        options['max_value'] = int(field.get("max_value", "999999999") )
        options['min_value'] = int(field.get("min_value", "-999999999") )
        return forms.IntegerField(**options)
    
    def create_field_for_float(self, field, options):
#         options['max_value'] = int(field.get("max_value", "999999999") )
#         options['min_value'] = int(field.get("min_value", "-999999999") )
        return forms.FloatField(**options)

    def create_field_for_radio(self, field, options):
        options['choices'] = [ (c['value'], c['name'] ) for c in field['choices'] ]
        return forms.ChoiceField(widget=forms.RadioSelect,   **options)

    def create_field_for_select(self, field, options):
        options['choices']  = [ (c['value'], c['name'] ) for c in field['choices'] ]
        return forms.ChoiceField(  **options)

    def create_field_for_checkbox(self, field, options):
        return forms.BooleanField(widget=forms.CheckboxInput, **options)





class ExtensibleModelForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        
        field_template = kwargs.pop('field_template', None)
        #Change any AJAX submitted data into same format expected by form data
        if len(args) > 0:
            if args[0].has_key('data'):
                if isinstance(args[0]['data'], dict):
                    for key,value in args[0]['data'].iteritems():
                        args[0]['data.'+key]=value    
        super(ExtensibleModelForm,self).__init__(*args, **kwargs)
        
        #Restrict type to the same content type as the model
        content_type = self.__class__._meta.model.__name__.lower()
        instance = kwargs.get('instance', None)
        if self.fields.has_key('type'):
            self.fields['type'].queryset = ModelType.objects.filter(content_type__model=content_type)

        #Find out type so we can add extra fields
        type = False
        data = {}
        type_id = self.initial.get('type',False)
        if len(args) > 0:
            type_id = args[0].get('type',False)
            if not type_id:
                type_id = self.initial.get('type',False)
            data = self.initial
        if type_id != False: #Type was submitted
            try: #try using submitted type
                type = ModelType.objects.get(id=type_id)
            except: #if fails or was blank, set to none
                type = None
        if type == False and instance: #Type was not submitted, use instance type if provided
            type = instance.type
            data = instance.data

        #Based on the type, add extra fields and set values            
        if type:
            
            if type.fields:
                fh = FieldHandler(type.fields,data)
                for key, field in fh.formfields.iteritems():
                    field_name = 'data.%s'%key
                    self.fields[field_name] = field#get_field(field,initial)
        
#         if instance:
#             if instance.type:
#                 if instance.type.fields:
#                     fh = FieldHandler(instance.type.fields,instance.data)
#                     for key, field in fh.formfields.iteritems():
#                         field_name = 'data.%s'%key
#                         self.fields[field_name] = field#get_field(field,initial)
                
        if field_template:
            self.helper = FormHelper(self)
            self.helper.field_template = field_template

    def save(self, commit=True):
        instance = super(ExtensibleModelForm, self).save(commit=False)
        if not instance.data:
            instance.data = {}
        for key in self.cleaned_data.keys():
            print key
            if key[:5] == 'data.':
                instance.data[key[5:]] = self.cleaned_data[key]
        if commit and instance:
            instance.save()
        return instance

class ModelTypeForm(forms.ModelForm):
    class Meta:
        model = ModelType
        fields = ('content_type','name','description','fields')

class CreateModelTypeForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super(CreateModelTypeForm, self).__init__(*args,**kwargs)
        cts = ContentType.objects.all()
        queryset = ContentType.objects.filter(id__in=[ct.id for ct in cts if ct.model_class() and issubclass(ct.model_class(), ExtensibleModel)])
        self.fields['content_type'].queryset=queryset
    class Meta:
        model = ModelType
        fields = ('content_type','name','description')
                
    