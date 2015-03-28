#!/usr/bin/env python3
import sys
import math
import tkinter as tk
from tkinter import filedialog
import itertools

from bisection_sequence import bisection_sequence
import sampled_response
import tkplot

class ResponsePlot(tkplot.TkPlot):
    def __init__(self, root, response, freqlim):
        tkplot.TkPlot.__init__(self, root, (9, 6))
        self.response = response
        self.freqlim = freqlim

        self.plot = self.figure.add_subplot(111)
        self.plot.set_xscale('log')
        self.plot.set_xlabel("Frequency (Hz)")
        self.plot.set_ylabel("Response (dB)")
        self.plot.set_xlim(*self.freqlim)
        self.plot.yaxis.set_ticks([-20, -12, -9, -6, -3, -1, 0])
        self.plot.set_ylim(-24, 0.5)
        self.line, = self.plot.plot(self.response.frequencies(), self.response.dbs(), marker='.')
        self.figure.tight_layout()

    def update(self):
        self.line.set_xdata(self.response.frequencies())
        self.line.set_ydata(self.response.dbs())
        self.figure.canvas.draw()


class Skardas:
    def __init__(self, root, start_freq, end_freq):
        self.root = root
        self.root.title("{}-{} Hz - skardas".format(start_freq, end_freq))

        self.response = sampled_response.SampledResponse()
        self.start_freq = start_freq
        self.end_freq = end_freq
        self.frequency = self.start_freq

        self.bisector = itertools.chain([0, 1], bisection_sequence(7))

        self.plot = ResponsePlot(self.root, self.response, (self.start_freq, self.end_freq))
        self.plot.pack(fill=tk.BOTH, expand=1)

        self.toolbar = tk.Frame(self.root)
        self.toolbar.pack(fill=tk.X)
        self.label = tk.Label(self.toolbar)
        self.label.pack(side=tk.RIGHT, fill=tk.BOTH, expand=1)
        self.save_button = tk.Button(self.toolbar, text="Save CSV", command=self.save_button_click)
        self.save_button.pack(side=tk.RIGHT)
        self.stop_button = tk.Button(self.toolbar, text="Stop", command=self.stop)
        self.stop_button.pack(side=tk.RIGHT)

    def save_button_click(self):
        f = filedialog.asksaveasfile(title="Save CSV", defaultextension='csv')
        if f:
            with f:
                self.response.write_csv(f)

    def stop(self):
        self.response.release_instruments()
        self.label.config(text="Sampling complete.")


    def sample(self):
        try:
            frequency = 10**((math.log10(self.end_freq) - math.log10(self.start_freq)) * next(self.bisector) + math.log10(self.start_freq))
            self.label.config(text="Sampling response at {} Hz".format(frequency))
            self.response.sample(frequency)
            self.plot.update()
            self.root.after(0, self.sample)
        except StopIteration:
            self.stop()

    def start(self):
        self.sample()

if __name__ == "__main__":
    assert(len(sys.argv) == 3)
    root = tk.Tk()
    root.geometry("1000x700")
    win = Skardas(root, float(sys.argv[1]), float(sys.argv[2]))
    win.start()
    tk.mainloop()
