
def use_in_clever(bundle):
    """
    clever/crazy choice where field will be used. We use limit GET attr
    to distinction of list view. Yes it is crazy but speed is incredible.
    So if you want use_in param to distinction list, detail view only, you can
    but not in django-tastypie==0.9.14 there is bug, you can try version 0.11.0 
    """
    if 'limit' in bundle.request.GET:
        return False
    return True
