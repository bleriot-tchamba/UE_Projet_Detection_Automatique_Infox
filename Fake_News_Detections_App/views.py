from audioop import avg
import json

import Levenshtein

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

import pytwitter
from pytwitter import Api

import tweepy

from gensim.summarization.summarizer import summarize
from gensim.summarization import keywords


# Create your views here.
b_token = "AAAAAAAAAAAAAAAAAAAAAEe0bgEAAAAAFljvcKIPBris5Mn2toYpNUaF%2BQE%3DDnaNicqUFJSq3J9wcDofcw8Ea7Wjb1ditpUCv8rcdZBbJskOHE"

# API keyws that yous saved earlier
api_key = "giK5hP8ly7aWhBSltyPdT9bKG"
api_secrets = "WomINuAmPz62sTlUJbUWYeLeU7YYWIuBEFfoZW7TymChNrA2Wk"
access_token = "1511063864884006918-Kym3fIV1YLx03WzKWufZj8Z13J7ukp"
access_secret = "cuZPDdGJMVZTqkr6qNv83HFRsCLF4NhTTbM6CaYWC4PMz"


def index(request):
    
    liste = [1,2,3,4,5,6]

    context = {
		'liste': liste	 
	};
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

        tweet = api_tweepy.get_status(link_tweet)
        
        key_words = keywords(tweet.text, words=5, lemmatize=True).replace('\n', ' ')
        
        tweets = api_tweepy.search_tweets(key_words, count=300)
        distances = []
        identique = []
        
        for search_tweet in tweets:
            print(search_tweet.text, ".......",tweet.text, "\n\n")
            identique.append(search_tweet.text==tweet.text)
            distances.append(Levenshtein.ratio(tweet.text, search_tweet.text))
        
        print(tweet.text, '....\n\n')
        print("keywords:",key_words, '....\n\n')
        print(tweets, '....\n\n\n')
        print(f'mayenne = {sum(distances)/len(distances)}', f'max={max(distances)}', f'min={min(distances)}')
        print(identique)
        
        pbc = dict()
        pbc['moyenne'] = sum(distances)/len(distances)
        pbc['max'] = max(distances)
        pbc['min'] = min(distances)
        
        
        

        
        return JsonResponse(status=200, data={'msg': tweet.text, 'user': json.dumps(tweet.user._json), 'keyword': key_words, 'probabilites': json.dumps(pbc)})
    except pytwitter.error.PyTwitterError as e:
        print("Execption ....:", e)
        return JsonResponse(status=500, data={'msg': 'Bad request'})
    except Exception as e:
        print("Execption:", e)
        return JsonResponse(status=500, data={'msg': 'Bad request'})


def login(request):
    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')
