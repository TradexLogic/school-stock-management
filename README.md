# school-stock-management
A Django-based role-based stock management system for schools

School Stock Management System
A Professional Django-Based Inventory Solution
for Educational Institutions
Django 5.x  |  SQLite  |  Bootstrap 5  |  Python 3.11+


Project Overview
The School Stock Management System is a comprehensive, web-based inventory management platform built with Django. It is specifically designed for schools and educational institutions that manage books, stationery, uniforms, and other inventory items across single or multiple campuses.

This system solves a real-world problem faced by school administrators: managing stock distribution across branches while keeping financial data confidential from branch-level staff.

Why This Project Matters
•	Schools often manage hundreds of products across multiple branches without a proper tracking system
•	Manual stock management leads to errors, losses, and inefficiencies
•	Financial data (buying prices, profit margins) must remain confidential from branch admins
•	Head offices need real-time visibility into every campus's inventory
•	Guardian and student transactions need to be properly recorded and traceable
•	Vendors and purchase history must be systematically maintained

Key Features
Role-Based Access Control
•	Super Admin (Head Office) has complete system control
•	Campus Admin manages only their assigned campus inventory
•	Buying prices are fully hidden from Campus Admins
•	Selling prices are visible to Campus Admins for sales operations
•	Product and category creation is restricted to Super Admin only

Multi-Campus Support
•	Separate dashboard for each campus with real-time data
•	Campus-wise stock overview in a single searchable table
•	Product search across all campuses simultaneously
•	Campus transaction history with date filtering
•	Campus-specific Stock IN and Stock OUT operations

Inventory Management
•	Full product lifecycle management with categories
•	Opening stock tracking for accurate reporting
•	Automatic low stock alerts with configurable threshold
•	Real-time stock quantity updates on every transaction
•	Product-wise transaction history

Voucher System
•	Auto-generated unique voucher numbers for every transaction
•	Printable vouchers for Stock IN and Stock OUT operations
•	Voucher lookup and history for audit purposes
•	Format: SIN-XXXX-XXXXXX (IN) and SOUT-XXXX-XXXXXX (OUT)

Vendor Management
•	Complete vendor profiles with mobile number and address
•	Bank account details storage for payment tracking
•	Vendor-wise purchase history and total transaction amounts
•	Vendor selection is mandatory for all Stock IN operations

Reports & Analytics
•	Opening Stock Report with category-wise filtering
•	Stock IN Report with vendor and date range filtering
•	Stock OUT Report with product and date filtering
•	Vendor Purchase Report with detailed transaction history
•	Campus Transaction Report (filterable by campus, type, and date)
•	Campus Stock Dashboard showing all campuses in one view
•	PDF export via browser print and Excel/CSV download

Activity Logging
•	All Super Admin and Campus Admin actions are logged
•	Timestamped activity trail for security and audit
•	Role-based activity identification


Technology Stack

Technology	Version	Purpose
Django	5.x	Backend Web Framework
Python	3.11+	Programming Language
SQLite	Built-in	Database (no setup required)
Bootstrap	5.3	Frontend UI Framework
Bootstrap Icons	1.11	Icon Library
HTML5 / CSS3	Latest	Templates & Styling


User Roles & Permissions

Super Admin (Head Office)

Feature	Access Level
Product Management	Full — Create, Edit, Delete, View
Category Management	Full — Create, Edit, Delete, View
Vendor Management	Full — Create, Edit, Delete, View
Campus Management	Full — Create, Edit, Assign Admins
Stock IN (Head Office)	Full with Voucher Generation
Stock OUT (Head Office)	Full with Voucher Generation
Buying Price	Visible
Selling Price	Visible
Profit Margin	Visible
All Reports	Full Access with Export
Campus Stock Dashboard	Full View — All Campuses
Campus Transactions	Full View — All Campuses
Activity Log	Full Access
Django Admin Panel	Full Access

Campus Admin

Feature	Access Level
Campus Stock IN	Own Campus Only
Campus Stock OUT	Own Campus Only
Campus Inventory View	Own Campus Only
Transaction Report	Own Campus Only
Buying Price	Hidden — Not Visible
Selling Price	Visible for Sales Operations
Product Creation	Not Allowed
Category Creation	Not Allowed
Vendor Management	Not Allowed
Head Office Stock	Not Allowed
Other Campus Data	Not Allowed


Database Models

Model	Description	Key Fields
Category	Product categories	name, description
Product	All products with pricing	name, category, purchase_price, selling_price, quantity
Vendor	Supplier information	name, mobile, address, bank_account
Campus	School branches	name, address, admin (OneToOne User)
StockLog	Head office transactions	product, type, quantity, vendor, voucher_number
CampusInventory	Per-campus stock levels	campus, product, quantity
CampusStockLog	Campus transaction history	campus, product, type, quantity, note
ActivityLog	User activity tracking	user, action, created_at


Installation & Setup
Prerequisites
•	Python 3.11 or higher installed
•	pip (Python package manager)
•	Git
•	A terminal or command prompt

Step-by-Step Installation

Step 1 — Clone the Repository
git clone https://github.com/your-username/school-stock.git
cd school-stock

Step 2 — Create Virtual Environment
On Windows:
python -m venv venv
venv\Scripts\activate

On Linux / Mac:
python3 -m venv venv
source venv/bin/activate

Step 3 — Install Dependencies
pip install -r requirements.txt

Step 4 — Run Database Migrations
python manage.py makemigrations
python manage.py migrate

Step 5 — Create Super Admin Account
python manage.py createsuperuser
Enter your desired username, email, and password when prompted.

Step 6 — Start the Development Server
python manage.py runserver

Step 7 — Access the System
http://127.0.0.1:8000/


First-Time Setup Guide
Setting Up as Super Admin
1.	Login with your superuser credentials at the main URL
2.	Go to Categories and create product categories (e.g., Books, Khata, Diary, Stationery)
3.	Go to Vendors and add your suppliers with their details
4.	Go to Products and add all products with buying and selling prices
5.	Go to Admin Panel and create User accounts for each Campus Admin
6.	Go to Campuses and create each campus, assigning the correct User as Campus Admin
7.	Use Stock IN to receive inventory from vendors with voucher generation

Campus Admin Operations
8.	Login with your campus admin credentials
9.	View your campus dashboard showing current inventory
10.	Use Stock IN to update product quantities received at your campus
11.	Use Stock OUT to record products issued to guardians or students
12.	View Transaction Report to see complete history of your campus operations


Project Structure

school_stock_system/
|-- school_stock/           # Main Django project
|   |-- settings.py         # Configuration
|   |-- urls.py             # Root URL routing
|   `-- wsgi.py             # WSGI entry point
|
|-- inventory/              # Main application
|   |-- models.py           # All database models
|   |-- views.py            # Business logic & views
|   |-- urls.py             # URL patterns
|   |-- forms.py            # Form definitions
|   |-- admin.py            # Admin panel config
|   `-- templates/          # HTML templates
|       `-- inventory/
|           |-- base.html
|           |-- dashboard_super.html
|           |-- dashboard_campus.html
|           |-- campus_stock_dashboard.html
|           |-- voucher_detail.html
|           `-- ... (20+ templates)
|
|-- manage.py
`-- requirements.txt


Security Features
•	All pages require authentication — no public access
•	Role-based access control enforced on every view function
•	Buying price completely hidden from Campus Admin role
•	CSRF protection on all forms
•	Activity logging for complete audit trail
•	Campus Admins can only access their own campus data
•	Negative stock prevention — Stock OUT validates available quantity


Ideal Use Cases

Organization Type	How It Helps
Multi-branch Schools	Centralized purchasing with branch-level distribution tracking
Educational Institutions	Complete stationery and book inventory management
Single Campus Schools	Full inventory with vendor and voucher management
NGO Education Programs	Transparent distribution tracking with audit logs


requirements.txt

Django>=5.0
Pillow>=10.0.0


License
This project is open source and available under the MIT License. You are free to use, modify, and distribute it for personal or commercial purposes.


Built with love for educational institutions
School Stock Management System — Making inventory simple, organized, and transparent.
