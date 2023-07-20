from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def anonymous_required(view_func):
    """
    Декоратор для запрета доступа авторизованным пользователям
    """
    def wrapped_view_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            # Если пользователь авторизован, перенаправляем его на другую страницу
            return redirect('home')
        else:
            return view_func(request, *args, **kwargs)

    return wrapped_view_func
