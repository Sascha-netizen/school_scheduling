from django.shortcuts import render


def error_403(request, exception):
    """Handle 403 Forbidden errors."""
    return render(request, 'errors/403.html', status=403)


def error_404(request, exception):
    """Handle 404 Not Found errors."""
    return render(request, 'errors/404.html', status=404)


def error_405(request, exception):
    """Handle 405 Method Not Allowed errors."""
    return render(request, 'errors/405.html', status=405)


def error_500(request):
    """Handle 500 Internal Server Error errors."""
    return render(request, 'errors/500.html', status=500)