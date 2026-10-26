
import re


def validate_username(username):
    pattern = r"^[A-Za-z][A-Za-z0-9_]{2,19}$"
    return re.fullmatch(pattern, username) is not None


def validate_email(email):
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return re.fullmatch(pattern, email) is not None
