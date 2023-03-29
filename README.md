# Talkatoo Translator

The goal of this project was to create a tool for recognizing and translating the moon names mentioned by Talkatoo in Super Mario Odyssey. The completed project allows the user to do runs of Talkatoo% in any language SMO supports, and could be a significant timesave over English, as there is less text to scroll through in some other languages. It may also serve as a project of interest for those users looking to learn the moon names in other languages. Currently, Simplified Chinese and Traditional Chinese are the most optimized, Korean has typically been successful, and all other languages are mostly usable but not fully tested/optimized.

![image](https://user-images.githubusercontent.com/58895947/226770639-0f0ed7f8-4fac-45f6-9819-86bdd14fc301.png)

# Setup Instructions (no programming required)
1. Download the talkatoo-translator.zip file of the latest release: https://github.com/AzHarcos/talkatoo-translator/releases. For compatibility reasons, when downloading a version beyond 1.0.0, ensure that you download the version of the program corresponding to your OS. Version 1.0.1 added a window capture feature that is currently only supported on Windows, so Mac and Linux users will unfortunately run into errors trying to use the Windows release.
2. Find the downloaded zip file in your file system and unzip it in a location you can find. Here we'll use the example that you unzip to the folder ```C:/Users/biakko/Downloads/talkatoo-translator```, replace your path along the way as needed. Note that I will be using the test release, ```talkatoo-translator-1.0.0-testing```.

3. To run the application, you'll need Python 3 installed. While many other versions will also work(Python 3.11 does not), testing was done on version 3.10.10, so this is the recommended version. You can find the correct version here: https://www.python.org/downloads/release/python-31010/. If you're on Windows or Mac, the installer is likely easiest. If you're on Linux, you can use the tarball.
    - If you use the installer, be sure to check the box that says "add python.exe to PATH" on the first screen, and then you can use the default installation. Should you wish to customize your installation, be sure that the "pip" box is checked.
    - Otherwise, you'll need to manually add Python to your PATH (https://realpython.com/add-python-to-path/) and install pip (https://pip.pypa.io/en/stable/installation/).

4. Open your terminal. If you're on Mac or Linux, it's an app called "Terminal", if you're on Windows then use the Command Prompt. (If you're not sure how to find it, use the search bar).
5. Run the command ```python --version``` by typing it out and pressing the Enter key. On Mac and Linux you might need to use ```python3 --version``` instead. If it gives an error('python' is not recognized as an internal or external command, operable program or batch file), Python was likely not added to your PATH. Follow instructions here to fix this: https://realpython.com/add-python-to-path/. If it tells you that the version is 3.10.10, then it has been set up correctly. If it's another 3.X version, then your default version of Python is not 3.10.10, but your program will likely still work. If you still get an error, you can look here to try to fix the issue: https://stackoverflow.com/questions/24186823/python-not-recognized-in-windows-cmd-even-after-adding-to-path. But, if you don't want to bother, you can do the following. 
    - Search for "Python", and find the file path to an app called "Python 3.10 (64 bit)" or similar. Note that Windows might take you to the Shortcut filepath-if this is the case, then right-click on the Python app and go to its file location. You know if you're in the right spot if you see folders such as DLLs, Tools, Lib, Scripts.
    - Copy whatever this path is on your machine (i.e. ```C:/Python310/python.exe```) and use it instead of ```python``` for all of these commands. For example, ```C:/Python310/python.exe --version```.
6. Install the necessary dependencies (external Python code used within our project).
   - Run the command ```cd talkatoo_path``` in the terminal, replacing talkatoo_path with the full file path to your *inner* talkatoo directory (the one that contains the README, Talkatoo.py, and so on). For example, ```cd C:/Users/biakko/Downloads/talkatoo-translator/talkatoo-translator-1.0.0-testing```.
   - Run ```pip install -r requirements.txt``` to install the necessary packages (if this doesn't work, use the Python path from step 5 troubleshooting and replace it in the command ```C:/Python310/python.exe -m pip install -r requirements.txt``` instead).
   - If pip is not properly installed, follow the instructions at https://pip.pypa.io/en/stable/installation/ and try again.
   - If one or more installations don't work, you can try to install the proper versions of the packages individually using ```pip install package_name==version```. An example, ```pip install pillow==9.4.0```.

# Run the program
To run the program:
- If you prefer to use your command line/terminal:
    - Run ```cd talkatoo_path``` in the command line/terminal on your machine, where talkatoo_path is your *inner* talkatoo directory. In this example, the command is ```cd C:/Users/biakko/Downloads/talkatoo-translator/talkatoo-translator-1.0.0-testing```.
    - Run ```python Talkatoo.py``` on Windows, or ```python3 Talkatoo.py``` on Linux/Mac. As in earlier steps, you can also insert the path to your Python executable instead, such as ```C:/Python311/python.exe Talkatoo.py```.
    - The program should now be running (it may take several seconds to boot up).
- IDLE:
    - IDLE is a free Python interpreter that comes with Python (unless you chose to exclude it in the custom installation). You can just open Talkatoo.py within the IDLE application and select "Run" on the top menu, then "Run Module".
- Or use an interpreter of your choice (PyCharm, Spyder, Visual Studio Code, Geany, etc.).
If you encounter errors, you do not have the packages properly installed. You can check installation status and version using ```pip show package_name``` in your command line/terminal(ex. ```pip show easyocr```). If it does not match with the one in requirements.txt, then install the proper version according to step 5 of the Setup Instructions.

# How to use
- Select your personal preferences in the settings menu
    - Select your capture card as the video source and verify it's working by clicking "SHOW PREVIEW IMAGE".
    - Select your game language and other preferences.
- Kingdom transitions, receiving moons from Talkatoo and marking moons as collected will all work automatically.
- To double-check specific moons, you can use the complete moon list that is being displayed on the right side of the screen for each kingdom.
- In case the recognition does not work perfectly or you want to make changes, you can do so with the buttons in the GUI.
    - You can use the kingdom list to manually add moons to the pending list by clicking on the name.
    - If you collect a pending moon and it does not get recognized, click on its name to manually mark it as collected.
    - If the program erroneously marks a moon as collected, you can move it back to the pending list by clicking on it if it was previously mentioned by Talkatoo.
    - If there are multiple recognized possibilities for a moon received from Talkatoo, you can select the correct option in the GUI.
    - If multiple options are recognized for a collected moon, nothing will happen to ensure the wrong moon will not be not marked.
    - When hovering on pending or collected moons, a delete button will be shown so wrong matches can be completely removed from both lists.
- If you wish to display the list of pending moons in OBS, you can do so using the generated file ```pending-moons.txt``` in the talkatoo directory.
    - It will contain the pending moons of the currently selected kingdom in the GUI, ignoring entries with multiple possible moon options.
    - To display the list in OBS, add a new text source, check "Read from file" and select the file path to ```pending-moons.txt```.
    - If done successfully it might look like this:

![image](https://user-images.githubusercontent.com/59027253/227715367-f81cd632-0592-4beb-87d9-0bfe32b61bcd.png)

# Troubleshooting
- My capture card isn't showing up!
    - Some capture cards aren't allowed to be open in multiple places. If you have one of these and it's open in OBS or another place, then you won't be able to open it here. To solve this, there are a few options. For all of these, try to ensure your resolution is at least 1280x720.
        - The first solution is through our Video Stream player. This comes with the app as of v1.0.1, and you just need to enable it within the settings menu. It will play full-size video and audio from your capture card, which can be used as a Window Share in OBS. Please feel free to report any synchronization issues should they arise.
        - The second solution is also included in the Windows version of our app as of v1.0.1, using Window Sharing. With this, you can take your OBS canvas, pull out a Full Screen or Windowed Projector, and then use that as input for our program. We recommend creating the projector from the capture card source, but if you have reason to use your whole canvas, then just be sure not to cover any of the marked areas in the below image. Be sure to crop out ALL borders so you have the game covering the full preview image. Currently it must be almost exact.
        - The third and final option will only be helpful for those with Elgato cards and fairly high end PCs, called Elgato StreamLink. You can find out about it here: https://help.elgato.com/hc/en-us/articles/360028241631. For this you will also need NDI Webcam(Windows) or NDI Virtual Input(Mac), which can be installed with the NDI Tools package. This sends the capture card's video feed to a virtual camera that can be used as an input device in our program. You can download it here: https://ndi.tv/tools/#download-tools.
        - OBS Virtual Camera may seem appealing but it has not been able to produce a high enough resolution for us in testing and should not be expected to work well.
![Mario](https://user-images.githubusercontent.com/58895947/227270510-0471c263-b695-4e2c-8eef-d1427830ae74.jpg)


- Nothing is working!
    - The most likely case is that you're either looking at the wrong video source, or that your capture card borders are improperly set. This can be fixed in the GUI, where you can set the video source and check sample images to see if it looks right.
    - Also ensure that your input language is set correctly.
    - A rarer but possible issue is that your capture card has highly distorted colors or dimensions. We do not currently have correction algorithms in place. The best current fix on Windows is to try to correct the issues manually in OBS with filters/cropping and use a Projector and Window Share in our program. There's no great fix for Mac/Linux currently, let us know if you have any ideas.


- The program isn't switching kingdoms!
    - If you're using a window capture, this probably means your cropping is off. You can use our window cropping tool to fix this. If you're using a capture card, this likely means that you have the wrong video source chosen. Once it properly switches kingdoms, you know that you're all set up and the rest should work fairly well.


- The program sometimes misses moons from Talkatoo!
    - The likely issue is run speed. This program has typically been somewhere around 30fps on average, and this is what it's designed for. On old or slow or somewhat overloaded machines where framerate drops below ~15, this may prove to be a problem. The best fix is to ensure that Python is running in the foreground with limited background activity.
    - Be sure you're not running in the wrong version of Chinese, as to a non-speaker the two can look quite similar.
    - Other issues might involve capture card color/dimension distortion or resolution issues. Try to ensure your input resolution is 1280x720 or higher.
    
    
- The program sometimes recognizes the wrong moon!
    - Unfortunately, this is an external tool and we do not have perfect game information. We have done our best to make it as robust as possible, but it is not perfect. Sometimes, only partial words will be read, at others the characters will be incorrectly recognized or dropped, and in exceedingly rare cases some extraneous text or white pixels may count as Talkatoo text or a moon. You are welcome to check the output logs in the Python console and report failures to us for future improvement.


# Process
For those curious, here's a more detailed description of the Talkatoo translation process:
- Pull raw image from USB capture card (using cv2 and PIL)
- Turn partial image into black text on a white background
- Run text detection algorithm
- If text is possible, run Optical Character Recognition
- Clean up OCR output by removing whitespace, replacing common mistakes, etc.
- Check string matches to all moons in the current kingdom using a language-dependent score function
- If the score for the best one is high enough, send the best matches (uncertainty outputs multiple matches) to the GUI

In addition:
- Check kingdom every few seconds by running a classifier on the purple coin counter
- Recognize moon names as they come (similar to Talkatoo processing) and automatically mark on the GUI
- Recognize story/multi moon names as they come (similar to Talkatoo processing) and automatically mark on the GUI

GUI information:
- The GUI was build using the Vue Framework and communicates with the Python script using Eel (https://github.com/python-eel/Eel)
- Eel starts a local Bottle server on localhost:8083 when the Python script is run and allows bidirectional communication between Python and JS via websocket
- The source code of the gui can be found in the /vue directory but to run the tool only the bundled contents (generated with Vite) in /gui are necessary


# Reporting Issues
- To report any GUI bugs or display suggestions, message AzHarcos#8767 on Discord.
- To report failures in moon/text recognition, try to find the problematic part of the output logs in the Python console (if applicable) and send that and a description of what went wrong to biakko#9890 on Discord. Note that this program is very consistent but not perfect, and that any changes will typically require a large amount of reworking and testing.


# Credits
- AzHarcos - User Interface, Graphics
- Biakko - Moon Recognition
