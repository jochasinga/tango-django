# Each view is a function (or class) which...
# ...takes in at least one argument - a HttpRequest object.
# ...return a HttpResponse object.
 
# A simple HttpResponse object takes a string parameter 
# representing the content of the page we wish to send to 
# the client requesting the view.

# Optionally, a helper function render_to_response takes 
# three arguments - an html url to render, a context dictionary,
# and a context.

# The general workflow of a view function are...
# Request a context of the HttpRequest => Set all your variables =>
# Put your variables into context_dict => Pass context_dict and context
# into render_to_response function to render away the template!

# Shortcuts
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import redirect
# Authentication
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
# Basic HTTP functions
from django.http import HttpResponseRedirect, HttpResponse
# Import the necessary models
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
# Basic Python modules
from datetime import datetime
# External functions
from rango.bing_search import run_query

def simple_encode_decode(any_string):

    """An adhoc, general function that replace ' ' with '_' in any string provided,
       and the other way round.
    """
    if type(any_string) == str or type(any_string) == unicode:
        # Detect if there's a blank space within the string
        # and replace it with '_'
        if ' ' in any_string:
            any_string = any_string.replace(' ', '_')
            # Else if '_' is detected, ' ' will replace it.
        elif '_' in any_string:
            any_string = any_string.replace('_', ' ')
        else:
            pass
    else:
        raise TypeError("Not of type <'str'> or <'unicode'>")

    return any_string

def get_cat_list(max_results=0, starts_with=''):
    
    """
    Helper function to get a list of categories according to specified
    maximum results and leading character(s)
    """
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__istartswith=starts_with)
    else:
        cat_list = Category.objects.all()

    if max_results > 0:
        if len(cat_list) > max_results:
            cat_list = cat_list[:max_results]

    for cat in cat_list:
        cat.url = simple_encode_decode(cat.name)

    return cat_list


def encode_to_url(cat_list):

    """Recursively replace ' ' in category's name with '_' by taking a list,
       iterating through each category name. 
    """
    for cat in cat_list:
        if hasattr(cat, 'name'):
            cat.url = cat.name.replace(' ', '_')
        else:
            raise AttributeError("Category object has no attribute 'name'")

    # return a string joined by '_'
    return cat_list

def decode_from_url(category_name_url):

    """Replace '_' in category's or page's url with ' '"""

    for category_name in category_name_url:
        # Make a category string out of URL string
        category_name = category_name_url.replace('_', ' ')

    # return a string joined by ' '
    return category_name

def get_category_list(n='all', order='likes'):

    """Helper function to get cat_list"""

    if n == 'all':
        cat_list = Category.objects.all()
        if order == 'likes':
            cat_list = Category.objects.order_by('-likes')[:]
        elif order == 'name':
            cat_list = Category.objects.order_by('-name')[:]
        elif order == 'visits':
            cat_list = Category.objects.order_by('-visits')[:]
        else:
            print "order = ['likes', 'name', 'visits']"
        
    elif type(n) == int and n >= 0:
        if order == 'likes':
            cat_list = Category.objects.order_by('-likes')[:n]
        elif order =='name':
            cat_list = Category.objects.order_by('-name')[:n]
        elif order == 'visits':
            cat_list = Category.objects.order_by('-visits')[:n]
        else:
            raise ValueError("Category object has no attribute %s" %(order,))
    else:
        raise TypeError("n must be an integer more than or equals to 0")
    
    for cat in cat_list:
        cat.url = simple_encode_decode(cat.name)

    return cat_list
    
# index view
def index(req):

    """View for index page"""

    # Request the context of the HTTP request
    context = RequestContext(req)

    # Query database for a list of ALL categories ordered by no. of likes(descending)
    # cat_list = Category.objects.order_by('-likes')[:5]
    
    # Query database for a list of ALL categories (see get_category_list function)
    # cat_list = Category.objects.all()
    # cat_list = encode_to_url(cat_list)

    cat_list = get_category_list()

    # Query database for a list of ALL pages ordered by number of views (descending)
    page_list = Page.objects.order_by('-views')[:5]

    # Set default
    visits = 0
    last_visit_time = str(datetime.now())

    # Place the lists in context_dict to be passed on as template argument
    context_dict = {'cat_list': cat_list, 'pages': page_list}

    # Does the cookie last_visit exist?
    if req.session.get('last_visit'):
        # Yes it does! Get the cookie's value.
        last_visit_time = req.session.get('last_visit')
        visits = req.session.get('visits', 0)
        # Cast the value to a Python date/time object.
        last_visit_time = datetime.strptime(last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")

        # If it's been more than a day since the last visit...
        if (datetime.now() - last_visit_time).seconds > 10:
            # increment the time visited
            req.session['visits'] = visits + 1
            req.session['last_visit'] = str(datetime.now())

    else:
        # The get returns None, and the session doesn't have a value for the last visit
        req.session['last_visit'] = str(datetime.now())
        req.session['visits'] = 1

    context_dict['visits'] = visits
    context_dict['last_visit_time'] = last_visit_time

    # Return response back to the user, updating any cookies that need changed
    return render_to_response('rango/index.html', context_dict, context)


# about view
def about(req):

    """View serving the about page"""

    # Query the HTTPRequest context
    context = RequestContext(req)

    cat_list = get_category_list()

    if req.session.get('last_visit'):
        last_visit_time = req.session.get('last_visit')
        visits = req.session.get('visits', 0)
        last_visit_time = datetime.strptime(last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")

        if (datetime.now() - last_visit_time).seconds > 10:
            req.session['visits'] = visits + 1
            req.session['last_visit'] = str(datetime.now())

    else:
        req.session['visits'] = visits + 1
        req.session['last_visit'] = str(datetime.now())

    context_dict = {'cat_list': cat_list, 'visits': visits, 'last_visit_time': last_visit_time}

    # Simply return the template, since no model data are used here
    return render_to_response('rango/about.html', context_dict, context)

# myass view
def myass(req):
    "Bonus view \|^_^|/"
    
    # Quary the HTTP Request context (GET or POST)
    context = RequestContext(req)

    # Simply return the myass template
    return render_to_response('rango/myass.html', context)

# category view
def category(req, category_name_url):

    """
    This view take an additional parameter, category_name_url
    which will store the decoded category name. We will need
    some help functions to encode and decode the category_name_url
    """

    # Request our context from the request passed to us.
    context = RequestContext(req)

    # Retrieve categories list for the left navbar
    cat_list = get_category_list()

    # Change underscores in the category name to spaces
    # URLs don't handle spaces well, so we encode them as underscores.
    # We can then simply replace the underscores with spaces again to get the name.
    # category_name = category_name_url.replace('_', ' ')
    
    category_name = decode_from_url(category_name_url)

    context_dict = {'cat_list': cat_list, 'category_name': category_name}
    try:
        # Can we find a category with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # So the .get() method returns one model instance or raises an exception
        category = Category.objects.get(name=category_name)
        
        # Add category to the context so that we can access the ids and likes
        context_dict['category'] = category

        # Retrieve all of the associated pages.
        # Note that filter returns >= 1 model instance
        pages = Page.objects.filter(category=category)
        
        # Adds our results list to the template context under name pages
        context_dict['pages'] = pages

        # We also add the category object from the database to the context dictionary
        # We'll use this in the template to verify that the category exists
        # context_dict = { 'category_name': category_name, 'pages':pages, 'category': category }
        # context_dict['category'] = category
    
    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything - the template displays the "no category" message for us.
        pass

    # Create a context dictionary which we can pass to the template rendering engine
    # We start by containing the name of the category passed by the user

    context_dict = {'cat_list': cat_list,
                    'category_name': category_name,
                    'category_name_url': category_name_url,
                    'pages': pages,
                    'category': category}

    if req.method == 'POST':
        query = req.POST['query'].strip()
        if query:
            result_list = run_query(query)
            context_dict['result_list'] = result_list

    # Go render the response and return it to the client using the over-convenient
    # render_to_response() shortcut function
    return render_to_response('rango/category.html', context_dict, context)

@login_required
def add_category(req):
    """View used to add new categories"""

    # Get the context from the request.
    context = RequestContext(req)

    # Retrieve categories list for the left navbar
    cat_list = get_category_list()

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

    context_dict = {'cat_list': cat_list, 'form': form}

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render_to_response('rango/add_category.html', context_dict, context)

@login_required
def add_page(req, category_name_url):

    """A view to add page to a category"""

    context = RequestContext(req)
    cat_list = get_category_list()
    category_name = decode_from_url(category_name_url)

    if req.method == 'POST':
        form = PageForm(req.POST)

        if form.is_valid():
            # This time we cannot commit straight away.
            # Not all fields are automatically populated!
            page = form.save(commit=False)

            try:
                cat = Category.objects.get(name=category_name)
                page.category = cat
            except Category.DoesNotExist:
                return render_to_response('rango/add_category.html', {}, context)

            # Also, create a default value for the number of views.
            page_views = 0

            # With this, we can then save our new model instance
            page.save()

            # Now that the page is saved, display the category instead.
            return category(req, category_name_url)
        else:
            print form.errors
    else:
        form = PageForm()

    context_dict = {'cat_list': cat_list,
                    'category_name_url': category_name_url,
                    'category_name': category_name,
                    'form': form}

    return render_to_response('rango/add_page.html', context_dict, context)

def register(req):
    # Like before, get the request's context
    context = RequestContext(req)
    cat_list = get_category_list()
    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data
    if req.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that mwe make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=req.POST)
        profile_form = UserProfileForm(data=req.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # save the data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # ONce hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and put it in the UserProfileForm
            if 'picture' in req.FILES:
                profile.picture = req.FILES['picture']

            # Now we save the UserProfile Model instance
            profile.save()

            # Update our variable to tell the template registration is successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal
        # They'll also be shown to the user.
        else:
            print user_form.errors, profile_form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    context_dict = {'cat_list': cat_list,
                    'user_form': user_form, 
                    'profile_form': profile_form, 
                    'registered': registered}

    # Render the template depending on the context
    return render_to_response('rango/register.html', context_dict, context)

def user_login(req):
    context = RequestContext(req)
    cat_list = get_category_list()
    if req.method == 'POST':
        # Gather the username and password provided by the user
        # This information is obtained from the login form
        username = req.POST['username']
        password = req.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is
        user = authenticate(username=username, password=password)

        # If we have obtained a User object, the details are correct
        # If None (Python's way of saying nil), no user with matching
        # credentials was found
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in
                # We'll send the user back to the homepage
                login(req, user)
                return HttpResponseRedirect('/rango/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your Rango account is disabled.")
                # Maybe lead the user to enabled his account

        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    # The request is not HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render_to_response('rango/login.html', {'cat_list': cat_list}, context)

@login_required
def restricted(req):
    context = RequestContext(req)
    cat_list = get_category_list()
    return render_to_response('rango/restricted.html', {'cat_list': cat_list}, context)

@login_required
def user_logout(req):
    # Since we know the user is logged in, we can now just log them out.
    logout(req)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/rango/')

@login_required
def profile(req):
    context = RequestContext(req)
    cat_list = get_category_list()
    context_dict = {'cat_list': cat_list}
    u = User.objects.get(username=req.user)

    try:
        up = UserProfile.objects.get(user=u)
    except:
        up = None

    context_dict['user'] = u
    context_dict['userprofile'] = up

    return render_to_response('rango/profile.html', context_dict, context)

def search(req):
    context = RequestContext(req)
    cat_list = get_category_list()
    result_list = []

    if req.method == 'POST':
        query = req.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list
            result_list = run_query(query)
            
    context_dict = {'cat_list': cat_list, 'result_list': result_list}

    return render_to_response('rango/search.html', context_dict, context)

def track_url(req):
    
    """Track the number of times each page is clicked and viewed"""

    context = RequestContext(req)
    page_id = None
    url = '/rango/'
    if req.method == 'GET':
        if 'page_id' in req.GET:
            page_id = req.GET['page_id']
            try:
                page = Page.objects.get(id=page_id)
                page.views = page.views + 1
                page.save()
                url = page.url
            except:
                pass
    
    return redirect(url)

@login_required
def like_category(req):
    context = RequestContext(req)
    # Set cat_id to None
    cat_id = None
    # If the browser is requesting...
    if req.method == 'GET':
        # get the 'category_id' from the client and store 
        # in cat_id
        cat_id = req.GET['category_id']

    # Set likes to 0
    likes = 0
    
    # If cat_id exists
    if cat_id:
        # Retrieve category with the id=cat_id
        category = Category.objects.get(id=int(cat_id))
        # And if that category object exists
        if category:
            # Add one like to category's like
            likes = category.likes + 1
            # Update the category.likes
            category.likes = likes
            # save the category's new data
            category.save()
            
    return HttpResponse(likes)

def suggest_category(req):
    
    """Return the top max_results matching category results"""

    context = RequestContext(req)

    cat_list = []
    starts_with = ''
    if req.method == 'GET':
        starts_with = req.GET['suggestion']

    cat_list = get_cat_list(8, starts_with)

    return render_to_response('rango/category_list.html', {'cat_list': cat_list}, context)
