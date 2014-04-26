# Each view is one function.
# Each view takes in at least one argument - a HttpRequest object.
# Each view must return a HttpResponse object. A simple HttpResponse
# object takes a string parameter representing the content of the page
# we wish to send to the client requesting the view.

# Import necessary modules
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

# Import the necessary models
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm

# Do function overloading here tonight
def encode_to_url(category_list):
    """Replace ' ' in category's or page's name with '_'"""

    for category in category_list:
        # Make a URL String out of category String
        category.url = category.name.replace(' ', '_')
    
    # return a list    
    return category_list

def decode_from_url(category_name_url):
    """Replace '_' in category's or page's url with ' '"""
    
    for category_name in category_name_url:
       # Make a category string out of URL string
       category_name = category_name_url.replace('_', ' ')
    
    # return a string
    return category_name

# index view
def index(req):
    
    """View for index page"""

    # Request the context of the HTTP request
    context = RequestContext(req)

    # Query database for a list of ALL categories ordered by no. of likes(descending)
    category_list = Category.objects.order_by('-likes')[:5]    
    
    # Query databse for a list of ALL pages ordered by number of views (descending)
    page_list = Page.objects.order_by('-views')[:5]

    # Place the lists in context_dict which will be passed as an argument
    context_dict = {'categories': category_list, 'pages': page_list}


    # for category in category_list:
        # Replace any space with an underscore for a 'pretty' url
        # category.url = category.name.replace(' ', '_')
    
    category_list = encode_to_url(category_list)    

    # Return a rendered response to send to the client
    # by mean of a render_to_response() shortcut function to make our lives easier.
    # Note that the first parameter is the template we wish to use.
    return render_to_response('rango/index.html', context_dict, context)

# about view
def about(req):
    
    """View serving the about page"""
    
    # Query the HTTPRequest context
    context = RequestContext(req)
     
    # Simply return the template, since no model data are used here
    return render_to_response('rango/about.html', context)


# category view
def category(req, category_name_url):
    
    """
    This view take an additional parameter, category_name_url
    which will store the decoded category name. We will need
    some help functions to encode and decode the category_name_url
    """

    # Request our context from the request passed to us.
    context = RequestContext(req)

    # Change underscores in the category name to spaces
    # URLs don't handle spaces well, so we encode them as underscores.
    # We can then simply replace the underscores with spaces again to get the name.
    # category_name = category_name_url.replace('_', ' ')
    category_name = decode_from_url(category_name_url)

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
        # context_dict = { 'category_name': category_name, 'pages': pages }
        context_dict['pages'] = pages

        # We also add the category object from the database to the context dictionary
        # We'll use this in the template to verify that the category exists
        # context_dict = { 'category_name': category_name, 'pages':pages, 'category': category }
        context_dict['category'] = category

    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything - the template displays the "no category" message for us.
        pass

    # Go render the response and return it to the client using the over-convenient
    # render_to_response() shortcut function
    return render_to_response('rango/category.html', context_dict, context)

# add_category view
def add_category(req):

    """View used to new categories"""
 
    # Get the context from the request.
    context = RequestContext(req)

    # A HTTP POST? If so, provide a form for posting a new category
    if req.method == 'POST':
        form = CategoryForm(req.POST)

        # Have we been provided with a valid form input from the user?
        if form.is_valid():
            # Save the new category to the database
            form.save(commit=True)

            # Now call the index() view.
            # The user will be served with the index.html template
            return index(req)

        else:
            # The supplied form contained errors - just print them to the terminal
            print form.errors

    else:
        # If the request wasn't a POST, display the form to enter details
        form = CategoryForm()

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render_to_response('rango/add_category.html', {'form':form}, context)
            
