# Simple Version

file_sync.py provides a simple script to set up folder synchronization.

Run directly from IDE or CMD and keep it open to synchronize at defined intervals.
All packages used are native to python with the exception of xxHash, which the script attempts to install using pip.

## Operation

To check for file modification, it uses size or modified date. If strict flag is set, it will use hashing to verify modified files.  
Also uses hashing to verify files after copy, to ensure no corruption. xxHash algorithm is used for its speed and safety.  
All alterations made to the target folder are logged in a separate file.

## Options

- Source - Select source path;
- Replica - Select replica path;
- Sync Interval - Select how long it will be between each sync. Whole numbers only;
- Log - Path to logfile. Write the name of the file as *.log ;
- Enable Strict Mode - Enforces hash check on all files. If disabled, file modification
                       will be checked using size/date modified. Increases Overhead;
- Sync Now - Sync immediately and then start schedule if enabled.

## Usage example

Navigate to the script location in CMD and input:

`python file_sync.py "-s C:/Users/<username>/Desktop/<SourceFolder> -r C:/Users/<username>/Desktop/<ReplicaFolder>" -i 10
 -u Minutes -l C:/Users/<username>/Desktop/logfile.log" --now 1"`

This will sync the specified folders now and then in 10 minute intevals, and log it to logfile.log.

##
Checked for compatibility with vermin:  
Compatible with Python 3.6+  
Compatible with Python 2.7+/3.2+ by removing f-strings  
Linted with Pylint  

[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)
[![compatibility: vermin](https://img.shields.io/badge/vermin-3.6%2B-text?style=flat
)](https://github.com/netromdk/vermin)
