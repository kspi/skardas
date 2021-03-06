import tkinter as tk
from tkinter import filedialog

from .bisection_sequence import frequency_bisection_sequence
from . import sampled_response
from . import tkplot


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
        self.plot.yaxis.set_ticks([-20, -12, -9, -6, -3, -1, 0, 1, 3, 6])
        self.plot.set_ylim(-24, 8)
        self.line, = self.plot.plot(self.response.frequencies(), self.response.dbs(), marker='.')
        self.figure.tight_layout()

    def update(self):
        self.line.set_xdata(self.response.frequencies())
        self.line.set_ydata(self.response.dbs())
        self.figure.canvas.draw()


def execute_delayed(root, generator):
    """For each yielded value wait the given amount of time (in seconds)
    without pausing the Tkinter main loop.

    See 'slowmotion' in http://effbot.org/zone/tkinter-generator-polyline.htm
    """
    try:
        root.after(int(next(generator) * 1000), execute_delayed, root, generator)
    except StopIteration:
        pass


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
        self.stop_button = tk.Button(self.toolbar, text="Stop", command=self.stop_button_click)
        self.stop_button.pack(side=tk.RIGHT)
        self.stop_sampling = False

    def set_status(self, status):
        self.label.config(text=status)

    def save_button_click(self):
        f = filedialog.asksaveasfile(title="Save CSV", defaultextension='csv')
        if f:
            with f:
                self.response.write_csv(f)

    def stop_button_click(self):
        self.stop_sampling = True

    def sample(self):
        self.set_status("Setting up instruments")
        yield from self.response.setup_instruments()
        for frequency in frequency_bisection_sequence(self.start_freq, self.end_freq, depth=7):
            if self.stop_sampling:
                break
            self.set_status("Sampling response at {} Hz".format(frequency))
            yield from self.response.sample(frequency)
            self.plot.update()
        self.response.release_instruments()
        self.set_status("Sampling complete.")

    def start(self):
        execute_delayed(self.root, self.sample())


def run(start_freq, end_freq):
    root = tk.Tk()
    root.geometry("1000x700")
    win = Skardas(root, start_freq, end_freq)
    win.start()
    tk.mainloop()
