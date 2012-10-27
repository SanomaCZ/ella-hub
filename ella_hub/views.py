from django.shortcuts import get_object_or_404
from ella.core.models import Publishable
from ella.core.views import ObjectDetail


def preview_publishable(request, id):
    publishable = get_object_or_404(Publishable, id=id)
    publishable.static = True
    publishable.published = True
    publishable.save()
    view = ObjectDetail()

    return view(request, category="", slug=publishable.slug, id=id)
