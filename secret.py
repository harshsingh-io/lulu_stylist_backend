import secrets

def generate_secret_key(length=50):
    """
    Generate a secure secret key.

    Args:
        length (int): The length of the secret key. Default is 50 characters.

    Returns:
        str: A securely generated secret key.
    """
    return secrets.token_urlsafe(length)

# Generate SECRET_KEY
secret_key = generate_secret_key()
print("SECRET_KEY:", secret_key)

# Generate REFRESH_SECRET_KEY
refresh_secret_key = generate_secret_key()
print("REFRESH_SECRET_KEY:", refresh_secret_key)
