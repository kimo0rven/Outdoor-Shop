from .cart import Cart
from .models import PopularSearchTerm

POPULAR_SEARCH_LIMIT = 8


def cart(request):
    return {'cart': Cart(request)}


def popular_searches(request):
    terms = PopularSearchTerm.objects.all()[:POPULAR_SEARCH_LIMIT]
    return {'popular_search_terms': terms}
