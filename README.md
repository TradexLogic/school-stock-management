# 🏫 School Stock Management System

<div align="center">

![Login Page]<img width="958" height="437" alt="login page" src="https://github.com/user-attachments/assets/22e427b1-af47-44e3-8f98-c32df3a4c4a9" />


**A professional, role-based inventory management system built with Django**
*Designed specifically for schools and educational institutions*

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.x-green.svg)](https://djangoproject.com)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 📌 Overview

The **School Stock Management System** is a comprehensive web-based inventory platform that helps schools manage books, stationery, and other items across **multiple campuses** — with **role-based access control**, **vendor tracking**, **voucher generation**, and **detailed reporting**.

---

## 📸 Screenshots

### 🖥️ Super Admin Dashboard
![Super Admin Dashboard]<img width="949" height="437" alt="dashoard page" src="https://github.com/user-attachments/assets/f7d6e579-7c25-4409-9364-38477a472cf8" />

### 📊 Dashboard — Recent Transactions & Campus Overview
![Dashboard Transactions]<img width="947" height="438" alt="dashboard page 2" src="https://github.com/user-attachments/assets/f8103d05-2976-4973-8531-81e12bca7d4b" />

### 📦 Inventory Overview
![Inventory]<img width="958" height="437" alt="inventory page" src="https://github.com/user-attachments/assets/ce01a044-e8f3-46df-8aef-f0ed6d76eccf" />

### 🏫 Campus Stock Dashboard
![Campus Stock]<img width="947" height="435" alt="campus stock page" src="https://github.com/user-attachments/assets/9f258baf-1ad6-4b48-8685-877c7b627117" />


### 📋 Reports & Analytics
![Reports]<img width="947" height="436" alt="report page" src="https://github.com/user-attachments/assets/ccb98414-ff61-4a1b-9589-fc090abf7195" />

---

## ✨ Features

### 🔐 Role-Based Access Control
- **Super Admin (Head Office)** — Full system control
- **Campus Admin** — Campus-specific inventory management only
- Buying price **completely hidden** from Campus Admins
- Selling price visible to Campus Admins for sales operations
- Product & category creation restricted to Super Admin only

### 🏫 Multi-Campus Support
- Separate personalized dashboard for each campus
- Campus-wise stock overview in a single searchable table
- Search any product across **all campuses simultaneously**
- Campus transaction history with date filtering
- Campus-specific Stock IN and Stock OUT operations

### 📦 Inventory Management
- Full product lifecycle — Create, Edit, Delete, View
- Category-based organization (Books, Khata, Diary, Stationery, etc.)
- Opening stock tracking for accurate reporting
- **Automatic low stock alerts** with configurable threshold
- Real-time stock quantity updates on every transaction
- Product-wise complete transaction history

### 🎫 Voucher System
- **Auto-generated unique voucher numbers** for every transaction
- Format: `SIN-XXXX-XXXXXX` (Stock IN) and `SOUT-XXXX-XXXXXX` (Stock OUT)
- Printable vouchers for every Stock IN and Stock OUT operation
- Full voucher history for audit purposes

### 🏪 Vendor Management
- Complete vendor profiles with mobile number and address
- Bank account details storage for payment tracking
- Vendor-wise purchase history and total transaction amounts
- Vendor selection **mandatory** for all Stock IN operations

### 📊 Reports & Analytics
- **Opening Stock Report** — Category-wise filtering
- **Stock IN Report** — Vendor and date range filtering
- **Stock OUT Report** — Product and date filtering
- **Vendor Purchase Report** — Complete transaction history per vendor
- **Campus Transaction Report** — Filter by campus, type, and date
- **Campus Stock Dashboard** — All campuses in one searchable view
- **PDF Export** via browser print
- **Excel/CSV Download** with one click

### 📋 Activity Logging
- All Super Admin and Campus Admin actions are logged
- Timestamped activity trail for security and audit
- Role-based activity identification

### 🖨️ PDF & Excel Export
- Inventory list downloadable as **CSV (Excel)**
- Any report page **printable as PDF**
- Vouchers are **individually printable**

---

## 🛠️ Tech Stack

| Technology | Version | Purpose |
|---|---|---|
| **Django** | 5.x | Backend Web Framework |
| **Python** | 3.11+ | Programming Language |
| **SQLite** | Built-in | Database (zero setup) |
| **Bootstrap** | 5.3 | Frontend UI Framework |
| **Bootstrap Icons** | 1.11 | Icon Library |

---

## 👥 User Roles & Permissions

### ✅ Super Admin (Head Office)

| Feature | Access |
|---|---|
| Product Management | ✅ Full |
| Category Management | ✅ Full |
| Vendor Management | ✅ Full |
| Campus Management | ✅ Full |
| Stock IN / OUT | ✅ Full with Voucher |
| Buying Price | ✅ Visible |
| Selling Price | ✅ Visible |
| Profit Margin | ✅ Visible |
| All Reports | ✅ Full with Export |
| Campus Stock Dashboard | ✅ All Campuses |
| Campus Transactions | ✅ All Campuses |
| Activity Log | ✅ Full |
| Django Admin Panel | ✅ Full |

### ✅ Campus Admin

| Feature | Access |
|---|---|
| Campus Stock IN | ✅ Own Campus Only |
| Campus Stock OUT | ✅ Own Campus Only |
| Campus Inventory View | ✅ Own Campus Only |
| Transaction Report | ✅ Own Campus Only |
| Buying Price | ❌ Hidden |
| Selling Price | ✅ Visible |
| Product Creation | ❌ Not Allowed |
| Category Creation | ❌ Not Allowed |
| Vendor Management | ❌ Not Allowed |
| Other Campus Data | ❌ Not Allowed |

---

## 🗄️ Database Models

| Model | Description |
|---|---|
| `Category` | Product categories (Books, Khata, etc.) |
| `Product` | Products with buying & selling prices |
| `Vendor` | Supplier profiles with bank details |
| `Campus` | School branches with assigned admins |
| `StockLog` | Head office stock transactions with vouchers |
| `CampusInventory` | Per-campus real-time stock levels |
| `CampusStockLog` | Campus IN/OUT transaction history |
| `ActivityLog` | Complete user activity audit trail |

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.11+
- pip
- Git

### Step 1 — Clone the Repository

```bash
git clone https://github.com/TradexLogic/school-stock-management.git
cd school-stock-management
```

### Step 2 — Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5 — Create Super Admin Account

```bash
python manage.py createsuperuser
```

### Step 6 — Start Development Server

```bash
python manage.py runserver
```

### Step 7 — Open in Browser

```
http://127.0.0.1:8000/
```

---

## ⚙️ First-Time Setup Guide

### As Super Admin:
1. Login with your superuser credentials
2. Go to **Categories** → Create product categories
3. Go to **Vendors** → Add your suppliers
4. Go to **Products** → Add products with pricing
5. Go to **Admin Panel** → Create Campus Admin user accounts
6. Go to **Campuses** → Create campuses and assign admin users
7. Use **Stock IN** to receive inventory from vendors

### As Campus Admin:
1. Login with your campus admin credentials
2. View your campus dashboard
3. Use **Stock IN** to update product quantities
4. Use **Stock OUT** to record items issued to students/guardians
5. View **Transaction Report** for complete history

---

## 📁 Project Structure

```
school-stock-management/
│
├── school_stock/           # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── inventory/              # Main application
│   ├── models.py           # Database models
│   ├── views.py            # Business logic
│   ├── urls.py             # URL routing
│   ├── forms.py            # Form definitions
│   ├── admin.py            # Admin configuration
│   └── templates/
│       └── inventory/      # 20+ HTML templates
│
├── screenshots/            # App screenshots
├── manage.py
└── requirements.txt
```

---

## 🔒 Security Features

- All pages require authentication — no public access
- Role-based access control enforced on every view
- Buying price completely hidden from Campus Admins
- CSRF protection on all forms
- Activity logging for complete audit trail
- Campus Admins can only access their own campus data
- Negative stock prevention on all OUT operations

---

## 🎯 Ideal Use Cases

| Organization | How It Helps |
|---|---|
| Multi-branch Schools | Centralized purchasing with branch-level distribution |
| Educational Institutions | Complete stationery and book inventory management |
| Single Campus Schools | Full inventory with vendor and voucher management |
| NGO Education Programs | Transparent distribution tracking with audit logs |

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 👨‍💻 Developer

Built with ❤️ for **Dar-ul-Madinah** and all educational institutions.

*Making school inventory simple, organized, and transparent.*
