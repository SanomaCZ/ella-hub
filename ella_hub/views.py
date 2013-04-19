from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from ella.core.models import Publishable
from ella.core.views import EllaCoreView


class ArticlePreview(EllaCoreView):
    template_name = 'object.html'

    def get_context(self, request, **kwargs):
        publishable = get_object_or_404(Publishable, pk=kwargs['id'])

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
    return view(request, id=id)
