# Each view is one function.
# Each view takes in at least one argument - a HttpRequest object.
# Each view must return a HttpResponse object. A simple HttpResponse
# object takes a string parameter representing the content of the page
# we wish to send to the client requesting the view.

# Create your views here.
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

# This is a view called "index"
def index(req):
    #return HttpResponse("Rango says hello!<br/><a href='/rango/about/'>About</a>")
    
    # Request the context of the request
    # The context contains information such as the client's machine details, for example
    context = RequestContext(req)
    
    # Construct a dictionary to pass to the template engine as its context.
    # Note the key boldmessage is the same as {{ boldmessage }} in the template!
    context_dict = {'boldmessage': "I am bold font from the context"}

    # Return a rendered response to send to the client
    # We make use of the shortcut function to make our lives easier.
    # Note that the first parameter is the template we wish to use.
    return render_to_response('rango/index.html', context_dict, context)

# This will be another view
def about(req):
    return HttpResponse("Rango Says: Here is the about page.<br/><a href='/rango/'>Index</a>")

# And this

# And this...

