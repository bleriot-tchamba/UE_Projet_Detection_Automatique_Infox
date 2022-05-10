import json

import Levenshtein

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required

import pytwitter
from pytwitter import Api

import tweepy

from gensim.summarization.summarizer import summarize
from gensim.summarization import keywords

from users.forms import UserForm, UserLoginForm

User = get_user_model()

# Create your views here.
b_token = "AAAAAAAAAAAAAAAAAAAAAEe0bgEAAAAAFljvcKIPBris5Mn2toYpNUaF%2BQE%3DDnaNicqUFJSq3J9wcDofcw8Ea7Wjb1ditpUCv8rcdZBbJskOHE"

# API keyws that yous saved earlier
api_key = "giK5hP8ly7aWhBSltyPdT9bKG"
api_secrets = "WomINuAmPz62sTlUJbUWYeLeU7YYWIuBEFfoZW7TymChNrA2Wk"
access_token = "1511063864884006918-Kym3fIV1YLx03WzKWufZj8Z13J7ukp"
access_secret = "cuZPDdGJMVZTqkr6qNv83HFRsCLF4NhTTbM6CaYWC4PMz"


@login_required(login_url='/signin/')
def index(request, **kwargs):
    
    liste = [1,2,3,4,5,6]

    context = {
		'liste': liste,    
	}
    return render(request, 'index.html', context)

# @require_POST
def extract_subject(request):
    try:
        link_tweet = request.POST.get('link_tweet').split('/')[-1]
        # api = Api(
        #     consumer_key=api_key,
        #     consumer_secret=api_secrets,
        #     access_token=access_token,
        #     access_secret=access_secret
        # )
        
        auth = tweepy.OAuthHandler(api_key, api_secrets)
        auth.set_access_token(access_token, access_secret)
        api_tweepy = tweepy.API(auth)
        
        # response = api.get_tweet(tweet_id=link_tweet,expansions="author_id",tweet_fields=["created_at"], user_fields=["id", "username","verified", 'name'])

        tweet = api_tweepy.get_status(link_tweet, tweet_mode="extended")
        
        key_words = keywords(tweet.full_text, words=5, lemmatize=True).replace('\n', ' ')
        
        tweets = api_tweepy.search_tweets(key_words, count=300, tweet_mode='extended')
        distances = []
        identique = []
        
        for search_tweet in tweets:
            print(search_tweet.full_text, ".......",tweet.full_text, "\n\n")
            identique.append(search_tweet.full_text==tweet.full_text)
            distances.append(Levenshtein.ratio(tweet.full_text, search_tweet.full_text))
        
        print(tweet.text, '....\n\n')
        print("keywords:",key_words, '....\n\n')
        print(tweets, '....\n\n\n')
        print(f'mayenne = {sum(distances)/len(distances)}', f'max={max(distances)}', f'min={min(distances)}')
        print(identique)
        
        pbc = dict()
        pbc['moyenne'] = sum(distances)/len(distances)
        pbc['max'] = max(distances)
        pbc['min'] = min(distances)

        
        return JsonResponse(status=200, data={'msg': tweet.full_text, 'user': json.dumps(tweet.user._json), 'keyword': key_words, 'probabilites': json.dumps(pbc)})
    except pytwitter.error.PyTwitterError as e:
        print("Execption ....:", e)
        return JsonResponse(status=500, data={'msg': 'Bad request'})
    except Exception as e:
        print("Execption:", e)
        return JsonResponse(status=500, data={'msg': 'Bad request'})


@login_required(login_url='/signin/')
def deconnecter(request):
    logout(request)
    return redirect('login')


def signin(request):
    if request.method == 'POST':
        user_form = UserLoginForm(request.POST)
        print("before")
        if user_form.is_valid():
            user = user_form.cleaned_data['username']
            login(request, user)
            return redirect('index')
        print('after')
    else:
        user_form = UserLoginForm()
    return render(request, 'login.html', {'form': user_form})


def register(request):
    val = True
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        print(request.POST)
        if user_form.is_valid():
            val = True
            user = user_form.save()
            login(request, user)
            return render(request, 'index.html', {'val':"first"})
    else:
        user_form = UserForm()
    print("Okj")
    return render(request, 'register.html', {'form' : user_form})

@login_required(login_url='/signin/')
def abonnement(request):
    return render(request, 'licence.html')