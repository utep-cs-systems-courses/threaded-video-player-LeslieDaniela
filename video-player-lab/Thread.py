#!/usr/bin/env python3


import threading
import cv2
import numpy as np


# global varaibles
videoFile = 'clip.mp4'
frameDelay = 42
delimiter = "\0"

class Queue:
    def __init__(self):
        self.queue = []
        self.lock = threading.Lock()
        self.full = threading.Semaphore(10)
        self.empty = threading.Semaphore(0)


    def enqueue(self, item):
        self.empty.acquire()
        self.lock.acquire()
        self.queue.append(item)
        self.lock.release()
        self.full.release()


    def dequeue(self):
        self.full.acquire()
        self.lock.acquire()
        item = self.queue.pop(0)
        self.lock.release()
        self.empty.release()
        return item


def extractFrames(frameQueue, fileName):
    # check for null values
    if fileName is None:
        raise TypeError
    if frameQueue is None:
        raise TypeError
    
    # Frame Count
    count = 0

    vidcap = cv2.VideoCapture(fileName)

    # read one frame
    success, image = vidcap.read()

    print(f'Reading frame {count} {success}')
    while success:
        # add frame to buffer
        frameQueue.enqueue(image)

        success, image = vidcap.read()
        print(f'Reading frame {count} {success}')
        count += 1

    print('Frames have been extracted...'); # signals that its done as per requirement
    frameQueue.enqueue(delimiter)


def convertToGrayscale(grayFrames, colorFrames):
    # check for null values
    if grayFrames is None:
        raise TypeError
    if colorFrames is None:
        raise TypeError

    count = 0 # initialize frame count

    colorFrame = colorFrames.dequeue() # get first color frame from colorFrames

    while colorFrame is not delimiter:
        print(f'Converting frame {count}')

        # convert the image to grayscale
        grayFrame = cv2.cvtColor(colorFrame, cv2.COLOR_BGR2GRAY)
        grayFrames.enqueue(grayFrame) # enqueue frame into the queue
        count += 1
        colorFrame = colorFrames.dequeue() # dequeue next color frame

    print('Conversion to grayscale complete') # signals that its done as per requirement
    grayFrames.enqueue(delimiter)

def displayFrames(frames):
    if frames is None:
        raise TypeError

    count = 0 # initialize frame count

    frame = frames.dequeue()

    while frame is not delimiter:
        print(f'Displaying frame {count}')

        # display the image in a window call "video"
        cv2.imshow('Video Play', frame)

        # wait 42ms (what was used in the demos) and check if the user wants to quit with (q)
        if cv2.waitKey(frameDelay) and 0xFF == ord("q"):
            break

        count += 1
        frame = frames.dequeue()

    print('Finished displaying all the frames') # signals that its done as per requirement
    cv2.destroyAllWindows() # cleanup windows

if __name__ == "__main__":

    colorFrames = Queue()
    grayFrames = Queue()

    # three functions needed: extract frames, convert frames to grayscale,
    # and display frames at original framerate (24fps)
    extractThread = threading.Thread(target = extractFrames, args = (colorFrames, videoFile))
    convertThread = threading.Thread(target = convertToGrayscale, args = (grayFrames, colorFrames))
    displayThread = threading.Thread(target = displayFrames, args = (grayFrames,)) # <- needed to suppress error

    # start threads
    extractThread.start()
    convertThread.start()
    displayThread.start()
