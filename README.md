# 🏘️ RentMaster — Django Property Management System

A complete backend property management system built with Django for landlords to manage properties, tenants, rent payments, and more.

---

## 🚀 Quick Start (Step-by-Step)

### 1. Prerequisites
Make sure you have Python 3.10+ installed:
```bash
python --version
```

### 2. Clone / Extract the Project
Place the project folder anywhere, e.g. `~/rentmaster/`

### 3. Create a Virtual Environment
```bash
python -m venv venv

# Activate it:
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install django pillow reportlab
```

### 5. Apply Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Your Admin (Landlord) Account
```bash
python manage.py createsuperuser
```
Follow the prompts to set username, email, and password.

### 7. Create Static Files Directory
```bash
mkdir -p static/css static/js media
```

### 8. Run the Development Server
```bash
python manage.py runserver
```

Then open your browser to: **http://127.0.0.1:8000/**

---

## 📁 Project Structure

```
rentmaster/
├── manage.py
├── db.sqlite3              ← Database (auto-created after migrate)
├── rentmaster/             ← Project settings
│   ├── settings.py
│   └── urls.py
├── core/                   ← Main app
│   ├── models.py           ← All database models
│   ├── views.py            ← All views/logic
│   ├── forms.py            ← All forms
│   ├── urls.py             ← URL routing
│   └── admin.py            ← Django admin config
├── templates/
│   └── core/               ← All HTML templates
│       ├── base.html       ← Sidebar layout
│       ├── dashboard.html
│       ├── properties/
│       ├── units/
│       ├── tenants/
│       ├── payments/
│       ├── announcements/
│       ├── maintenance/
│       ├── agreements/
│       └── auth/
└── static/
    └── css/
        └── main.css        ← All styles
```

---

## 🗄️ Database Models

| Model | Purpose |
|-------|---------|
| `User` | Django built-in — each user is a landlord |
| `Property` | A building (e.g. Green Apartments) |
| `Unit` | A room/apartment within a property |
| `Tenant` | A tenant assigned to a unit |
| `Payment` | A rent payment with auto status |
| `Announcement` | Notices sent to tenants |
| `MaintenanceRequest` | Issues reported + tracking |
| `LeaseEvent` | Move-in / move-out history |
| `Agreement` | Documents (terms, rental agreements) |

---

## 🔗 Key URLs

| URL | Page |
|-----|------|
| `/` | Redirects to Dashboard |
| `/login/` | Login page |
| `/register/` | Register as landlord |
| `/dashboard/` | Main dashboard |
| `/properties/` | List all properties |
| `/tenants/` | List all tenants |
| `/payments/` | Payment records + filter |
| `/reports/` | Financial & occupancy reports |
| `/announcements/` | Create & view notices |
| `/maintenance/` | Track maintenance issues |
| `/agreements/` | Manage legal documents |
| `/legal/agreements/` | Public footer agreements page |
| `/admin/` | Django admin panel |

---

## 💡 Key Features

- ✅ Multi-property management
- ✅ Unit status tracking (Occupied / Vacant / Reserved / Maintenance)
- ✅ Tenant profiles with full history
- ✅ Rent payment tracking with auto status (Paid / Due / Late)
- ✅ M-Pesa transaction code support
- ✅ Printable receipts for every payment
- ✅ Dashboard with live KPIs
- ✅ Monthly financial reports with visual bars
- ✅ Announcement/notice system
- ✅ Maintenance request tracker
- ✅ Move-in / move-out tracking with lease events
- ✅ Agreement document management + public footer page
- ✅ Each landlord sees ONLY their own data

---

## 🔐 Security Notes

- Each landlord's data is isolated — landlords cannot see each other's data
- All views require login (`@login_required`)
- CSRF protection on all forms (built-in Django)
- **For production:** Change `SECRET_KEY` in `settings.py` and set `DEBUG = False`

---

## 📦 Phase 2 (Future Features)

After the MVP is working:
- SMS/Email notifications (Africa's Talking, SendGrid)
- M-Pesa Daraja API integration
- Tenant login portal
- Expense tracking
- Advanced analytics

---

## 🛠️ Demo Login

After running the server, if you used the demo seed script:
- **Username:** `admin`
- **Password:** `admin123`

> Change this immediately in production!
