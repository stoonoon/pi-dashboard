# gtasks-frame.py
import os
import tkinter as tk
from gtasks import Gtasks
from urllib.error import HTTPError
from datetime import datetime

class GTasksFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.auto_refresh_time_ms = 10*60*1000 # 10 minutes in ms
        self.tasksButton = tk.Button(self, text="test", justify=tk.LEFT, command=self.update_tasks)
        self.tasksButton.grid(sticky="new")
        #self.backlightToggleButton = tk.Button(self, text="BACKLIGHT ON/OFF",\
            #height=3)#, command=backlight_toggle)
        #self.backlightToggleButton.grid(sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.update_tasks()

    # Timed autoupdater for gtasks
    def update_tasks(self):
        gt = Gtasks()
        task_list=-1
        try:
            task_list=gt.get_tasks()
        except HTTPError as err:
            if err.code ==503:
                print("Google Tasks service unavailable. Refresh skipped.")
            else:
                print(f"HTTP error in update_tasks() : {err.code}")
            raise

        if task_list != -1:
            tasks_dict = {}

            for task in task_list:
                if task.parent == None:
                    # then this is a root task
                    tasks_dict[task.title] = []

            for task in task_list:
                if task.parent != None:
                    prnt = task.parent
                    tasks_dict[prnt.title].append(task.title)

            tasks_str=""
            for task in tasks_dict:
                tasks_str += (task + "\n")
                for subtask in tasks_dict[task]:
                    tasks_str += ("- " + subtask + "\n")

            tasks_str += ("Last updated: " + datetime.now().strftime("%a, %d %b at %H:%M"))

            self.tasksButton.configure(text=tasks_str)

        self.after(self.auto_refresh_time_ms, self.update_tasks)




def main():
    # Removes requirement to run ' export DISPLAY=:0.0 ' first in
    # terminal if running from remote SSH session
    os.environ['DISPLAY'] = ':0.0' 

    # create tkinter root    
    root = tk.Tk()
    
    # add our Frame to the root
    GTasksFrame(root).pack(side="top", fill="both", expand=True)

    # cede control to tkinter scheduler
    root.mainloop()

# Allow the module to run standalone for testing
if __name__ == "__main__":
    main()