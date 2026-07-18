from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
import io
import qrcode
from urllib.parse import quote_plus
from django.utils import timezone
from functools import wraps
from django.contrib.auth.hashers import check_password, make_password

from .models import AdminAccount, BankAccount, Device, MenuItem, PaymentRecord, ServiceItem
from .supabase_sync import SupabaseSync, SupabaseSyncError

KITCHEN_SEED = [
 {"id": "KIT-001", "name": "Jollof Rice", "category": "Local Dishes", "price": 3500, "available": True, "description": "Smoky rice served with grilled chicken."},
 {"id": "KIT-002", "name": "Fried Rice", "category": "Local Dishes", "price": 3000, "available": True, "description": "Seasoned rice with vegetables."},
 {"id": "KIT-003", "name": "Chicken Alfredo", "category": "Intercontinental", "price": 6200, "available": True, "description": "Creamy pasta with grilled chicken."},
 {"id": "KIT-004", "name": "Pepper Soup", "category": "Soups", "price": 2800, "available": False, "description": "Hot goat-meat pepper soup."},
 {"id": "KIT-005", "name": "Grilled Chicken", "category": "Grills", "price": 4500, "available": True, "description": "Char-grilled chicken with pepper sauce."},
 {"id": "KIT-006", "name": "Chocolate Cake", "category": "Desserts", "price": 2400, "available": False, "description": "Chocolate sponge with ganache."},
]

BAR_SEED = [
 {"id": "BAR-001", "name": "Chapman", "category": "Soft Drinks", "price": 2500, "available": True, "description": "Classic Nigerian fruit refreshment."},
 {"id": "BAR-002", "name": "Mojito", "category": "Cocktails", "price": 3500, "available": True, "description": "Mint, lime and soda cocktail."},
 {"id": "BAR-003", "name": "Red Wine", "category": "Wines", "price": 4000, "available": True, "description": "Premium red wine by the glass."},
 {"id": "BAR-004", "name": "Heineken", "category": "Beers", "price": 1500, "available": False, "description": "Chilled 330ml bottle."},
 {"id": "BAR-005", "name": "Premium Whisky", "category": "Spirits", "price": 6500, "available": True, "description": "Premium whisky by the glass."},
]

SERVICES_SEED = [
 {"id": "SRV-001", "name": "Room Cleaning", "category": "Housekeeping", "price": 2500, "available": True, "note": "Complete room cleaning service."},
 {"id": "SRV-002", "name": "Laundry", "category": "Housekeeping", "price": 3000, "available": True, "note": "Wash, dry and fold."},
 {"id": "SRV-003", "name": "Concierge Request", "category": "Reception", "price": 0, "available": True, "note": "Contact reception for assistance."},
 {"id": "SRV-004", "name": "Airport Taxi", "category": "Transport", "price": 15000, "available": False, "note": "Pre-booked airport transfer."},
 {"id": "SRV-005", "name": "Maintenance", "category": "Maintenance", "price": 0, "available": True, "note": "Report a room fault."},
 {"id": "SRV-006", "name": "Spa Session", "category": "Wellness", "price": 18000, "available": False, "note": "One-hour wellness session."},
]

DEVICES_SEED = [
 {"id": "DEV-001", "location": "Room 205", "type": "Room", "wifi_ssid": "Hotel_Guest_5G", "ip": "192.168.1.23", "wifi": True, "online": True, "active": True, "last_seen": "10 seconds ago"},
 {"id": "DEV-002", "location": "Table 7", "type": "Restaurant Table", "wifi_ssid": "Hotel_Restaurant", "ip": "192.168.1.24", "wifi": True, "online": True, "active": True, "last_seen": "8 seconds ago"},
 {"id": "DEV-003", "location": "Room 118", "type": "Room", "wifi_ssid": "Hotel_Guest_5G", "ip": "192.168.1.25", "wifi": False, "online": False, "active": False, "last_seen": "18 minutes ago"},
 {"id": "DEV-004", "location": "Lounge 2", "type": "Lounge", "wifi_ssid": "Hotel_Lounge", "ip": "192.168.1.26", "wifi": True, "online": False, "active": True, "last_seen": "3 minutes ago"},
]

BANK_ACCOUNTS_SEED = [
 {"bank": "OPay", "name": "HAIDWARE HOTEL", "number": "8123456789", "icon": "O", "bg": "#e8f5e9", "fg": "#16a34a", "display_order": 1},
 {"bank": "Access Bank", "name": "HAIDWARE HOTEL", "number": "0123456789", "icon": "◈", "bg": "#fff3e0", "fg": "#e65100", "display_order": 2},
]

PAYMENTS_SEED = [
 {"reference": "ROOM205-4821", "order": "ORD-1024", "customer": "Room 205", "amount": 9500, "method": "OPay", "account": "8123456789", "status": "Pending Confirmation", "date": "Today, 10:31"},
 {"reference": "TABLE7-3291", "order": "ORD-1023", "customer": "Table 7", "amount": 7000, "method": "Access Bank", "account": "0123456789", "status": "Confirmed", "date": "Today, 10:27"},
 {"reference": "ROOM118-2847", "order": "ORD-1022", "customer": "Room 118", "amount": 3000, "method": "OPay", "account": "8123456789", "status": "Confirmed", "date": "Today, 10:14"},
 {"reference": "LOUNGE2-9103", "order": "ORD-1021", "customer": "Lounge 2", "amount": 6200, "method": "Access Bank", "account": "0123456789", "status": "Pending Confirmation", "date": "Today, 09:58"},
]

ORDERS = [
 {"id": "ORD-1024", "location": "Room 205", "department": "Kitchen", "items": "Jollof Rice x2, Chapman x1", "total": 9500, "payment": "Paid", "status": "Pending", "handler": "Kitchen User", "updated": "2 minutes ago"},
 {"id": "ORD-1023", "location": "Table 7", "department": "Bar", "items": "Mojito x2", "total": 7000, "payment": "Paid", "status": "Preparing", "handler": "Bar User", "updated": "5 minutes ago"},
 {"id": "ORD-1022", "location": "Room 118", "department": "Housekeeping", "items": "Laundry", "total": 3000, "payment": "Room Billing", "status": "Completed", "handler": "Housekeeping", "updated": "20 minutes ago"},
 {"id": "ORD-1021", "location": "Lounge 2", "department": "Kitchen", "items": "Chicken Alfredo x1", "total": 6200, "payment": "Pending", "status": "Pending", "handler": "Unassigned", "updated": "25 minutes ago"},
]

STAFF = [
 {"name": "Hotel Manager", "email": "manager@hotel.com", "role": "Manager", "status": "Active"},
 {"name": "Kitchen User", "email": "kitchen@hotel.com", "role": "Kitchen Staff", "status": "Active"},
 {"name": "Bar User", "email": "bar@hotel.com", "role": "Bar Staff", "status": "Active"},
 {"name": "Reception Desk", "email": "reception@hotel.com", "role": "Reception", "status": "Active"},
 {"name": "Night Supervisor", "email": "night@hotel.com", "role": "Manager", "status": "Suspended"},
]

_SEEDED = False
SUPABASE_SYNC = SupabaseSync()


def _seed_db_once():
 global _SEEDED
 if _SEEDED:
  return
 if not MenuItem.objects.exists():
  MenuItem.objects.bulk_create([MenuItem(section="Kitchen", **x) for x in KITCHEN_SEED] + [MenuItem(section="Bar", **x) for x in BAR_SEED], ignore_conflicts=True)
 if not ServiceItem.objects.exists():
  ServiceItem.objects.bulk_create([ServiceItem(**x) for x in SERVICES_SEED], ignore_conflicts=True)
 if not Device.objects.exists():
  Device.objects.bulk_create([Device(**x) for x in DEVICES_SEED], ignore_conflicts=True)
 if not BankAccount.objects.exists():
  BankAccount.objects.bulk_create([BankAccount(**x) for x in BANK_ACCOUNTS_SEED], ignore_conflicts=True)
 if not PaymentRecord.objects.exists():
  PaymentRecord.objects.bulk_create([PaymentRecord(**x) for x in PAYMENTS_SEED], ignore_conflicts=True)
 _SEEDED = True


def _network_for(device_type):
 return {"Room": "Hotel_Guest_5G", "Restaurant Table": "Hotel_Restaurant", "Bar Table": "Hotel_Bar", "Lounge": "Hotel_Lounge"}.get(device_type, "Hotel_Guest_5G")


def _next_ip():
 octets = [int(x.ip.split(".")[-1]) for x in Device.objects.all() if x.ip.count(".") == 3 and x.ip.split(".")[-1].isdigit()]
 return f"192.168.1.{(max(octets) + 1) if octets else 21}"

def _to_int(value, default=0):
 try:
  return int(str(value).strip())
 except (TypeError, ValueError):
  return default


def _unique_reference(reference):
 ref = reference
 index = 1
 while PaymentRecord.objects.filter(reference=ref).exists():
  ref = f"{reference}-{index}"
  index += 1
 return ref


def base(title, eyebrow, description):
 return {"page_title": title, "eyebrow": eyebrow, "description": description, "admin_name": "Admin Handler"}


def admin_required(view_func):
 @wraps(view_func)
 def _wrapped(request, *args, **kwargs):
  if request.session.get("admin_account_id"):
   return view_func(request, *args, **kwargs)
  return redirect(f"/admin-login/?next={quote_plus(request.get_full_path())}")
 return _wrapped


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


@admin_required
def overview(request):
 _seed_db_once()
 all_menu = list(MenuItem.objects.all())
 all_services = list(ServiceItem.objects.all())
 all_items = all_menu + all_services
 visible = [x for x in all_items if x.available]
 c = base("Smart Hotel Control Center", "ADMIN OVERVIEW", "Manage available menu items, payment-confirmed orders, tracking updates, handler workflow, IoT WiFi devices, and customer service requests.")
 c.update(metrics=[{"value": len(all_items), "label": "Total Items"}, {"value": len(visible), "label": "Visible on Device"}, {"value": len([o for o in ORDERS if o["status"] == "Pending"]), "label": "Pending Orders"}, {"value": Device.objects.count(), "label": "IoT Devices"}], preview_items=visible[:7], recent_orders=ORDERS[:3])
 return render(request, "dashboard/overview.html", c)


@admin_required
def device_page(request):
 c = base("Device Description Page", "SMART HOTEL DEVICE", "Public-facing product description and authorized admin entry foundation.")
 c["features"] = ["Kitchen Menu", "Bar Menu", "Hotel Services", "Bank Transfer Payment", "WiFi IoT Device", "Admin Control"]
 return render(request, "dashboard/device_page.html", c)


@admin_required
def app_web(request):
 _seed_db_once()
 c = base("App-Web Version", "CUSTOMER APP WEB", "Standalone customer web app window synchronized to this admin portal database.")
 c.update(sample_rooms=list(Device.objects.all()[:4]), stats=[{"label": "Customer UI", "value": "Ready"}, {"label": "Data Source", "value": "SQLite Database"}, {"label": "Next Step", "value": "Connect external API clients"}, {"label": "Sync Target", "value": "Admin Portal"}], services_preview=list(ServiceItem.objects.filter(available=True)[:4]))
 return render(request, "dashboard/app_web.html", c)


@admin_required
def kitchen(request):
 _seed_db_once()
 flash_success = None
 flash_error = None
 if request.method == "POST":
  action = request.POST.get("action", "add").strip().lower()
  item_id = request.POST.get("item_id", "").strip().upper()
  if action == "toggle":
   item = MenuItem.objects.filter(id=item_id, section="Kitchen").first()
   if item:
    item.available = not item.available
    item.save(update_fields=["available"])
    flash_success = f"{item.name} visibility updated."
    try:
     SUPABASE_SYNC.upsert_menu(section="Kitchen", name=item.name, description=item.description, price=item.price, active=item.available)
    except SupabaseSyncError as exc:
      flash_error = str(exc)
   else:
    flash_error = f"{item_id} not found."
  elif action == "delete":
   item = MenuItem.objects.filter(id=item_id, section="Kitchen").first()
   if item:
    item_name = item.name
    item.delete()
    flash_success = f"{item_name} deleted."
    try:
     SUPABASE_SYNC.delete_menu(section="Kitchen", name=item_name)
    except SupabaseSyncError as exc:
      flash_error = str(exc)
   else:
    flash_error = f"{item_id} not found."
  else:
   name = request.POST.get("name", "").strip()
   category = request.POST.get("category", "").strip()
   price = _to_int(request.POST.get("price"), 0)
   description = request.POST.get("description", "").strip()
   if not item_id or not name or not category:
    flash_error = "Item ID, name and category are required."
   elif MenuItem.objects.filter(id=item_id).exists():
    flash_error = f"{item_id} already exists."
   else:
    item = MenuItem.objects.create(id=item_id, section="Kitchen", name=name, category=category, price=price, available=True, description=description)
    flash_success = f"{item.name} added."
    try:
     SUPABASE_SYNC.upsert_menu(section="Kitchen", name=item.name, description=item.description, price=item.price, active=item.available)
    except SupabaseSyncError as exc:
      flash_error = str(exc)
 c = base("Kitchen Menu", "SMART HOTEL DEVICE", "Available items appear on the guest device; unavailable items remain hidden.")
 c.update(items=list(MenuItem.objects.filter(section="Kitchen")), categories=["All", "Local Dishes", "Intercontinental", "Soups", "Grills", "Desserts"], item_type="Food", flash_success=flash_success, flash_error=flash_error)
 return render(request, "dashboard/menu.html", c)


@admin_required
def bar(request):
 _seed_db_once()
 flash_success = None
 flash_error = None
 if request.method == "POST":
  action = request.POST.get("action", "add").strip().lower()
  item_id = request.POST.get("item_id", "").strip().upper()
  if action == "toggle":
   item = MenuItem.objects.filter(id=item_id, section="Bar").first()
   if item:
    item.available = not item.available
    item.save(update_fields=["available"])
    flash_success = f"{item.name} visibility updated."
    try:
     SUPABASE_SYNC.upsert_menu(section="Bar", name=item.name, description=item.description, price=item.price, active=item.available)
    except SupabaseSyncError as exc:
      flash_error = str(exc)
   else:
    flash_error = f"{item_id} not found."
  elif action == "delete":
   item = MenuItem.objects.filter(id=item_id, section="Bar").first()
   if item:
    item_name = item.name
    item.delete()
    flash_success = f"{item_name} deleted."
    try:
     SUPABASE_SYNC.delete_menu(section="Bar", name=item_name)
    except SupabaseSyncError as exc:
      flash_error = str(exc)
   else:
    flash_error = f"{item_id} not found."
  else:
   name = request.POST.get("name", "").strip()
   category = request.POST.get("category", "").strip()
   price = _to_int(request.POST.get("price"), 0)
   description = request.POST.get("description", "").strip()
   if not item_id or not name or not category:
    flash_error = "Item ID, name and category are required."
   elif MenuItem.objects.filter(id=item_id).exists():
    flash_error = f"{item_id} already exists."
   else:
    item = MenuItem.objects.create(id=item_id, section="Bar", name=name, category=category, price=price, available=True, description=description)
    flash_success = f"{item.name} added."
    try:
     SUPABASE_SYNC.upsert_menu(section="Bar", name=item.name, description=item.description, price=item.price, active=item.available)
    except SupabaseSyncError as exc:
      flash_error = str(exc)
 c = base("Bar Menu", "SMART HOTEL DEVICE", "Control which drinks are available for guests to browse and order.")
 c.update(items=list(MenuItem.objects.filter(section="Bar")), categories=["All", "Soft Drinks", "Cocktails", "Wines", "Beers", "Spirits"], item_type="Drink", flash_success=flash_success, flash_error=flash_error)
 return render(request, "dashboard/menu.html", c)


@admin_required
def services(request):
 _seed_db_once()
 flash_success = None
 flash_error = None
 if request.method == "POST":
  action = request.POST.get("action", "add").strip().lower()
  item_id = request.POST.get("item_id", "").strip().upper()
  if action == "toggle":
   item = ServiceItem.objects.filter(id=item_id).first()
   if item:
    item.available = not item.available
    item.save(update_fields=["available"])
    flash_success = f"{item.name} visibility updated."
    try:
     SUPABASE_SYNC.upsert_menu(section="Services", name=item.name, description=item.note, price=item.price, active=item.available)
    except SupabaseSyncError as exc:
      flash_error = str(exc)
   else:
    flash_error = f"{item_id} not found."
  elif action == "delete":
   item = ServiceItem.objects.filter(id=item_id).first()
   if item:
    item_name = item.name
    item.delete()
    flash_success = f"{item_name} deleted."
    try:
     SUPABASE_SYNC.delete_menu(section="Services", name=item_name)
    except SupabaseSyncError as exc:
      flash_error = str(exc)
   else:
    flash_error = f"{item_id} not found."
  else:
   name = request.POST.get("name", "").strip()
   category = request.POST.get("category", "").strip()
   price = _to_int(request.POST.get("price"), 0)
   note = request.POST.get("note", "").strip()
   if not item_id or not name or not category:
    flash_error = "Service ID, name and category are required."
   elif ServiceItem.objects.filter(id=item_id).exists():
    flash_error = f"{item_id} already exists."
   else:
    item = ServiceItem.objects.create(id=item_id, name=name, category=category, price=price, available=True, note=note)
    flash_success = f"{item.name} added."
    try:
     SUPABASE_SYNC.upsert_menu(section="Services", name=item.name, description=item.note, price=item.price, active=item.available)
    except SupabaseSyncError as exc:
      flash_error = str(exc)
 c = base("Services", "SMART HOTEL DEVICE", "Manage guest-facing hotel services and route requests to the correct department.")
 c.update(items=list(ServiceItem.objects.all()), categories=["All", "Housekeeping", "Reception", "Transport", "Maintenance", "Wellness"], flash_success=flash_success, flash_error=flash_error)
 return render(request, "dashboard/services.html", c)


@admin_required
def orders(request):
 c = base("Orders", "ORDERS", "Review guest orders by room or table, department, payment state and fulfilment status.")
 c.update(orders=ORDERS, metrics=[{"value": len(ORDERS), "label": "Total Orders"}, {"value": len([o for o in ORDERS if o["status"] == "Pending"]), "label": "Pending"}, {"value": len([o for o in ORDERS if o["status"] == "Preparing"]), "label": "Preparing"}, {"value": len([o for o in ORDERS if o["status"] == "Completed"]), "label": "Completed"}])
 return render(request, "dashboard/orders.html", c)


@admin_required
def payments(request):
 _seed_db_once()
 flash_success = None
 flash_error = None
 if request.method == "POST":
  action = request.POST.get("action", "").strip().lower()
  reference = request.POST.get("reference", "").strip().upper()
  payment = PaymentRecord.objects.filter(reference=reference).first()
  if action != "confirm":
   flash_error = "Unsupported payment action."
  elif not payment:
   flash_error = f"{reference} not found."
  elif payment.status == "Confirmed":
   flash_success = f"{payment.reference} is already confirmed."
  else:
   payment.status = "Confirmed"
   payment.save(update_fields=["status"])
   flash_success = f"{payment.reference} confirmed."
 all_payments = list(PaymentRecord.objects.all())
 confirmed = [p for p in all_payments if p.status == "Confirmed"]
 pending = [p for p in all_payments if p.status == "Pending Confirmation"]
 c = base("Payment Management", "ORDERS", "Track bank transfer payments via OPay and Access Bank. Confirm transfers once verified in your bank app.")
 c.update(payments=all_payments, bank_accounts=list(BankAccount.objects.filter(active=True)), metrics=[{"value": f"₦{sum(p.amount for p in confirmed):,}", "label": "Confirmed Revenue"}, {"value": f"₦{sum(p.amount for p in pending):,}", "label": "Awaiting Confirmation"}, {"value": len(pending), "label": "Pending Orders"}, {"value": f"₦{sum(p.amount for p in all_payments):,}", "label": "Total Today"}], flash_success=flash_success, flash_error=flash_error)
 return render(request, "dashboard/payments.html", c)


@admin_required
def workflow(request):
 c = base("Handler Workflow", "HANDLER WORKFLOW", "Standard operating flow from payment confirmation to service delivery.")
 c["steps"] = [("Payment Confirmed", "Order details enter the admin portal."), ("Department Assignment", "Kitchen, bar, housekeeping or reception receives the request."), ("Preparation", "Staff processes the request and updates its status."), ("Delivery / Completion", "The handler marks the order or request as completed.")]
 return render(request, "dashboard/workflow.html", c)


@admin_required
def tracking(request):
 c = base("Tracking Updates", "TRACKING UPDATES", "Monitor order movement and department responsibility.")
 c["orders"] = ORDERS
 return render(request, "dashboard/tracking.html", c)


@admin_required
def devices(request):
 _seed_db_once()
 all_devices = list(Device.objects.all())
 c = base("Device Management", "IOT DEVICE SYSTEM", "Monitor each IoT WiFi device, connection state, operating permission and heartbeat.")
 c.update(devices=all_devices, metrics=[{"value": len(all_devices), "label": "Total Devices"}, {"value": len([d for d in all_devices if d.wifi]), "label": "WiFi Connected"}, {"value": len([d for d in all_devices if d.active]), "label": "Active Devices"}, {"value": len([d for d in all_devices if not d.online]), "label": "Offline / Faulty"}])
 return render(request, "dashboard/devices.html", c)


@admin_required
def staff(request):
 c = base("Staff Access", "STAFF ACCESS", "Manage hotel staff roles and future access permissions.")
 c["staff_members"] = STAFF
 return render(request, "dashboard/staff.html", c)


@admin_required
def web_qr_operation(request):
 _seed_db_once()
 add_success = None
 add_error = None
 highlighted_room_id = None
 if request.method == "POST":
  action = request.POST.get("action", "add").strip().lower()
  if action == "delete":
   device_id = request.POST.get("device_id", "").strip().upper()
   deleted, _ = Device.objects.filter(id=device_id).delete()
   if deleted:
    add_success = f"{device_id} deleted."
   else:
    add_error = f"{device_id} not found."
  elif action == "edit":
   original_id = request.POST.get("original_device_id", "").strip().upper()
   device_id = request.POST.get("device_id", "").strip().upper()
   location = request.POST.get("location", "").strip()
   device_type = request.POST.get("device_type", "").strip()
   active = request.POST.get("active", "off") == "on"
   if not original_id or not device_id or not location or not device_type:
    add_error = "Device ID, location and type are required for edit."
   elif original_id != device_id and Device.objects.filter(id=device_id).exists():
    add_error = f"{device_id} already exists."
   else:
    target = Device.objects.filter(id=original_id).first()
    if not target:
      add_error = f"{original_id} not found."
    else:
      target.id = device_id
      target.location = location
      target.type = device_type
      target.wifi_ssid = _network_for(device_type)
      target.active = active
      target.last_seen = "just now"
      target.save()
      highlighted_room_id = target.id
      add_success = f"{location} ({device_id}) updated."
  else:
   device_id = request.POST.get("device_id", "").strip().upper()
   location = request.POST.get("location", "").strip()
   device_type = request.POST.get("device_type", "").strip()
   if not device_id or not location or not device_type:
    add_error = "Device ID, location and type are required."
   elif Device.objects.filter(id=device_id).exists():
    add_error = f"{device_id} already exists."
   else:
    Device.objects.create(id=device_id, location=location, type=device_type, wifi_ssid=_network_for(device_type), ip=_next_ip(), wifi=True, online=True, active=True, last_seen="just now")
    highlighted_room_id = device_id
    add_success = f"{location} ({device_id}) added. QR is ready."

 rooms = list(Device.objects.all())
 active = [r for r in rooms if r.active]
 featured_room = Device.objects.filter(id=highlighted_room_id).first() if highlighted_room_id else (rooms[0] if rooms else None)
 c = base("Web QR Operation", "WEB QR OPERATION", "Each room has a unique QR code that links guests directly to the web device page - where they can browse menus, order, and pay.")
 c.update(rooms=rooms, featured_room=featured_room, add_success=add_success, add_error=add_error, metrics=[{"value": len(rooms), "label": "Total Rooms"}, {"value": len(active), "label": "Active Rooms"}, {"value": len([r for r in rooms if r.online]), "label": "Online Now"}, {"value": len([r for r in rooms if not r.active]), "label": "QR Disabled"}])
 return render(request, "dashboard/web_qr_operation.html", c)


@admin_required
def guest_preview(request):
 _seed_db_once()
 requested_room_id = request.GET.get('device_id', '').strip().upper()
 if requested_room_id:
  selected_room = Device.objects.filter(id=requested_room_id).first()
  if selected_room:
   return redirect(f"/guest/{selected_room.id}/")
 preferred_room = Device.objects.filter(id='DEV-001').first()
 if preferred_room:
  return redirect('/guest/DEV-001/')
 room = Device.objects.filter(active=True).order_by('id').first() or Device.objects.order_by('id').first()
 if room:
  return redirect(f"/guest/{room.id}/")
 return redirect('/web-qr-operation/')


def qr_code(request, room_id):
 _seed_db_once()
 if not Device.objects.filter(id=room_id).exists():
  return HttpResponse("Device not found", status=404)
 guest_url = request.build_absolute_uri(f"/guest/{room_id}/")
 img = qrcode.make(guest_url)
 buf = io.BytesIO()
 img.save(buf, "PNG")
 buf.seek(0)
 return HttpResponse(buf.read(), content_type="image/png")


def guest_device(request, room_id):
 _seed_db_once()
 room = Device.objects.filter(id=room_id).first()
 submission_error = None
 submitted_reference = request.GET.get("ref", "").strip()
 submitted_payment = PaymentRecord.objects.filter(reference=submitted_reference).first() if submitted_reference else None
 if request.method == "POST":
  action = request.POST.get("action", "").strip().lower()
  if action != "submit_transfer":
   submission_error = "Unsupported guest payment action."
  else:
   amount = _to_int(request.POST.get("amount"), 0)
   method = request.POST.get("method", "").strip()
   account = request.POST.get("account", "").strip()
   raw_reference = request.POST.get("reference", "").strip().upper()
   if amount <= 0:
    submission_error = "Select at least one item before submitting transfer."
   elif not method or not account or not raw_reference:
    submission_error = "Payment details are missing. Please reselect a bank and try again."
   else:
    reference = _unique_reference(raw_reference)
    PaymentRecord.objects.create(
     reference=reference,
     order=f"ORD-WEB-{timezone.localtime().strftime('%H%M%S')}",
     customer=room.location if room else room_id,
     amount=amount,
     method=method,
     account=account,
     status="Pending Confirmation",
     date=timezone.localtime().strftime("%b %d, %H:%M"),
    )
    return redirect(f"{request.path}?submitted=1&ref={quote_plus(reference)}")
 kitchen_items = list(MenuItem.objects.filter(section="Kitchen", available=True))
 bar_items = list(MenuItem.objects.filter(section="Bar", available=True))
 available_services = list(ServiceItem.objects.filter(available=True))
 available_menu = kitchen_items + bar_items
 popular_items = (kitchen_items[:2] + bar_items[:1] + available_services[:1])[:3]
 featured_item = kitchen_items[0] if kitchen_items else (bar_items[0] if bar_items else (available_services[0] if available_services else None))
 initial_page = "homePage"
 if submitted_payment:
  initial_page = "successPage" if submitted_payment.status == "Confirmed" else "waitingPage"
 c = {
  "page_title": f"{room.location if room else room_id} - Guest Device",
  "room": room,
  "room_id": room_id,
  "menu_items": available_menu,
  "kitchen_items": kitchen_items,
  "bar_items": bar_items,
  "services": available_services,
  "popular_items": popular_items,
  "featured_item": featured_item,
  "bank_accounts": list(BankAccount.objects.filter(active=True)),
  "payment_submitted": request.GET.get("submitted") == "1",
  "submitted_reference": submitted_reference,
  "submitted_payment": submitted_payment,
  "submission_error": submission_error,
  "initial_page": initial_page,
 }
 return render(request, "dashboard/guest_device.html", c)

def web_qr_sync_bootstrap(request):
 _seed_db_once()
 payload = {
  "devices": list(Device.objects.values("id", "location", "type", "wifi_ssid", "ip", "wifi", "online", "active", "last_seen")),
  "menu_items": list(MenuItem.objects.filter(available=True).values("id", "section", "name", "category", "price", "description")),
  "services": list(ServiceItem.objects.filter(available=True).values("id", "name", "category", "price", "note")),
  "bank_accounts": list(BankAccount.objects.filter(active=True).values("bank", "name", "number", "icon", "bg", "fg")),
 }
 return JsonResponse(payload)


@admin_required
def settings_page(request):
 _seed_db_once()
 return render(request, "dashboard/settings.html", {**base("Settings", "SYSTEM SETTINGS", "Configure hotel identity, bank accounts for guest payments, and IoT operating rules."), "bank_accounts": list(BankAccount.objects.filter(active=True))})
