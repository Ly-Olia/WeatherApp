# Weather Assistant

A FastAPI-based application that provides real-time weather data, allows users to manage favorite locations, and sends email alerts for severe weather conditions.

## Features

- **User Authentication**: Register, login, logout, and change password functionality.
- **Current Weather**: Fetch real-time weather details by city.
- **Favorites Management**: Add/remove favorite locations.
- **Severe Weather Monitoring**: Automatically checks and notifies users by emails of extreme weather events in their favorite locations.


## Technologies Used

- **Backend**: FastAPI
- **Database**: SQLAlchemy (SQLite)
- **Templates**: Jinja2
- **Authentication**: OAuth2 (JWT Tokens)
- **Email Alerts**: SMTP server integration
- **Weather API**: OpenWeatherMap
- 
## Project Structure

WeatherApp/
│
├── app/
│   ├── __init__.py
│   ├── confid.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── database.py
│   ├── email_utils.py
│   ├── utils.py
│   └── routers/
│       ├── __init__.py
│       ├── auth.py
│       ├── users.py
│       └── weather.py
│
├── templates/
│   ├── login.html
│   ├── layout.html
│   ├── main_page.html
│   ├── navbar.html
│   ├── register.html
│   ├── weather_details.html
│   └── change-password.html
│ 
├── templates/
│   ├── login.html
│   ├── layout.html
│   ├── main_page.html
│   ├── navbar.html
│   ├── register.html
│   ├── weather_details.html
│   └── change-password.html
│
├── requirements.txt
├── env.py
├── .gitignore
└── README.md

## Installation

### Prerequisites

- Python 3.10+
- FastAPI
- SQLAlchemy
- OpenWeatherMap API Key
- SMTP credentials for email functionality

### Setup

1. **Clone the repository**:
   ```bash
   https://github.com/Ly-Olia/HabitsApp
   ```
2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   # On Windows use
   venv\Scripts\activate
   ```
3. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Set environment variables** (e.g., OpenWeatherMap API key, SMTP settings) in `.env`.
5.  **Set up the database**:

- Make sure PostgreSQL is running.
- Create a new database for the app.
- Configure the database URL in the `.env` file.


5. **Apply migrations**:
   ```bash
   alembic upgrade head
   ```

7. **Run the application**:
- Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```
- Access the app at `http://127.0.0.1:8000`.











   
