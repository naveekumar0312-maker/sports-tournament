from django.shortcuts import render
from django.http import JsonResponse
from .models import District, Taluk, Village

def district_list_view(request):
    districts = District.objects.all().prefetch_related('taluks', 'tournaments', 'teams')
    return render(request, 'locations/district_list.html', {
        'districts': districts
    })

def taluks_api_view(request):
    district_id = request.GET.get('district_id')
    if district_id:
        taluks = Taluk.objects.filter(district_id=district_id).values('id', 'name')
        return JsonResponse(list(taluks), safe=False)
    return JsonResponse([], safe=False)

def villages_api_view(request):
    taluk_id = request.GET.get('taluk_id')
    if taluk_id:
        villages = Village.objects.filter(taluk_id=taluk_id).values('id', 'name')
        return JsonResponse(list(villages), safe=False)
    return JsonResponse([], safe=False)

