from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.template.context import RequestContext
from django.http import HttpResponse, HttpResponseForbidden
from forms import JSONForm, ModelTypeForm
# from models import JSONFormModel, Response as JSONFormResponse
from models import ModelType
import json
from django.contrib.auth.decorators import user_passes_test
from django.views.generic.edit import CreateView
from extensible.forms import CreateModelTypeForm
# from decorators import download_permission, form_permission

def test(request):
    json_form = None
    fields = request.POST.get('fields',None)
    submitted = request.POST.get('submitted',None)
    message = None
    if fields:
        if submitted:
            json_form = JSONForm(request.POST,request.FILES,fields=fields)
            if json_form.is_valid():
                message = 'Form is valid'
            else:
                message = 'Validation Error'
        else:
            json_form = JSONForm(fields=fields)
    
    return render(request, 'json_form/test.html', {'json_form':json_form,'fields':fields,'message':message})

def update_model_type(request,pk):
    json_form = ModelType.objects.get(pk=pk)
    data = json.loads(request.body)
    form = ModelTypeForm(data,instance=json_form)
    if form.is_valid():
        instance = json_form.save()
#         print instance.fields
        return HttpResponse(json.dumps({'status':'success'}), content_type='application/json')
    else:
        return HttpResponse(json.dumps({'status':'failed','errors':form.errors}), content_type='application/json')

def create_modeltype(request):
    initial = {'content_type':request.GET.get('content_type',None)}
    if request.method == 'GET':
        form = CreateModelTypeForm(initial=initial)
    elif request.method == 'POST':
        form = CreateModelTypeForm(request.POST,initial=initial)
        if form.is_valid():
            model_type = form.save()
            return redirect(model_type.get_absolute_url()) 
    return render(request, 'extensible/create.html', {'form':form} )

# class ModelTypeCreate(CreateView):
#     form_class = CreateModelTypeForm
#     model = ModelType
#     template_name = 'extensible/create.html'

