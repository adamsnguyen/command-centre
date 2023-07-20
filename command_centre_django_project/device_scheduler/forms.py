from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Device, ScheduledTimer, DEVICE_CHOICES, BOOL_CHOICES, BOOL_ALARM_STATUS_CHOICES
from bootstrap_datepicker_plus.widgets import TimePickerInput
from datetime import datetime, time


class DeviceForm(forms.ModelForm):
    
    class Meta:
        model = Device
        fields = '__all__'
        widgets = {
            'device_type': forms.Select(attrs={'class': 'form-control'}, choices=DEVICE_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['status'] = 'OFF'  # Set the default value of 'status' to 'OFF'
        self.fields['status'].widget = forms.HiddenInput()  # Hide field from the form's display


class MinutesSecondsTimeField(forms.Field):
    def clean(self, value):
        super().clean(value)
        try:
            minutes, seconds = value.split(':')
            minutes = int(minutes)
            seconds = int(seconds)
        except (ValueError, TypeError):
            raise forms.ValidationError('Enter a valid time in MM:SS format.')

        if minutes < 0 or minutes >= 60 or seconds < 0 or seconds >= 60:
            raise forms.ValidationError('Enter a valid time in MM:SS format.')

        return time(minute=minutes, second=seconds)
    
class ScheduledTimerForm(forms.ModelForm):
    # device = forms.ModelChoiceField(queryset=Device.objects.all().values_list('name', flat=True), widget=forms.Select(attrs={'class': 'form-control'}))
    device = forms.ModelChoiceField(queryset=Device.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    single = forms.RadioSelect(choices=BOOL_CHOICES, attrs={'class': 'form-control'})
    status = forms.RadioSelect(choices=BOOL_ALARM_STATUS_CHOICES, attrs={'class': 'form-control'})
    monday = forms.RadioSelect(choices=BOOL_CHOICES, attrs={'class': 'form-control'})
    tuesday = forms.RadioSelect(choices=BOOL_CHOICES, attrs={'class': 'form-control'})
    wednesday = forms.RadioSelect(choices=BOOL_CHOICES, attrs={'class': 'form-control'})
    thursday = forms.RadioSelect(choices=BOOL_CHOICES, attrs={'class': 'form-control'})
    friday = forms.RadioSelect(choices=BOOL_CHOICES, attrs={'class': 'form-control'})
    saturday = forms.RadioSelect(choices=BOOL_CHOICES, attrs={'class': 'form-control'})
    sunday = forms.RadioSelect(choices=BOOL_CHOICES, attrs={'class': 'form-control'})
    duration_minutes_seconds = MinutesSecondsTimeField(help_text='Minutes:Seconds', label="Duration")

    class Meta:
        model = ScheduledTimer
        fields = ['device', 'alarm_type', 'status', 'single','start_time', 'duration_minutes_seconds', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        widgets = {
            'device': forms.Select(attrs={'class': 'form-control'}),
            'start_time': TimePickerInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.initial['monday'] = False
        # self.initial['tuesday'] = False
        # self.initial['wednesday'] = False
        # self.initial['thursday'] = False
        # self.initial['friday'] = False
        # self.initial['saturday'] = False
        # self.initial['sunday'] = False
        self.initial['single'] = True
        self.initial['status'] = True
        self.initial['alarm_type'] = 'scheduled_timer'  # Set the default value of 'status' to 'OFF'
        self.fields['alarm_type'].widget = forms.HiddenInput()  # Hide field from the form's display


