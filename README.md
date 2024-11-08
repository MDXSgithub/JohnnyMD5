Overview:

This application provides a simple bare bones graphical user interface (GUI) for calculating MD5 checksums of files in specified directories. The app name comes from the movie "Short Circuit" in which the robot Johnny 5 proclaims "I'm alive" - so now he is alive and doing MD5. 

It allows users to select multiple directories, calculate the MD5 hash for all files within those directories, and display the progress for each directory. The application is built using the Tkinter library in Python.

Features:

- Add Multiple Directories: Users can add multiple base directories and select subdirectories for processing.
- MD5 Checksum Calculation: Computes the MD5 checksum for each file in the selected directories.
- Progress Display: Shows the progress of the checksum calculation for each directory.
- Logging: Provides detailed logging of the checksum calculation process.
- Debug Mode: Option to enable detailed debug logging.
- Recalculation Option: Option to recalculate checksums even if they already exist.

Requirements
Python 3.x
Tkinter library (included with Python standard library)

How to Run:
- Download the Script
- Ensure you have the script file (md5_checksum_calculator.py) on your local machine.
- Run the Script
- Open a terminal or command prompt, navigate to the directory containing the script and run johnnymd5.py

Using the Application

Add a Base Directory:
Click the "Browse" button to select a base directory.
The application will list any subdirectories within the selected base directory.
You can select specific subdirectories if needed.
Add More Directories:

Click "Add Another Base Directory" to add more directories.
You can add up to five base directories.

Configure Options

Debug: 
Check this option to enable detailed debug logging.
Recalculate: Check this option to force recalculation of MD5 checksums even if they already exist.

Start the Process:
Click the "Start" button to begin the checksum calculation.
Progress will be displayed for each directory.

View Logs:
Logs will be displayed in the text area within the application.
Logs are also saved to md5_log.txt in the directory from which you ran the script.

Example Usage:
Run the script to open the application window.
Add a base directory by clicking "Browse" and selecting the directory.
Optionally, select subdirectories from the listed options.
Click "Add Another Base Directory" to add more directories if needed.
Configure options by checking "Debug" for detailed logging or "Recalculate" to force checksum recalculations.
Click "Start" to begin the checksum calculation process.
Monitor progress and view the logs in the text area or in the md5_log.txt file, located in the directory from which the script was run.
