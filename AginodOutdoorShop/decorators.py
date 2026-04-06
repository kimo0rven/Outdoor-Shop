from functools import wraps

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse


def staff_member_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('staff_login')
        if not request.user.is_active:
            messages.error(request, 'Your account is inactive.')
            return redirect('staff_login')
        if not request.user.is_staff:
            messages.warning(request, 'That area is for staff only.')
            return redirect('home')
        return view_func(request, *args, **kwargs)

    return _wrapped


def staff_api_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse(
                {
                    'ok': False,
                    'error': 'authentication_required',
                    'login_url': reverse('staff_login'),
                },
                status=401,
            )
        if not request.user.is_active or not request.user.is_staff:
            return JsonResponse(
                {'ok': False, 'error': 'staff_required'},
                status=403,
            )
        return view_func(request, *args, **kwargs)

    return _wrapped
