from django.shortcuts import render
from django.http import HttpResponse
from . import link_crawling

def schedule(request):
    return HttpResponse('hello')
