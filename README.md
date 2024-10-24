# File Synchronization Script

File Sync script and optional GUI created as a task for Veeam Software.
The scripts here allow for two folders to be selected for one-way synchronization.

## Operation

There are two versions to this script: **Simplified** and **Extended** with an optional **GUI**.  
The simplified version is run from CMD or an IDE. It will allow for folder synchronization at defined intervals.
To check for file modification between the source and replica folder, it uses size or modified date by default.  
A flag (strict) can be set to enforce a hash check on all existing files to check for modifications. This is more accurate but increases overhead.
It always uses hashing to verify files after copy, to ensure no corruption. xxHash algorithm was chosen for its speed and safety.
All alterations made to the target folder are logged in a separate file defined by the user.  
   
In the Extended version, an option for multiprocessing was added, to speed up operation. The number of processes can be set by the user.  
Task scheduling for Windows OS was also added, to automate synchronization at the defined intervals. Uses Schtasks.  
An option for automated task removal was included.

A simple GUI was also created using Tkinter to provide an intuitive way to set up synchronization.  

Apart from xxHash, all included packages are native to Python. Scripts are compatible with Python 3.6+, or 3.2+ if f-strings are removed.

## Usage

Additional instructions can be found in the respective folder. A quick example of usage of the simple script:  

`python file_sync_simple.py" -s C:/Users/<username>/Desktop/<SourceFolder> -r C:/Users/<username>/Desktop/<ReplicaFolder>" -i 10
 -u Minutes -l C:/Users/<username>/Desktop/logfile.log" --now 1"`

This will sync the specified folders now and then in 10 minute intevals, and log it to logfile.log.

To use the GUI, simply open file_sync_gui.py in a CMD console.

## Possible Future Modifications

There are several possible additions and modifications to this script that could improve it if required:
- Alternative hashing algorithms can be implemented if required. Blake in particular would be more efficient for large files.
- The **Simple** version of the script is Linux/Unix compatible. The **Extended** version can be adapted by setting up task scheduling with cron.
- Additional settings can be added to task scheduling on Windows, like synchronization on log on or log off, finer interval or timing, and maximum task duration.
- If folders to be synchronized contain large amounts of small files, it could be useful to implement multithreading.
- Scripts are impletmented in a way that folder synchronization is only possible for the current user.
Additional paramenters could be set to allow for elevation or synchronization across users of the same computer with provided login details.
- Folder synchronization across the network could be implemented.
- An executable could be created to run folder synchronization on machines with no python installation. Requires script to be adapted.

##
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)
[![compatibility: vermin](https://img.shields.io/badge/vermin-3.6%2B-text?style=flat
)](https://github.com/netromdk/vermin)

