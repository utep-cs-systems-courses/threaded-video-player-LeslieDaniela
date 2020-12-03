import threading

class ThreadQueue(): # queue implemented with python list
    def __init__(self):
        self.queue = []
        self.lock = threading.Lock()
        self.full = threading.Semaphore(10)
        self.empty = threading.Semaphore(0)

    def put(self, item): # enqueue
        self.empty.acquire()
        self.lock.acquire()
        self.queue.append(item)
        self.lock.release()
        self.full.release()

    def obtain(self): # dequeue
        self.full.acquire()
        self.lock.acquire()
        item = self.queue.pop(0)
        self.lock.release()
        self.empty.release()
        return item
