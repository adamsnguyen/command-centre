from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from .forms import DeviceForm, ScheduledTimerForm
from .models import Device, ScheduledTimer, Alarm
from itertools import chain
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import paho.mqtt.client as mqtt
import os

# Load configuration from config.json file two directories up
config_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'config.json')
with open(config_file_path, 'r') as config_file:
    config = json.load(config_file)

mqtt_broker_url = config["mqtt"]["broker_url"]
mqtt_broker_port = config["mqtt"]["broker_port"]

import requests

class AppViews:

    class CustomLoginView(LoginView):
        template_name = 'login.html'

    class CustomLogoutView(LogoutView):
        next_page = 'home'

    class HomeView(TemplateView):
        template_name = 'home.html'

    # def get_device_statuses():
    #     devices = Device.objects.all()


    class DeviceListView(TemplateView):
        template_name = 'device_list.html'

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['devices'] = Device.objects.all().order_by('name')

            return context

    def device_create(request):
        if request.method == 'POST':
            form = DeviceForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('device-list')
        else:
            form = DeviceForm()
        return render(request, 'device_create.html', {'form': form})

    class DeviceDetailView(TemplateView):
        template_name = 'device_detail.html'

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            device_name = kwargs['name']
            context['device'] = Device.objects.get(name=device_name)
            return context

    def device_update(request, name):
        device = Device.objects.get(name=name)
        if request.method == 'POST':
            form = DeviceForm(request.POST, instance=device)
            if form.is_valid():
                form.save()
                return redirect('device-list')
        else:
            form = DeviceForm(instance=device)
        return render(request, 'device_update.html', {'form': form, 'device': device})

    def device_delete(request, name):
        device = Device.objects.get(name=name)
        device.delete()
        return redirect('device-list')

    def device_on(request, name):
        device = Device.objects.get(name=name)
        topic = None
        message = None

        if device.device_type == "solenoid":
            topic = f"/{device.name}/change_status"
            message = "ON"

        print(f"topic: {topic}, message: {message}")

        client = mqtt.Client()
        client.connect(mqtt_broker_url, mqtt_broker_port, 60)
        client.subscribe(topic)

        print(client.publish(topic, message, qos=1, retain=True))

        client.disconnect()

        return redirect('device-list')

    def device_off(request, name):
        device = Device.objects.get(name=name)
        topic = None
        message = None

        if device.device_type == "solenoid":
            topic = f"/{device.name}/change_status"
            message = "OFF"

        print(f"topic: {topic}, message: {message}")
        client = mqtt.Client()
        client.connect(mqtt_broker_url, mqtt_broker_port, 60)
        client.subscribe(topic)

        client.publish(topic, message, qos=1, retain=True)

        client.disconnect()

        return redirect('device-list')

    # class AlarmListView(TemplateView):
    #     template_name = 'alarm_list.html'

    #     def get_context_data(self, **kwargs):
    #         context = super().get_context_data(**kwargs)
    #         context['alarms'] = Alarm.objects.filter(alarm_type='alarm') | ScheduledTimer.objects.all()
    #         context['alarms'] = chain
    #         all().order_by('device', 'status')
    #         return context

    class AlarmListView(TemplateView):
        template_name = 'alarm_list.html'

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)

            alarms = Alarm.objects.filter(alarm_type='alarm')
            
            scheduled_timers = ScheduledTimer.objects.all()

            all_alarms = list(alarms) + list(scheduled_timers)

            sorted_alarms = sorted(all_alarms, key=lambda alarm: (-alarm.status, alarm.device.name))

            context['alarms'] = sorted_alarms

            # Print the context values
            print("Context Values:")
            for item in context['alarms']:
                try:
                    print(f"{item.device.name}, {item.status}")
                except Exception as e:
                    pass

            return context

    def alarm_create(request):
        if request.method == 'POST':
            form = ScheduledTimerForm(request.POST)
            if form.is_valid():
                alarm = form.save()
                print(form.cleaned_data)

                timer = ScheduledTimer.objects.get(pk=form.instance.id)  # Filter only enabled alarms
                print(form.instance.id)

                timer_data = {
                    'id': timer.pk,
                    'start_time': timer.start_time,
                    'device': timer.device.name,
                    'status': timer.status,
                    'single': timer.single,
                    'alarm_type': timer.alarm_type,
                    'monday': timer.monday,
                    'tuesday': timer.tuesday,
                    'wednesday': timer.wednesday,
                    'thursday': timer.thursday,
                    'friday': timer.friday,
                    'saturday': timer.saturday,
                    'sunday': timer.sunday,
                    'duration_minutes_seconds': timer.duration_minutes_seconds,  # Added field specific to ScheduledTimer
                }

                print(timer_data)

                url = 'http://127.0.0.1:8001/alarm-set'
                response = requests.post(url, data=json.dumps(timer_data, indent=4, sort_keys=True, default=str))
                print(response.status_code)
                
                return redirect('alarm-list')
        else:
            form = ScheduledTimerForm()

        return render(request, 'alarm_create.html', {'form': form})

    class AlarmDetailView(TemplateView):
        template_name = 'alarm_detail.html'

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            alarm_id = kwargs['pk']
            context['alarm'] = ScheduledTimer.objects.get(id=alarm_id)
            return context

    def alarm_update(request, pk):
        alarm = ScheduledTimer.objects.get(id=pk)
        if request.method == 'POST':
            form = ScheduledTimerForm(request.POST, instance=alarm)
            if form.is_valid():
                form.save()
                timerList = list(ScheduledTimer.objects.filter(id=pk))  # Filter only enabled alarms
                timer = timerList[0]
                timer_data = {
                    'id': timer.id,
                    'start_time': timer.start_time,
                    'device': timer.device.name,
                    'status': timer.status,
                    'single': timer.single,
                    'alarm_type': timer.alarm_type,
                    'monday': timer.monday,
                    'tuesday': timer.tuesday,
                    'wednesday': timer.wednesday,
                    'thursday': timer.thursday,
                    'friday': timer.friday,
                    'saturday': timer.saturday,
                    'sunday': timer.sunday,
                    'duration_minutes_seconds': timer.duration_minutes_seconds,  # Added field specific to ScheduledTimer
                }

                print(timer_data)

                # response = requests.post(url, json=payload)

                # if response.status_code == 200:
                #     return redirect('alarm-list')
        else:
            form = ScheduledTimerForm(instance=alarm)

        return render(request, 'alarm_update.html', {'form': form, 'alarm': alarm})

    def alarm_delete(request, pk):
        alarm = ScheduledTimer.objects.get(id=pk)
        alarm.delete()
        # if request.method == 'POST':
        #     # Notify the FastAPI app
        #     url = 'http://127.0.0.1:8001//alarms/delete' # Replace with the actual FastAPI endpoint URL
        #     payload = {
        #         'id': ScheduledTimer.id,
        #     }
        #     response = requests.post(url, json=payload)

        #     if response.status_code == 200:
        #         ScheduledTimer.delete()
        #         return redirect('alarm-list')

        return redirect('/alarm')
    
    def active_alarms(request):
        queryset = ScheduledTimer.objects.filter(status=True)  # Filter only enabled alarms
        data = []

        for timer in queryset:
            timer_data = {
                'id': timer.pk,
                'start_time': timer.start_time,
                'device': timer.device.name,
                'status': timer.status,
                'single': timer.single,
                'alarm_type': timer.alarm_type,
                'monday': timer.monday,
                'tuesday': timer.tuesday,
                'wednesday': timer.wednesday,
                'thursday': timer.thursday,
                'friday': timer.friday,
                'saturday': timer.saturday,
                'sunday': timer.sunday,
                'duration_minutes_seconds': timer.duration_minutes_seconds,  # Added field specific to ScheduledTimer
            }

            data.append(timer_data)

        return JsonResponse(data, safe=False)
    
    @csrf_exempt
    def get_devices(request):
        devices = Device.objects.all()
        data = []

        for device in devices:
            device_data = {
                'name': device.name,
                'device_type': device.device_type,
                'status': device.status,
            }

            data.append(device_data)

        print(data)
        print("test")
        return JsonResponse(data, safe=False)
    
    @csrf_exempt
    def acknowledge_alarms(request):
        if request.method == 'POST':
            data = request.POST.get('new_alarms')
            if data:
                # Process the acknowledgement data as needed
                print('Received acknowledgement:', data)
            return JsonResponse({'message': 'Acknowledgement received'})

        return JsonResponse({'message': 'Invalid request method'})

    @csrf_exempt
    def acknowledge_disable(request):
        if request.method == 'POST':
            data = request.POST.get('alarms_to_disable')
            if data:
                # Process the disable acknowledgement data as needed
                print('Received disable acknowledgement:', data)
                return JsonResponse({'message': 'Disable acknowledgement received'})
            else:
                return JsonResponse({'message': 'No alarms to disable acknowledgement'})
        return JsonResponse({'message': 'Invalid request method'})
    
    @csrf_exempt
    def update_device_status(request, name):
        if request.method == 'POST':
            try:
                status = request.POST.get('status')

                # Retrieve the device from the database
                try:
                    device = Device.objects.get(name=name)
                except Device.DoesNotExist:
                    return JsonResponse({'message': 'Device not found.'}, status=404)

                # Update the device status
                device.status = status
                device.save()

                return JsonResponse({'message': 'Device status updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Failed to update device status.', 'error': str(e)}, status=500)
        else:
            return JsonResponse({'message': 'Invalid request method.'}, status=400)