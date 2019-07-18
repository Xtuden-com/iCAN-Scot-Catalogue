from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import permission_required, login_required
from catalogueapp.forms import AddForm
from catalogueapp.tools import ALISS_URL, ALISS_Importer
from catalogueapp.models import Service, Organisation


def index(request):
    context = {
        'services': Service.objects.filter(active=True),
    }
    return render(request, 'catalogueapp/index.html', context)


def organisation_index(request, aliss_id):
    context = {
        'organisation': Organisation.objects.get(aliss_id=aliss_id),
    }
    context['services'] = Service.objects.filter(organisation=context['organisation'], active=True)

    if not context['services']:
        raise Http404
    return render(request, 'catalogueapp/organisation/index.html', context)


@permission_required('catalogueapp.catalogueadmin', login_url='/accounts/login/')
def adminindex(request):
    context = {}
    return render(request, 'catalogueapp/admin/index.html', context)


@permission_required('catalogueapp.catalogueadmin', login_url='/accounts/login/')
def admin_add(request):
    context = {}

    if request.method == 'POST':
        context['form'] = AddForm(request.POST)
        if context['form'].is_valid():
            url = ALISS_URL(context['form'].cleaned_data['url'])
            if url.is_service():
                importer = ALISS_Importer()
                service = importer.import_from_service_URL(url)
                importer.update_organisation(service.organisation)
                return redirect('admin_service_index', aliss_id=service.aliss_id)

            else:
                context['form'].add_error('url', "That does not look like a service URL?")

    else:
        context['form'] = AddForm()

    return render(request, 'catalogueapp/admin/add.html', context)


@permission_required('catalogueapp.catalogueadmin', login_url='/accounts/login/')
def admin_service_list(request):
    context = {
        'services': Service.objects.all(),
    }
    return render(request, 'catalogueapp/admin/services.html', context)


@permission_required('catalogueapp.catalogueadmin', login_url='/accounts/login/')
def admin_service_index(request, aliss_id):
    context = {
        'service': Service.objects.get(aliss_id=aliss_id),
    }

    if request.method == 'POST' and request.POST['action'] == 'update':
        importer = ALISS_Importer()
        importer.update_service(context['service'])

    return render(request, 'catalogueapp/admin/service/index.html', context)


@permission_required('catalogueapp.catalogueadmin', login_url='/accounts/login/')
def admin_organisation_list(request):
    context = {
        'organisations': Organisation.objects.all(),
    }
    return render(request, 'catalogueapp/admin/organisations.html', context)


@permission_required('catalogueapp.catalogueadmin', login_url='/accounts/login/')
def admin_organisation_index(request, aliss_id):
    context = {
        'organisation': Organisation.objects.get(aliss_id=aliss_id),
    }
    context['services'] = Service.objects.filter(organisation=context['organisation'])

    if request.method == 'POST' and request.POST['action'] == 'update':
        importer = ALISS_Importer()
        importer.update_organisation(context['organisation'])

    return render(request, 'catalogueapp/admin/organisation/index.html', context)


@login_required()
def user_profile(request):
    context = {}
    return render(request, 'registration/profile.html', context)

