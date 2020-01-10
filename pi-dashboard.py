#!/usr/bin/python3
# pylint: disable=no-member

import tkinter as tk
import pi_dashboard_config as cfg
from gtasks_frame import GTasksFrame
from sonos_frame import SonosFrame
from backlight import Backlight
from datetime import datetime, timedelta
import os

# Removes requirement to run ' export DISPLAY=:0.0 ' first in
# terminal if running from remote SSH session
os.environ['DISPLAY'] = ':0.0' 

#tkinter root object and screen config
root = tk.Tk()

#do not allow window to be moved / resized
root.overrideredirect(cfg.prevent_move_resize)

# set size and position of window
root.geometry(str(cfg.width)+"x"+str(cfg.height)+"+"+str(cfg.relx)+\
  "+"+str(cfg.rely))

# visual styling 

# make all widgets dark green
root.option_add("*Background", cfg.background_colour)
root.option_add("*Foreground", cfg.foreground_colour)
root.option_add("*highlightForeground", cfg.highlight_background_colour)
root.option_add("*highlightBackground", cfg.highlight_background_colour)

# tweak button highlight when mouseover
root.option_add("*activeForeground", cfg.active_foreground_colour)
root.option_add("*activeBackground", cfg.highlight_background_colour)

# mouse_watcher globals (for hiding cursor)
cursor_is_visible = True
mouse_last_moved = datetime.now()
cursor_last_relocated = datetime.now()
mouse_last_known_location = root.winfo_pointerxy()

backlight = Backlight()

def check_backlight_timer():
  backlight.check_timer()
  root.after(cfg.backlight_auto_refresh_time, check_backlight_timer)

def mouse_watcher():
  global root, cursor_is_visible, mouse_last_moved, mouse_last_known_location,\
    cursor_last_relocated
  xy = root.winfo_pointerxy()
  if xy==mouse_last_known_location: # cursor hasn't moved since last loop
    if cursor_is_visible:
      dt = datetime.now()
      if dt > (mouse_last_moved + timedelta(seconds=cfg.mouse_idle_timeout)):
        # Move pointer away from any highlightable widgets
        root.event_generate('<Motion>', warp=True, x=cfg.pointer_home[0], \
          y=cfg.pointer_home[1])
        cursor_last_relocated=datetime.now()
                
        # Hide mouse pointer
        root.config(cursor= "none")
        cursor_is_visible = False
  else: #cursor has moved since last loop
    mouse_last_moved = datetime.now()
    mouse_last_known_location = xy
    if (cursor_last_relocated+timedelta(seconds=(1))<datetime.now()):
      backlight.set_on()
    if not cursor_is_visible:
      # turn cursor back on
      root.config(cursor= "left_ptr")
      cursor_is_visible = True
    
  root.after(1*cfg.mouse_watcher_refresh_time, mouse_watcher)

def update_clock():
  dt=datetime.now()
  dt_string= dt.strftime("%d/%m/%Y %H:%M")
  clockLabel.configure(text=dt_string)
  root.after(1*cfg.MS_IN_MINUTES, update_clock)

# Main window layout frames

# Top menu bar
menuFrame = tk.Frame(root, bg=cfg.title_background_colour)
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
clockLabel = tk.Label(menuFrame, text="XX:XX", bg=cfg.title_background_colour)
clockLabel.pack(side=tk.LEFT)
quitButton = tk.Button(menuFrame, text="X", command=exit, \
  bg=cfg.title_background_colour, highlightbackground=cfg.title_background_colour,\
     relief=tk.FLAT, activebackground=cfg.foreground_colour, \
       activeforeground=cfg.title_background_colour)
quitButton.pack(side=tk.RIGHT)

# backlightFrame widgets
backlightToggleButton = tk.Button(backlightFrame, text="BACKLIGHT ON/OFF",\
  height=3, command=backlight.toggle)
backlightToggleButton.grid(sticky="nsew")
backlightFrame.columnconfigure(0, weight=1)
backlightFrame.rowconfigure(0, weight=1)

# Trigger recurring autoupdate methods
update_clock()
check_backlight_timer()
mouse_watcher()
root.mainloop()
