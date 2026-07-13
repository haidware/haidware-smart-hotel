import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from django.conf import settings


class SupabaseSyncError(Exception):
 pass


def _price_as_naira(value):
 return f"₦{int(value):,}"


class SupabaseSync:
 def __init__(self):
  self.enabled = bool(settings.SUPABASE_SYNC_ENABLED)
  self.base_url = settings.SUPABASE_URL.rstrip("/")
  self.key = settings.SUPABASE_SERVICE_ROLE_KEY
  self.hotel_table = settings.SUPABASE_HOTEL_TABLE
  self.menu_table = settings.SUPABASE_MENU_TABLE
  self.hotel_name = settings.SUPABASE_HOTEL_NAME
  self._hotel_id = None

 def _check_ready(self):
  if not self.enabled:
   return False
  if not self.base_url or not self.key:
   raise SupabaseSyncError("SUPABASE_SYNC_ENABLED is true but SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY is missing.")
  return True

 def _request(self, method, path, data=None):
  url = f"{self.base_url}/rest/v1/{path}"
  headers = {
   "apikey": self.key,
   "Authorization": f"Bearer {self.key}",
   "Accept": "application/json",
   "Content-Type": "application/json",
   "Prefer": "return=representation",
  }
  body = json.dumps(data).encode("utf-8") if data is not None else None
  req = Request(url=url, data=body, headers=headers, method=method)
  try:
   with urlopen(req, timeout=10) as resp:
    payload = resp.read().decode("utf-8")
    if not payload:
     return []
    parsed = json.loads(payload)
    return parsed if isinstance(parsed, list) else [parsed]
  except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
   raise SupabaseSyncError(f"Supabase request failed: {method} {path}") from exc

 def _ensure_hotel_id(self):
  if self._hotel_id:
   return self._hotel_id
  if not self._check_ready():
   return None
  rows = self._request("GET", f"{self.hotel_table}?select=id,name&name=eq.{quote(self.hotel_name)}&limit=1")
  if rows:
   self._hotel_id = rows[0]["id"]
   return self._hotel_id
  created = self._request("POST", self.hotel_table, data={
   "name": self.hotel_name,
   "brand_name": "HAIDWARE",
   "brand_tagline": "SMART HOTEL EXPERIENCE",
   "operations_account_name": f"{self.hotel_name} Hotel Operations",
   "is_active": True,
  })
  if not created:
   raise SupabaseSyncError("Could not create hotel account in Supabase.")
  self._hotel_id = created[0]["id"]
  return self._hotel_id

 def upsert_menu(self, *, section, name, description, price, active):
  if not self._check_ready():
   return
  category = "kitchen" if section.lower() == "kitchen" else "bar" if section.lower() == "bar" else "services"
  hotel_id = self._ensure_hotel_id()
  q_name = quote(name)
  existing = self._request("GET", f"{self.menu_table}?select=id&hotel_id=eq.{hotel_id}&name=eq.{q_name}&category=eq.{category}&limit=1")
  payload = {
   "hotel_id": hotel_id,
   "name": name,
   "description": description or "",
   "price": _price_as_naira(price),
   "emoji": "🍽️" if category == "kitchen" else "🍹" if category == "bar" else "🛎️",
   "category": category,
   "is_active": bool(active),
  }
  if existing:
   self._request("PATCH", f"{self.menu_table}?id=eq.{existing[0]['id']}", data=payload)
  else:
   self._request("POST", self.menu_table, data=payload)

 def delete_menu(self, *, section, name):
  if not self._check_ready():
   return
  category = "kitchen" if section.lower() == "kitchen" else "bar" if section.lower() == "bar" else "services"
  hotel_id = self._ensure_hotel_id()
  q_name = quote(name)
  self._request("DELETE", f"{self.menu_table}?hotel_id=eq.{hotel_id}&name=eq.{q_name}&category=eq.{category}")
