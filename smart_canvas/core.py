""" core.py """

# Default packages

# External packages
import cv2
import numpy as np
from threading import Thread
import time

# Internal packages
import filtering
from gestureDetection import HandDetector

class CanvasCore:
    def __init__(self, frame=None):
        self.current_filter = filtering.catalog[next(filtering.carousel)]
        self.fg_mask = None
        self.pictureframe = None
        self.frame = None
        self.stopped = False
        self.frameout = None
        self.tick = time.time()
        self.apply_filter_freeze_time = self.tick
        self.change_filter_freeze_time = self.tick
        self.fgbg = cv2.createBackgroundSubtractorMOG2(history=240, varThreshold=150, detectShadows=False)
        self.bg_mask = None
        self.hand_detector = HandDetector(min_detection_confidence=0.9, max_num_hands=2)

    def change_filter(self):
        self.current_filter = filtering.catalog[next(filtering.carousel)]
        self.change_filter_freeze_time += 3

    def apply_filter(self):
        frame = self.frame
        masked_frame = cv2.bitwise_and(frame, frame, mask=self.bg_mask)
        self.pictureframe = self.current_filter(masked_frame)
        self.apply_filter_freeze_time += 5

    def process(self):
        while not self.stopped:
            frame = self.frame
            if frame is None:
                continue
            
            self.tick = time.time()
            self.bg_mask = self.fgbg.apply(frame)
            finger_count = self.hand_detector.count_fingers(frame)
           
            apply_filter_freeze = (self.apply_filter_freeze_time - self.tick) > 0
            if apply_filter_freeze:
                self.frameout = self.pictureframe
                continue

            change_filter_freeze = (self.change_filter_freeze_time - self.tick) > 0
            if change_filter_freeze:
                cv2.putText(frame, self.current_filter.__name__, (45, 375), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)

            cv2.putText(frame, str(finger_count), (45, 375), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)
            self.frameout = frame

            if apply_filter_freeze or change_filter_freeze:
                continue

            if finger_count == 2:
                self.change_filter()
                continue

            if finger_count == 5:
                self.apply_filter()
                continue

            self.apply_filter_freeze_time = self.tick
            self.change_filter_freeze_time = self.tick

    def start(self):
        Thread(target=self.process, args=()).start()
        return self

    def stop(self):
        self.stopped = True
