from datetime import date, timedelta

# "distance" "movingDuration" , 

def activity_data_slicer(data):
    """Slects data from garminconnect"""
    all_activites = []
    if len(data)>1:
        # print(len(data))
        for activity in data:
            garmin_activites ={}
            # print(activity)
            for key, value in activity.items():
                if key == "activityId":
                    garmin_activites[key] = value
                elif key == "startTimeLocal":
                    garmin_activites[key] = value
                elif key == "distance":
                    garmin_activites[key] = value
                elif key == "activityType":
                    for key_actTyp, val_actTyp in value.items():
                        if key_actTyp == 'typeKey':
                            garmin_activites[key_actTyp] = val_actTyp
                elif key == "duration":
                    # act_time = devider(value)
                    garmin_activites[key] = value
                elif key == "elevationGain":
                    garmin_activites[key] = value
                elif key == "elevationLoss":
                    garmin_activites[key] = value
                elif key == "averageSpeed":
                    garmin_activites[key] = round(value, 2)
                elif key == "maxSpeed":
                    garmin_activites[key] = round(value, 2)
                elif key == "calories":
                    garmin_activites[key] = value
                elif key == "averageHR":
                    garmin_activites[key] = value
                elif key == "maxHR":
                    garmin_activites[key] = value
                elif key == "averageRunningCadenceInStepsPerMinute":
                    garmin_activites[key] = value
                elif key == "avgPower":
                    garmin_activites[key] = value
                elif key == "aerobicTrainingEffect":
                    garmin_activites[key] = value
                elif key == "anaerobicTrainingEffect":
                    garmin_activites[key] = value
                elif key == "vO2MaxValue":
                    garmin_activites[key] = value
                elif key == "vigorousIntensityMinutes":
                    garmin_activites[key] = value
            all_activites.append(garmin_activites)
    return all_activites
        
def devider(seconds):
    """ Devides seconds into hh:mm:ss"""
    minutes = int(seconds // 60)
    sec = int(round((seconds / 60 - minutes) * 60))
    
    if sec == 60:
        sec = 0
        minutes += 1

    if minutes < 60:
        time_measured = f"{minutes:02d}:{sec:02d}"
    else:
        hours = minutes // 60
        minutes = minutes % 60
        time_measured = f"{hours}:{minutes:02d}:{sec:02d}"
    return time_measured     

# sleep_data = {}
# for key,value in data.items():
#     if key == "calendarDate":
#         sleep_data[key] = value
#     elif key == "sleepTimeSeconds":
#         time = devider(value)
#         sleep_data["sleepTime"] = time 
#     elif key == "deepSleepSeconds":
#         time = devider(value)
#         sleep_data["deepSleep"] = time
        