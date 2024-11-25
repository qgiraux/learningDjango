from django.shortcuts import render
from datetime import datetime

# Create your views here.
from django.shortcuts import render
def home(request):
    context = {
        'greeting': 'Hello, world!',
        'time': datetime.now().strftime('%H:%M:%S')
    }
    return render(request, 'home.html', context)