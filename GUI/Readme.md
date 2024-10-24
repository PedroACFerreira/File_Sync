# GUI/Extended Version

Scripts to synchronize files and directories between two folders.
file_sync_gui.py provides a simple GUI to set the options for folder synchronization.

Tu run directly from CMD/IDE without GUI, use file_sync_extended.py

## Operation

To check for file modification, it uses size or modified date. If strict flag is set, it will use hashing to verify modified files.  
Also uses hashing to verify files after copy, to ensure no corruption. xxHash algorithm is used for its speed and safety.  
All alterations made to the target folder are logged in a separate file.  
Multiprocessing can be enabled to speed up operation with the defined number of processes.  
A task can be created in Windows Task Scheduler to automate synchronization at the defined intervals. 
Options are provided to automate removing the task if required.

## Options

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

## Usage Example (CMD)

Navigate to the script location in CMD and input:

`python file_sync_extended.py "-s C:/Users/<username>/Desktop/<SourceFolder> -r C:/Users/<username>/Desktop/<ReplicaFolder>" -i 1
 -u Days -l C:/Users/<username>/Desktop/logfile.log" --sched --multi --procnum 6 --now 1"`

This will sync the specified folders now and then every day, and log it to logfile.log. 
It will also enable multiprocessing with 6 processes. 
Sched is set to create a task in Windows Task Scheduler.

To use the GUI, just open file_sync_gui in CMD:  

![image](https://github.com/user-attachments/assets/75a56616-1bab-4f9f-8f6b-98d2b6fc088c)


##
Checked for compatibility with vermin:  
Compatible with Python 3.6+  
Compatible with Python 3.2+ by removing f-strings  
Linted with Pylint  

[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)
[![compatibility: vermin](https://img.shields.io/badge/vermin-3.6%2B-text?style=flat
)](https://github.com/netromdk/vermin)
