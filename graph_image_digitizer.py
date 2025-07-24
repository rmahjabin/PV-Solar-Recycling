#!/usr/bin/env python
# coding: utf-8

# In[7]:


import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import os

class GraphDigitizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Image Digitizer")
        self.root.geometry("1000x800")
        
        # Variables
        self.image_path = None
        self.img = None
        self.calibration_points = []
        self.data_points = []
        self.axis_values = {'x_min': 0, 'x_max': 0, 'y_min': 0, 'y_max': 0}
        self.calibration_complete = False
        
        # Create frames
        self.control_frame = tk.Frame(root, width=200)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control panel
        tk.Label(self.control_frame, text="Graph Image Digitizer", font=("Arial", 16)).pack(pady=10)
        
        # Load image button
        tk.Button(self.control_frame, text="Load Image", command=self.load_image).pack(fill=tk.X, pady=5)
        
        # Calibration section
        tk.Label(self.control_frame, text="Calibration", font=("Arial", 12)).pack(pady=10)
        tk.Button(self.control_frame, text="Set Axis Values", command=self.set_axis_values).pack(fill=tk.X, pady=5)
        tk.Button(self.control_frame, text="Calibrate (3 points)", command=self.start_calibration).pack(fill=tk.X, pady=5)
        
        # Data extraction section
        tk.Label(self.control_frame, text="Data Extraction", font=("Arial", 12)).pack(pady=10)
        tk.Button(self.control_frame, text="Extract Data Points", command=self.extract_data_points).pack(fill=tk.X, pady=5)
        tk.Button(self.control_frame, text="Clear Points", command=self.clear_points).pack(fill=tk.X, pady=5)
        tk.Button(self.control_frame, text="Save Data", command=self.save_data).pack(fill=tk.X, pady=5)
        
        # Status
        self.status_var = tk.StringVar()
        self.status_var.set("Load an image to begin")
        tk.Label(self.control_frame, textvariable=self.status_var, wraplength=180).pack(pady=10)
        
        # Create matplotlib figure
        self.fig = plt.Figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(111)
        
        # Embed matplotlib figure in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Connect events
        self.canvas.mpl_connect('button_press_event', self.on_click)
    
    def load_image(self):
        self.image_path = filedialog.askopenfilename(
            title="Select Graph Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")]
        )
        
        if not self.image_path:
            return
        
        # Reset
        self.calibration_points = []
        self.data_points = []
        self.calibration_complete = False
        
        # Load and display image
        self.img = plt.imread(self.image_path)
        self.ax.clear()
        self.ax.imshow(self.img)
        self.ax.set_title("Loaded Graph Image")
        self.canvas.draw()
        
        self.status_var.set("Image loaded. Set axis values and calibrate.")
    
    def set_axis_values(self):
        if self.img is None:
            messagebox.showwarning("Warning", "Please load an image first")
            return
        
        self.axis_values['x_min'] = simpledialog.askfloat("Input", "Enter X-axis minimum value:", parent=self.root)
        self.axis_values['x_max'] = simpledialog.askfloat("Input", "Enter X-axis maximum value:", parent=self.root)
        self.axis_values['y_min'] = simpledialog.askfloat("Input", "Enter Y-axis minimum value:", parent=self.root)
        self.axis_values['y_max'] = simpledialog.askfloat("Input", "Enter Y-axis maximum value:", parent=self.root)
        
        self.status_var.set(f"Axis values set. X: [{self.axis_values['x_min']}, {self.axis_values['x_max']}], Y: [{self.axis_values['y_min']}, {self.axis_values['y_max']}]")
    
    def start_calibration(self):
        if self.img is None:
            messagebox.showwarning("Warning", "Please load an image first")
            return
        
        if not all(val != 0 for val in self.axis_values.values()):
            messagebox.showwarning("Warning", "Please set all axis values first")
            return
        
        self.calibration_points = []
        self.ax.clear()
        self.ax.imshow(self.img)
        self.ax.set_title("Click on: 1. Bottom-left (x_min, y_min), 2. Bottom-right (x_max, y_min), 3. Top-left (x_min, y_max)")
        self.canvas.draw()
        
        self.status_var.set("Click on the 3 calibration points as instructed")
    
    def extract_data_points(self):
        if not self.calibration_complete:
            messagebox.showwarning("Warning", "Please complete calibration first")
            return
        
        self.data_points = []
        self.ax.clear()
        self.ax.imshow(self.img)
        self.ax.set_title("Click on data points. Right-click when done.")
        self.canvas.draw()
        
        self.status_var.set("Click on data points. Right-click when done.")
    
    def on_click(self, event):
        if event.inaxes != self.ax:
            return
        
        # During calibration
        if len(self.calibration_points) < 3 and not self.calibration_complete:
            self.calibration_points.append((event.xdata, event.ydata))
            self.ax.plot(event.xdata, event.ydata, 'ro', markersize=8)
            self.canvas.draw()
            
            if len(self.calibration_points) == 3:
                self.complete_calibration()
            
        # During data extraction
        elif self.calibration_complete and event.button == 1:  # Left click
            # Convert to actual values
            x_val, y_val = self.pixel_to_value(event.xdata, event.ydata)
            self.data_points.append((x_val, y_val))
            
            # Plot in pixel space
            self.ax.plot(event.xdata, event.ydata, 'bx', markersize=6)
            self.canvas.draw()
            
            self.status_var.set(f"Added point: ({x_val:.2f}, {y_val:.2f}). Total points: {len(self.data_points)}")
            
        elif self.calibration_complete and event.button == 3:  # Right click
            self.display_extracted_data()
    
    def complete_calibration(self):
        if len(self.calibration_points) != 3:
            return
        
        self.calibration_complete = True
        self.status_var.set("Calibration complete. Now extract data points.")
        
        # Draw lines to show calibration
        points = np.array(self.calibration_points)
        self.ax.plot(points[:, 0], points[:, 1], 'r-', linewidth=2)
        self.canvas.draw()
    
    def pixel_to_value(self, px, py):
        if not self.calibration_complete or len(self.calibration_points) != 3:
            return (0, 0)
        
        # Calibration points
        origin_px = self.calibration_points[0]      # Bottom-left
        x_max_px = self.calibration_points[1]       # Bottom-right
        y_max_px = self.calibration_points[2]       # Top-left
        
        # Calculate scaling factors
        x_scale = (self.axis_values['x_max'] - self.axis_values['x_min']) / (x_max_px[0] - origin_px[0])
        y_scale = (self.axis_values['y_max'] - self.axis_values['y_min']) / (origin_px[1] - y_max_px[1])
        
        # Convert pixel to value
        x_val = self.axis_values['x_min'] + (px - origin_px[0]) * x_scale
        y_val = self.axis_values['y_min'] + (origin_px[1] - py) * y_scale  # Y is inverted
        
        return (x_val, y_val)
    
    def display_extracted_data(self):
        if not self.data_points:
            messagebox.showinfo("Info", "No data points extracted")
            return
        
        # Sort by x-value
        self.data_points.sort(key=lambda p: p[0])
        
        # Create arrays for plotting
        x_values = [p[0] for p in self.data_points]
        y_values = [p[1] for p in self.data_points]
        
        # Display data in new window
        data_window = tk.Toplevel(self.root)
        data_window.title("Extracted Data")
        data_window.geometry("600x500")
        
        # Data frame
        data_frame = tk.Frame(data_window)
        data_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollable text area for data
        tk.Label(data_frame, text="Extracted Data Points", font=("Arial", 12)).pack(pady=5)
        
        text_area = tk.Text(data_frame, height=10, width=30)
        scrollbar = tk.Scrollbar(data_frame, command=text_area.yview)
        text_area.configure(yscrollcommand=scrollbar.set)
        
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Insert data
        text_area.insert(tk.END, "X,Y\n")
        for x, y in self.data_points:
            text_area.insert(tk.END, f"{x:.4f},{y:.4f}\n")
        
        # Plot in value space
        plot_frame = tk.Frame(data_window)
        plot_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        fig = plt.Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)
        ax.plot(x_values, y_values, 'bo-')
        ax.set_title("Extracted Data")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.grid(True)
        
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.status_var.set(f"Extracted {len(self.data_points)} data points")
    
    def clear_points(self):
        self.data_points = []
        
        # Redraw
        self.ax.clear()
        self.ax.imshow(self.img)
        
        # Redraw calibration points
        if self.calibration_complete:
            points = np.array(self.calibration_points)
            self.ax.plot(points[:, 0], points[:, 1], 'ro', markersize=8)
            self.ax.plot(points[:, 0], points[:, 1], 'r-', linewidth=2)
        
        self.canvas.draw()
        self.status_var.set("Data points cleared")
    
    def save_data(self):
        if not self.data_points:
            messagebox.showwarning("Warning", "No data points to save")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Data",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        # Sort by x-value
        self.data_points.sort(key=lambda p: p[0])
        
        # Create DataFrame
        df = pd.DataFrame(self.data_points, columns=['x', 'y'])
        
        # Save based on extension
        if file_path.endswith('.csv'):
            df.to_csv(file_path, index=False)
        elif file_path.endswith('.xlsx'):
            df.to_excel(file_path, index=False)
        else:
            df.to_csv(file_path, index=False)
        
        self.status_var.set(f"Data saved to {os.path.basename(file_path)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphDigitizer(root)
    root.mainloop()


# In[ ]:




