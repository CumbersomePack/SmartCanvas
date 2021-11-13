""" core.py """

# Default packages

# External packages
import cv2
import numpy as np
from threading import Thread
import time

# Internal packages
from smart_canvas.background import ForegroundMask
from smart_canvas.gesture_detection import HandDetect
from smart_canvas.filters.carousel import FilterCarousel


class CanvasCore:
    """
    Class that processes the frame with a dedicated thread.
    """

    def __init__(self):
        self.first_frame_in = False
        self.first_frame_in_old = False

        self.frame = None
        self.stopped = False
        self.out_frame = None
        self.tick = time.time()

        self.fg_masker = ForegroundMask()
        self.fg_mask = None

        self.hand_detector = None
        self.finger_count = 0

        self.filters = FilterCarousel()
        self.filtered_frame = None

        self.apply_filter_freeze_time = self.tick
        self.change_filter_freeze_time = self.tick
        self.create_background_freeze_time = self.tick + 5

    def change_filter(self):
        self.filters.next_filter()
        self.change_filter_freeze_time += 3

    def apply_filter(self, frame):
        fg_mask = self.fg_masker.apply(frame)
        masked_frame = cv2.bitwise_and(frame, frame, mask=fg_mask)
        self.filtered_frame = self.filters.current_filter(masked_frame)
        self.apply_filter_freeze_time += 5

    def process(self):
        while not self.stopped:
            time.sleep(0.01)
            self.tick = time.time()

            frame = self.frame
            if frame is None:
                continue
            
            self.first_frame_in = True

            if self.first_frame_in != self.first_frame_in_old:
                self.hand_detector = HandDetect(frame).start()

            self.first_frame_in_old = self.first_frame_in

            self.hand_detector.frame = frame

            apply_filter = (self.apply_filter_freeze_time - self.tick) > 0
            if apply_filter:
                self.out_frame = self.filtered_frame
                continue

            change_filter = (self.change_filter_freeze_time - self.tick) > 0
            if change_filter:
                cv2.putText(frame, self.filters.current_filter.__name__,
                            (45, 375), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            create_background = (self.create_background_freeze_time - self.tick) > 0
            if create_background:
                self.fg_masker.create_background(frame)
                continue

            finger_count = self.hand_detector.finger_count

            cv2.putText(frame, str(finger_count), (45, 45),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            self.out_frame = frame

            if apply_filter or change_filter or create_background:
                continue

            if finger_count == 2:
                self.change_filter()
                continue

            if finger_count == 5:
                self.apply_filter(frame)
                continue

            self.apply_filter_freeze_time = self.tick
            self.change_filter_freeze_time = self.tick
            self.create_background_freeze_time = self.tick

    def start(self):
        Thread(target=self.process, args=()).start()
        return self

    def stop(self):
        self.stopped = True
        if self.fg_masker is not None:
            self.fg_masker.stop()
        if self.hand_detector is not None:
            self.hand_detector.stop()
