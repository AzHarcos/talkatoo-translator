# Talkatoo Translator

The goal of this project was to create a tool for recognizing and translating the moon names mentioned by Talkatoo in Super Mario Odyssey. The completed project allows the user to do runs of Talkatoo% in any language SMO supports, and could be a significant timesave over English, as there is less text to scroll through in other languages. Currently, Simplified Chinese, Traditional Chinese, and Korean have been proven successful. All other languages are mostly usable but not fully tested/optimized.

# Setup Instructions (no programming required)
1. Download the zip or tar file of the latest release: https://github.com/AzHarcos/talkatoo-translator/releases
2. Find the ZIP file in your file system and unzip it in a location you can find. Here we'll use the example that you unzip to the folder C:/Users/biakko/Downloads/talkatoo, replace your path along the way as needed.

3. To run the application, you'll need Python 3 installed. While newer and some older versions will also work, testing was done on version 3.10.10, so this is the recommended version. You can find it here: https://www.python.org/downloads/release/python-31010/. If you're on Windows or Mac, the installer is likely easiest. If you're on Linux, you can use the tarball.
- If you use the installer, be sure to check the box that says "add python.exe to PATH" on the first screen, and then you can install the default packages. Should you wish to customize your installation, just make sure that the "pip" box is checked.
- Otherwise, you'll need to add Python to your PATH (https://realpython.com/add-python-to-path/) and install pip (https://pip.pypa.io/en/stable/installation/)

4. Open your terminal. If you're on Mac or Linux, it's an app called "Terminal", if you're on Windows then use the Command Prompt.
5. Run the command "python" by typing it out and pressing enter. On Mac and Linux you might need to use "python3" instead. If it gives an error, Python was not added to your PATH. Follow instructions here to fix this: https://realpython.com/add-python-to-path/.
6. Install the necessary dependencies
   - Run the command "cd talkatoo_path" in the terminal, replacing talkatoo_path with the full file path to your *inner* talkatoo directory. For example, "cd C:/Users/biakko/Downloads/talkatoo/talkatoo-translator-1.0.0-testing"
   - Run "pip install -r requirements.txt" to install the necessary packages
   - If pip is not properly installed, follow the instructions at https://pip.pypa.io/en/stable/installation/
   - If one or more installations don't work, you'll need to install the proper versions of the packages individually using "pip install package_name==version". An example, "pip install pillow==9.4.0".

# Run the program
To run the program:
- If you prefer to use your command line/terminal:
    - Run "cd talkatoo_path" in the command line/terminal on your machine, where talkatoo_path is your *inner* talkatoo directory (in this example, "C:/Users/biakko/Downloads/talkatoo/talkatoo-translator-1.0.0-testing")
    - Run "python Talkatoo.py" on Windows, or "python3 Talkatoo.py" on Linux/Mac
    - The program should now be running.
    - If you encounter errors, most likely you do not have the packages properly installed. For each one, run "pip show package_name" (ex. "pip show easyocr"). You'll see the version listed. If it does not match with the one in requirements.txt, then install the proper version according to the instructions in Setup step 5.
- IDLE:
    - IDLE is a free Python interpreter that comes with Python (unless you chose to exclude it in the custom installation). You can just open Talkatoo.py within the IDLE application and click "Run".
- Or use an interpreter of your choice (PyCharm, Spyder, Visual Studio Code, Geany, etc.)

# How to use
- In the settings menu, ensure that the video source is your capture card by clicking the "Preview Image" button.
- Ensure that the languages and toggles are set to your preferences.
- Kingdom transitions, receiving moons from Talkatoo and marking moons as collected should all work automatically
- In case the recognition does not work perfectly, you can also make changes to pending and collected moons in the GUI yourself
- To doublecheck specific moons you can use the total moon list that is being displayed on the right for each kingdom
- You can also use this list to manually add moons by clicking on their name in case a moon does not get recognized by the tool at all
- If there are multiple possibilities for a moon received from Talkatoo, you can select the correct option in the GUI
- If you collect a pending moon and it does not get recognized, click on its name to manually mark it as collected
- If a moon was mentioned by Talkatoo before it was set to collected, you can move it back to pending at any point by clicking on its name
- When hovering on pending or collected moons, a delete button will be shown so wrong matches can be completely removed from both lists


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
- Eel starts a local Bottle server on localhost:8083 when the Python script is run and allows bidirectional communication between Python and JS via websocket
- The source code of the gui can be found in the /vue directory but to run the tool only the bundled contents (generated with Vite) in /gui are necessary
- The GUI maintains its own state for pending and collected moons and can therefore add and remove moons from both lists without affecting the lists in Python
