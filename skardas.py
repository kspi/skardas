#!/usr/bin/env python3
import sys
import tkinter as tk
from tkinter import filedialog

from bisection_sequence import frequency_bisection_sequence
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


def execute_delayed(generator):
    """For each yielded value wait the given amount of time (in seconds)
    without pausing the Tkinter main loop.

    See 'slowmotion' in http://effbot.org/zone/tkinter-generator-polyline.htm
    """
    root.after(generator.next() * 1000, execute_delayed, generator)


class Skardas:
    def __init__(self, root, start_freq, end_freq):
        self.root = root
        self.root.title("{}-{} Hz - skardas".format(start_freq, end_freq))

        self.response = sampled_response.SampledResponse()
        self.start_freq = start_freq
        self.end_freq = end_freq

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
        for frequency in frequency_bisection_sequence(self.start_freq, self.end_freq, depth=7):
            self.label.config(text="Sampling response at {} Hz".format(frequency))
            yield from self.response.sample(frequency)
            self.plot.update()

    def start(self):
        execute_delayed(self.sample())

if __name__ == "__main__":
    assert(len(sys.argv) == 3)
    root = tk.Tk()
    root.geometry("1000x700")
    win = Skardas(root, float(sys.argv[1]), float(sys.argv[2]))
    win.start()
    tk.mainloop()
