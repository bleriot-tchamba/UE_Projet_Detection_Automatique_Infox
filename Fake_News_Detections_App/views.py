import json
import time
from datetime import timedelta
from traceback import print_tb
import Levenshtein
import uuid

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required

import pytwitter
from pytwitter import Api

import tweepy

from gensim.summarization.summarizer import summarize
from gensim.summarization import keywords

#Invoke libraries
from nltk import pos_tag, word_tokenize
from nltk.corpus import wordnet as wn

import re
import nltk.corpus
#nltk.download('stopwords')
from nltk.corpus import stopwords
import nltk
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer

from users.forms import UserForm, UserLoginForm
from users.models import License, MyUser

User = get_user_model()
w_tokenizer = nltk.tokenize.WhitespaceTokenizer()
lemmatizer = nltk.stem.WordNetLemmatizer()

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
    end_date = timezone.now() - request.user.date_joined
    context = {
		'liste': liste,
        'firstime': True
	}
    print(request.user._wrapped.__dict__)
    
    if request.user.myuser.is_free_trial:
        if end_date.days > 30:
            return render(request, 'licence.html')
        context['start_date'] = int(time.mktime(request.user.date_joined.timetuple())) * 1000
        context['free_trial'] = "free"
            
    else:
        is_expired = request.user.myuser.is_expired
        context['is_expired'] = is_expired
    
    return render(request, 'index.html', context)

#Eleminons les emojis
def remove_emoji(text):
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
                      "]+", re.UNICODE)
    return emoji_pattern.sub(r'', text)

#Nettoyage des donnees
def clean_text(text):
    
    text = re.sub('https\S+',"",text) #Suprression des liens
    #text = re.sub('#\S+',"",text) #Suppression des hastags
    pattern = r'[@&!\?\.#(-:/\\0123456789\+\n\t;\|_$.%''"‘’↓→' '\(\)°]'
    text = re.sub(pattern, " ", text) #Suppression des caracteres
    text = text.lower() #Mettre en minuscule
    stop = stopwords.words('english') #Suppression des mots d'arrets de la langue anglaise
    text = " ".join([word for word in text.split() if word not in (stop)])  #Supression des mots d'arrets
    text = " ".join([lemmatizer.lemmatize(w) for w in w_tokenizer.tokenize(text)]) #Lemmatization
    tokens = nltk.word_tokenize(text) # tokenization
    text = " ".join(tokens)
    return text


#Supression des mots de longueur inferieur a deux
def delete_w(texts):
    L = []
    F = []
    L = texts.split() 
    t=""
    for words in L:
        if len(words)>2:
            F.append(words)
        t=' '.join(F)
    return t


#Build functions to compute similarity
def ptb_to_wn(tag):    
    if tag.startswith('N'):
        return 'n' 
    if tag.startswith('V'):
        return 'v' 
    if tag.startswith('J'):
        return 'a' 
    if tag.startswith('R'):
        return 'r' 
    return None


def tagged_to_synset(word, tag):
    wn_tag = ptb_to_wn(tag)
    if wn_tag is None:
        return None 
    try:
        return wn.synsets(word, wn_tag)[0]
    except:
        return None


def sentence_similarity(s1, s2):    
    s1 = pos_tag(word_tokenize(s1))
    s2 = pos_tag(word_tokenize(s2)) 

    synsets1 = [tagged_to_synset(*tagged_word) for tagged_word in s1]
    synsets2 = [tagged_to_synset(*tagged_word) for tagged_word in s2]


    #suppress "none"
    synsets1 = [ss for ss in synsets1 if ss]
    synsets2 = [ss for ss in synsets2 if ss]

    score, count = 0.0, 0

    for synset in synsets1:
        best_score = max([synset.path_similarity(ss) for ss in synsets2])
        if best_score is not None:
            score += best_score
            count += 1

    # Average the values
    if count != 0:
        score /= count
    return score

#compute the symmetric sentence similarity
def symSentSim(s1, s2):
    sss_score = (sentence_similarity(s1, s2) + sentence_similarity(s2,s1)) / 2
    return (sss_score)

def extract_subject(request):
    from sklearn.feature_extraction.text import TfidfVectorizer
    import pickle
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('wordnet')
    nltk.download('omw-1.4')
    tft = None
    kmean = None
    cluster_map = {0: "Tech", 1: "Nutrition", 2: "World", 3: "Health", 4: "Cancer", 5: "Bussinness", 6: "Basketball", 7: "Education", 8: "Football", 9: "Africa",10:"News"}
    
    from os import listdir
    from os.path import isfile, join
    import pandas as pd
    onlyfiles = [f for f in listdir('./') if isfile(join('./', f))]

    with open('models_ds/tfid.vectorizer', 'rb') as f:
        tft = pickle.load(f)
    
    with open('models_ds/kmeans.model', 'rb') as f:
        kmean = pickle.load(f)
        
    try:
        from .account import account as legitimate_account
        
        link_tweet = request.POST.get('link_tweet').split('/')
        if 'twitter.com' not in link_tweet or not link_tweet[-1].isnumeric():
            return JsonResponse(status=400, data={'msg': 'Entrez un lien Twitter Valide'})
        
        link_tweet = link_tweet[-1]
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
        
        print(tweet.full_text)
        
        # Pretraitement
        text = remove_emoji(tweet.full_text)
        text = clean_text(text)
        text = delete_w(text)
        
        # Vectorisation
        text = tft.transform([text])

        text = pd.DataFrame(text.toarray(), columns = tft.get_feature_names_out())
        
        print(text, '.....!!!!!')
        
        pred = kmean.predict(text)
        
        print(pred)

        
        
        key_words = keywords(tweet.full_text, words=5, lemmatize=True).replace('\n', ' ')
        
        seach2 = api_tweepy.search_tweets(cluster_map[pred[0]], count=10, tweet_mode='extended')
        
        tweets = api_tweepy.search_tweets(key_words, count=300, tweet_mode='extended')
        distances = []
        t = []
        for search_tweet in [tweet] + tweets + seach2:
            #print(search_tweet.full_text, ".......",tweet.full_text, "\n\n")
            if search_tweet.user.screen_name in legitimate_account or search_tweet.user.verified:
                print(f"Un compte légitime: {search_tweet.user.screen_name}, msg: {search_tweet.full_text}")
                a = symSentSim(tweet.full_text, search_tweet.full_text)
                t.append(search_tweet)    
                distances.append(a) 
            #distances.append(Levenshtein.ratio(tweet.full_text, search_tweet.full_text))
        # print("keywords:",key_words, '....\n\n')
        # print(tweets, '....\n\n\n')
        # print(f'mayenne = {sum(distances)/len(distances)}', f'max={max(distances)}', f'min={min(distances)}')
        # print(identique)
        
        
        # print(f"Valeur prédite: {cluster_map[pred[0]]}")
        # print(f'Nombre de resultat de recherche : {len(tweets)}')
        # print(f'Nombre de resultat provenant de compte certifié : {count_legitime}')
        
        
        pbc = dict()
        if len(distances) > 0:
            pbc['moyenne'] = 100*sum(distances)/len(distances)
        else:
            pbc['moyenne'] = 0
        
        if len(distances) > 0:
            pbc['max'] = max(distances)
            pbc['min'] = min(distances)
        else:
            pbc['max'] = 0
            pbc['min'] = 0
        tweets_validated = []
        for search_tweet in t:
            tweets_validated.append(json.dumps(search_tweet._json))

        
        return JsonResponse(status=200, data={'msg': tweet.full_text, 'user': json.dumps(tweet.user._json), 'keyword': key_words, 'probabilites': json.dumps(pbc), 'sujet':cluster_map[pred[0]], 'tweets':json.dumps(tweets_validated)})
    except pytwitter.error.PyTwitterError as e:
        print("Execption ....:", e)
        return JsonResponse(status=403, data={'msg': 'Problème de connexion vérifiez votre connexion internet et recommencer'})
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
    return render(request, 'register.html', {'form' : user_form})

@login_required(login_url='/signin/')
def abonnement(request):
    return render(request, 'licence.html')

@login_required(login_url='/signin/')
def valid_abonnement(request):
    licence = License(
        type = 'NUMBER',
        token = uuid.uuid1()
    )
    licence.save()
    u = MyUser.objects.get(user=request.user)
    u.license = licence
    u.save()
    return redirect('index')

def paiement(request):
    context = dict()
    context['amount'] = int(request.GET.get('amount', 100))
    context['paiement_id'] = uuid.uuid1()
    return render(request, 'paiment.html', context)