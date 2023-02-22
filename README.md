# Talkatoo Translator

The goal of this project was to create a tool for recognizing and translating the moon names mentioned by Talkatoo in Super Mario Odyssey, which would allow you to do runs of Talkatoo% in any language you want, and could be a significant timesave over English. Currently, Simplified Chinese, Traditional Chinese, and Korean have been proven successful, and Japanese is usable. Other languages are still in testing phases.

To set up, you'll need Python 3 installed. Any OS may be used. Make sure to install the libraries listed at the beginning of Talkatoo.py (use comments). Once running, use the Settings tab in the user interface to ensure you're using the right video source and change any run-dependent variables you choose.


For those curious, here's a more detailed description of the Talkatoo translation process:
- Pull raw image from USB capture card (using cv2 and PIL)
- Turn partial image into black text on a white background
- Run text checker algorithm
- If text is possible, run Optical Character Recognition
- Clean up OCR output by removing whitespace, replacing common mistakes, etc.
- Check string matches to all moons in the current kingdom using a score function
- If the score for the best one is high enough, output the best match (uncertainty outputs multiple matches and specially marked on the GUI)
- Display results on the user interface using eel and html/JS.

In addition:
- Check kingdom every few seconds by running a classifier on the purple coin counter
- Recognize moon names as they come and automatically mark on the GUI
- Recignize story/multi moon names as they come and automatically mark on the GUI


Troubleshooting:

"Nothing is working"
The most likely case is that you're either looking at the wrong video source, or that your capture card borders are improperly set. This can be fixed in the GUI, where you can set the video source and check sample images to see if it looks right.
Another possible issue is run speed. This program has typically been somewhere around 30fps on average, and this is what it's designed for. On especially old/slow machines where framerate drops below ~15, this may prove to be a problem, and the best thing to do is ensure that Python is running in the foreground with limited background activity. For Linux/Mac, you can also consider changing the line "p.nice(15)" to "p.nice(20)".
The final possible issue is that your capture card has highly distorted colors (distorted dimensions also, to a lesser extent). We do not currently have a color correction algorithm in place.

"I just switched languages in the GUI, now it's not working!"
Switching between languages takes time. For languages you've used before, it's a matter of a few seconds, but for languages that you haven't used for, you'll need to wait for the new language data to be downloaded, which may take a short while (typically less than 30s).
