import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import pytz # For timezone handling
import math
import time

# --- Constants ---
UPDATE_INTERVAL_MS = 100 # Update interval for clocks and stopwatch (milliseconds)
ANALOG_CLOCK_SIZE = 200
CENTER_X = ANALOG_CLOCK_SIZE / 2
CENTER_Y = ANALOG_CLOCK_SIZE / 2
HOUR_HAND_LENGTH = ANALOG_CLOCK_SIZE * 0.25
MINUTE_HAND_LENGTH = ANALOG_CLOCK_SIZE * 0.35
SECOND_HAND_LENGTH = ANALOG_CLOCK_SIZE * 0.4

# --- Main Application Class ---
class ClockApp(tk.Tk):
    """Main application window for the Clock App."""
    def __init__(self):
        super().__init__()
        self.title("Clock App")
        self.geometry("450x550") # Adjusted size for better layout
        self.resizable(False, False)

        # --- Style ---
        style = ttk.Style(self)
        style.theme_use('clam') # Use a modern theme

        # --- Main Frame ---
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Notebook for Tabs ---
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # --- Create Tabs ---
        self.clock_tab = ClockTab(self.notebook)
        self.stopwatch_tab = StopwatchTab(self.notebook)
        self.timer_tab = TimerTab(self.notebook)
        self.timezone_tab = TimezoneTab(self.notebook)

        self.notebook.add(self.clock_tab, text='Clock')
        self.notebook.add(self.stopwatch_tab, text='Stopwatch')
        self.notebook.add(self.timer_tab, text='Timer')
        self.notebook.add(self.timezone_tab, text='Timezone')

        # --- Exit Button ---
        # Place it at the bottom right for better standard placement
        exit_button = ttk.Button(main_frame, text="Exit", command=self.quit_app)
        exit_button.pack(side=tk.RIGHT, pady=(0, 5), padx=(0, 5))

        # --- Start Updates ---
        # Start the clock updates immediately
        self.clock_tab.update_clocks()
        # Start timezone update loop
        self.timezone_tab.update_timezone_time()

        # Handle window close event
        self.protocol("WM_DELETE_WINDOW", self.quit_app)

    def quit_app(self):
        """Cleanly exits the application."""
        # Potentially add cleanup code here if needed (e.g., stopping threads)
        self.destroy()

# --- Clock Tab ---
class ClockTab(ttk.Frame):
    """Tab containing the Analog and Digital Clocks."""
    def __init__(self, parent):
        super().__init__(parent, padding="10")

        # --- Digital Clock ---
        self.digital_time_label = ttk.Label(self, text="", font=("Helvetica", 48))
        self.digital_time_label.pack(pady=(10, 5))

        self.digital_date_label = ttk.Label(self, text="", font=("Helvetica", 14))
        self.digital_date_label.pack(pady=(0, 20))

        # --- Analog Clock ---
        self.analog_canvas = tk.Canvas(self, width=ANALOG_CLOCK_SIZE, height=ANALOG_CLOCK_SIZE, bg="white", highlightthickness=1, highlightbackground="grey")
        self.analog_canvas.pack(pady=10)

        # Draw clock face elements that don't change
        self._draw_clock_face()

        # Create clock hands (will be updated)
        self.hour_hand = self.analog_canvas.create_line(0, 0, 0, 0, width=6, fill="black", capstyle=tk.ROUND)
        self.minute_hand = self.analog_canvas.create_line(0, 0, 0, 0, width=4, fill="black", capstyle=tk.ROUND)
        self.second_hand = self.analog_canvas.create_line(0, 0, 0, 0, width=2, fill="red", capstyle=tk.ROUND)
        # Center pivot circle
        self.analog_canvas.create_oval(CENTER_X - 4, CENTER_Y - 4, CENTER_X + 4, CENTER_Y + 4, fill="black")

        # Placeholder for after ID
        self._clock_update_job = None

    def _draw_clock_face(self):
        """Draws the static elements of the analog clock face."""
        # Outer circle
        self.analog_canvas.create_oval(5, 5, ANALOG_CLOCK_SIZE - 5, ANALOG_CLOCK_SIZE - 5, outline="black", width=2)

        # Hour markings
        for i in range(12):
            angle = math.radians(i * 30 - 90) # 360/12 = 30 degrees per hour, offset by -90
            x1 = CENTER_X + (ANALOG_CLOCK_SIZE * 0.45) * math.cos(angle)
            y1 = CENTER_Y + (ANALOG_CLOCK_SIZE * 0.45) * math.sin(angle)
            x2 = CENTER_X + (ANALOG_CLOCK_SIZE * 0.40) * math.cos(angle)
            y2 = CENTER_Y + (ANALOG_CLOCK_SIZE * 0.40) * math.sin(angle)
            self.analog_canvas.create_line(x1, y1, x2, y2, width=2 if (i % 3 == 0) else 1) # Thicker lines for 12, 3, 6, 9

        # Minute markings (optional, can make it look cluttered)
        # for i in range(60):
        #     if i % 5 != 0: # Don't draw over hour marks
        #         angle = math.radians(i * 6 - 90) # 360/60 = 6 degrees per minute
        #         x1 = CENTER_X + (ANALOG_CLOCK_SIZE * 0.45) * math.cos(angle)
        #         y1 = CENTER_Y + (ANALOG_CLOCK_SIZE * 0.45) * math.sin(angle)
        #         x2 = CENTER_X + (ANALOG_CLOCK_SIZE * 0.43) * math.cos(angle)
        #         y2 = CENTER_Y + (ANALOG_CLOCK_SIZE * 0.43) * math.sin(angle)
        #         self.analog_canvas.create_line(x1, y1, x2, y2, width=1)


    def update_clocks(self):
        """Updates both digital and analog clocks."""
        now = datetime.datetime.now()

        # --- Update Digital Clock ---
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%A, %B %d, %Y")
        self.digital_time_label.config(text=time_str)
        self.digital_date_label.config(text=date_str)

        # --- Update Analog Clock ---
        # Calculate angles (degrees, adjusted for Tkinter's coordinate system)
        # Hour: 360 degrees / 12 hours = 30 deg/hr. Add minutes contribution.
        hour_angle = (now.hour % 12 + now.minute / 60) * 30
        # Minute: 360 degrees / 60 minutes = 6 deg/min
        minute_angle = (now.minute + now.second / 60) * 6
        # Second: 360 degrees / 60 seconds = 6 deg/sec
        second_angle = now.second * 6

        # Convert angles to radians and adjust for 0 degrees being at 3 o'clock (-90 deg offset)
        hour_rad = math.radians(hour_angle - 90)
        minute_rad = math.radians(minute_angle - 90)
        second_rad = math.radians(second_angle - 90)

        # Calculate end points of hands
        hour_x = CENTER_X + HOUR_HAND_LENGTH * math.cos(hour_rad)
        hour_y = CENTER_Y + HOUR_HAND_LENGTH * math.sin(hour_rad)
        minute_x = CENTER_X + MINUTE_HAND_LENGTH * math.cos(minute_rad)
        minute_y = CENTER_Y + MINUTE_HAND_LENGTH * math.sin(minute_rad)
        second_x = CENTER_X + SECOND_HAND_LENGTH * math.cos(second_rad)
        second_y = CENTER_Y + SECOND_HAND_LENGTH * math.sin(second_rad)

        # Update hand positions
        self.analog_canvas.coords(self.hour_hand, CENTER_X, CENTER_Y, hour_x, hour_y)
        self.analog_canvas.coords(self.minute_hand, CENTER_X, CENTER_Y, minute_x, minute_y)
        self.analog_canvas.coords(self.second_hand, CENTER_X, CENTER_Y, second_x, second_y)

        # Schedule next update
        # Cancel previous job if it exists to prevent duplicates
        if self._clock_update_job:
            self.after_cancel(self._clock_update_job)
        self._clock_update_job = self.after(UPDATE_INTERVAL_MS, self.update_clocks)

# --- Stopwatch Tab ---
class StopwatchTab(ttk.Frame):
    """Tab containing the Stopwatch."""
    def __init__(self, parent):
        super().__init__(parent, padding="20")
        self.start_time = None
        self.elapsed_time = 0.0
        self.is_running = False
        self._stopwatch_job = None # ID for the after() job

        # --- Display Label ---
        self.time_label = ttk.Label(self, text="00:00:00.0", font=("Helvetica", 48))
        self.time_label.pack(pady=20)

        # --- Button Frame ---
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        self.start_button = ttk.Button(button_frame, text="Start", command=self.start)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = ttk.Button(button_frame, text="Reset", command=self.reset, state=tk.DISABLED)
        self.reset_button.pack(side=tk.LEFT, padx=5)

    def _update_time(self):
        """Updates the stopwatch display."""
        if self.is_running:
            # Calculate elapsed time since start OR since last update if paused/resumed
            current_elapsed = time.time() - self.start_time + self.elapsed_time
            self._display_time(current_elapsed)
            # Schedule the next update
            self._stopwatch_job = self.after(UPDATE_INTERVAL_MS, self._update_time)

    def _display_time(self, elapsed_seconds):
        """Formats and displays the time."""
        total_milliseconds = int(elapsed_seconds * 1000)
        milliseconds = (total_milliseconds % 1000) // 100 # Show tenths of a second
        total_seconds = total_milliseconds // 1000
        seconds = total_seconds % 60
        minutes = (total_seconds // 60) % 60
        hours = total_seconds // 3600
        time_str = f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds}"
        self.time_label.config(text=time_str)

    def start(self):
        """Starts or resumes the stopwatch."""
        if not self.is_running:
            self.start_time = time.time() # Record the moment it starts/resumes
            self.is_running = True
            self._update_time() # Start the update loop
            # Update button states
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.reset_button.config(state=tk.DISABLED) # Can't reset while running

    def stop(self):
        """Stops or pauses the stopwatch."""
        if self.is_running:
            # Cancel the update loop
            if self._stopwatch_job:
                self.after_cancel(self._stopwatch_job)
                self._stopwatch_job = None
            # Record elapsed time up to this point
            self.elapsed_time += time.time() - self.start_time
            self.is_running = False
            # Update button states
            self.start_button.config(state=tk.NORMAL) # Allow resuming
            self.stop_button.config(state=tk.DISABLED)
            self.reset_button.config(state=tk.NORMAL) # Allow reset when stopped

    def reset(self):
        """Resets the stopwatch."""
        # Ensure it's stopped first
        if self.is_running:
            self.stop()
        # Reset variables and display
        self.start_time = None
        self.elapsed_time = 0.0
        self._display_time(0.0)
        # Update button states
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.DISABLED) # Already reset

# --- Timer Tab ---
class TimerTab(ttk.Frame):
    """Tab containing the Timer."""
    def __init__(self, parent):
        super().__init__(parent, padding="20")
        self.remaining_time = 0 # Total seconds remaining
        self.total_duration = 0 # Store the initial duration for reset
        self.is_running = False
        self.end_time = None
        self._timer_job = None # ID for the after() job

        # --- Input Frame ---
        input_frame = ttk.Frame(self)
        input_frame.pack(pady=10)

        ttk.Label(input_frame, text="H:").pack(side=tk.LEFT)
        self.hour_spinbox = ttk.Spinbox(input_frame, from_=0, to=99, width=3, format="%02.0f")
        self.hour_spinbox.pack(side=tk.LEFT, padx=(0, 5))
        self.hour_spinbox.set("00") # Default value

        ttk.Label(input_frame, text="M:").pack(side=tk.LEFT)
        self.minute_spinbox = ttk.Spinbox(input_frame, from_=0, to=59, width=3, format="%02.0f")
        self.minute_spinbox.pack(side=tk.LEFT, padx=(0, 5))
        self.minute_spinbox.set("05") # Default value 5 minutes

        ttk.Label(input_frame, text="S:").pack(side=tk.LEFT)
        self.second_spinbox = ttk.Spinbox(input_frame, from_=0, to=59, width=3, format="%02.0f")
        self.second_spinbox.pack(side=tk.LEFT)
        self.second_spinbox.set("00") # Default value

        # --- Display Label ---
        self.time_label = ttk.Label(self, text="00:05:00", font=("Helvetica", 48))
        self.time_label.pack(pady=20)

        # --- Button Frame ---
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        self.start_button = ttk.Button(button_frame, text="Start", command=self.start)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = ttk.Button(button_frame, text="Reset", command=self.reset, state=tk.DISABLED)
        self.reset_button.pack(side=tk.LEFT, padx=5)

        # Initialize display based on default spinbox values
        self._update_display_from_spinboxes()


    def _update_timer(self):
        """Updates the timer display during countdown."""
        if self.is_running:
            # Calculate remaining time based on target end time
            self.remaining_time = max(0, self.end_time - time.time())
            self._display_time(self.remaining_time)

            if self.remaining_time <= 0:
                self.stop() # Stop the timer internally
                self.time_label.config(foreground="red") # Indicate completion
                messagebox.showinfo("Timer Finished", "Time's up!")
                self.time_label.config(foreground="") # Reset color after message
                self._enable_inputs() # Allow setting a new time
                self.reset_button.config(state=tk.NORMAL) # Allow reset
            else:
                # Schedule the next update more frequently for smoother countdown
                self._timer_job = self.after(100, self._update_timer)


    def _display_time(self, total_seconds):
        """Formats and displays the remaining time."""
        total_seconds = int(round(total_seconds)) # Round to nearest second for display
        seconds = total_seconds % 60
        minutes = (total_seconds // 60) % 60
        hours = total_seconds // 3600
        time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
        self.time_label.config(text=time_str)

    def _update_display_from_spinboxes(self):
        """Updates the label based on current spinbox values when timer is not running."""
        if not self.is_running:
             try:
                h = int(self.hour_spinbox.get())
                m = int(self.minute_spinbox.get())
                s = int(self.second_spinbox.get())
                self.total_duration = h * 3600 + m * 60 + s
                self._display_time(self.total_duration)
             except ValueError:
                 self._display_time(0) # Show 0 if input is invalid

    def _disable_inputs(self):
        """Disables spinboxes when timer is running."""
        self.hour_spinbox.config(state=tk.DISABLED)
        self.minute_spinbox.config(state=tk.DISABLED)
        self.second_spinbox.config(state=tk.DISABLED)

    def _enable_inputs(self):
        """Enables spinboxes when timer is stopped/reset."""
        self.hour_spinbox.config(state=tk.NORMAL)
        self.minute_spinbox.config(state=tk.NORMAL)
        self.second_spinbox.config(state=tk.NORMAL)

    def start(self):
        """Starts or resumes the timer."""
        if not self.is_running:
            try:
                # Get duration from spinboxes if timer hasn't run yet or was reset
                if self.remaining_time <= 0:
                    h = int(self.hour_spinbox.get())
                    m = int(self.minute_spinbox.get())
                    s = int(self.second_spinbox.get())
                    self.total_duration = h * 3600 + m * 60 + s
                    self.remaining_time = self.total_duration

                if self.remaining_time <= 0:
                    messagebox.showwarning("Timer", "Please set a duration greater than zero.")
                    return

                self.is_running = True
                # Calculate end time based on remaining duration
                self.end_time = time.time() + self.remaining_time
                self._disable_inputs()
                self._update_timer() # Start the update loop

                # Update button states
                self.start_button.config(state=tk.DISABLED)
                self.stop_button.config(state=tk.NORMAL)
                self.reset_button.config(state=tk.DISABLED) # Can't reset while running

            except ValueError:
                messagebox.showerror("Input Error", "Please enter valid numbers for hours, minutes, and seconds.")

    def stop(self):
        """Stops or pauses the timer."""
        if self.is_running:
            # Cancel the update loop
            if self._timer_job:
                self.after_cancel(self._timer_job)
                self._timer_job = None

            # Update remaining time (important for resume)
            self.remaining_time = max(0, self.end_time - time.time())
            self.is_running = False
            self.end_time = None # Clear end time

            # Update button states
            self.start_button.config(state=tk.NORMAL) # Allow resuming
            self.stop_button.config(state=tk.DISABLED)
            self.reset_button.config(state=tk.NORMAL) # Allow reset when stopped
            # Don't enable inputs here, only on reset or finish

    def reset(self):
        """Resets the timer to the last set duration or the current spinbox values."""
        if self.is_running:
            self.stop() # Stop it first

        self.remaining_time = 0 # Reset remaining time calculation flag
        self._enable_inputs() # Enable inputs for setting new time
        self._update_display_from_spinboxes() # Display based on spinboxes
        self.time_label.config(foreground="") # Reset color if it was red

        # Update button states
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.DISABLED) # Already reset

# --- Timezone Tab ---
class TimezoneTab(ttk.Frame):
    """Tab for looking up time in different timezones."""
    def __init__(self, parent):
        super().__init__(parent, padding="20")

        # --- Input Frame ---
        input_frame = ttk.Frame(self)
        input_frame.pack(pady=10, fill=tk.X)

        ttk.Label(input_frame, text="Select Timezone:").pack(side=tk.LEFT, padx=(0, 5))

        # Use Combobox for easier selection
        self.timezone_var = tk.StringVar()
        self.timezone_combo = ttk.Combobox(input_frame, textvariable=self.timezone_var, width=35, state="readonly")

        # Populate with available timezones
        try:
            all_timezones = sorted(pytz.all_timezones)
            self.timezone_combo['values'] = all_timezones
            # Set a default value (e.g., UTC or a common one)
            if 'UTC' in all_timezones:
                 self.timezone_combo.set('UTC')
            elif all_timezones:
                self.timezone_combo.set(all_timezones[0]) # Set first one if UTC not found
        except Exception as e:
            messagebox.showerror("Timezone Error", f"Could not load timezones: {e}")
            self.timezone_combo['values'] = [] # Clear if error

        self.timezone_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.timezone_combo.bind('<<ComboboxSelected>>', self.display_selected_timezone_time)

        # --- Display Area ---
        self.timezone_name_label = ttk.Label(self, text="Timezone: UTC", font=("Helvetica", 14))
        self.timezone_name_label.pack(pady=(20, 5))

        self.timezone_time_label = ttk.Label(self, text="--:--:--", font=("Helvetica", 40))
        self.timezone_time_label.pack(pady=5)

        self.timezone_date_label = ttk.Label(self, text="---", font=("Helvetica", 12))
        self.timezone_date_label.pack(pady=(0, 10))

        self._timezone_update_job = None
        # Initial display
        self.display_selected_timezone_time()


    def display_selected_timezone_time(self, event=None):
         """Gets the current time for the selected timezone and displays it."""
         selected_tz_str = self.timezone_var.get()
         if not selected_tz_str:
             self.timezone_name_label.config(text="Timezone: -")
             self.timezone_time_label.config(text="--:--:--")
             self.timezone_date_label.config(text="---")
             return

         try:
             target_tz = pytz.timezone(selected_tz_str)
             # Get current UTC time
             utc_now = datetime.datetime.now(pytz.utc)
             # Convert to target timezone
             target_time = utc_now.astimezone(target_tz)

             time_str = target_time.strftime("%H:%M:%S")
             date_str = target_time.strftime("%A, %B %d, %Y")
             tz_name_str = target_time.strftime("%Z (%z)") # Get abbreviation and offset

             self.timezone_name_label.config(text=f"Timezone: {selected_tz_str}\n({tz_name_str})")
             self.timezone_time_label.config(text=time_str)
             self.timezone_date_label.config(text=date_str)

         except pytz.UnknownTimeZoneError:
             self.timezone_name_label.config(text=f"Timezone: {selected_tz_str} (Unknown)")
             self.timezone_time_label.config(text="Error")
             self.timezone_date_label.config(text="Invalid Timezone")
         except Exception as e:
             self.timezone_name_label.config(text=f"Timezone: {selected_tz_str} (Error)")
             self.timezone_time_label.config(text="Error")
             self.timezone_date_label.config(text=f"An error occurred: {e}")

    def update_timezone_time(self):
        """Periodically updates the time for the currently selected timezone."""
        self.display_selected_timezone_time() # Update based on current selection
        # Schedule next update
        if self._timezone_update_job:
            self.after_cancel(self._timezone_update_job)
        self._timezone_update_job = self.after(1000, self.update_timezone_time) # Update every second


# --- Run the Application ---
if __name__ == "__main__":
    app = ClockApp()
    app.mainloop()
