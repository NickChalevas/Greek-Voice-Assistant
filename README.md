# Greek Voice Assistant Script Documentation

## Overview
This Python script runs a desktop voice assistant application with a graphical interface using PyQt5. The assistant listens to Greek speech input, processes it using OpenAI's GPT-4 model, and responds in Greek using text-to-speech.

## Features
- Speech recognition in Greek
- Text-to-speech responses in Greek
- Modern GUI with dark theme
- Real-time conversation display
- Visual feedback during recording

## Dependencies
```python
import sys
import threading
import tempfile
import openai
import speech_recognition as sr
from gtts import gTTS
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, QSize, QObject, pyqtSignal
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QStatusBar
)
```

## Configuration
```python
# Replace with your OpenAI API key
openai.api_key = ""
MODEL_ENGINE = "gpt-4"
```

## Classes

### `Communicate`
Handles inter-thread communication using PyQt signals.

**Signals:**
- `update_conversation(str, str)`: Emits speaker and message
- `update_status(str)`: Emits status messages
- `toggle_button_style(bool)`: Toggles button recording state

### `VoiceAssistant(QMainWindow)`
Main application window and logic.

#### Key Methods:
- `__init__()`: Initializes UI and components
- `setup_ui()`: Creates the GUI layout
- `update_button_style(recording)`: Changes button color based on recording state
- `update_conversation_display(speaker, message)`: Updates chat display
- `toggle_recording()`: Starts/stops recording thread
- `process_audio()`: Handles audio input in a background thread
- `get_ai_response(text)`: Gets response from OpenAI API
- `text_to_speech(text)`: Converts text to spoken Greek

## UI Components
- **Header**: "Ελληνικός Φωνητικός Βοηθός" (Greek Voice Assistant)
- **Conversation Display**: Scrollable chat history
- **Record Button**: Large circular button with mic icon
- **Status Bar**: Shows current state (Ready/Recording/Processing)

## Workflow
1. User clicks record button
2. System captures audio through microphone
3. Speech converted to text using Google's speech recognition
4. Text sent to OpenAI GPT-4 with Greek language preference
5. AI response shown in conversation display
6. Response converted to Greek speech using gTTS
7. Audio played through system speakers

## System Requirements
- Python 3.6+
- Windows (for `os.system("start ...")` command)
- Microphone
- Internet connection (for API calls)

## Setup
1. Install dependencies:
```bash
pip install openai speechrecognition gtts PyQt5
```
2. Add your OpenAI API key in the configuration section
3. Run the script:
```bash
python script_name.py
```

## Notes
- The UI uses a dark theme with blue accent colors
- Audio processing happens in a background thread to prevent UI freezing
- Temporary MP3 files are used for text-to-speech playback
- Error handling for speech recognition and API calls is implemented

