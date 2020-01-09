#!/usr/bin/python3
# pylint: disable=no-member

import tkinter as tk
from gtasks_frame import GTasksFrame
from sonos_frame import SonosFrame
from datetime import datetime
from datetime import timedelta
import os

my_background_colour = "#162D32" # dark green
my_highlight_background_colour = "#122928" # darker green
my_title_background_colour = "#202020" # dark grey
my_foreground_colour = "#AAAAAA" # light grey
my_active_foreground_colour = "#AAAA00" # yellow
separator_v = ",\n"
backlight_timeout_start_time = -1
MS_IN_MINUTES = 1000*60
S_IN_MINUTES = 60
S_IN_HOURS = S_IN_MINUTES*60
BACKLIGHT_TIMEOUT_SHORT = 10 * S_IN_MINUTES
BACKLIGHT_TIMEOUT_LONG = 10*S_IN_HOURS
BACKLIGHT_DAYTIME_HOUR_START = 8
BACKLIGHT_DAYTIME_HOUR_END = 22
backlight_is_on = False

# Removes requirement to run ' export DISPLAY=:0.0 ' first in
# terminal if running from remote SSH session
os.environ['DISPLAY'] = ':0.0' 

#tkinter root object and screen config
root = tk.Tk()

#comment this out to allow window to be moved / resized
root.overrideredirect(True)

# set size to match pi touchscreen resolution and location -
# top left (desktop) / full screen (on pi)
root.geometry("800x480+0+0")

# visual styling 

# make all widgets dark green
root.option_add("*Background", my_background_colour)
root.option_add("*Foreground", my_foreground_colour)
root.option_add("*highlightForeground", my_highlight_background_colour)
root.option_add("*highlightBackground", my_highlight_background_colour)

# tweak button highlight when mouseover
root.option_add("*activeForeground", my_active_foreground_colour)
root.option_add("*activeBackground", my_highlight_background_colour)

# mouse_watcher globals (for hiding cursor)
cursor_is_visible = True
mouse_last_moved = datetime.now()
mouse_idle_timeout = 1 # seconds
mouse_last_known_location = root.winfo_pointerxy()

def backlight_on():
  global backlight_is_on
  os.popen('sudo bash -c "echo 0 > /sys/class/backlight/rpi_backlight/bl_power"')
  reset_backlight_timer()
  backlight_is_on = True

def backlight_off():
  global backlight_is_on
  os.popen('sudo bash -c "echo 1 > /sys/class/backlight/rpi_backlight/bl_power"')
  backlight_is_on = False

def backlight_toggle(action="TOGGLE"):
  global backlight_is_on

  if action=="TOGGLE":
    stream = os.popen('cat /sys/class/backlight/rpi_backlight/bl_power')
    output = stream.read()
    if '0' in output:
      # then backlight was on
      action = "OFF"
    else:
      # then backlight was off, or bl_power not readable
      action = "ON"
  
  if action=="ON":
    backlight_on()
  elif action=="OFF":
    backlight_off()
  else:
    output = -1 # invalid action -> ignore
    print(f"Invalid parameter sent to backlight_toggle(action): {action}")

def reset_backlight_timer():
  global backlight_timeout_start_time
  backlight_timeout_start_time = datetime.now()
  
def check_backlight_timer():
  global backlight_timeout_start_time
  current_datetime = datetime.now()

  # Check if we are in daytime hours
  if BACKLIGHT_DAYTIME_HOUR_START <= current_datetime.hour <= BACKLIGHT_DAYTIME_HOUR_END:
    
    # daytime - use longer timeout
    backlight_timeout=BACKLIGHT_TIMEOUT_LONG

    # check if we need to wake the screen
    if BACKLIGHT_DAYTIME_HOUR_START == current_datetime.hour:
      # then we are in the first hour of daytime zone
      if current_datetime > (backlight_timeout_start_time + timedelta(hours=1)):
        # then backlight timer has been running for longer than an hour
        backlight_toggle("ON")

  else:
    
    #nighttime - use shorter timeout
    backlight_timeout=BACKLIGHT_TIMEOUT_SHORT

  # Check whether we have initialised the timer  
  if backlight_timeout_start_time==-1:
    
    # Then we need to initialise it
    reset_backlight_timer()
    backlight_toggle("ON")

  else:
    
    # we can check against it
    elapsed_time = datetime.now()-backlight_timeout_start_time
    
    # Test if timeout period has been exceeded
    if elapsed_time.seconds >= (backlight_timeout):
      backlight_toggle("OFF")
  
  # Schedule the function to run again
  root.after(1*MS_IN_MINUTES, check_backlight_timer)

def mouse_watcher():
  global root, cursor_is_visible, mouse_last_moved, mouse_last_known_location
  xy = root.winfo_pointerxy()
  if xy==mouse_last_known_location: # cursor hasn't moved since last loop
    if cursor_is_visible:
      dt = datetime.now()
      if dt > (mouse_last_moved + timedelta(seconds=mouse_idle_timeout)):
        # Move pointer away from any highlightable widgets
        pointer_home=(799,239)
        root.event_generate('<Motion>', warp=True, x=pointer_home[0], y=pointer_home[1])
                
        # Hide mouse pointer
        root.config(cursor= "none")
        cursor_is_visible = False
  else: #cursor has moved since last loop
    mouse_last_moved = datetime.now()
    mouse_last_known_location = xy
    if not cursor_is_visible:
      # turn cursor back on
      root.config(cursor= "left_ptr")
      cursor_is_visible = True
    
  root.after(1, mouse_watcher)

def update_clock():
  dt=datetime.now()
  dt_string= dt.strftime("%d/%m/%Y %H:%M")
  clockLabel.configure(text=dt_string)
  root.after(1, update_clock)

# Main window layout frames

# Top menu bar
menuFrame = tk.Frame(root, bg=my_title_background_colour)
menuFrame.place(relwidth=1, relheight=0.05, relx=0, rely=0)

#LH gtasks frame
tasksFrame = GTasksFrame(root)
tasksFrame.place(relwidth=0.5, relheight=0.85, relx=0, rely=0.05)

#LH backlight frame
backlightFrame = tk.Frame(root)
backlightFrame.place(relwidth=0.5, relheight=0.1, relx=0, rely=0.9)

#RH sonos frame
sonosFrame = SonosFrame(root)
sonosFrame.place(relwidth=0.5, relheight=0.95, relx=0.5, rely=0.05)

# menuFrame widgets
clockLabel = tk.Label(menuFrame, text="XX:XX", bg=my_title_background_colour)
clockLabel.pack(side=tk.LEFT)
quitButton = tk.Button(menuFrame, text="X", command=exit, bg=my_title_background_colour,\
  highlightbackground=my_title_background_colour, relief=tk.FLAT,\
  activebackground=my_foreground_colour, activeforeground=my_title_background_colour)
quitButton.pack(side=tk.RIGHT)

# backlightFrame widgets
backlightToggleButton = tk.Button(backlightFrame, text="BACKLIGHT ON/OFF",\
  height=3, command=backlight_toggle)
backlightToggleButton.grid(sticky="nsew")
backlightFrame.columnconfigure(0, weight=1)
backlightFrame.rowconfigure(0, weight=1)

# Trigger recurring autoupdate methods
update_clock()
check_backlight_timer()
mouse_watcher()
root.mainloop()
