from django.shortcuts import render

# Create your views here.

def index(request):
    
    liste = [1,2,3,4,5,6]

    context = {
		'liste': liste	 
	};
    return render(request, 'index.html', context)
    


def login(request):
    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')
