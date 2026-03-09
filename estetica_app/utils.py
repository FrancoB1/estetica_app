from django.shortcuts import redirect


def redirect_back(request, fallback):

    referer = request.META.get('HTTP_REFERER')

    if referer:
        return redirect(referer)

    return redirect(fallback)