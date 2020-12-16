from django.http import HttpResponse
from django.shortcuts import render


def home_view(request, *args, **kwargs):
    return HttpResponse('<h1>Hello</h1>')


def tweet_detail_view(request, tweet_id, *args, **kwargs):
    return HttpResponse(f'<h1>Hello</h1> {tweet_id}')


