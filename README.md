A full-stack web application for browsing the Rwanda Penal Code (Law Nº68/2018 of 30/08/2018), built with Django and plain CSS.
Features

📖 Browse all 335 articles organized by Title and Chapter
🌍 Trilingual — switch between English, Français and Ikinyarwanda
🔍 Search across all articles by keyword
🎨 Clean, professional dark theme with Rwanda's colors

Tech Stack

Backend: Python 3.13, Django 6.0
Database: SQLite
Frontend: HTML, CSS (no frameworks)
PDF Parsing: pdfplumber

**Project Structure**
penal_code/
├── laws/                  # Main app
│   ├── models.py          # Title, Chapter, Article models
│   ├── views.py           # Page logic
│   ├── urls.py            # URL routing
│   ├── templates/laws/    # HTML templates
│   ├── static/laws/       # CSS and images
│   └── import_pdf.py      # PDF parser script
├── penal_code/            # Project settings
└── manage.py

**Setup & Installation**

bash# 1. Clone the repository
git clone https://github.com/yourusername/penal_code.git
cd penal_code

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install django pdfplumber

# 4. Run migrations
python manage.py migrate

# 5. Import articles (place articles.json on Desktop first)
python laws/import_pdf.py

# 6. Start the server
python manage.py runserver
**Then open http://127.0.0.1:8000/ in your browser**.

Data Source
Law Nº68/2018 of 30/08/2018 — Determining Offences and Penalties in General
Official Gazette no. Special of 27/09/2018
Republic of Rwanda
