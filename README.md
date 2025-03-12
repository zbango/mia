# Voice Assistant - Speech to Clipboard

A lightweight voice assistant application that listens to your speech in Spanish, transcribes it, and automatically copies the text to your clipboard. Perfect for hands-free text input.

## Features

- **Speech Recognition**: Converts spoken Spanish to text
- **Clipboard Integration**: Automatically copies recognized text to clipboard
- **Minimal UI**: Small floating button that stays out of your way
- **Visual Feedback**: Elegant tooltips show the application's status
- **Drag & Drop**: Easily move the button anywhere on your screen
- **Persistence**: Always on top of other windows for easy access

## About MIA (Disclaimer)

This project plays on the phrase **"IA with MIA"**, using a digital assistant concept that visually changes between two states: **REC (Listening)** and **STANDBY**. The assistant interface features images inspired by Mia Khalifa as a **fun and engaging visual element**, leveraging cultural recognition to make the tool more appealing.

However, **this project is not affiliated, endorsed, or connected to Mia Khalifa in any way**. The images used in the application are purely for **entertainment and aesthetic purposes**. If any concerns arise regarding the use of imagery, modifications can be made accordingly.

If you plan to distribute this project, consider replacing the images with original artwork or AI-generated visuals to avoid potential issues.

## Requirements

- Windows operating system
- Python 3.8 or higher
- Internet connection (for speech recognition)
- Microphone

## Installation

1. Clone this repository:

```
git clone https://github.com/zbango/mia.git
cd mia
```

2. Install the required dependencies:

```
pip install -r requirements.txt
```

3. Run the application:

```
python main.py
```

## Usage

1. **Start the application**: Run `python main.py`
2. **Record voice**: Click the microphone button to start recording
3. **Stop recording**: The application will automatically stop recording once you stop speaking, or you can click the stop button
4. **Use the text**: The recognized text is automatically copied to your clipboard - just paste it anywhere
5. **Move the button**: Drag and drop to position it anywhere on your screen
6. **Close the application**: Double right-click the button

## Creating the Executable

You can create a standalone executable using PyInstaller:

1. Install PyInstaller:

```
pip install pyinstaller
```

2. Create the executable:

```
pyinstaller --onefile --windowed --add-data "mia_listen.png;." --add-data "mia_stop.png;." --icon=mia_listen.png --name Voice_Assistant main.py
```

3. The executable will be created in the `dist` folder

## Code Structure

The application is built using object-oriented programming with the following main classes:

- **ResourceManager**: Handles access to external resources like images
- **MessageProvider**: Manages feedback messages shown to the user
- **ClipboardManager**: Handles clipboard operations
- **SpeechRecognizer**: Manages the speech recognition functionality
- **UserInterface**: Controls the application's UI elements
- **VoiceAssistantApp**: Main application class that coordinates everything

## Technical Details

### Dependencies

- **tkinter**: For the graphical user interface
- **PIL/Pillow**: For image processing
- **SpeechRecognition**: For converting speech to text
- **pywin32**: For clipboard operations
- **threading**: For non-blocking operations

### Speech Recognition

The application uses Google's speech recognition API through the SpeechRecognition library. The recognized language is set to Spanish (`es-ES`).

## Demo

[Watch Demo Video](https://www.youtube.com/watch?v=62mspGxxGFE)

## Building from Source

### Setting up the Development Environment

1. Create a virtual environment:

```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install the dependencies:

```
pip install -r requirements.txt
```

3. Make your changes to the code

4. Test your changes:

```
python main.py
```

### Creating Requirements File

If you've added new dependencies, update the requirements file:

```
pip freeze > requirements.txt
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [SpeechRecognition](https://github.com/Uberi/speech_recognition) for the excellent speech recognition library
- **Special thanks to Mia Khalifa** – While this project is in no way affiliated with her, the name "MIA" perfectly aligns with the **Vibe Coding** movement in the era of AI. A simple coincidence that turned into inspiration.
- **To all the silent contributors** – The AI models and tools that shaped this project, proving that coding in the era of AI is no longer a solo act, but a symphony between human creativity and artificial intelligence.
