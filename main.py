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
# Configuration (Replace with your API key)
openai.api_key = ""
MODEL_ENGINE = "gpt-4"

class Communicate(QObject):
    update_conversation = pyqtSignal(str, str)
    update_status = pyqtSignal(str)
    toggle_button_style = pyqtSignal(bool)

class VoiceAssistant(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()  # Create UI first
        self.comm = Communicate()
        self.comm.update_conversation.connect(self.update_conversation_display)
        self.comm.update_status.connect(self.status_bar.showMessage)
        self.comm.toggle_button_style.connect(self.update_button_style)
        self.recognizer = sr.Recognizer()
        self.is_recording = False
        self.audio_thread = None
        self.setStyleSheet(self.get_stylesheet())
        
    def setup_ui(self):
        self.setWindowTitle("Greek Voice Assistant")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header = QLabel("Ελληνικός Φωνητικός Βοηθός")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px; color: #FFFFFF;")
        main_layout.addWidget(header)
        
        # Conversation display
        self.conversation = QTextEdit()
        self.conversation.setReadOnly(True)
        self.conversation.setStyleSheet("""
            background-color: #2D2D30;
            color: #FFFFFF;
            border-radius: 10px;
            padding: 15px;
            font-size: 16px;
        """)
        main_layout.addWidget(self.conversation, 1)
        
        # Button container
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(50, 20, 50, 30)
        
        # Record button
        self.record_btn = QPushButton()
        # Create a simple mic icon if file is missing
        pixmap = QtGui.QPixmap(48, 48)
        pixmap.fill(Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setBrush(QtGui.QColor(255, 255, 255))
        painter.setPen(QtGui.QColor(255, 255, 255))
        painter.drawEllipse(10, 10, 28, 28)
        painter.drawEllipse(20, 15, 8, 15)
        painter.end()
        self.record_btn.setIcon(QtGui.QIcon(pixmap))
        self.record_btn.setIconSize(QSize(48, 48))
        self.record_btn.setFixedSize(80, 80)
        self.record_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078D7;
                border-radius: 40px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1C97EA;
            }
            QPushButton:pressed {
                background-color: #005A9E;
            }
        """)
        self.record_btn.clicked.connect(self.toggle_recording)
        button_layout.addWidget(self.record_btn, 0, Qt.AlignCenter)
        
        main_layout.addLayout(button_layout)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def update_button_style(self, recording):
        if recording:
            self.record_btn.setStyleSheet("""
                QPushButton {
                    background-color: #D70000;
                    border-radius: 40px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #FF0000;
                }
            """)
        else:
            self.record_btn.setStyleSheet("""
                QPushButton {
                    background-color: #0078D7;
                    border-radius: 40px;
                    border: none;
                }
            """)
    
    def update_conversation_display(self, speaker, message):
        self.conversation.append(f"<b>{speaker}:</b> {message}")
        # Auto-scroll to bottom
        self.conversation.verticalScrollBar().setValue(
            self.conversation.verticalScrollBar().maximum()
        )
    
    def get_stylesheet(self):
        return """
            QMainWindow {
                background-color: #1E1E1E;
            }
            QStatusBar {
                background-color: #252526;
                color: #AAAAAA;
            }
        """
    
    def toggle_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.comm.update_status.emit("Processing...")
            self.comm.toggle_button_style.emit(False)
        else:
            self.is_recording = True
            self.comm.update_status.emit("Recording...")
            self.comm.toggle_button_style.emit(True)
            self.audio_thread = threading.Thread(target=self.process_audio)
            self.audio_thread.daemon = True
            self.audio_thread.start()
    
    def process_audio(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while self.is_recording:
                try:
                    audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=10)
                    user_input = self.recognizer.recognize_google(audio, language="el-GR")
                    
                    # Update UI with user input
                    self.comm.update_conversation.emit("You", user_input)
                    
                    # Get AI response
                    ai_response = self.get_ai_response(user_input)
                    self.comm.update_conversation.emit("Assistant", ai_response)
                    
                    # Convert to speech
                    self.text_to_speech(ai_response)
                    
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    self.comm.update_status.emit("Could not understand audio")
                except sr.RequestError as e:
                    self.comm.update_status.emit(f"Speech recognition error: {e}")
                except Exception as e:
                    self.comm.update_status.emit(f"Error: {str(e)}")
    
    def get_ai_response(self, text):
        try:
            response = openai.ChatCompletion.create(
                model=MODEL_ENGINE,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Respond in Greek."},
                    {"role": "user", "content": text}
                ],
                temperature=0.7,
                max_tokens=150
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            return f"Σφάλμα AI: {str(e)}"
    
    def text_to_speech(self, text):
        try:
            tts = gTTS(text=text, lang='el', slow=False)
            with tempfile.NamedTemporaryFile(delete=True, suffix='.mp3') as fp:
                tts.save(fp.name)
                # For Windows
                os.system(f"start {fp.name}")
                
                # For macOS (uncomment below)
                # os.system(f"afplay {fp.name}")
                
                # For Linux (uncomment below)
                # os.system(f"mpg321 {fp.name}")
        except Exception as e:
            self.comm.update_status.emit(f"TTS Error: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Set dark palette
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(30, 30, 30))
    palette.setColor(QtGui.QPalette.WindowText, Qt.white)
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ToolTipBase, Qt.white)
    palette.setColor(QtGui.QPalette.ToolTipText, Qt.white)
    palette.setColor(QtGui.QPalette.Text, Qt.white)
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ButtonText, Qt.white)
    palette.setColor(QtGui.QPalette.BrightText, Qt.red)
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(0, 120, 215))
    palette.setColor(QtGui.QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    
    window = VoiceAssistant()
    window.show()
    sys.exit(app.exec_())