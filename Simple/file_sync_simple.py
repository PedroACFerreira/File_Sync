"""
Script produced as a task to Veeam Software by Pedro Ferreira.
This is a simplified version.
This script will perform a one-way sync between two folders.
To check for file modification, it uses size or modified date.
If strict flag is set, it will use hashing to verify modified files.
Also uses hashing to verify files after copy, to ensure no corruption.
xxHash algorithm is used for its speed and safety.
All alterations made to the target folder are logged in a separate file.

This function can be run from CMD with args or IDE using main().

Here is an explanation of all options:
    - Source - Select source path;
    - Replica - Select replica path;
    - Interval - Select how long it will take between each sync. Whole numbers only;
    - Log - Path to logfile. Write the name of the file as *.log ;
    - Strict - Enforces hash check on all files. If disabled, file modification
                           will be checked using size/date modified. Increases Overhead;
    - Now - Option to sync now and continue on interval, or just sync now and stop.

Example usage in CMD:

 python file_sync_simple.py "-s C:/Users/<username>/Desktop/<SourceFolder>
                               -r C:/Users/<username>/Desktop/<ReplicaFolder>"
                               -i 10
                               -u Minutes
                               -l C:/Users/<username>/Desktop/logfile.log"
                               --now 1"

Inputs are verified with appropriate error message outputs.
It can run in set intervals by keeping the CMD/IDE open.

All packages apart from xxHash are native to Python.

For more information check the repository at https://github.com/PedroACFerreira/File_Sync

Checked for compatibility with vermin:
Compatible with Python 3.6+
Compatible with Python 2.7+/3.2+ by removing f-strings
Linted with Pylint
"""

# Import required packages
import argparse
import logging
import os
import shutil
import time
import sys
import subprocess

# Check if xxhash is installed, and if not, install it using pip.
try:
    import xxhash
except ImportError:
    print("xxhash is not installed. Installing it now...")
    try:
        if "VIRTUAL_ENV" in os.environ:
            # Check if we are in a virtual environment, remove --user flag.
            subprocess.check_call([sys.executable, "-m", "pip", "install", "xxhash"])
        else:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "xxhash"])
        import xxhash  # Import after installation.
    except Exception as e:
        print(f"Error: Could not install xxhash. Details: {e}")
        sys.exit(1)


def setup_logger(log_file):
    """ Set up the logger according to the defined path. """

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create a file handler and set its encoding to utf-8.
    file_handler = logging.FileHandler(log_file, encoding='utf-8')

    # Create a stream handler to log to console.
    stream_handler = logging.StreamHandler()

    # Create a formatter and set it for both handlers.
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # Add handlers to the logger.
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger

def calculate_xxhash(file_path, chunk_size=4096):
    """ Use the xxHash algorithm to generate hashes for every file."""

    hash_xx = xxhash.xxh64()  # Initialize an xxHash object (64-bit).

    # Open the file in binary read mode ('rb'), as the hash needs to work on raw bytes.
    with open(file_path, "rb") as f:
        # Iterate in chunks of 'chunk_size' bytes to avoid memory overflow on large files.
        for chunk in iter(lambda: f.read(chunk_size), b""):
            # Update the hash with each chunk of data read from the file.
            hash_xx.update(chunk)

    # Return the computed hash as a hexadecimal string.
    return hash_xx.hexdigest()


def normalize_path(input_path):
    """ Parse syntax of path input when calling script."""

    # Convert relative path to absolute path.
    abs_path = os.path.abspath(input_path)

    # Normalize the path (handles trailing slashes, mixed slashes).
    norm_path = os.path.normpath(abs_path)

    return norm_path


def modified_check(source_file, replica_file):
    """ Check if files were modified since last check"""

    if not os.path.exists(replica_file):
        return [False,0]  # Replica file doesn't exist, so it's considered "modified".

    source_stat = os.stat(source_file)
    replica_stat = os.stat(replica_file)

    # Compare size and modification times.
    if source_stat.st_size != replica_stat.st_size or source_stat.st_mtime != replica_stat.st_mtime:
        return [False,1]  # File is modified (size or time differs).

    return [True,1]  # File is considered unchanged.


def sync_directory(source_dir, replica_dir, strict, log):
    """ Synchronize the source and replica directories. """

    file_tasks = []  # Initialize tasklist.

    # Traverse the source directory tree.
    for root, _, files in os.walk(source_dir):
        relative_path = os.path.relpath(root, source_dir)
        if relative_path != ".":
            replica_root = os.path.join(replica_dir, relative_path)
        else:
            replica_root = replica_dir
        # Ensure the directory exists in the replica.
        if not os.path.exists(replica_root):
            os.makedirs(replica_root)

        # Add files that need to be copied/updated to a list.
        for file in files:
            source_file = os.path.join(root, file)
            replica_file = os.path.join(replica_root, file)
            check = modified_check(source_file, replica_file)
            if strict:
                if not check[0]:
                    log.info(copy_validate(source_file, replica_file, log, check[1]))
                elif calculate_xxhash(source_file) != calculate_xxhash(replica_file):
                    log.info(copy_validate(source_file, replica_file, log, check[1]))
            elif not check[0]:
                log.info(copy_validate(source_file, replica_file, log, check[1]))


def copy_validate(original_file, replica_file, log, check):
    """ Copy and validate files and return the result to the main process for logging. """

    retry_count = 0
    max_retries = 3  # Moved inside to avoid passing too many parameters

    while retry_count <= max_retries:
        try:

            # Perform the copy operation.
            shutil.copy2(original_file, replica_file)

            # Calculate hashes.
            source_hash = calculate_xxhash(original_file)
            replica_hash = calculate_xxhash(replica_file)

            # Check if the hashes match to check for corruption after copy.
            if source_hash == replica_hash:
                if check:
                    return f"File updated successfully: {replica_file}"
                return f"File copied successfully: {replica_file} to {replica_file}"

            log.error(f"Hash mismatch detected! Original: "
                      f"{original_file}, Replica: {replica_file}. Retrying...")
            retry_count += 1

        except Exception as error:
            log.error(f"Error copying file: {original_file} to {replica_file}: {error}")
            retry_count += 1

    return f"Failed to copy {original_file} after {max_retries} attempts"


def cleanup_replica(source_dir, replica_dir, log):
    """ Remove files and directories that no longer exist from Replica folder. """

    # Walk directories with topdown=False to log all deleted files and directories.
    for root, dirs, files in os.walk(replica_dir, topdown=False):
        relative_path = os.path.relpath(root, replica_dir)
        source_root = os.path.join(source_dir, relative_path)

        # Remove files that no longer exist in the source directory and log.
        for file in files:
            source_file = os.path.join(source_root, file)
            replica_file = os.path.join(root, file)
            if not os.path.exists(source_file):
                os.remove(replica_file)
                log.info(f"File removed: {replica_file}")

        # Remove directories that no longer exist in the source directory and log.
        for currdir in dirs[:]:
            source_dir_path = os.path.join(source_root, currdir)
            replica_dir_path = os.path.join(root, currdir)
            if not os.path.exists(source_dir_path):
                shutil.rmtree(replica_dir_path)
                log.info(f"Directory removed: {replica_dir_path}")
                dirs.remove(currdir)


def synchronization(source, replica, logfile, strict):
    """ Main synchronization function."""

    log = setup_logger(logfile)
    sync_directory(source, replica, strict, log)
    cleanup_replica(source, replica, log)

def unit_conv(unit):
    """ Check if unit variable is valid"""
    if unit in ("minutes", "m"):
        return "MINUTES"
    if unit == ("hours", "h"):
        return "HOURS"
    if unit == ("days", "d"):
        return "DAYS"

    print("Chosen units are not correct. "
          "Please input m (Minutes), h (Hours), d (Days)")
    sys.exit(0)


def check_paths(source, replica, log):
    """ Check if provided paths are valid, specify which aren't if needed."""

    message = ""
    if not os.path.isdir(source):
        message += "Source Folder\n"
    if not os.path.isdir(replica):
        message += "Replica Folder\n"
    if not os.path.isdir(os.path.dirname(log)):
        message += "Log\n"
    if message:
        print(f"The path to the:\n{message}is not valid or does not exist.")
        sys.exit(0)
    if source == replica:
        print("Invalid Path", "The Source and Replica folders cannot be the same.")
        sys.exit(0)
    return True


def validate_inputs(source, replica, log, interval, unit, now):
    """ Run checks on all inputs and provide error messages if they are invalid. """

    check_paths(source, replica, log)  # Check paths.

    # Check if interval is integer.
    try:
        int(interval)
    except ValueError:
        print("Please input a whole number for the interval!")
        sys.exit(0)

    unit_conv(unit)  # Check units.

    # Check if now is one of the valid inputs.
    if now not in ("0", "1", "2"):
        print("Invalid now parameter. Please choose from:\n"
              "0 - Do nothing. | "
              "1 - Sync now and continue script. | "
              "2 - Just sync now and terminate.")
        sys.exit(0)


def run(source, replica, log_file, interval, unit, strict, now):
    """ Run synchronization."""

    # If now is 1, synchronize and proceed. Sync and terminate if 2.
    if now == "1":
        synchronization(source, replica, log_file, strict)
        print(f"Synchronization complete. Next sync in {interval} {unit}.")
    elif now == "2":
        synchronization(source, replica, log_file, strict)
        sys.exit(0)
    else:
        print(f"Synchronization is starting. First sync in {interval} {unit}.")

    # Main loop for periodic sync in CMD or IDE, without task scheduling.
    while True:

        # Convert interval input to seconds.
        if unit_conv(unit) == "MINUTES":
            time.sleep(interval * 60)
        if unit_conv(unit) == "HOURS":
            time.sleep(interval * 3600)
        if unit_conv(unit) == "DAYS":
            time.sleep(interval * 86400)

        synchronization(source, replica, log_file, strict)
        print(f"Synchronization complete. Next sync in {interval} {unit}.")


# Main function to handle command line or default values.
def main(source=None, replica=None, log=os.path.join(os.getcwd(), "logfile.log"), interval="10",
         unit="Minutes", strict=False, now="0"):
    """
    Will handle calls from CMD and IDE.
    Default values are set for all except source and replica folder paths.
    """

    # Use argparse to handle CMD inputs.
    parser = argparse.ArgumentParser(description=
                                     "This script one-way syncs two folders. Use -h for help!"
                                     "Example usage: \n"
                                     "-s C:/Users/<username>/Desktop/<SourceFolder> "
                                     "-r C:/Users/<username>/Desktop/<ReplicaFolder> "
                                     "-i 10 "
                                     "-u Minutes"
                                     "-l C:/Users/<username>/Desktop/logfile.log"
                                     )
    parser.add_argument("-s", "-source", nargs='?', default="",
                        help="Source folder path.")
    parser.add_argument("-r", "-replica", nargs='?', default="",
                        help="Replica folder path.")
    parser.add_argument("-i", "-interval", nargs='?', type=int, default=10,
                        help="Sync interval in the selected unit. Default 10.")
    parser.add_argument("-u", "-unit", nargs='?', default="Minutes",
                        help="Unit of time. "
                             "m (Minutes), h (Hours), d (Days)")
    parser.add_argument("-l", "-logfile", nargs='?', default=os.path.join(os.getcwd(), "logfile.log"),
                        help="Log file path. " "Defaults to script directory.")
    parser.add_argument("--strict", action="store_true",
                        help="Hash check of all files regardless of state.")
    parser.add_argument("--now", type=int, default=0,
                        help="Flag to sync now. "
                             "0 - Do nothing. | "
                             "1 - Sync now and continue script. | "
                             "2 - Just sync now and terminate. ")
    args = parser.parse_args()

    # Check if arguments are provided (CMD), print help if not.
    # If arguments are not provided, run with main() function input.
    if not (args.s and args.r):
        if source and replica:

            # Validate inputs then run.
            validate_inputs(source, replica, log, interval, unit.casefold(), now)
            run(source, replica, log, int(interval), unit.casefold(), strict, now)

        # If no path arguments are passed, print help.
        else:
            parser.print_help()
            sys.exit("\nPlease input parameters! "
                     "Source and Replica folders are required! Use -h for help!")

    else:

        # If running from CMD, use provided arguments.
        source = normalize_path(args.s)
        replica = normalize_path(args.r)
        log_file = args.l
        interval = args.i
        unit = args.u
        strict = args.strict

        # Validate inputs then run.
        validate_inputs(source, replica, log, interval, unit.casefold(), now)
        run(source, replica, log_file, int(interval), unit.casefold(), strict, now)

if __name__ == "__main__":
    # To run from IDE, provide inputs to main.
    main()


