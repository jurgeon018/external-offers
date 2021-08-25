class DegradationException(Exception):
    pass


USER_ROLES_REQUEST_MAX_TRIES_ERROR = """
    Failed to fetch user roles within %(tries)s attempts. Realty user id = %(user_id)s
"""
