# backlight.py
import os
import pi_dashboard_config as cfg
from datetime import datetime, timedelta

class Backlight:
    def __init__(self):
        # datetime for start of screensaver timeout
        self.timer_start_time = -1

        # whether the backlight is currently on
        self.is_on = False

        # whether we are using shorter timeout for night time
        self.night_mode=False
        
        # datetime for next time we wake the screen
        self.next_wake=-1

        
        self.update_timeout()
        self.set_on()
        self.set_next_wake()
        
    def read_current_status(self):
        stream = os.popen('cat /sys/class/backlight/rpi_backlight/bl_power')
        output = stream.read()
        if '0' in output:
            # then backlight was on
            self.is_on = True
        else:
            # then backlight was off, or bl_power not readable
            self.is_on = False
        self.last_status_read=datetime.now()

    def set_on(self):
        self.read_current_status()
        if not self.is_on:
            os.popen('sudo bash -c "echo 0 > /sys/class/backlight/rpi_backlight/bl_power"')
            self.is_on = True
        self.reset_timer()

    def set_off(self):
        self.read_current_status()
        if self.is_on:
            os.popen('sudo bash -c "echo 1 > /sys/class/backlight/rpi_backlight/bl_power"')
            self.is_on = False

    def toggle(self, action="TOGGLE"):
        if action=="TOGGLE":
            self.read_current_status()
            if self.is_on:
                action = "OFF"
            else:
                action = "ON"
        
        if action=="ON":
            self.set_on()
        elif action=="OFF":
            self.set_off()
        else:
            print(f"Invalid parameter sent to backlight_toggle(action): {action}")

    def reset_timer(self):
        # Set timer start time to now
        self.timer_start_time = datetime.now()
    
    def timeout(self):
        if self.night_mode:
            return cfg.BACKLIGHT_TIMEOUT_SHORT
        else:
            return cfg.BACKLIGHT_TIMEOUT_LONG

    def update_timeout(self):
        # Get current datetime
        current_datetime = datetime.now()
        
        # Check if we are in daytime hours
        if cfg.BACKLIGHT_DAYTIME_HOUR_START <= current_datetime.hour <= \
            cfg.BACKLIGHT_DAYTIME_HOUR_END:

            # daytime - use longer timeout
            self.night_mode = False
        else:
            # nighttime - use shorter timeout
            self.night_mode = True

    def set_next_wake(self):
        now = datetime.now()
        wake_dt = now.replace(hour=cfg.BACKLIGHT_DAYTIME_HOUR_START, minute=0)
        while wake_dt < now:
            wake_dt = wake_dt + timedelta(hours=24)
        self.next_wake = wake_dt

    def check_timer(self):
        now = datetime.now()
        if self.is_on:
            # screen is on, check if timer expired
            if (now > (self.timer_start_time + self.timeout())) :
                # Timer has expired, turn off screen
                self.set_off()
        else:
            # screen is off, check if we need to wake it
            if now > self.next_wake:
                # turn on screen
                self.set_on()
                # update next wake time
                self.set_next_wake()
