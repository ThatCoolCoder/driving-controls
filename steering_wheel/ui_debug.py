import tkinter as tk
from tkinter import ttk

progress = None

def main():
    global progress

    root = tk.Tk()
    root.title('FFB visualizer')
    root.geometry("400x150")
    progress = tk.IntVar()
    progressbar = ttk.Progressbar(variable=progress)
    progressbar.place(x=100, y=60, width=200)
    root.mainloop()

def set_val(val):
    if progress is None:
        return
    
    progress.set(map_value(val, -32768, 32768, 0, 100))

def map_value(value, in_min, in_max, out_min, out_max):
    return out_min + (((value - in_min) / (in_max - in_min)) * (out_max - out_min))