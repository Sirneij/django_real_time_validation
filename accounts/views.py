from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls.base import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from . import tasks, utils
from .forms import LoginForm, StudentRegistrationForm
from .tokens import account_activation_token


def index(request):
    return render(request, "accounts/index.html")


def login_user(request):
    form = LoginForm(request.POST or None)
    msg = "Enter your credentials"
    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get("username").replace("/", "")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(
                        request, user, backend="accounts.authentication.EmailAuthenticationBackend"
                    )
                    messages.success(request, f"Login successful!")
                    if "next" in request.POST:
                        return redirect(request.POST.get("next"))
                    else:
                        return redirect("accounts:index")
                else:
                    messages.error(
                        request,
                        f"Login unsuccessful! Your account has not been activated. Activate your account via {reverse('accounts:resend_email')}",
                    )
                    msg = "Inactive account details"
            else:
                messages.error(request, f"No user with the provided details exists in our system.")
        else:
            messages.error(request, f"Error validating the form")
            msg = "Error validating the form"
    context = {
        "form": form,
        "page_title": "Login in",
        "msg": msg,
    }
    return render(request, "accounts/login.html", context)


def validate_email(request):
    email = request.POST.get("email", None)
    validated_email = utils.validate_email(email)
    res = JsonResponse({"success": True, "msg": "Valid e-mail address"})
    if not validated_email["success"]:
        res = JsonResponse({"success": False, "msg": validated_email["reason"]})
    return res


def validate_username(request):
    username = request.POST.get("username", None).replace("/", "")
    validated_username = utils.validate_username(username)
    res = JsonResponse({"success": True, "msg": "Valid student number."})
    if not validated_username["success"]:
        res = JsonResponse({"success": False, "msg": validated_username["reason"]})
    return res


def student_signup(request):
    form = StudentRegistrationForm(request.POST or None)
    if request.method == "POST":
        post_data = request.POST.copy()
        email = post_data.get("email")
        username = post_data.get("username").replace("/", "")
        password = post_data.get("password1")

        if utils.is_valid_email(email):
            user = get_user_model().objects.create(email=post_data.get("email"))

        if utils.is_valid_password(password, user) and utils.is_valid_username(username):
            user.set_password(password)
            user.username = username
            user.first_name = post_data.get("first_name")
            user.last_name = post_data.get("last_name")
            user.level = post_data.get("level")
            user.gender = post_data.get("gender")
            user.is_active = False
            user.is_student = True
            user.save()
            subject = "Please Activate Your Student Account"
            ctx = {
                "fullname": user.get_full_name(),
                "domain": str(get_current_site(request)),
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": account_activation_token.make_token(user),
            }

            if settings.DEBUG:
                tasks.send_email_message.delay(
                    subject=subject,
                    template_name="accounts/activation_request.txt",
                    user_id=user.id,
                    ctx=ctx,
                )
            else:
                tasks.send_email_message.delay(
                    subject=subject,
                    template_name="accounts/activation_request.html",
                    user_id=user.id,
                    ctx=ctx,
                )
            raw_password = password
            user = authenticate(username=username, password=raw_password)
            return JsonResponse(
                {
                    "success": True,
                    "msg": "Your account has been created! You need to verify your email address to be able to log in.",
                    "next": reverse("accounts:activation_sent"),
                }
            )
        else:
            get_user_model().objects.get(email=post_data.get("email")).delete()
            return JsonResponse(
                {
                    "success": False,
                    "msg": "Check your credentials: your password, username, and email! Ensure you adhere to all the specified measures.",
                }
            )
    context = {"page_title": "Student registration", "form": form}
    return render(request, "accounts/student_signup.html", context)
