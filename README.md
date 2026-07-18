# HAIDWARE Smart Hotel Admin Portal

HAIDWARE hospitality admin portal built with Django for managing rooms, QR access, guest ordering, payments, and service operations.

## Current features

- Admin entry, signup, login, and logout flow
- Session-protected dashboard pages
- Kitchen, bar, services, orders, payments, staff, tracking, workflow, and device pages
- Guest-facing room and table pages with payment flow
- Web QR management with QR preview, download, edit, and delete controls
- Database-backed menu, services, devices, bank accounts, admin accounts, and payment records

## Main routes

- `/` - Admin entry page
- `/admin-login/` - Admin login
- `/admin-signup/` - Admin signup
- `/dashboard/` - Main admin dashboard
- `/devices/` - Device management
- `/payments/` - Payment management
- `/web-qr-operation/` - Web QR operations

## Run locally

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Or use:

```powershell
run_windows.bat
```

Open `http://127.0.0.1:8000/` after the server starts.

## Deployment note

For Render deployment, run migrations before starting Gunicorn so the latest models and admin auth flow are available.
