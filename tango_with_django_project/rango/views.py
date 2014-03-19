# Each view is one function.
# Each view takes in at least one argument - a HttpRequest object.
# Each view must return a HttpResponse object. A simple HttpResponse
# object takes a string parameter representing the content of the page
# we wish to send to the client requesting the view.

# Create your views here.
from django.http import HttpResponse

# This is a view called "index"
def index(req):
    return HttpResponse("Rango says hello!")

# This will be another view

# And this

# And this...

