import garminconnect
import os
from datetime import date, timedelta, datetime
import datetime
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import func, Integer, String, Float
import sqlalchemy
from data_garmin_slicer import activity_data_slicer, devider
from plots import generate_plot_week_activity, generate_bar_chart_calories, generate_weekly_activites_plot
import json
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,SelectField 
from wtforms.validators import DataRequired
from google import genai 
from markdown import markdown
import pandas as pd
from flask_apscheduler import APScheduler

app = Flask(__name__, static_folder='static')


garmin_log = os.environ.get('EMAIL_GARMIN')
garmin_pswd = os.environ.get('PASSWORD_GARMIN')
gemini_key = os.environ.get('GEMINI_API')
database_url = os.environ.get('DATABASE_URL_GAR')

client = genai.Client(api_key=gemini_key)

gapka_id =  os.environ.get('GAPKA')
app.config['SECRET_KEY'] = gapka_id

# run_start_date = "2025-03-26"
# data_metrics = garmin.get_max_metrics(run_start_date)
# print(data_metrics)

class Config:
    SCHEDULER_API_ENABLED = True

app.config.from_object(Config())

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

#Database
db = SQLAlchemy()
# database_url = "sqlite:///garmin_data.db"
class Base(DeclarativeBase):
    pass

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
db.init_app(app)

Bootstrap5(app)

class MealChoice(FlaskForm):
    type_of_meal = SelectField('What type of meal would you like to have?', choices=["Breakfast", "Lunch", "Dinner", "Snack"], validators=[DataRequired()])
    type_of_food = SelectField('What type of food would you like to eat?', choices=["Meat", "Veggies", "Fruits","Soup"], validators=[DataRequired()])
    power = SelectField('Would you like to reduce or gain weight?', choices=["Reduce","Maintain","Gain"], validators=[DataRequired()])
    calories = StringField("How many calories?")
    leftovers = StringField("What have you got in the fridge?")
    submit = SubmitField('Generate meal')

class Activity(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    activity_id = db.Column(db.Integer, unique=True)
    date_time = db.Column(db.DateTime,  nullable=False)
    distance = db.Column(db.Float)
    activity_type = db.Column(db.String(30), nullable=False)
    duration = db.Column(db.Float, nullable=False)
    elevation_gain = db.Column(db.Float)
    elevation_loss = db.Column(db.Float)
    average_speed = db.Column(db.Float)
    max_speed = db.Column(db.Float)
    calories = db.Column(db.Float)
    average_HR = db.Column(db.Float)
    max_HR = db.Column(db.Float)
    average_Running_Cadence_In_Steps_Per_Minute = db.Column(db.Float)
    avg_Power = db.Column(db.Float)
    aerobic_Training_Effect = db.Column(db.Float)
    anaerobic_Training_Effect = db.Column(db.Float)
    vO2MaxValue = db.Column(db.Float)
    vigorous_Intensity_Minutes = db.Column(db.Float)

    def to_dict(self):
        dictionary = {}
        # loop through each column in the data record
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

def database_update():
    """ It logs in to garminconnect and takes out data """
    garmin = garminconnect.Garmin(garmin_log, garmin_pswd)
    garmin.login()

    GARTH_HOME = os.getenv("GARTH_HOME", "~/.garth")
    garmin.garth.dump(GARTH_HOME)

    today = date.today() 
    past_three_months = date.today()- timedelta(days=90)

    today = today.isoformat()
    past_three_months = past_three_months.isoformat()
    data = garmin.get_activities_by_date(past_three_months,today)

    # activity_data_slicer takes certain data from garminconnect 
    all_activites = activity_data_slicer(data)

    rever_list = all_activites[::-1]
    with app.app_context():
        for activity in rever_list:
            activity_id = activity["activityId"]
            date_time_conv = datetime.datetime.strptime(activity["startTimeLocal"], "%Y-%m-%d %H:%M:%S")
            exists = db.session.query(Activity).filter_by(activity_id=activity["activityId"]).first()
            if not exists: 
                new_activity = Activity( activity_id = activity["activityId"] , date_time=date_time_conv, distance=activity.get("distance"), 
                                    activity_type = activity.get("typeKey"), duration = activity.get("duration"), elevation_gain = activity.get("elevationGain"), 
                                    elevation_loss=activity.get("elevationLoss"),average_speed=activity.get("averageSpeed"), max_speed = activity.get("maxSpeed"),
                                    calories =activity.get("calories"), average_HR = activity.get("averageHR"),max_HR = activity.get("maxHR"), average_Running_Cadence_In_Steps_Per_Minute = activity.get("averageRunningCadenceInStepsPerMinute"),
                                    avg_Power = activity.get("avgPower"), aerobic_Training_Effect = activity.get("aerobicTrainingEffect") , anaerobic_Training_Effect = activity.get("anaerobicTrainingEffect"),
                                    vO2MaxValue = activity.get("vO2MaxValue"), vigorous_Intensity_Minutes = activity.get("vigorousIntensityMinutes") )
                db.session.add(new_activity)
                try:
                    db.session.commit()
                    print(f"Following activity added {activity_id}")
                except sqlalchemy.exc.IntegrityError as error:
                    db.session.rollback() 
                    print(f"IntegrityError adding activity {activity_id}: {error}")

with app.app_context():
        db.create_all()
        database_update()
    

# Query for records between start and end date 
def database_data(start_date, end_date):
    # start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    # end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    with app.app_context():
        activities_data = Activity.query.filter( func.date(Activity.date_time) >= start_date, func.date(Activity.date_time) <= end_date).all()
        activites_period = [{"date_time": activity.date_time, "distance": activity.distance, "duration": activity.duration, "activity_type": activity.activity_type,
                    "calories": activity.calories } for activity in activities_data]
        return activites_period
    

@app.route("/")
def home():
    today = date.today()
    one_week_back = date.today() - timedelta(days=7)
    three_months = date.today() - timedelta(days=90)
    
    last_week_data = database_data(one_week_back,today)
    three_months_data = database_data(three_months,today)
    
    if last_week_data:
        act_last_week = generate_plot_week_activity(last_week_data)
        calories_last_week = generate_bar_chart_calories(last_week_data)
    else:
        act_last_week = "<p>No activities in the past week</p>"
        calories_last_week = "<p>No activities in the past week</p>"
    
    weekly_act = generate_weekly_activites_plot(three_months_data)

    return render_template("index.html", act_plot=act_last_week, cal_bar = calories_last_week, weekly_plt =weekly_act)


@app.route("/meal", methods = ["GET", "POST"])
def meal_idea():
    form = MealChoice()
    text = None  
    if form.validate_on_submit():
        type_of_meal = form.type_of_meal.data
        type_of_food = form.type_of_food.data
        power = form.power.data
        leftovers = form.leftovers.data
        calories = form.calories.data

        today = date.today()
        three_days_ago = date.today() - timedelta(days=4)
        three_days_activity = database_data(three_days_ago, today)
        last_days =[]
        for item in three_days_activity:
            if item["duration"]: 
                # time = devider(item["duration"])
                item["duration"] = devider(item["duration"])
            if item["distance"]>1:
                item["distance"] = f"{round(item['distance'], 2)}m"
            last_days.append(f"- Activity: {item['activity_type']}, duration: {item['duration']}, distance: {item['distance']}, calories burnt: {item['calories']}")
        formatted_activity = "My recent activities over the past 3 days include:\n" + "\n".join(last_days)
        # print(last_days)
        if len(leftovers) >=1:
            fridge_stock = f"I have the following ingredients in my fridge: {leftovers}. Please prioritize using them if possible."
        else:
            fridge_stock = ""
        if len(calories)>=1:
            cal_range = f" Meal should have aprox. {calories} calories"
        else:
            cal_range = ""
        prompt = f"""
        Given my recent activities over the last 3 days.
        {formatted_activity}
        I'm a 28 years old male, 176 cm tall, weighing 72 kg. My goal is to {power} my weight.
        Please recommend exactly 2 detailed {type_of_meal} recipes that include {type_of_food}. {fridge_stock} 
        
        Each recipe should be structured like this:
        - Meal Name
        - Ingredients (bullet points, including spices)
        - Short, clear cooking instructions
        - Calories per portion
        
        Requirements:
        - Meals must be high in nutrients, high in protein, and suitable for someone who works out regularly.
        - Meals must be filling and aligned with my weight {power} goal. {cal_range}
        - Start the response with the name of the first meal.
        - Keep the tone motivating but concise.
        """
        # print(prompt)
        try:
            response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
            text = markdown(response.text)
        except Exception as e:
            text = "Sorry, I couldn't generate a meal idea this time"
            print(f"Error: {e}")

    return render_template("meal_idea.html", form=form, text=text)

@scheduler.task('cron', id='update_db', hour='12,19,23', timezone='UTC')
def scheduled_database_update():
    print("Running scheduled database update")
    database_update()  

if __name__ == "__main__":
    app.run()


