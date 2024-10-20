from django.views.generic import TemplateView

class IndexView(TemplateView):
    """
    View to render the index.html page.
    """
    template_name = 'index.html'

