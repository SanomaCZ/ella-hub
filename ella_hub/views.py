from django.http import Http404
from django.shortcuts import get_object_or_404

from ella.core.models import Publishable
from ella.core.views import EllaCoreView
from tastypie.models import ApiKey


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

    try:
        api_key = ApiKey.objects.get(user_id=request.GET.get('user'))
    except ApiKey.DoesNotExist:
        raise Http404("Invalid user")
    else:
        if api_key.key[:8] != request.GET.get('hash'):
            raise Http404("Invalid key")

    view = ArticlePreview()

    return view(request, id=id)
