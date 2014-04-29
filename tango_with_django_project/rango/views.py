# Each view is one function.
# Each view takes in at least one argument - a HttpRequest object.
# Each view must return a HttpResponse object. A simple HttpResponse
# object takes a string parameter representing the content of the page
# we wish to send to the client requesting the view.

# Import necessary modules
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse

# Import the necessary models
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from datetime import datetime

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

    category_list = encode_to_url(category_list)    

    # Place the lists in context_dict to be passed on as template argument
    context_dict = {'categories': category_list, 'pages': page_list}

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

    context_dict = {'visits': visits, 'last_visit_time': last_visit_time}
        
     
    # Simply return the template, since no model data are used here
    return render_to_response('rango/about.html', context_dict, context)


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
    context_dict = { 'category_name': category_name,
                     'category_name_url': category_name_url }

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


@login_required
def add_category(req):

    """View used to add new categories"""
 
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

@login_required            
def add_page(req, category_name_url):
    context = RequestContext(req)

    category_name = decode_from_url(category_name_url)
    if req.method == 'POST':
        form = PageForm(req.POST)

        if form.is_valid():
            # This time we cannot commit straight away.
            # Not all fields are automatically populated!
            page = form.save(commit=False)

            try:
                cat = Category.objects.get(name = category_name)
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

    return render_to_response( 'rango/add_page.html', {'category_name_url': category_name_url,
                                                       'category_name': category_name,
                                                       'form': form}, context)

def register(req):

    # Like before, get the request's context
    context = RequestContext(req)

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

        # Invalide form or forms - mistakes or something else?
        # Print problems to the terminal
        # They'll also be shown to the user.
        else:
            print user_form.errors, profile_form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context
    return render_to_response(
        'rango/register.html',
        {'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
        context)

def user_login(req):
    context = RequestContext(req)

    
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
        return render_to_response('rango/login.html', {}, context)

@login_required
def restricted(req):
    context = RequestContext(req)
    return render_to_response('rango/restricted.html', {}, context )

@login_required
def user_logout(req):
    # Since we know the user is logged in, we can now just log them out.
    logout(req)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/rango/')
