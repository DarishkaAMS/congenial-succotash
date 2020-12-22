import random
from django.conf import settings
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render, redirect
from django.utils.http import is_safe_url
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .forms import TweetForm
from .models import Tweet
from .serializers import TweetSerializer

ALLOWED_HOSTS = settings.ALLOWED_HOSTS


def home_view(request, *args, **kwargs):
    return render(request, 'pages/home.html', context={}, status=200)

@api_view(['POST'])  #http method the client == POST
@permission_classes([IsAuthenticated])
def tweet_create_view(request, *args, **kwargs):
    # data = request.POST or None
    serializer = TweetSerializer(data=request.POST or None)
    if serializer.is_valid(raise_exception=True):
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)
    return Response({}, status=400)


def tweet_create_view_pure_django(request, *args, **kwargs):
    user = request.user
    if not request.user.is_authenticated:
        user = None  # for the anonymous Users
        if request.is_ajax():
            return JsonResponse({}, status=401)
        return redirect(settings.LOGIN_URL)
    form = TweetForm(request.POST or None)
    next_url = request.POST.get('next') or None
    if form.is_valid():
        obj = form.save(commit=False)
        obj.user = user
        obj.save()
        if request.is_ajax():
            return JsonResponse(obj.serialize(), status=201)  # 201 - created items
        if next_url != None and is_safe_url(next_url, ALLOWED_HOSTS):
            return redirect(next_url)
        form = TweetForm()
    if form.errors:
        if request.is_ajax():
            return JsonResponse(form.errors, status=400)
    return render(request, 'components/form.html', context={'form': form})


@api_view(['GET'])  #http method the client == POST
def tweet_list_view(request, *args, **kwargs):
    query_set = Tweet.objects.all()
    serializer = TweetSerializer(query_set, many=True)
    return Response(serializer.data, status=200)


def tweet_list_view_pure_django(request, *args, **kwargs):
    """
    REST API VIEW
    Consume by JavaScript or Swift or Java/iOS/Android
    return json dat
    """
    query_set = Tweet.objects.all()
    tweets_list = [x.serialize() for x in query_set]
    data = {
        'is_user': False,
        'response': tweets_list
    }
    return JsonResponse(data)


@api_view(['GET'])  #http method the client == POST
def tweet_detail_view(request, tweet_id, *args, **kwargs):
    query_set = Tweet.objects.filter(id=tweet_id)
    if not query_set.exists():
        return Response({}, status=404)
    obj = query_set.first()
    serializer = TweetSerializer(obj)
    return Response(serializer.data, status=200)


def tweet_detail_view_pure_django(request, tweet_id, *args, **kwargs):
    """
    REST API VIEW
    Consume by JavaScript or Swift or Java/iOS/Android
    return json dat
    """
    data = {
        'id': tweet_id,
        # 'content': obj.content,
        # 'img_path': obj.image.url
    }
    status = 200
    try:
        obj = Tweet.objects.get(id=tweet_id)
        data['content'] = obj.content
    except:
        data['message'] = 'Sorry this page is not found'
        status = 404
        # raise Http404
    return JsonResponse(data, status=status)  # json.dumps content_type='application/json'
