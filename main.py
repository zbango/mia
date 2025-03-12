import tkinter as tk
from PIL import Image, ImageTk
import time
import sys
import os
import speech_recognition as sr
import threading
import random


class ResourceManager:
    """Class responsible for managing resources like images and paths."""

    @staticmethod
    def get_resource_path(relative_path):
        """
        Gets the absolute path to a resource, works for both development and executable.

        Args:
            relative_path (str): Relative path to the resource

        Returns:
            str: Absolute path to the resource
        """
        try:
            # PyInstaller creates a temp folder and stores the path in _MEIPASS
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            return os.path.join(base_path, relative_path)
        except Exception:
            return relative_path


class MessageProvider:
    """Class for managing random messages in the application."""

    # Predefined messages for different situations
    GREETING_MESSAGES = [
        "¿Dime?",
        "Te escucho",
        "¿Qué necesitas?",
        "Cuéntame",
        "Soy toda oídos",
        "A tus órdenes",
        "Dime lo que necesitas",
        "Habla con confianza",
        "Estoy atenta",
    ]

    ACKNOWLEDGMENT_MESSAGES = [
        "Entendido",
        "Ok, lo tengo",
        "Claro que sí",
        "Por supuesto",
        "Recibido",
        "Comprendido",
        "Anotado",
    ]

    @staticmethod
    def get_random_message(message_list):
        """
        Selects a random message from a list.

        Args:
            message_list (list): List of messages

        Returns:
            str: Selected random message
        """
        return random.choice(message_list)


class ClipboardManager:
    """Class for handling clipboard operations."""

    @staticmethod
    def set_clipboard_text(text):
        """
        Copies text to the clipboard in Windows.

        Args:
            text (str): Text to copy

        Returns:
            bool: True if copied successfully, False otherwise
        """
        try:
            import win32clipboard
            import win32con
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            print(f"Copied: {text}")
            return True
        except Exception as e:
            print(f"Error copying to clipboard with win32clipboard: {e}")
            return False


class SpeechRecognizer:
    """Class responsible for voice recognition."""

    def __init__(self, app):
        """
        Initializes the speech recognizer.

        Args:
            app (VoiceAssistantApp): Reference to the main application
        """
        self.app = app
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        self.stop_listening = None
        self.is_recording = False
        self.recognized_text = ""

    def toggle_recording(self):
        """
        Toggles between starting and stopping voice recording.
        """
        if not self.is_recording:
            self._start_recording()
        else:
            self._stop_recording()

    def _start_recording(self):
        """
        Starts the voice recording process.
        """
        self.recognized_text = ""  # Clear previous recognized text

        # Start the calibration process in a separate thread
        threading.Thread(target=self._calibrate_and_start).start()

        # Change the icon immediately
        self.app.ui.record_button.config(image=self.app.ui.stop_icon)
        self.is_recording = True

    def _stop_recording(self):
        """
        Stops the voice recording process.
        """
        if self.stop_listening:
            self.stop_listening(wait_for_stop=False)
            self.stop_listening = None
        self.app.ui.record_button.config(image=self.app.ui.mic_icon)
        self.is_recording = False

    def _calibrate_and_start(self):
        """
        Calibrates the microphone and starts listening in the background.
        """
        with self.mic as source:
            print("Adjusting ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source)

        print("Start speaking in Spanish...")
        # Start listening in the background
        self.stop_listening = self.recognizer.listen_in_background(self.mic, self._process_audio)

        # Select a random greeting message
        greeting = MessageProvider.get_random_message(MessageProvider.GREETING_MESSAGES)
        # Update the UI from the main thread
        self.app.root.after(0, lambda: self.app.ui.show_tooltip(greeting, 1500))

    def _process_audio(self, recognizer, audio):
        """
        Processes the captured audio and converts it to text.

        Args:
            recognizer: Recognizer instance
            audio: Captured audio
        """
        try:
            # Recognize the audio using Google (Spanish language)
            text = recognizer.recognize_google(audio, language="es-ES")
            if text:
                self.recognized_text += text + " "
                # Use a random acknowledgment message
                ack_message = MessageProvider.get_random_message(MessageProvider.ACKNOWLEDGMENT_MESSAGES)
                # Show the acknowledgment message
                self.app.ui.show_tooltip(f"{ack_message}", 1500)
                print(f"You said: {text}")
                ClipboardManager.set_clipboard_text(text)

                # Stop recording
                self._stop_recording()

        except sr.UnknownValueError:
            print("Could not understand what you said.")
            self.app.ui.show_tooltip("Sorry, I couldn't understand you. Could you repeat that?", 2000)
            ClipboardManager.set_clipboard_text("")
        except sr.RequestError as e:
            print(f"Error in recognition service: {e}")
            self.app.ui.show_tooltip("Sorry, I'm having a connection problem. Please try again.", 3000)


class UserInterface:
    """Class for managing the user interface."""

    def __init__(self, app):
        """
        Initializes the user interface.

        Args:
            app (VoiceAssistantApp): Reference to the main application
        """
        self.app = app
        self.root = app.root
        self.bg_color = self._configure_window()
        self.button_frame = self._create_button_frame()
        self.mic_icon, self.stop_icon = self._load_icons()
        self.record_button = self._create_record_button()
        self._setup_window_position()
        self._bind_events()

    def _configure_window(self):
        """
        Configures the main window.

        Returns:
            str: Background color to use
        """
        self.root.title("")
        self.root.attributes("-topmost", True)  # Keep window always on top
        self.root.overrideredirect(True)  # Remove borders and title bar

        # Make the window transparent in Windows
        if sys.platform == "win32":
            self.root.wm_attributes("-transparentcolor", "white")
            bg_color = "white"
        else:
            # On other systems
            self.root.attributes("-alpha", 0.95)
            bg_color = "systemTransparent" if sys.platform == "darwin" else "white"

        self.root.configure(bg=bg_color)
        return bg_color

    def _create_button_frame(self):
        """
        Creates the frame for the button.

        Returns:
            tk.Frame: Created frame
        """
        button_frame = tk.Frame(self.root, bg=self.bg_color)
        button_frame.pack(padx=0, pady=0)
        return button_frame

    def _load_icons(self):
        """
        Loads the icons for the button.

        Returns:
            tuple: (mic_icon, stop_icon) - loaded icons
        """
        try:
            # Define image files
            listen_file = ResourceManager.get_resource_path("mia_listen.png")
            stop_file = ResourceManager.get_resource_path("mia_stop.png")

            # Load and resize images
            mic_icon = self._load_and_resize_image(listen_file)
            stop_icon = self._load_and_resize_image(stop_file)
            print("Images loaded correctly from current directory")
            return mic_icon, stop_icon
        except Exception as e:
            print(f"Error loading images: {str(e)}")
            return self._create_fallback_icons()

    def _load_and_resize_image(self, file_path, max_size=288):
        """
        Loads and resizes an image.

        Args:
            file_path (str): Path to image file
            max_size (int): Maximum size of the image

        Returns:
            ImageTk.PhotoImage: Loaded and resized image
        """
        print(f"Trying to load image from: {file_path}")
        image = Image.open(file_path)

        # Resize the image if it's too large or too small
        if image.width != max_size or image.height != max_size:
            # Maintain aspect ratio
            ratio = min(max_size / image.width, max_size / image.height)
            new_width = int(image.width * ratio)
            new_height = int(image.height * ratio)
            image = image.resize((new_width, new_height), Image.LANCZOS)
            print(f"Image resized to {new_width}x{new_height}")

        return ImageTk.PhotoImage(image)

    def _create_fallback_icons(self):
        """
        Creates fallback icons in case images can't be loaded.

        Returns:
            tuple: (mic_icon, stop_icon) - fallback icons
        """
        mic_icon = tk.PhotoImage(width=100, height=100)
        stop_icon = tk.PhotoImage(width=100, height=100)

        # Draw a green circle for the microphone
        for x in range(100):
            for y in range(100):
                if (x - 50) ** 2 + (y - 50) ** 2 <= 40 ** 2:
                    mic_icon.put("green", (x, y))

        # Draw a red circle for stop
        for x in range(100):
            for y in range(100):
                if (x - 50) ** 2 + (y - 50) ** 2 <= 40 ** 2:
                    stop_icon.put("red", (x, y))

        print("Using generated fallback icons")
        return mic_icon, stop_icon

    def _create_record_button(self):
        """
        Creates the button to start/stop recording.

        Returns:
            tk.Button: Created button
        """
        record_button = tk.Button(self.button_frame,
                                  image=self.mic_icon,
                                  command=self.app.speech_recognizer.toggle_recording,
                                  bd=0,
                                  highlightthickness=0,
                                  bg=self.bg_color,
                                  activebackground=self.bg_color,
                                  padx=15,
                                  pady=15)
        record_button.pack(padx=8, pady=8)
        return record_button

    def _setup_window_position(self):
        """
        Sets the initial position of the window.
        """
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = screen_width - 680  # Adjusted for moderate-sized button
        y = screen_height - 260  # Adjusted for moderate-sized button
        self.root.geometry(f"+{x}+{y}")

    def _bind_events(self):
        """
        Binds events to interface widgets.
        """
        # Events to allow dragging the window
        self.record_button.bind("<ButtonPress-1>", self._start_move)
        self.record_button.bind("<ButtonRelease-1>", self._stop_move)
        self.record_button.bind("<B1-Motion>", self._do_move)

        # Event to close the application with double right-click
        self.record_button.bind("<Double-Button-3>", self._close_app)

    def _start_move(self, event):
        """
        Starts window movement.

        Args:
            event: Click event
        """
        self.root.x = event.x
        self.root.y = event.y

    def _stop_move(self, event):
        """
        Stops window movement.

        Args:
            event: Click release event
        """
        self.root.x = None
        self.root.y = None

    def _do_move(self, event):
        """
        Performs window movement.

        Args:
            event: Mouse movement event
        """
        dx = event.x - self.root.x
        dy = event.y - self.root.y
        x = self.root.winfo_x() + dx
        y = self.root.winfo_y() + dy
        self.root.geometry(f"+{x}+{y}")

    def _close_app(self, event):
        """
        Closes the application.

        Args:
            event: Double right-click event
        """
        self.root.destroy()

    def show_tooltip(self, message, duration=1000):
        """
        Shows a temporary tooltip that fades away.

        Args:
            message (str): Message to display
            duration (int): Duration in milliseconds of the tooltip
        """
        tooltip = tk.Toplevel(self.root)
        tooltip.overrideredirect(True)  # No borders or title bar
        tooltip.attributes("-topmost", True)
        tooltip.attributes("-alpha", 0)  # Start invisible for animation

        bg_color = "#2C3E50"
        fg_color = "#ECF0F1"
        tooltip.configure(bg=bg_color)

        # Create a frame with rounded corners
        frame = tk.Frame(tooltip, bg=bg_color, padx=1, pady=1)
        frame.pack(fill="both", expand=True)

        # Add a subtle border
        frame.configure(highlightbackground="#4A6B8A", highlightthickness=1)

        # Container for the text
        content_frame = tk.Frame(frame, bg=bg_color)
        content_frame.pack(padx=5, pady=5)

        # Create the tooltip content
        label = tk.Label(content_frame, text=message, fg=fg_color, bg=bg_color, padx=6, pady=6,
                         font=("Arial", 12), wraplength=200, justify=tk.LEFT)
        label.pack(side=tk.LEFT)

        # Position the tooltip
        self._position_tooltip(tooltip)

        # Start the entrance animation
        self._fade_in(tooltip)

        # Schedule the fade-out
        self.root.after(duration, lambda: self._fade_out(tooltip))

    def _position_tooltip(self, tooltip):
        """
        Positions the tooltip in relation to the button.

        Args:
            tooltip: Tooltip to position
        """
        # Update to calculate tooltip size
        tooltip.update_idletasks()
        tooltip_width = tooltip.winfo_width()
        tooltip_height = tooltip.winfo_height()

        # Calculate base position (top-left of button)
        button_x = self.root.winfo_x() + self.button_frame.winfo_x() + self.record_button.winfo_x()
        button_y = self.root.winfo_y() + self.button_frame.winfo_y() + self.record_button.winfo_y()
        button_width = self.record_button.winfo_width()

        # Position the tooltip above the button
        x = button_x + (button_width // 2) - (tooltip_width // 2)  # Horizontally centered over button
        y = button_y - tooltip_height - 5  # 5 pixels above the button

        # Ensure tooltip doesn't go off-screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        if x < 10:
            x = 10
        if y < 10:
            y = 10

        tooltip.geometry(f"+{x}+{y}")

    def _fade_in(self, tooltip):
        """
        Animates the tooltip entrance with a fade effect.

        Args:
            tooltip: Tooltip to animate
        """
        alpha = 0.0
        while alpha < 0.9:
            tooltip.attributes("-alpha", alpha)
            tooltip.update()
            time.sleep(0.02)
            alpha += 0.1
        tooltip.attributes("-alpha", 0.9)

    def _fade_out(self, tooltip):
        """
        Animates the tooltip exit with a fade effect.

        Args:
            tooltip: Tooltip to animate
        """
        alpha = 0.9
        while alpha > 0:
            tooltip.attributes("-alpha", alpha)
            tooltip.update()
            time.sleep(0.05)
            alpha -= 0.1
        tooltip.destroy()


class VoiceAssistantApp:
    """Main voice assistant application class."""

    def __init__(self):
        """Initializes the application."""
        self.root = tk.Tk()
        self.speech_recognizer = SpeechRecognizer(self)
        self.ui = UserInterface(self)

    def run(self):
        """Runs the application."""
        self.root.mainloop()


# Entry point when script is run directly
if __name__ == "__main__":
    app = VoiceAssistantApp()
    app.run()
