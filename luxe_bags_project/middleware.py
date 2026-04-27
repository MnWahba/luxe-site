"""
Permanent language middleware fix.
Ensures language is always read from cookie/session on every request.
Handles both /ar/ URL prefix and cookie-based switching.
"""
from django.utils import translation
from django.conf import settings


class PermanentLanguageMiddleware:
    """
    Reads django_language cookie on EVERY request and activates it.
    This ensures language persists across ALL pages even without URL prefix.
    Must come AFTER LocaleMiddleware so URL prefix takes priority.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get language from cookie (set by language_view)
        cookie_lang = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
        
        # Get language from URL path
        path = request.path_info
        url_lang = None
        for code, _ in settings.LANGUAGES:
            if path.startswith(f'/{code}/') or path == f'/{code}':
                url_lang = code
                break
        
        # URL prefix takes priority, then cookie
        final_lang = url_lang or cookie_lang
        
        if final_lang and final_lang in [c for c, _ in settings.LANGUAGES]:
            translation.activate(final_lang)
            request.LANGUAGE_CODE = final_lang
        
        response = self.get_response(request)
        return response
