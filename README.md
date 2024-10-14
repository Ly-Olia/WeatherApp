# Weather Assistant

A FastAPI-based application that provides real-time weather data, allows users to manage favorite locations, and sends email alerts for severe weather conditions.

## Features

- **User Authentication**: Register, login, logout, and change password functionality.
- **Current Weather**: Fetch real-time weather details by city.
- **Favorites Management**: Add/remove favorite locations.
- **Severe Weather Monitoring**: Automatically checks and notifies users by emails of extreme weather events in their favorite locations.


## Technologies Used

- **Backend**: FastAPI
- **Database**: PostgreSQL, SQLAlchemy
- **Templates**: Jinja2
- **Authentication**: OAuth2 (JWT Tokens)
- **Password Hashing**: Passlib (bcrypt)
- **Email Alerts**: SMTP server integration
- **Weather API**: OpenWeatherMap
- **Frontend**: HTML, CSS, JavaScript
- **Migrations**: Alembic

  
## Project Structure

```plaintext
WeatherApp/
├── alembic/
│   ├── versions/
│   └── env.py
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
├── static/
│   ├── css/
│   │   ├── base.css
│   │   └── bootstrap.css
│   └── js/
│       ├── bootstrap.js
│       ├── jquery-slim.js
│       └── popper.js
│
├── requirements.txt
├── env.py
├── .gitignore
└── README.md
```
## Installation

### Prerequisites

- Python 3.10+
- FastAPI
- SQLAlchemy
- PostgreSQL
- OpenWeatherMap API Key
- SMTP credentials for email functionality
- Virtual Environment (optional but recommended)


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


## API Endpoints

### Weather Data
- `GET /weather/`: Render the main weather page with favorite cities.
- `GET /weather/current_weather`: Get current weather for a specific city.
- `POST /weather/favorite_city/`: Add a city to the user's favorite locations.
- `POST /weather/favorite_city/{city_name}/delete`: Remove a favorite city.
- `GET /weather/rain-forecast/{city}`: Get rain forecast for the specified city.

## Alerts
- `POST /weather/send-severe-weather-alert/`: Check for severe weather and send an alert via email.
- `POST /weather/toggle-auto-check`: Enable/disable auto-check of weather for alerts.
- `POST /weather/favorite_city/{city_id}/toggle_alert`: Toggle the alert flag for a favorite city.

### Authentication

 - `GET /auth`: Render the authentication (login) page.
 - `POST /auth`: Handle user login.
 - `POST /auth/token`: Obtain a token for a user.
 - `GET /auth/logout`: Logout the current user.
 - `GET /auth/register`: Render the registration page.
 - `POST /auth/register`: Register a new user.

### User Management

 - `GET /users/change-password`: Render the form to change user password.
 - `POST /users/change-password`: Handle the password change form submission.

## License

- This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.









   
