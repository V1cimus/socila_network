from django.core.paginator import Paginator
from django.conf import settings


def add_paginator_on_page(post_list, request):
    """Пагинация страинцы."""
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
