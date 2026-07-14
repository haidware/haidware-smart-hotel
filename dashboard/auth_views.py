from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import redirect, render

from .models import AdminAccount


def admin_entry(request):
 return render(request, "dashboard/admin_entry.html")


def admin_signup(request):
 flash_error = None
 next_path = request.GET.get("next", request.POST.get("next", "/dashboard/"))
 if request.method == "POST":
  name = request.POST.get("name", "").strip()
  email = request.POST.get("email", "").strip().lower()
  password = request.POST.get("password", "")
  confirm_password = request.POST.get("confirm_password", "")
  if not name or not email or not password:
   flash_error = "Name, email, and password are required."
  elif password != confirm_password:
   flash_error = "Passwords do not match."
  elif AdminAccount.objects.filter(email=email).exists():
   flash_error = "Email already exists. Please login instead."
  else:
   account = AdminAccount.objects.create(name=name, email=email, password_hash=make_password(password))
   request.session["admin_account_id"] = account.id
   request.session["admin_account_name"] = account.name
   return redirect(next_path)
 return render(request, "dashboard/admin_signup.html", {"flash_error": flash_error, "next": next_path})


def admin_login(request):
 flash_error = None
 next_path = request.GET.get("next", request.POST.get("next", "/dashboard/"))
 if request.method == "POST":
  email = request.POST.get("email", "").strip().lower()
  password = request.POST.get("password", "")
  account = AdminAccount.objects.filter(email=email, is_active=True).first()
  if not account or not check_password(password, account.password_hash):
   flash_error = "Invalid login details."
  else:
   request.session["admin_account_id"] = account.id
   request.session["admin_account_name"] = account.name
   return redirect(next_path)
 return render(request, "dashboard/admin_login.html", {"flash_error": flash_error, "next": next_path})


def admin_logout(request):
 request.session.flush()
 return redirect("/admin-login/")
