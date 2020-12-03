#!/usr/bin/env python3

import cv2
import threading
from ThreadQueue import ThreadQueue # separated ThreadQueue class for modularization

VIDEOFILE = "../clip.mp4" # video clip path
DELIMITER = "\0"
FRAMEDELAY = 42 # the answer to everything, as said in the demos

# based on extractFrames.py demo
def extractFrames(fileName, frameQueue):
    # check for null values
    if fileName is None:
        raise TypeError
    if frameQueue is None:
        raise TypeError

    count = 0 # initialize frame count

    vidcap = cv2.VideoCapture(fileName)

    # read one frame
    success, image = vidcap.read()

    print(f'Reading frame {count} {success}')
    while success:
        # add frame to buffer
        frameQueue.put(image)

        success, image = vidcap.read()
        print(f'Reading frame {count} {success}')
        count += 1

    print('Finished extracting frames'); # signals that its done as per requirement
    frameQueue.put(DELIMITER)

# based on convertGrayscale.py demo
def convertGrayscale(colorFrames, grayFrames):
    # check for null values
    if colorFrames is None:
        raise TypeError
    if grayFrames is None:
        raise TypeError

    count = 0 # initialize frame count

    colorFrame = colorFrames.obtain() # get first color frame from colorFrames

    while colorFrame is not DELIMITER:
        print(f'Converting frame {count}')

        # convert the image to grayscale
        grayFrame = cv2.cvtColor(colorFrame, cv2.COLOR_BGR2GRAY)
        grayFrames.put(grayFrame) # enqueue frame into the queue
        count += 1
        colorFrame = colorFrames.obtain() # dequeue next color frame

    print('Conversion to grayscale complete') # signals that its done as per requirement
    grayFrames.put(DELIMITER)

def displayFrames(frames):
    if frames is None:
        raise TypeError

    count = 0 # initialize frame count

    frame = frames.obtain()

    while frame is not DELIMITER:
        print(f'Displaying frame {count}')

        # display the image in a window call "video"
        cv2.imshow('Video Play', frame)

        # wait 42ms (what was used in the demos) and check if the user wants to quit with (q)
        if cv2.waitKey(FRAMEDELAY) and 0xFF == ord("q"):
            break

        count += 1
        frame = frames.obtain()

    print('Finished displaying all the frames') # signals that its done as per requirement
    cv2.destroyAllWindows() # cleanup windows

if __name__ == "__main__":

    colorFrames = ThreadQueue()
    grayFrames = ThreadQueue()

    # three functions needed: extract frames, convert frames to grayscale,
    # and display frames at original framerate (24fps)
    extractThread = threading.Thread(target = extractFrames, args = (VIDEOFILE, colorFrames))
    convertThread = threading.Thread(target = convertGrayscale, args = (colorFrames, grayFrames))
    displayThread = threading.Thread(target = displayFrames, args = (grayFrames,)) # <- needed to suppress error

    # start threads
    extractThread.start()
    convertThread.start()
    displayThread.start()