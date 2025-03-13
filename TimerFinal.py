import tkinter as tk
from tkinter import ttk, font
import math
from PIL import Image, ImageTk, ImageSequence


class AnimatedGIF:
    def __init__(self, canvas, x, y, filepath, size=(60, 60)):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.size = size
        self.frames = []
        self.current_frame = 0
        self.animation_id = None

        img = Image.open(filepath)
        for frame in ImageSequence.Iterator(img):
            frame = frame.convert("RGBA").resize(self.size, Image.LANCZOS)
            self.frames.append(ImageTk.PhotoImage(frame))

        self.image_id = self.canvas.create_image(self.x, self.y, image=self.frames[0])

    def start_animation(self):
        self._animate()

    def _animate(self):
        self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.canvas.itemconfig(self.image_id, image=self.frames[self.current_frame])
        self.animation_id = self.canvas.after(50, self._animate)

    def stop_animation(self):
        if self.animation_id:
            self.canvas.after_cancel(self.animation_id)
            self.animation_id = None


class CircularProgressBar:
    def __init__(self, parent):
        self.parent = parent
        self.canvas = tk.Canvas(parent, width=300, height=300, bg='#f0e6d3', highlightthickness=0)
        self.canvas.pack(pady=20)

        self.bg_color = '#d2b48c'
        self.fg_color = '#8b4513'
        self.text_color = '#4a2b0f'

        self.progress_id = None
        self.text1_id = None
        self.text2_id = None
        self.running = False
        self.paused = False
        self.remaining = 0
        self.total_time = 0
        self.flame = None

        self.create_progress_circle()
        self.create_text()

    def create_progress_circle(self):
        self.canvas.create_oval(20, 20, 280, 280, outline=self.bg_color, width=20)

    def create_text(self):
        self.text1_id = self.canvas.create_text(150, 135, text='',
                                                font=('Helvetica', 16, 'bold'),
                                                fill=self.text_color)
        self.text2_id = self.canvas.create_text(150, 165, text='',
                                                font=('Helvetica', 14),
                                                fill=self.text_color)

    def update_progress(self, percentage):
        angle = percentage * 360 / 100

        if self.progress_id:
            self.canvas.delete(self.progress_id)

        # رسم نوار پیشرفت با جهت صحیح
        self.progress_id = self.canvas.create_arc(20, 20, 280, 280,
                                                  start=90,
                                                  extent=-angle,  # جهت عقربه‌های ساعت
                                                  outline=self.fg_color,
                                                  width=20,
                                                  style=tk.ARC)

        self.update_flame_position(angle)

    def update_flame_position(self, angle):
        radius = 130
        center_x, center_y = 150, 150

        # فرمول اصلاح شده برای جهت صحیح
        radian = math.radians(90 - angle)
        x = center_x + radius * math.cos(radian)
        y = center_y - radius * math.sin(radian) - 10  # 10 پیکسل بالاتر

        if self.flame:
            self.flame.stop_animation()
            self.canvas.delete(self.flame.image_id)

        self.flame = AnimatedGIF(self.canvas, x, y, "flame1.gif", size=(60, 60))
        self.flame.start_animation()

class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Animated Circular Timer')
        self.root.configure(bg='#f0e6d3')

        # Font configurations
        self.custom_font = font.Font(family='Helvetica', size=12)
        self.small_font = font.Font(family='Helvetica', size=10)

        # Create progress bar
        self.progress_bar = CircularProgressBar(root)

        # Time entry frame
        self.entry_frame = ttk.Frame(root, style='Custom.TFrame')
        self.entry_frame.pack(pady=10)

        # Time label
        self.time_label = ttk.Label(self.entry_frame,
                                    text="(ثانیه)",
                                    font=self.small_font,
                                    foreground='#666666',
                                    background='#f0e6d3')
        self.time_label.pack()

        # Time entry
        self.time_entry = ttk.Entry(self.entry_frame,
                                    width=10,
                                    font=self.custom_font,
                                    justify='center')
        self.time_entry.pack(pady=5)
        self.time_entry.insert(0, "60")

        # Button frame
        self.btn_frame = ttk.Frame(root, style='Custom.TFrame')
        self.btn_frame.pack(pady=15)

        # Control buttons
        self.start_btn = ttk.Button(self.btn_frame,
                                    text='Start',
                                    command=self.start_timer)
        self.start_btn.grid(row=0, column=0, padx=5)

        self.reset_btn = ttk.Button(self.btn_frame,
                                    text='Reset',
                                    command=self.reset_timer)
        self.reset_btn.grid(row=0, column=1, padx=5)

        # Lock checkbox
        self.lock_var = tk.BooleanVar()
        self.lock_checkbox = ttk.Checkbutton(self.btn_frame,
                                             text='قفل هنگام اجرا',
                                             variable=self.lock_var,
                                             style='Custom.TCheckbutton')
        self.lock_checkbox.grid(row=1, column=0, columnspan=2, pady=5)

        # Timer variables
        self.timer_id = None
        self.start_time = 0
        self.paused_time = 0

        # Style configurations
        self.apply_styles()

    def apply_styles(self):
        style = ttk.Style()
        style.configure('Custom.TFrame', background='#f0e6d3')
        style.configure('Custom.TCheckbutton', background='#f0e6d3')
        style.configure('TButton', background='#e7d9c6')
        style.configure('TEntry', fieldbackground='white')

    def toggle_widgets_state(self, state):
        state = 'normal' if state else 'disabled'
        self.time_entry.config(state=state)
        self.start_btn.config(state=state)
        self.reset_btn.config(state=state)
        self.lock_checkbox.config(state=state)

    def start_timer(self):
        if not self.progress_bar.running:
            try:
                total = int(self.time_entry.get())
                if total <= 0:
                    return
            except ValueError:
                return

            if self.lock_var.get():
                self.toggle_widgets_state(False)

            self.progress_bar.total_time = total
            self.progress_bar.remaining = total
            self.progress_bar.running = True
            self.start_btn.config(text='Pause')
            self.update_timer()
        else:
            if not self.progress_bar.paused:
                self.progress_bar.paused = True
                self.paused_time = self.progress_bar.remaining
                self.start_btn.config(text='Resume')
                if self.timer_id:
                    self.root.after_cancel(self.timer_id)
            else:
                self.progress_bar.paused = False
                self.progress_bar.remaining = self.paused_time
                self.start_btn.config(text='Pause')
                self.update_timer()

    def update_timer(self):
        if self.progress_bar.running and not self.progress_bar.paused:
            self.progress_bar.remaining -= 1

            if self.progress_bar.remaining >= 0:
                percentage = (self.progress_bar.remaining / self.progress_bar.total_time) * 100
                self.progress_bar.update_progress(percentage)

                remaining = self.progress_bar.remaining
                hours, remainder = divmod(remaining, 3600)
                mins, secs = divmod(remainder, 60)

                time_str = (f'{hours}:{mins:02d}:{secs:02d}'
                            if hours > 0 else f'{mins:02d}:{secs:02d}')

                self.progress_bar.canvas.itemconfig(
                    self.progress_bar.text1_id,
                    text=f'{int(percentage)}%'
                )
                self.progress_bar.canvas.itemconfig(
                    self.progress_bar.text2_id,
                    text=time_str
                )

                self.timer_id = self.root.after(1000, self.update_timer)
            else:
                self.reset_timer()

    def reset_timer(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        if self.progress_bar.flame:
            self.progress_bar.flame.stop_animation()
        self.progress_bar.running = False
        self.progress_bar.paused = False
        self.progress_bar.remaining = 0
        self.start_btn.config(text='Start')
        self.progress_bar.canvas.itemconfig(self.progress_bar.text1_id, text='')
        self.progress_bar.canvas.itemconfig(self.progress_bar.text2_id, text='')
        self.progress_bar.update_progress(0)
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, "60")
        self.toggle_widgets_state(True)


if __name__ == '__main__':
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()