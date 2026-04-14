
# REPOSITORY UNDER CONSTRUCTIONS !!!!!!!

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square)
![Django](https://img.shields.io/badge/Django-5.x-green?style=flat-square)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow?style=flat-square)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?style=flat-square)
![Linux](https://img.shields.io/badge/Linux-Ubuntu-orange?style=flat-square)
![Nginx](https://img.shields.io/badge/Nginx-Production-green?style=flat-square)

# QR Menu System (SaaS Platform)

## Short Introduction

QR Menu System is a **multi-business SaaS platform** designed to help restaurants, cafes, KTVs, and small food businesses **digitize their menus using QR codes**.

Customers simply scan a QR code and instantly view the menu on their phone — while business owners can **manage products, categories, and availability in real-time** without reprinting menus.

This system is built with scalability in mind, evolving into a **full digital ordering and restaurant management platform**.

---

## Core Features

### 🔹 Landing Page (Marketing)
- High-converting B2B landing page
- Designed to attract restaurant and cafe owners
- Lead capture ready

### 🔹 Customer QR Menu
- Mobile-first interface
- Fast loading (optimized for low-end devices)
- Category-based browsing
- Product images, prices, availability

Access format:
```

/m/<code>

```

Example:
```

/m/table-1
/m/ktv-room-2

```

### 🔹 System Owner Admin Panel
- Register and manage businesses
- Control:
  - Categories
  - Products
  - QR locations
- Multi-business support

### 🔹 Business Owner Dashboard (Client Self-Service)
- Manage own menu
- CRUD:
  - Categories
  - Products
  - QR locations
- Menu preview
- Business profile management
- Strict data isolation

---

## Technologies Used

- **Backend:** Python, Django
- **Frontend:** HTML, CSS, JavaScript
- **Database:** PostgreSQL
- **Deployment:** Ubuntu, Nginx, Gunicorn
- **Architecture:** Multi-tenant (business isolation)

---

## System Architecture

```

Landing Page
↓
QR Menu (/m/<code>)
↓
-

| Django Backend |
| -------------- |
| Businesses     |
| Categories     |
| Products       |
| QR Locations   |

---

```
 ↓
```

Admin Panel (Owner)
↓
Business Dashboard

````

---

## Build Process

1. **Market Validation**
   - Identified need for digital menus
   - Focused on reducing printing costs

2. **Landing Page**
   - Built for lead generation

3. **Customer Menu**
   - Mobile-first UI
   - Optimized performance

4. **Admin Panel**
   - Multi-business onboarding

5. **Client Dashboard**
   - Self-service menu control

6. **Scalable Design**
   - SaaS-ready architecture

---

## Key Learnings

- Multi-tenant SaaS architecture
- Business-level data isolation
- Mobile-first UI design
- Conversion-focused product thinking
- Balancing simplicity vs scalability

---

## Future Improvements

- QR Ordering System (Phase 2)
- Real-time order dashboard
- Analytics (top products, scans)
- Subscription & billing
- Multi-branch support
- AI recommendations

---

## Running the Project

Clone:
```bash
git clone https://github.com/AnsonGit-MakieTech/ansonqr.git
cd ansonqr
````

Setup environment:

```bash
python -m venv venv
source venv/bin/activate
```

Install:

```bash
pip install -r requirements.txt
```

Setup env:

```bash
cp .env.example .env
```

Migrate:

```bash
python manage.py makemigrations
python manage.py migrate
```

Create admin:

```bash
python manage.py createsuperuser
```

Run:

```bash
python manage.py runserver
```

Open:

```
http://127.0.0.1:8000
```

---

## Key URLs

```
Landing Page:
/

Customer Menu:
/m/<code>

Admin:
/admin

Dashboard:
/dashboard
```

---

## Future Vision

This project evolves into a:

**Restaurant Operating System (ROS)**

Including:

* QR ordering
* POS integration
* kitchen workflow
* analytics
* customer engagement
 
 