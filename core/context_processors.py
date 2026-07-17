def anonymous_mode_processor(request):
    """Injects anonymous mode state into all templates."""
    return {
        'anonymous_mode': request.session.get('anonymous_mode', False)
    }
