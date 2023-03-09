# Talkatoo Translator

The goal of this project was to create a tool for recognizing and translating the moon names mentioned by Talkatoo in Super Mario Odyssey, which would allow you to do runs of Talkatoo% in any language you want, and could be a significant timesave over English. Currently, Simplified Chinese, Traditional Chinese, and Korean have been proven successful. All other languages are mostly usable but not fully tested/optimized.

# Setup Instructions (no programming required)
To set up, you'll need Python 3 installed. Go to https://www.python.org/downloads/ and download the newest version.
- If you use the installer, make sure to check the box that says "install pip", as well as the one that adds Python to your PATH
- Otherwise, install pip following these instructions: https://pip.pypa.io/en/stable/installation/

Make sure to install the libraries listed in requirements.txt
- Run "cd talkatoo_path" in the command line/terminal on your machine, where talkatoo_path is the full file path to your talkatoo directory
- Run "pip install -r requirements.txt"
- Note that if one or more don't work, you'll need to install them separately.

To run the program:
- Command Line/Terminal:
    - Run "cd talkatoo_path" in the command line/terminal on your machine, where talkatoo_path is the full file path to your talkatoo directory
    - Run "python Talkatoo.py" on Windows, or "python3 Talkatoo.py" on Linux/Mac
- IDLE:
    - IDLE is a free Python interpreter that comes with Python. You can just open Talkatoo.py within IDLE and click "Run"
- Or use an interpreter of your choice


Important settings:
- When first starting the application the settings will open so you can make sure your capture card is selected and working
- Also make sure you select the correct game language in the settings because this language will be used for the moon recognition process

# How to use

- Kingdom transitions, receiving moons from Talkatoo and marking moons as collected should all work automatically
- In case the recognition does not work perfectly, you can also make changes to pending and collected moons in the GUI yourself
- To doublecheck specific moons you can use the total moon list that is being displayed per kingdom
- You can use this list to manually add moons by clicking on their name in case a moon does not get recognized by the tool at all
- If there are multiple possibilities for a moon received from Talkatoo you can select the correct option in the GUI
- The choice of a correct option out of multiple possibilities for a mentioned moon can be undone at any point
- If you collect a pending moon and it does not get recognized simply click on its name to manually mark it as collected
- If a moon was mentioned by Talkatoo before it was set to collected you can move it back to pending at any point by clicking on its name
- When hovering on pending or collected moons a delete button will be shown so wrong matches can be completely removed from both lists


# Troubleshooting
- "Nothing is working"
The most likely case is that you're either looking at the wrong video source, or that your capture card borders are improperly set. This can be fixed in the GUI, where you can set the video source and check sample images to see if it looks right.
The final possible issue is that your capture card has highly distorted colors (distorted dimensions also, to a lesser extent). We do not currently have a color correction algorithm in place.


- "It sometimes works"
The likely issue is run speed. This program has typically been somewhere around 30fps on average, and this is what it's designed for. On especially old/slow machines where framerate drops below ~15, this may prove to be a problem, and the best thing to do is ensure that Python is running in the foreground with limited background activity. You can try changing RUN_FASTER to True (towards the top of Talkatoo.py), which ensures that your computer highly prioritizes this program over others. 

  

# Misc
For those curious, here's a more detailed description of the Talkatoo translation process:
- Pull raw image from USB capture card (using cv2 and PIL)
- Turn partial image into black text on a white background
- Run text checker algorithm
- If text is possible, run Optical Character Recognition
- Clean up OCR output by removing whitespace, replacing common mistakes, etc.
- Check string matches to all moons in the current kingdom using a language-dependent score function
- If the score for the best one is high enough, send the best matches (uncertainty outputs multiple matches) to the GUI

In addition:
- Check kingdom every few seconds by running a classifier on the purple coin counter
- Recognize moon names as they come (similar to Talkatoo processing) and automatically mark on the GUI
- Recognize story/multi moon names as they come (similar to Talkatoo processing) and automatically mark on the GUI
- The GUI was build using the Vue Framework and communicates with the Python script using Eel (https://github.com/python-eel/Eel)
- Eel starts a local Bottle server on localhost:8083 when the Python script is run and allows bidirectional communication between Python and JS via websockets
- The source code of the gui can be found in the /vue directory but to run the tool only the bundled contents (generated with Vite) in /gui are necessary
- The GUI maintains its own state for pending and collected moons and can therefore add and remove moons from both lists without affecting the lists in Python



