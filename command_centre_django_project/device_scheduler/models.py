from django.db import models

DEVICE_CHOICES = [
    ('solenoid', 'Solenoid'),
    # Other choices...
]

BOOL_CHOICES = [
    (True, 'Yes'),
    (False, 'No')
]

BOOL_STATUS_CHOICES = [
    (True, 'On'),
    (False, 'Off')
]

BOOL_ALARM_STATUS_CHOICES = [
    (True, 'Enabled'),
    (False, 'Disabled')
]

class Device(models.Model):
    name = models.CharField(max_length=100, primary_key=True, blank=False)
    device_type = models.CharField(max_length=100, default="solenoid", choices=DEVICE_CHOICES, blank=False)
    status = models.CharField(max_length=100, default="OFF", blank=False)

    def __str__(self):
        return self.name

class Alarm(models.Model):
    start_time = models.TimeField(blank=False)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    status = models.BooleanField(choices=BOOL_ALARM_STATUS_CHOICES, default=True, blank=False)
    single = models.BooleanField(choices=BOOL_CHOICES, blank=False)
    alarm_type = models.CharField(max_length=100, default="alarm", blank=False)
    monday = models.BooleanField(choices=BOOL_CHOICES, blank=False, default=True)
    tuesday = models.BooleanField(choices=BOOL_CHOICES, blank=False, default=True)
    wednesday = models.BooleanField(choices=BOOL_CHOICES, blank=False, default=True)
    thursday = models.BooleanField(choices=BOOL_CHOICES, blank=False, default=True)
    friday = models.BooleanField(choices=BOOL_CHOICES, blank=False, default=True)
    saturday = models.BooleanField(choices=BOOL_CHOICES, blank=False, default=True)
    sunday = models.BooleanField(choices=BOOL_CHOICES, blank=False, default=True)

    def __str__(self):
        return self.name

class ScheduledTimer(Alarm):
    duration_minutes_seconds = models.TimeField(blank=False)    
