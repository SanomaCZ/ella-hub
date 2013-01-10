from django.shortcuts import get_object_or_404

from ella.core.models import Publishable
from ella.core.views import ObjectDetail


def preview_publishable(request, id):
    publishable = get_object_or_404(Publishable, id=id)
    view = ObjectDetail()

    return view(request, category=publishable.category.tree_path, slug=publishable.slug, id=id)
