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
- If the score for the best one is high enough, output the best match (uncertainty outputs multiple matches and specially marked on the GUI)
- Display results on the user interface using eel and html/JS.

In addition:
- Check kingdom every few seconds by running a classifier on the purple coin counter
- Recognize moon names as they come (similar to Talkatoo processing) and automatically mark on the GUI
- Recignize story/multi moon names as they come (similar to Talkatoo processing) and automatically mark on the GUI
