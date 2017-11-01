from rest_framework import viewsets

from extensible.drf.filters import HstoreFilter, HstoreOrderFilter,\
    MultiFieldFilter
from extensible.models import ModelType
from rest_framework.settings import api_settings

class ExtensibleViewset(viewsets.ModelViewSet):
    hstore_field = 'data'
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS + [HstoreFilter,HstoreOrderFilter,MultiFieldFilter]
    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        print self.request.method
#         print args
#         print kwargs
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        if self.request.method in ['POST','PUT','PATCH']:
            kwargs['model_type'] = self.get_model_type(*args, **kwargs)
#             print kwargs['data']['type']['id']
        return serializer_class(*args, **kwargs)
    def get_model_type_fields(self,*args,**kwargs):
        try: #If a type object with "id" is sent
            type_id = kwargs['data']['type']['id']
        except:
            try: #If a type is sent as an integer
                type_id = int(kwargs['data']['type'])
            except:
                type_id = None
        if type_id: #return fields for sent type id
            return ModelType.objects.get(id=type_id).fields
        try: #Otherwise, if the object already has a type, use its fields
            if type(args[0].type) == ModelType:
                return args[0].type.fields
            return []
        except:
            return []
    def get_model_type(self,*args,**kwargs):
        type_id=None
        try: #If a type object with "id" is sent
            type_id = kwargs['data']['type']['id']
        except:
            try: #If a type is sent as an integer
                type_id = int(kwargs['data']['type'])
            except:
                type_id = None
        return type_id
