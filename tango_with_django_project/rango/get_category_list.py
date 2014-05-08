from rango.models import Category

def get_category_list(max_results=0, starts_with=''):

    """
    Helper function to get and filter categories into a list
    according to maximum results and beginning character
    """
    # Set an empty cat_list 
    cat_list = []
    # if starts_with parameter is provided
    if starts_with:
        # Filter (get) category's name that starts with starts_with
        cat_list = Category.objects.filter(name__istartwith=starts_with)
    else:
        # Get every object
        cat_list = Category.objects.all()

    # if max_results is more than 0 
    if max_results > 0:
        # if cat_list length is bigger than max_results
        if len(cat_list) > max_results:
            # set cat_list to get up to the max_results
            # (i.e. max_results = 3, then slice cat_list[0:3]
            cat_list = cat_list[:max_results]

    return cat_list
