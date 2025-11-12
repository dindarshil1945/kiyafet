from store_app.models import CartItem

def cart_item_count(request):
    """
    Returns the number of cart items for the logged-in user.
    If not logged in, returns 0.
    """
    if request.user.is_authenticated:
        count = CartItem.objects.filter(user=request.user).count()
    else:
        count = 0
    return {'cart_item_count': count}
