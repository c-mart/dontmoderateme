from hashlib import pbkdf2_hmac


def pw_hash(password, salt):
    """Returns pbkdf2 hash of salted password"""
    return pbkdf2_hmac('sha512', str.encode(password), salt, 100000)
