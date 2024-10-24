# File Synchronization Script

The scripts here allow for two folders to be selected for one-way synchronization.  
Includes a **Simple** and **Extended** script and optional an **GUI**.  
   
![GitHub License](https://img.shields.io/github/license/PedroACFerreira/File_Sync)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)
[![compatibility: vermin](https://img.shields.io/badge/vermin-3.6%2B-text?style=flat
)](https://github.com/netromdk/vermin)
[![CodeFactor](https://www.codefactor.io/repository/github/pedroacferreira/file_sync/badge)](https://www.codefactor.io/repository/github/pedroacferreira/file_sync)

## Operation
 
The simplified version of the script is run from CMD or an IDE. It will allow for folder synchronization at defined intervals.
   
To check for file modification between the source and replica folder, it uses size or modified date by default.  
A flag (strict) can be set to enforce a hash check on all existing files to check for modifications. This is more accurate but increases overhead.
It always uses hashing to verify files after copy, to ensure no corruption. xxHash algorithm was chosen for its speed and safety.
   
All alterations made to the target folder are logged in a separate file defined by the user.  
   
In the Extended version, an option for multiprocessing was added, to speed up operation. The number of processes can be set by the user.  
Task scheduling for Windows OS was also added to automate synchronization at the defined intervals. Uses Schtasks.  
Task remains operational after reboot. An option for automated task removal was included.

A simple GUI was also created using Tkinter to provide an intuitive way to set up synchronization.  

Apart from xxHash, all included packages are native to Python. Script attempts to install xxHash using pip.  
Scripts are compatible with Python 3.6+ (3.2+ if f-strings are removed).

## Usage

Additional instructions can be found in the respective folder. A quick example of usage of the simple script:  

`python file_sync_simple.py" -s C:/Users/<username>/Desktop/<SourceFolder> -r C:/Users/<username>/Desktop/<ReplicaFolder>" -i 10
 -u Minutes -l C:/Users/<username>/Desktop/logfile.log" --now 1"`

This will sync the specified folders now and then in 10 minute intervals, and log it to logfile.log.

To use the GUI, simply open file_sync_gui.py in a CMD console.

![image](https://github.com/user-attachments/assets/07f22926-4114-4dea-9617-6e65fc7bf44c)


## Possible Future Modifications

There are several possible additions and modifications to this script that could improve it if required:
- Alternative hashing algorithms can be implemented if required. Blake in particular would be more efficient for large files.
- The **Simple** version of the script is Linux/Unix compatible. The **Extended** version can be adapted by setting up task scheduling with cron.
- Additional settings can be added to task scheduling on Windows, like synchronization on log on or log off, finer interval or timing, and maximum task duration.
This would required using Powershell and the ScheduledTask module as Schtasks does not allow for fine tuning of these parameters.
- If folders to be synchronized contain large amounts of small files, it could be useful to implement multithreading.
- Currently local to current user, additional paramenters could be set to allow for elevation or synchronization across users of the same computer with provided login details.
- Folder synchronization across the network could be implemented.
- An executable could be created to run folder synchronization on machines with no python installation. Requires script to be adapted.

## Feedback

Scripts were developed for Veeam Software as a task. You can reach out to me at ferreira.pedro.ac@gmail.com for any questions!

