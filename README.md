## Overview

This project is a Flask web application that integrates with Garmin Connect to fetch recent fitness activity data and visualize it using Plotly.

It also includes a simple meal planning feature powered by Gemini, which suggests meals based on recent activity, dietary goals, and optionally available ingredients.

## Features

* Activity visualizations for the last week and last 3 months:

  * duration grouped by activity type
  * calories burned
* Meal suggestions based on:

  * recent workouts
  * weight goal (gain, maintain, reduce)
  * optional ingredients provided by the user
* Local database (SQLite) for storing activity history
* Web interface built with Flask and Bootstrap 5

## Tech Stack

* Flask
* SQLAlchemy
* Plotly
* Garmin Connect API (unofficial)
* Google Gemini API
* Bootstrap 5

## Setup

1. Clone the repository:

```
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

2. Create and activate a virtual environment:

```
python -m venv venv
source venv/bin/activate   # on macOS/Linux
venv\Scripts\activate      # on Windows
```

3. Install dependencies:

```
pip install -r requirements.txt
```

4. Set environment variables:

```
EMAIL_GARMIN=your_email
PASSWORD_GARMIN=your_password
GEMINI_API=your_api_key
SECRET_KEY=your_secret_key
```

5. Run the app:

```
python main.py
```
