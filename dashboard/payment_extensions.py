from urllib.parse import quote_plus

from django.shortcuts import redirect, render
from django.utils import timezone

from .models import BankAccount, MenuItem, PaymentRecord, ServiceItem, Device
from .views import _seed_db_once, _to_int, base


def _unique_reference(reference):
 ref = reference
 index = 1
 while PaymentRecord.objects.filter(reference=ref).exists():
  ref = f"{reference}-{index}"
  index += 1
 return ref


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
 c.update(
  payments=all_payments,
  bank_accounts=list(BankAccount.objects.filter(active=True)),
  metrics=[
   {"value": f"â‚¦{sum(p.amount for p in confirmed):,}", "label": "Confirmed Revenue"},
   {"value": f"â‚¦{sum(p.amount for p in pending):,}", "label": "Awaiting Confirmation"},
   {"value": len(pending), "label": "Pending Orders"},
   {"value": f"â‚¦{sum(p.amount for p in all_payments):,}", "label": "Total Today"},
  ],
  flash_success=flash_success,
  flash_error=flash_error,
 )
 return render(request, "dashboard/payments.html", c)


def guest_device(request, room_id):
 _seed_db_once()
 room = Device.objects.filter(id=room_id).first()
 submission_error = None
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
 available_menu = list(MenuItem.objects.filter(available=True))
 available_services = list(ServiceItem.objects.filter(available=True))
 c = {
  "page_title": f"{room.location if room else room_id} â€” Guest Device",
  "room": room,
  "room_id": room_id,
  "menu_items": available_menu,
  "services": available_services,
  "bank_accounts": list(BankAccount.objects.filter(active=True)),
  "payment_submitted": request.GET.get("submitted") == "1",
  "submitted_reference": request.GET.get("ref", "").strip(),
  "submission_error": submission_error,
 }
 return render(request, "dashboard/guest_device.html", c)
