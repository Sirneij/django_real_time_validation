from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.urls.base import reverse

from .forms import LoginForm


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
