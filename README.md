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

### Supabase as primary database

To store admin login, devices, menu, services, and payment confirmations in Supabase, set `DATABASE_URL` to your Supabase Postgres connection string in Render environment variables.

Example format:

`postgresql://postgres:<password>@db.<project-ref>.supabase.co:5432/postgres?sslmode=require`

After setting `DATABASE_URL`, redeploy so Django migrates tables into Supabase.

### GitHub-driven deployment with Supabase

This repository now includes `.github/workflows/render-deploy.yml`:

- Runs `python manage.py check` on push to `main`
- Triggers Render deploy via deploy hook after validation

Add this GitHub repository secret:

- `RENDER_DEPLOY_HOOK_URL` = your Render service deploy hook URL

Also ensure these env vars are set in Render (for Supabase DB):

- `DATABASE_URL`
- `SUPABASE_URL`
- `SUPABASE_SYNC_ENABLED`
- `SUPABASE_SERVICE_ROLE_KEY`
