from threading import Thread, Event
import cv2
from queue import Queue

class VideoRead:
    def __init__(self, src=0, q=None):
        self.stream = cv2.VideoCapture(src)
        self.stream.set(3, 1280)
        self.stream.set(4, 720)
        (self.status, self.frame) = self.stream.read()
        self.stopped = False
        self.frame_available = Event()
        self.queue = q

    def start(self,q=None):
        Thread(target=self.get, args=()).start()
        return self

    def get(self):
        while not self.stopped:
            if not self.status:
                self.stop()
            else:
                (self.status, self.frame) = self.stream.read()
                self.queue.put(self.frame)
                self.frame.flags.writeable = False
                self.frame_available.set()
                self.frame_available.clear()
        self.stream.release()

    def stop(self):
        self.stopped = True