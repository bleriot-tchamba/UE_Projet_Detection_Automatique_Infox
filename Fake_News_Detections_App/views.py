from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
import pytwitter
from pytwitter import Api


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
        api = Api(
            consumer_key=api_key,
            consumer_secret=api_secrets,
            access_token=access_token,
            access_secret=access_secret
        )
        response = api.get_tweet(tweet_id=link_tweet,expansions="author_id",tweet_fields=["created_at"], user_fields=["id", "username","verified", 'name'])

        tweet_msg = response.data.text
        print(tweet_msg, response.includes.users[0].name)
        return JsonResponse(status=200, data={'msg': tweet_msg, 'username': response.includes.users[0].username, 'name': response.includes.users[0].name, 'subject':None})
    except pytwitter.error.PyTwitterError:
        return JsonResponse(status=500, data={'msg': 'Bad request'})
    except Exception as e:
        return JsonResponse(status=500, data={'msg': 'Bad request'})


def login(request):
    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')
