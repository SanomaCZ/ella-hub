

def get_full_path(request, path=None):
    return "%s://%s%s" % (
        "https" if request.is_secure() else "http",
        request.META["HTTP_HOST"],
        path if path is not None else request.get_full_path(),
    )
