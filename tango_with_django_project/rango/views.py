# Each view is one function.
# Each view takes in at least one argument - a HttpRequest object.
# Each view must return a HttpResponse object. A simple HttpResponse
# object takes a string parameter representing the content of the page
# we wish to send to the client requesting the view.

# Create your views here.
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

# Import the Category and Page models
from rango.models import Category, Page

# This is a view called "index"
def index(req):
    #return HttpResponse("Rango says hello!<br/><a href='/rango/about/'>About</a>")
    
    # Request the context of the HTTP request
    context = RequestContext(req)

    # Query the database for a list of ALL categories currently stored.
    # Order the categories by no. likes in descending order.
    # Retrieve the top 5 only - or all if less than 5.
    # Place the list in our context_dict dictionary which will be passed
    category_list = Category.objects.order_by('-likes')[:5]    
    context_dict = {'categories': category_list}

    for category in category_list:
        category.url = category.name.replace(' ', '_')

    # Return a rendered response to send to the client
    # We make use of the shortcut function to make our lives easier.
    # Note that the first parameter is the template we wish to use.
    return render_to_response('rango/index.html', context_dict, context)

# This will be another view
def about(req):
    #return HttpResponse("Rango Says: Here is the about page.<br/><a href='/rango/'>Index</a>")
    context = RequestContext(req)
    return render_to_response('rango/about.html', context)


# And this
def category(req, category_name_url):
    # Request our context from the request passed to us.
    context = RequestContext(req)

    # Change underscores in the category name to spaces
    # URLs don't handle spaces well, so we encode them as underscores.
    # We can then simply replace the underscores with spaces again to get the name.
    category_name = category_name_url.replace('_', ' ')

    # Create a context dictionary which we can pass to the template rendering engine
    # We start by containing the name of the category passed by the user
    context_dict = {'category_name': category_name}

    try:
        # Can we find a category with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # So the .get() method returns one model instance or raises an exception
        category = Category.objects.get(name=category_name)

        # Retrieve all of the associated pages.
        # Note that filter returns >= 1 model instance
        pages = Page.objects.filter(category=category)

        # Adds our results list to the template context under name pages
        context_dict['pages'] = pages
        # We also add the category object from the database to the context dictionary
        # We'll use this in the template to verify that the category exists
        context_dict['category'] = category
    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything - the template displays the "no category" message for us.
        pass

    # Go render the response and return it to the client
    return render_to_response('rango/category.html', context_dict, context)

# And this...

