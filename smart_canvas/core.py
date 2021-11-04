""" core.py """

# Default packages

# External packages
import cv2
import numpy as np
from threading import Thread

# Internal packages
from . import filtering
from . import background
from . import gestureDetection


class CanvasCore:
    def __init__(self, frame=None):

        self.current_filter = filtering.catalog[next(filtering.carousel)]
        self.framecount = 0
        self.pictureframe = None
        self.delaycounter = 0
        self.filtercounter = 0
        self.frame = frame
        self.stopped = False
        self.frameout = frame

        self.gesture_debounce = 0

    def create_background(self, frame):
        background.foregroundMask(frame)

    def process(self):
        while not self.stopped:
            self.frameout = self.frame
            # Fix this to use timers and not fck frames!!
            if self.delaycounter > 0:
                self.delaycounter -= 1
                self.frameout = self.pictureframe
            if self.gesture_debounce > 0:
                self.gesture_debounce -= 1
            if self.filtercounter > 0:
                self.filtercounter -= 1
                cv2.putText(self.frame, self.current_filter.__name__, (45, 375), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)
                self.frameout = self.frame
            if self.framecount < 50:  # make a reference background out of 50 frames
                self.pictureframe = self.frame
                background.foregroundMask(self.frame)
            self.run_gesture()
            self.framecount += 1
            
    def run_gesture(self):
        finger_count = gestureDetection.detect_fingercount(self.frame)

        if finger_count == 2:
            if self.gesture_debounce == 0:
                self.current_filter = filtering.catalog[next(filtering.carousel)]
                self.filtercounter = 50
                self.gesture_debounce = 20
        if finger_count == 5:  # take a picture and process it
            fgmask = background.foregroundMask(self.frame)
            masked_frame = cv2.bitwise_and(self.frame, self.frame, mask=fgmask)
            handled_frame = self.current_filter(masked_frame)
            self.pictureframe = handled_frame
            self.delaycounter = 100



    def start(self):
        Thread(target=self.process, args=()).start()
        return self

    def stop(self):
        self.stopped = True

