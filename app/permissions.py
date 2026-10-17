# placeholder permission helpers

def is_admin(user):
    return getattr(user, 'is_admin', False)
