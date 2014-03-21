from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from ella.core.models import Publishable
from ella.core.views import ObjectDetail


class ArticlePreview(ObjectDetail):
    template_name = 'object.html'

    def get_context(self, request, category, slug, year, month, day, id):
        publishable = get_object_or_404(Publishable, pk=id)

        context = {
            'object': publishable.target,
            'category': publishable.category,
            'content_type': publishable.content_type
        }

        return context


def preview_publishable(request, id):
    item = get_object_or_404(Publishable, pk=id)
    if item.is_published():
        return HttpResponseRedirect(item.get_absolute_url())

    view = ArticlePreview()
    return view(request, category=item.category, slug=item.slug, id=id)
