import asyncio
from fastapi import FastAPI, Request
from fastapi import APIRouter
from pydantic import BaseModel
import datetime
import json
import requests
import uvicorn

local_alarm_list = []  # Local list to store enabled alarms
scheduled_tasks = {}  # Dictionary to store scheduled tasks and their alarm IDs
scheduled_tasks_list = []
scheduled_tasks_meta = {}  # Dictionary to store scheduled tasks and their alarm IDs
devices = []

# Read configuration from config.json file one directory up
config_file_path = "/app/common/config.json"
with open(config_file_path, 'r') as config_file:
    config = json.load(config_file)

# FastAPI app configuration
fastapi_port = config["device_scheduler_app"]["port"]
fastapi_port_address = config["device_scheduler_app"]["address"]

# Django app configuration
command_centre_address = config["command-centre"]["address"]
api_active_alarms_path = config["command-centre"]["get_active_alarms_path"]
api_active_alarms_url = f"{command_centre_address}{api_active_alarms_path}"

# device status checker
status_checker_address = config["device_scheduler_status_checker_app"]["address"]
status_checker_port = config["device_scheduler_status_checker_app"]["port"]
status_checker_path = config["device_scheduler_status_checker_app"]["device_status_path"]
device_status_url = f"http://{status_checker_address}:{status_checker_port}{status_checker_path}"

# scheduler_mqtt_helper_app
scheduler_mqtt_helper_address = config["scheduler_mqtt_helper_app"]["address"]
scheduler_mqtt_helper_port = config["scheduler_mqtt_helper_app"]["port"]
scheduler_mqtt_helper_url = f"http://{scheduler_mqtt_helper_address}:{scheduler_mqtt_helper_port}"

class Alarm(BaseModel):
    id: int
    name: str
    start_time: str
    duration_minutes_seconds: str
    device_name: str

acknowledgement_url = 'http://localhost:8000/api/acknowledge_alarms/'
disable_url = 'http://your-api-url/api/disable_alarms/'

app = FastAPI()

# Dictionary to keep track of expected acknowledgments
expected_acknowledgements = {}

async def publish_with_acknowledgement(device:str, topic_suffix:str, payload, qos=1, retain=False):
    max_retries = 10
    count = 0
    status: str
    confirmed_status = False
    topic=f"/{device}{topic_suffix}"

    mqtt_publish_url = f"{scheduler_mqtt_helper_url}/{device}/change_status/{payload}"
    print(mqtt_publish_url)
    response = requests.get(mqtt_publish_url)
    
    while(not confirmed_status):
        print(f"MQTT message publish request to {topic} with payload {payload}. Waiting for acknowledgement...")
        await asyncio.sleep(2)  # wait for 5 seconds for acknowledgement
        status_check_url = device_status_url+device
        response = requests.get(status_check_url)
        device_status_msg = response.json()
        status = device_status_msg['status']

        if status == payload:  # If acknowledgement received and removed from dict
            current_time = datetime.datetime.now()
            print(f"Command {payload} set successfully by {current_time}")
            confirmed_status = True
            break
        else:  # if the loop completed and no acknowledgement received
            print(f"Attempting to send command {payload} again")
            response = requests.get(mqtt_publish_url)
        count+=1

        if count == max_retries:
            break

def send_acknowledgement(new_alarms):
    payload = {
        'new_alarms': new_alarms
    }

    response = requests.post(acknowledgement_url, json=payload)

    if response.status_code == 200:
        print('Acknowledgement sent successfully')
    else:
        print('Failed to send acknowledgement:', response.status_code)

def send_disable_acknowledgement(alarms_to_disable):
    payload = {
        'alarms_to_disable': alarms_to_disable
    }

    response = requests.post(disable_url, json=payload)

    if response.status_code == 200:
        print('Disable acknowledgement sent successfully')
        remove_from_list(alarms_to_disable)
    else:
        print('Failed to send disable acknowledgement:', response.status_code)

def remove_from_list(alarms_to_remove):
    for alarm in alarms_to_remove:
        local_alarm_list.remove(alarm)

def remove_extra_alarms(extra_alarms):
    for alarm in extra_alarms:
        local_alarm_list.remove(alarm)

# Routes
router = APIRouter()
 
@router.post("/alarms/notify")
async def notify_alarm(alarm):
    print(f"Received alarm notification. alarm id: {alarm['id']}, Start Time: {alarm['start_time']}, End Time: {alarm['duration_minutes_seconds']}, Device Name: {alarm['device']}")
    # Logic to handle the alarm notification
    # You can perform actions based on the received alarm data
    # For example, schedule the alarm to turn on/off the device at the specified times
    task = asyncio.create_task(schedule_alarm(alarm))  # Schedule the alarm asynchronously
    scheduled_tasks[alarm['id']] = task  # Store the task in the dictionary
    scheduled_tasks_meta["id"] = alarm

def get_true_days_from_alarm(alarm):
    days = []

    if alarm.get('monday', False):
        days.append('Monday')
    if alarm.get('tuesday', False):
        days.append('Tuesday')
    if alarm.get('wednesday', False):
        days.append('Wednesday')
    if alarm.get('thursday', False):
        days.append('Thursday')
    if alarm.get('friday', False):
        days.append('Friday')
    if alarm.get('saturday', False):
        days.append('Saturday')
    if alarm.get('sunday', False):
        days.append('Sunday')

    return days

def get_next_alarm(days_list, day_check, time):
    
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']  
    days = [day.capitalize() for day in days_list]  # Capitalize the days in the list
    days.sort(key=lambda day: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'].index(day))

    day_check_string = day_check.strftime('%A')
    index = 0

    print(days)
    print(day_check_string)
    if day_check_string in days:
        next_enabled_day = days[days.index(day_check_string.capitalize()):][0]
        print("True")
        print(next_enabled_day)
    else:
        next_enabled_day = days[0]
        print("False")
        print(next_enabled_day)
        
    days_ahead = (weekdays.index(next_enabled_day) - day_check.weekday() + 7) % 7
    print(days_ahead)
    target_day = day_check + datetime.timedelta(days=days_ahead)
    print(target_day)
    next_alarm = datetime.datetime.combine(target_day, datetime.datetime.min.time()) + datetime.timedelta(hours=time.hour, minutes=time.minute)
    print(next_alarm)

    if next_alarm < datetime.datetime.now():
        print("Already passed")
        day_after = day_check + datetime.timedelta(days=1)
        print(day_after)
        next_alarm = get_next_alarm(days_list, day_after, time)
        

    print(next_alarm)
    return next_alarm

    # return next_enabled_day

def combine_day_and_time(day, time):
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    day_index = days_of_week.index(day)

    # Get today's date
    today = datetime.date.today()

    # Calculate the number of days to add
    days_to_add = (day_index - today.weekday()) % 7

    # Create a datetime object with the combined day and time
    combined_datetime = datetime.datetime.combine(today + datetime.timedelta(days=days_to_add), time)

    if combined_datetime < datetime.datetime.now():
        combined_datetime = datetime.datetime.combine(today + datetime.timedelta(days=7), time)
    
    return combined_datetime

async def schedule_alarm(alarm):
    days_enabled = get_true_days_from_alarm(alarm)
    if len(days_enabled) == 0:
        return

    print(alarm["id"])
    print(days_enabled)

    while(alarm["status"]):
        # print(next_enabled_day)
        start_time = datetime.datetime.strptime(alarm['start_time'], "%H:%M:%S")
        today = datetime.datetime.today()
        next_start = get_next_alarm(days_enabled, today, start_time)
        duration_minutes_seconds = datetime.datetime.strptime(alarm['duration_minutes_seconds'], "%H:%M:%S")
        next_end = next_start + datetime.timedelta(minutes=duration_minutes_seconds.minute, seconds=duration_minutes_seconds.second)

        print(f"next start: {next_start}")
        print(f"next end: {next_end}")     
        current_time = datetime.datetime.now()

        if next_start > current_time:
            # Calculate the time difference until the start time
            time_diff = (next_start - datetime.datetime.now()).total_seconds()
            print("time to next: ", next_start - datetime.datetime.now())
            await asyncio.sleep(time_diff)
            # Turn on the device
            print(f"Scheduled alarm to turn ON device: {alarm['device']} at {alarm['start_time']}")
            try:
                await publish_with_acknowledgement(device=alarm['device'], topic_suffix="/change_status", payload="ON")
            except Exception as e:
                print(e)         

            if next_end > current_time:
                # Calculate the time difference until the end time
                time_diff = (next_end - datetime.datetime.now()).total_seconds()
                await asyncio.sleep(time_diff)
                # Turn off the device
                await publish_with_acknowledgement(device=alarm['device'], topic_suffix="/change_status", payload="OFF")
                print(f"Scheduled alarm to turn OFF device: {alarm['device']} at {next_end}")

@router.post("/alarms/delete")
def delete_alarm(alarm_id: int):
    print(f"Received alarm deletion request. Alarm ID: {alarm_id}")
    # Logic to handle the alarm deletion
    # You can delete the alarm from the database or perform any other necessary actions
    if alarm_id in scheduled_tasks:
        task = scheduled_tasks[alarm_id]
        task.cancel()  # Cancel the scheduled task
        del scheduled_tasks[alarm_id]  # Remove the task from the dictionary
        # get_active_alarms()
    else:
        print(f"No scheduled task found for Alarm ID: {alarm_id}")

@router.get("/get-alarms")
def get_alarms():
    # Logic to handle the alarm deletion
    # You can delete the alarm from the database or perform any other necessary actions
    print(scheduled_tasks_meta)
    print("number of alarms: ", len(scheduled_tasks_list))

@router.post("/alarms/update")
def update_alarm(alarm):
    print(f"Received alarm update request. Name: {alarm.name}, Start Time: {alarm.start_time}, End Time: {alarm.duration_minutes_seconds}, Device Name: {alarm['device']}")
    # Logic to handle the alarm update
    # You can update the alarm in the database or perform any other necessary actions
    if alarm.id in scheduled_tasks:
        task = scheduled_tasks[alarm.id]
        task.cancel()  # Cancel the existing scheduled task
        del scheduled_tasks[alarm.id]  # Remove the task from the dictionary
    task = asyncio.create_task(schedule_alarm(alarm))  # Schedule the updated alarm asynchronously
    scheduled_tasks[alarm.id] = task  # Store the updated task in the dictionary

@app.on_event("startup")
async def schedule_alarms():
    asyncio.create_task(get_alarm())
    # background_tasks = BackgroundTasks()
    # background_tasks.add_task(asyncio.run, get_alarm())
    # await background_tasks()

@router.post("/alarm-set")
async def set_alarm(req: Request):
     global scheduled_tasks
     global scheduled_tasks_meta
     global scheduled_tasks_list

     alarm = await req.json()
     print(alarm)
     if alarm["id"] not in scheduled_tasks:
        task = asyncio.create_task(schedule_alarm(alarm))
        scheduled_tasks[alarm["id"]] = task
        scheduled_tasks_meta[alarm["id"]] = alarm
        scheduled_tasks_list.append(task)

async def get_alarm():
    global local_alarm_list
    global scheduled_tasks_list
    global scheduled_tasks_meta
    global scheduled_tasks
    global devices
    response = None

    while True:
        try:
            response = requests.get(api_active_alarms_url)
            if response is None:
                continue
       
            elif response.status_code == 200:
                new_alarm_list = response.json()
                new_alarms = []
                for alarm in new_alarm_list:
                    if alarm not in local_alarm_list:
                        local_alarm_list.append(alarm)
                        new_alarms.append(alarm)

                        if alarm["id"] not in scheduled_tasks:
                            task = asyncio.create_task(schedule_alarm(alarm))
                            scheduled_tasks[alarm["id"]] = task
                            scheduled_tasks_meta[alarm["id"]] = alarm
                            scheduled_tasks_list.append(task)
                
                # Check for extra alarms in the local list
                extra_alarms = []
                for alarm in local_alarm_list:
                    if alarm not in new_alarm_list:
                        extra_alarms.append(alarm)
                        # logger.info(f"extra alarms: {extra_alarms}")

                if len(new_alarms) > 0:
                    print(new_alarms)
                    send_acknowledgement(new_alarms)

                if len(extra_alarms) > 0:
                    remove_extra_alarms(extra_alarms)

            else:
                print('Request failed with status code:', response.status_code)
        except Exception as e:
            print(e)

        await asyncio.sleep(10)  # Adjust the delay as per your requirements    

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host=fastapi_port_address, port=fastapi_port)


    
