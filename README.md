# 🐾 Spy Cat Agency (SCA)

This is a small Django REST Framework project for managing **spy cats**, their **missions**, and **targets**.  
It was built as a test task to show understanding of CRUD APIs, database models, and external API integration.

---

## 🚀 What it does

- Manage spy cats (name, breed, experience, salary)
- Validate cat breeds using [TheCatAPI](https://api.thecatapi.com/v1/breeds)
- Create missions with 1–3 targets
- Assign one cat per mission
- Update notes on targets (until they’re marked complete)
- Automatically mark missions complete when all targets are done

---

## ⚙️ Setup

```bash
git clone https://github.com/<your-username>/spy-cat-agency.git
cd spy-cat-agency
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

API runs at:  
👉 http://127.0.0.1:8000/api/

---

## 🧩 Main Endpoints

### 🐱 Cats
```
POST   /api/cats/              - create a cat
GET    /api/cats/              - list cats
GET    /api/cats/<id>/         - get cat
PATCH  /api/cats/<id>/         - update salary
DELETE /api/cats/<id>/         - remove cat
```

### 🎯 Missions
```
POST   /api/missions/          - create mission with targets
GET    /api/missions/          - list missions
GET    /api/missions/<id>/     - get mission
PATCH  /api/missions/<id>/     - update mission/targets
POST   /api/missions/<id>/assign-cat/  - assign a cat
DELETE /api/missions/<id>/     - delete (if unassigned)
```

---

## 🧪 Example

Create a mission:
```json
{
  "targets": [
    {"name": "Doggo", "country": "France", "notes": "Suspicious", "complete": false}
  ]
}
```

Assign a cat:
```json
POST /api/missions/5/assign-cat/
{
  "cat_id": 2
}
```

---

## 🧰 Notes

- A cat can only have **one active mission**.
- A mission must have **1–3 targets**.
- Notes freeze when a target or mission is marked complete.
- Deleting an assigned mission isn’t allowed.

---

## 🧾 About

Built using Django + DRF.  
Database: SQLite (you can switch to Postgres).  

