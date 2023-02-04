# Talkatoo Translator

The goal of this project was to create a tool for recognizing and translating the moon names mentioned by Talkatoo in Super Mario Odyssey, which would allow you to do runs of Talkatoo% in any language you want and could be a significant timesave over English. The current version has only has been confirmed to work with Traditional and Simplified Chinese as these are what it is tuned for. Some languages have different text placement and our program currently does not work properly with these.

To set up, you'll need Python 3 installed. Any OS may be used. Make sure to install the libraries listed at the beginning of Talkatoo.py (use comments). Once running, use the Settings tab in the user interface to modify important variables, such as capture card image size.


For those curious, here's a more detailed description of the Talkatoo translation process:
- Pull raw image from USB capture card (using cv2 and PIL)
- Turn partial image into black text on a white background
- Run classifier to check if text is possible (weeds out a lot of unnecessary and extremely slow OCR passes)
- If all of this works, run Optical Character Recognition (takes about a second so very important to only do this when necessary)
- Clean up OCR output by removing whitespace, replacing common mistakes, etc.
- Check string matches to all moons in the current kingdom using a score function
- If the score for the best one is high enough, output the best match (uncertainty outputs multiple matches and specially marked on the GUI)
- Display results on the user interface using eel and html/JS.

In addition:
- Check kingdom every few seconds by running a classifier on the purple coin counter
- Recognize moon names as they come and automatically mark on the GUI (mostly successful)


Troubleshooting:

Problem: I don't see any moons appearing!
Solution: This program has typically been somewhere around 30fps on average, and this is what it's designed for. However, note that this number will decrease greatly when other apps/processes are running in the foreground, and a low framerate will give bad performance. If the program misses moons entirely, it's likely due to this, and the best solution is to close these and keep Python in the foreground.

Problem: Kingdom isn't changing or is changing to the wrong kingdom consistently
Solution: The kingdom is determined using a classifier, which was trained on cropped images. It uses a very small part of the image, and if the kingdom is consistently wrong, it's almost certainly due to poor cropping-which in turn would only happen in two cases: incorrect capture card image dimensions, and capture card borders.

Problem: It worked perfectly last time, why is nothing changing now?
Solution: The program automatically detects the capture card borders before starting its loop. So, if you start the program on a fully black screen, or on a screen with fully black sides, it may crop the image far too much and not work properly.
