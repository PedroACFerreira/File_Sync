"""
Script produced as a task to Veeam Software by Pedro Ferreira.
This script will perform a one-way sync between two folders.
Provides an easy GUI to set up this operation.
Tu run directly from CMD without GUI, use file_sync_extended.py
All alterations made to the target folder are logged in a separate file.

For more information on sync operation, check the GitHub repo below or file_sync_extended.py

Here is an explanation of all options:
    - Source - Select source path;
    - Replica - Select replica path;
    - Sync Interval - Select how long it will be between each sync. Whole numbers only;
    - Log - Path to logfile. Write the name of the file as *.log ;
    - Multiprocessing - Enable multiprocessing to speed up synchronization;
    - Number of processes - Select number of processes to be used;
    - Enable Strict Mode - Enforces hash check on all files. If disabled, file modification
                           will be checked using size/date modified. Increases Overhead;
    - Create Task - Creates a new task in Windows Scheduler to run at specified intervals.
    - Remove Task - Remove a previously created task from Windows Scheduler.
    - Sync Now - Sync immediately and then start schedule if enabled.

Depending on the set flags, it can run in intervals by keeping the CMD/IDE open,
or it can create a task in Windows Task Scheduler to run it periodically.

For more information check the repository at https://github.com/PedroACFerreira/File_Sync

Checked for compatibility with vermin:
Compatible with Python 3.6+
Compatible with Python 3+ by removing f-strings
Linted with Pylint
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Combobox, Spinbox
import os
import multiprocessing
import file_sync_extended


def browse_source():
    """ Browse to select source folder and update source entry in tkinter."""
    source_path = filedialog.askdirectory(title="Select Source Folder")
    if source_path:
        entry_source.delete(0, 'end')
        entry_source.insert(0, source_path)
        update_submit()


def browse_replica():
    """ Browse to select replica folder and update replica entry in tkinter."""
    replica_path = filedialog.askdirectory(title="Select Replica Folder")
    if replica_path:
        entry_replica.delete(0, 'end')
        entry_replica.insert(0, replica_path)
        update_submit()


def browse_log():
    """ Browse to select log file and update log entry in tkinter.
    Provide default as script path."""
    log_file = filedialog.asksaveasfilename(defaultextension=".log",
                                            filetypes=[("Log files", "*.log")],
                                            title="Save Log File",
                                            initialdir= os.getcwd(),
                                            initialfile="logfile.log")

    if log_file:
        entry_log.delete(0, 'end')
        entry_log.insert(0, log_file)


def update_submit():
    """ Check conditions to enable submit button. Source and Replica need to be selected."""
    if entry_source.get() and entry_replica.get() and entry_log.get():
        btn_submit.config(state="normal")
    else:
        btn_submit.config(state="disabled")


def check_paths(source,replica,log):
    """ Check if selected paths are valid, prompt for correction if needed."""
    message = ""
    if not os.path.isdir(source):
        message += "Source Folder\n"
    if not os.path.isdir(replica):
        message += "Replica Folder\n"
    if not os.path.isdir(os.path.dirname(log)):
        message += "Log\n"
    if message:
        messagebox.showerror("Invalid Path",
                             f"The path to the:\n{message}is not valid or does not exist.")
        return False
    if source == replica:
        messagebox.showerror("Invalid Path",
                             "The Source and Replica folders cannot be the same.")
        return False
    return True


def on_multi_toggle():

    """ Toggle number of cores selection if multiprocessing is selected."""
    if var_multi.get() == 1:
        countprocnum.config(state="normal")
    else:
        countprocnum.config(state="disabled")




def on_submit():
    """ After submitting values, parse and pass to synchronization function."""

    source_folder = entry_source.get()
    replica_folder = entry_replica.get()

    # Just in case user deletes the default log path.
    if entry_log.get():
        log_file = entry_log.get()
    else:
        log_file = os.getcwd()+r"\logfile.log"

    # Run if paths are valid.
    if check_paths(source_folder,replica_folder,log_file):

        settings.update({
                        "source": source_folder,
                        "replica": replica_folder,
                        "log": log_file,
                        "interval": int(entry_interval.get()),
                        "unit": combo_interval_unit.get(),
                        "multi": var_multi.get(),
                        "procnum": int(countprocnum.get()),
                        "strict": var_strict.get(),
                        "sched": var_sched.get(),
                        "remove": var_rem.get(),
                        "now": str(var_now.get()),
                        "Run": True
                        })

        # Confirmation boxes after validation, give option to cancel
        # Tell user to keep window open if sched was not selected.
        if not settings["sched"]:
            root.withdraw()
            result = messagebox.askquestion("Start Sync?",
                                            "Settings validated! Click YES to start syncing!\n"
                                            "Keep IDE or CMD open.\n"
                                            "Click NO to cancel.")
            if result == "no":
                settings["Run"] = False
                root.deiconify()
            else:
                root.destroy()
        else:
            root.withdraw()
            result = messagebox.askquestion("Start Sync?",
                                            "Settings validated!\n"
                                            "Click YES to create task and start syncing!\n"
                                            "Click NO to cancel.")
            if result == "no":
                settings["Run"] = False
                root.deiconify()
            else:
                root.destroy()


def on_help():
    """ Help message for the help button."""

    messagebox.showinfo("Help",
    """This GUI lets you setup a one-way sync between two folders.
    Source folder will be replicated in the Replica Folder.
    Here is an explanation of all options:
        - Source - Select source path;
        - Replica - Select replica path;
        - Sync Interval - Select how long it will be between each sync. Whole numbers only;
        - Log - Path to logfile. Write the name of the file as *.log ;
        - Multiprocessing - Enable multiprocessing to speed up synchronization;
        - Number of processes - Select number of processes to be used;
        - Enable Strict Mode - Enforces hash check on all files. If disabled, file modification will be checked using size/date modified. Increases Overhead;
        - Create Task - Creates a new task in Windows Scheduler to run at specified intervals.
        - Remove Task - Remove a previously created task from Windows Scheduler.
        - Sync Now - Sync immediately and then start schedule if enabled.
        
    For more help, refer to: github.com/PedroACFerreira/File_Sync
    """)


def validate_number_input(p):
    """ Function to restrict input to integers, used for interval and procnum. """
    return p.isdigit()


# Main GUI setup
root = tk.Tk()
root.title("Folder Sync")
root.resizable(False, False)  # Disable window resizing.

# Source folder input.
tk.Label(root, text="Source Folder:").grid(row=0, column=0)
entry_source = tk.Entry(root, width=40)
entry_source.grid(row=0, column=1)
btn_browse_source = tk.Button(root, text="Browse",
                              command=browse_source)
btn_browse_source.grid(row=0, column=2)

# Replica folder input.
tk.Label(root, text="Replica Folder:").grid(row=1, column=0)
entry_replica = tk.Entry(root, width=40)
entry_replica.grid(row=1, column=1)
btn_browse_replica = tk.Button(root, text="Browse",
                               command=browse_replica)
btn_browse_replica.grid(row=1, column=2, padx = 10)

vcmd = (root.register(validate_number_input), '%P')

# Sync interval input. Default 10 min.
tk.Label(root, text="Sync Interval:", width=27).grid(row=2, column=0)
entry_interval = tk.Entry(root, width=5,
                          validate='key',
                          validatecommand=vcmd)
entry_interval.grid(row=2, column=1, sticky="w")
entry_interval.insert(0, "10")
combo_interval_unit = Combobox(root, values=["Minutes", "Hours", "Days", "Weeks", "Months"],
                               state="readonly", width=10)
combo_interval_unit.grid(row=2, column=1, padx=100)
combo_interval_unit.set("Minutes")

# Log file input.
tk.Label(root, text="Log File:").grid(row=3, column=0)
entry_log = tk.Entry(root, width=40)
entry_log.insert(0, os.getcwd()+r"\logfile.log")
entry_log.grid(row=3, column=1)
btn_browse_log = tk.Button(root, text="Browse",
                           command=browse_log)
btn_browse_log.grid(row=3, column=2)

# Frame to center multi checkbox and procNum.
multi_frame = tk.Frame(root)
multi_frame.grid(row=4, column=0, columnspan=3)

# Multiprocessing checkbox.
var_multi = tk.IntVar()
check_multi = tk.Checkbutton(multi_frame, text="Enable Multiprocessing",
                             variable=var_multi,
                             command=on_multi_toggle)
check_multi.pack(side="left", padx=20)

# Number of cores input. Default to 4. Only enable if multi is selected.
tk.Label(multi_frame, text="Number of Processes:").pack(side="left", padx=(10, 5))
max_procs = multiprocessing.cpu_count()
countprocnum = Spinbox(multi_frame, from_=1, to=max_procs, width=5,
                       validate='key',
                       validatecommand=vcmd)
countprocnum.pack(side="left")
countprocnum.insert(0, "4")
countprocnum['state'] = tk.DISABLED

# Frame to center strict, sched checkboxes.
checkbox_frame = tk.Frame(root)
checkbox_frame.grid(row=5, column=0, columnspan=3)

# Strict mode checkbox.
var_strict = tk.BooleanVar()
check_strict = tk.Checkbutton(checkbox_frame,
                              text="Enable Strict Mode",
                              variable=var_strict)
check_strict.pack(side="left", padx=20)

# Schedule checkbox.
var_sched = tk.BooleanVar()
check_sched = tk.Checkbutton(checkbox_frame,
                             text="Create Task in Windows Task Scheduler",
                             variable=var_sched)
check_sched.pack(side="left", padx=20)

# Frame to center strict, sched and run now checkboxes.
checkbox_frame = tk.Frame(root)
checkbox_frame.grid(row=6, column=0, columnspan=3)

# Remove checkbox.
var_rem = tk.IntVar()
check_now = tk.Checkbutton(checkbox_frame,
                           text="Remove previous task?",
                           variable=var_rem)
check_now.pack(side="left", padx=10)

# Run now checkbox.
var_now = tk.IntVar()
check_now = tk.Checkbutton(checkbox_frame,
                           text="Sync Now?",
                           variable=var_now)
check_now.pack(side="left", padx=10)

# Frame to center submit and cancel buttons.
button_frame = tk.Frame(root)
button_frame.grid(row=7, column=0, columnspan=3, pady=(10, 20))

# Submit button.
# Settings dictionary to be updated in the function on_submit.
settings = {"Run":False}

btn_submit = tk.Button(button_frame, text="Submit", command=on_submit, state="disabled")
btn_submit.pack(side="left", padx=10)

# Cancel button.
btn_cancel = tk.Button(button_frame, text="Cancel", command=root.destroy)
btn_cancel.pack(side="left")

# Help button.
btn_help = tk.Button(button_frame, text="Help", command=on_help)
btn_help.pack(side="left", padx=10)

if __name__ == "__main__":
    root.mainloop()

    if settings["Run"]:
        file_sync_extended.main(gui=True, source=settings["source"],
                                replica=settings["replica"], log=settings["log"],
                                interval=settings["interval"], unit=settings["unit"],
                                multi=settings["multi"], procnum=settings["procnum"],
                                strict=settings["strict"], sched=settings["sched"],
                                remove=settings["remove"], now=settings["now"])
