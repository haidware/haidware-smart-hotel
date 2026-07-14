from urllib.parse import quote_plus

from django.http import HttpResponseRedirect


class AdminAuthRequiredMiddleware:
 def __init__(self, get_response):
  self.get_response = get_response
  self.protected_prefixes = (
   "/dashboard/",
   "/device-page/",
   "/app-web/",
   "/kitchen/",
   "/bar/",
   "/services/",
   "/orders/",
   "/payments/",
   "/workflow/",
   "/tracking/",
   "/devices/",
   "/staff/",
   "/settings/",
   "/web-qr-operation/",
  )
  self.public_prefixes = (
   "/admin-login/",
   "/admin-signup/",
   "/admin-logout/",
   "/guest/",
   "/qr/",
   "/api/web-qr/bootstrap/",
   "/static/",
  )

 def __call__(self, request):
  path = request.path
  if path in ("/",):
   return self.get_response(request)
  if any(path.startswith(prefix) for prefix in self.public_prefixes):
   return self.get_response(request)
  if any(path.startswith(prefix) for prefix in self.protected_prefixes):
   if not request.session.get("admin_account_id"):
    target = quote_plus(request.get_full_path())
    return HttpResponseRedirect(f"/admin-login/?next={target}")
  return self.get_response(request)
