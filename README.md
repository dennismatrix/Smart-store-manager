# 🛒 Smart Store Manager

![Django](https://img.shields.io/badge/Django-Framework-green)
![License](https://img.shields.io/badge/License-MIT-blue)
![Status](https://img.shields.io/badge/Status-Active-success)

Smart Store Manager is a modern, web-based stock and sales management system built with Django. It helps retail businesses track inventory, manage sales, and analyze performance with an intuitive dashboard.

## 🚀 Features

- Product catalog management
- Stock tracking and alerts
- Sales recording and analytics
- User roles & permissions (admin, staff)
- Responsive UI for desktop & mobile
- Easy reporting and data export (CSV/Excel)
- Secure authentication system

## 🏁 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/dennismatrix/Smart-store-manager.git
cd Smart-store-manager
```

### 2. Set up a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Create a superuser (admin account)

```bash
python manage.py createsuperuser
```

### 6. Start the development server

```bash
python manage.py runserver
```

Access the app at [http://localhost:8000](http://localhost:8000).

---

## 📦 Technologies Used

- Django & Django REST Framework
- HTML5, CSS3, JavaScript
- Bootstrap (UI)
- SQLite (default, easily switchable to PostgreSQL/MySQL)
- Chart.js (analytics & charts)

## 💡 Usage

- Log in as admin to manage products, view sales, and generate reports.
- Staff users can record sales and update stock.
- Customize roles and permissions through the admin panel.

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

---

> Made with ❤️ by [dennismatrix](https://github.com/dennismatrix)
