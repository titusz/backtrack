# -*- coding: utf-8 -*-
import pyaudio
from collections import deque
import wave
from threading import Thread
from Queue import Queue, Empty

# Python2 -> Tkinter / Python3 -> tkinter
try:
    from Tkinter import *
except ImportError:
    from tkinter import *
try:
    from ttk import *
    TTK = True
except ImportError:
    TTK = False

class BackTrackApp(object):

    def __init__(self):


        self.root = Tk()
        self.root.title('BackTrack v 0.1')
        if TTK:
            self.mainframe = Frame(self.root, padding="12 12 12 12")
        else:
            self.mainframe = Frame(self.root)
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Buttons
        self.btn_listen = Button(self.mainframe, text='Listen',
            command=self.listen).grid(column=0, row=0, sticky=W)
        self.btn_save = Button(self.mainframe, text='Save',
            command=self.save).grid(column=1, row=0, sticky=E)

        # Statusbar
        self.statusmsg = StringVar()
        self.statusmsg.set('Click Listen to start listening!')
        self.lbl_status = Label(self.mainframe, textvariable=self.statusmsg,
            anchor=W)
        self.lbl_status.grid(column=0, row=1, columnspan=2, sticky=(W,E))


        # Audio listening Process
        self.signal_queue = Queue()
        self.process = Thread(target=Listener, args=(self.signal_queue,))

    def listen(self):
        self.statusmsg.set('Starting listening process')
        self.process.start()
        self.statusmsg.set('Listening to Audio')

    def save(self):
        self.statusmsg.set('Saving Audio')
        self.signal_queue.put('STOOOOOP')

    def run(self):
        self.root.mainloop()

class Listener(object):

    def __init__(self, signal_queue, buffer_time=5):
        self.signal_queue = signal_queue
        self.buffer_time = buffer_time + 1
        self.rate = 44100
        self.chunk = 1024
        self.buffer = deque(maxlen=self.rate / self.chunk * self.buffer_time)
        self.listen()

    def listen(self):
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        WAVE_OUTPUT_FILENAME = "output.wav"
        p = pyaudio.PyAudio()
        stream = p.open(format = FORMAT,
                        channels = CHANNELS,
                        rate = self.rate,
                        input = True,
                        frames_per_buffer = self.chunk)
        while True:
            data = stream.read(self.chunk)
            self.buffer.append(data)
            try:
                self.signal_queue.get_nowait()
                break
            except Empty:
                pass

        stream.close()
        p.terminate()

        data = ''.join(self.buffer)
        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(self.rate)
        wf.writeframes(data)
        wf.close()

if __name__ == '__main__':
    app = BackTrackApp()
    app.run()