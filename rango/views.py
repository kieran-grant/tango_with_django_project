from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category

def index(request):
    # Query the database for a list of all categories currently stored.
    # Order the categories by the number of likes in decending order.
    # Retrieve the top 5 -- or all if less than 5.
    # Place the list in context_dict
    category_list = Category.objects.order_by('-likes')[:5]

    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    # Return a rendered reponse to send to the client
    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    #return HttpResponse("Rango says here is the about page. <a href='/rango/'>Index</a>")

    # Construct a dictionary to pass to the template engine as its context
    # context_dict = {'boldmessage': 'This tutorial has been put together by Kieran Grant.'}

    # Return a rendered reponse to send to the client
    return render(request, 'rango/about.html')