import re

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions

USERNAME_MIN_LENGTH = 9


def is_valid_username(username):
    if get_user_model().objects.filter(username=username).exists():
        return False
    if not username.lower().startswith("cpe"):
        return False
    if len(username.replace("/", "")) < USERNAME_MIN_LENGTH:
        return False
    if not username.isalnum():
        return False
    return True


def is_valid_password(password, user):
    try:
        validate_password(password, user=user)
    except exceptions.ValidationError:
        return False
    return True


def is_valid_email(email):
    if get_user_model().objects.filter(email=email).exists():
        return False
    if not re.match(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", email):
        return False
    if email is None:
        return False
    return True


def validate_username(username):
    if get_user_model().objects.filter(username=username).exists():
        return {
            "success": False,
            "reason": "User with that matriculation number already exists",
        }
    if not isinstance(username, six.string_types):

        return {
            "success": False,
            "reason": "Matriculation number should be alphanumeric",
        }

    if len(username.replace("/", "")) < USERNAME_MIN_LENGTH:
        return {
            "success": False,
            "reason": "Matriculation number too long",
        }

    if not username.isalnum():

        return {
            "success": False,
            "reason": "Matriculation number should be alphanumeric",
        }

    if not username.lower().startswith("cpe"):
        return {
            "success": False,
            "reason": "Matriculation number is not valid",
        }

    return {
        "success": True,
    }


def validate_email(email):
    if get_user_model().objects.filter(email=email).exists():
        return {"success": False, "reason": "Email Address already exists"}
    if not re.match(r"^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$", email):
        return {"success": False, "reason": "Invalid Email Address"}
    if email is None:
        return {"success": False, "reason": "Email is required."}
    return {"success": True}
