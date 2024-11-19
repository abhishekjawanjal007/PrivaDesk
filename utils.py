import secrets


def generate_verification_code():
    # Generate a random 6-digit verification code
    return str(secrets.randbelow(1000000)).zfill(6)
