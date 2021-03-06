from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from datetime import datetime


def index(request):
    # Query the database for a list of all categories currently stored.
    # Order the categories by the number of likes in decending order.
    # Retrieve the top 5 -- or all if less than 5.
    # Place the list in context_dict
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list

    # Obtain our Response object early so we can add cookie information.

    # Call the helper function to handle the cookies
    visitor_cookie_handler(request)

    response = render(request, 'rango/index.html', context=context_dict)
    return response


def about(request):
    context_dict = {}
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits'] 
    return render(request, 'rango/about.html', context_dict)

def show_category(request, category_name_slug):
    # Create a context dictionary which we can pass to the template rendering engine.
    context_dict = {}

    try:
        # Either find category_name_slug or raise exception
        category = Category.objects.get(slug=category_name_slug)

        # Get assosiated pages
        pages = Page.objects.filter(category=category)

        #Add results list to the template context under name pages
        context_dict['pages'] = pages

        # Also add the category object from the database to context dictionary
        context_dict['category'] = category

    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None

    return render(request, 'rango/category.html', context=context_dict)


def add_category(request):
    form = CategoryForm()

    if request.user.is_authenticated == False:
        return redirect("rango:login")

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            # Save the new category to the database
            form.save(commit=True)     
            # Redirect to index view
            return redirect('/rango/')   
        else:
            print(form.errors)
    
    # render form with error messages (if any)
    return render(request, 'rango/add_category.html', {'form': form})


def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    if request.user.is_authenticated == False:
        return redirect("rango:login")
    
    if category is None:
        return redirect('/rango/')
    
    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()

                return redirect(reverse('rango:show_category', 
                                kwargs={'category_name_slug': 
                                category_name_slug}))

        else:
            print(form.errors)

    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)


def register(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            # Hash password, update
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()
            registered = True
        else:
            # Invalid form
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request,
                  'rango/register.html',
                  context = {'user_form': user_form,
                             'profile_form': profile_form,
                             'registered': registered})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                # Inactive account
                return HttpResponse("Your Rango account is disabled")
        else:
            # Bad login details
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")

    else:
        return render(request, 'rango/login.html')

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')

@login_required
def user_logout(request):
    logout(request)
    # Return user to homepage
    return redirect(reverse('rango:index'))


# A helper method
def get_server_side_cookie(request, cookie, default_val = None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))

    last_visit_cookie = get_server_side_cookie(request, 'last_visit',
                                                str(datetime.now()))
    late_visit_time = datetime.strptime(last_visit_cookie[:-7],
                                        '%Y-%m-%d %H:%M:%S')

    # If it's been more than 1 day since last visit...
    if (datetime.now()-late_visit_time).days > 0:
        visits = visits + 1
        # Update teh last visit cookie now that we have updated the count
        request.session['last_visit'] = str(datetime.now())
    else:
        # Set the last visit cookie
        request.session['last_visit'] = last_visit_cookie

    # Update/set the visits cookie
    request.session['visits'] = visits