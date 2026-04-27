"""
Custom language switching view - compatible with Django 4.0+
LANGUAGE_SESSION_KEY was removed in Django 4.0
"""
from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils import translation
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect


@csrf_protect
@require_POST
def switch_language(request):
    lang = request.POST.get('language', settings.LANGUAGE_CODE)
    next_url = request.POST.get('next', '/')

    # Validate language code
    available = [code for code, _ in settings.LANGUAGES]
    if lang not in available:
        lang = settings.LANGUAGE_CODE

    # Activate the new language
    translation.activate(lang)

    # Build correct URL with language prefix
    path = next_url.split('?')[0]   # strip query
    query = ('?' + next_url.split('?', 1)[1]) if '?' in next_url else ''

    # Strip any existing /ar/ or /en/ prefix
    for code, _ in settings.LANGUAGES:
        if path.startswith(f'/{code}/'):
            path = path[len(f'/{code}'):]   # → '/products/' etc.
            break
        if path == f'/{code}':
            path = '/'
            break

    # Ensure leading slash
    if not path.startswith('/'):
        path = '/' + path

    # Build new URL:
    # default language (en) → no prefix  (prefix_default_language=False)
    # other languages (ar)  → /ar/...
    default_lang = settings.LANGUAGE_CODE   # 'en'
    if lang == default_lang:
        new_url = path + query
    else:
        if path == '/':
            new_url = f'/{lang}/' + query
        else:
            new_url = f'/{lang}{path}' + query

    response = HttpResponseRedirect(new_url or '/')

    # Set language cookie (Django 4+ standard way)
    response.set_cookie(
        settings.LANGUAGE_COOKIE_NAME,          # 'django_language'
        lang,
        max_age=60 * 60 * 24 * 365,            # 1 year
        path='/',
        samesite='Lax',
    )

    return response
