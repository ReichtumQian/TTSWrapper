import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QFileDialog, QComboBox, QMessageBox
from PyQt5.QtCore import Qt
from pydub import AudioSegment
from pydub.playback import play
import io
import requests

class TTSApp(QWidget):
    def __init__(self):
        super().__init__()
        self.config_file = 'config.json'
        self.initUI()
        self.load_config()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        self.api_key_label = QLabel('API Key:')
        self.api_key_input = QLineEdit()
        layout.addWidget(self.api_key_label)
        layout.addWidget(self.api_key_input)
        
        self.host_label = QLabel('Host:')
        self.host_input = QLineEdit()
        layout.addWidget(self.host_label)
        layout.addWidget(self.host_input)
        
        self.voice_label = QLabel('Voice:')
        self.voice_combo = QComboBox()
        self.voice_combo.addItems(["alloy", "echo", "fable", "onyx", "nova", "shimmer"])
        layout.addWidget(self.voice_label)
        layout.addWidget(self.voice_combo)
        
        self.text_label = QLabel('Text to convert:')
        self.text_input = QLineEdit()
        layout.addWidget(self.text_label)
        layout.addWidget(self.text_input)
        
        self.convert_text_button = QPushButton('Convert Text to Speech')
        self.convert_text_button.clicked.connect(self.convert_text_to_speech)
        layout.addWidget(self.convert_text_button)
        
        self.convert_file_button = QPushButton('Convert File to Speech')
        self.convert_file_button.clicked.connect(self.select_file_and_convert)
        layout.addWidget(self.convert_file_button)
        
        self.play_button = QPushButton('Play Audio')
        self.play_button.clicked.connect(self.play_audio)
        layout.addWidget(self.play_button)
        
        self.save_button = QPushButton('Save Audio')
        self.save_button.clicked.connect(self.save_audio)
        layout.addWidget(self.save_button)
        
        self.setLayout(layout)
        self.setWindowTitle('TTS Application')
        self.audio_data = None
        
        # Connect text changed signals to save config
        self.api_key_input.textChanged.connect(self.save_config)
        self.host_input.textChanged.connect(self.save_config)
        self.voice_combo.currentIndexChanged.connect(self.save_config)
    
    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as file:
                config = json.load(file)
                self.api_key_input.setText(config.get('api_key', ''))
                self.host_input.setText(config.get('host', ''))
                voice = config.get('voice', 'voice-1')
                self.voice_combo.setCurrentText(voice)
    
    def save_config(self):
        config = {
            'api_key': self.api_key_input.text(),
            'host': self.host_input.text(),
            'voice': self.voice_combo.currentText()
        }
        with open(self.config_file, 'w') as file:
            json.dump(config, file)
    
    def convert_text_to_speech(self):
        api_key = self.api_key_input.text()
        host = self.host_input.text()
        text = self.text_input.text()
        voice = self.voice_combo.currentText()

        self.convert_text(api_key, host, text, voice)
    
    def select_file_and_convert(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Text File", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as file:
                    text = file.read()
                    self.text_input.setText(text)
                    self.convert_text_to_speech()
            except UnicodeDecodeError:
                print("Error: Could not decode the file. Please ensure the file is encoded in UTF-8.")
    
    def convert_text(self, api_key, host, text, voice):
        url = f"{host}/v1/audio/speech"
        payload = json.dumps({
            "model": "tts-1",
            "input": text,
            "voice": voice
        })
        headers = {
            'Authorization': f'Bearer {api_key}',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json'
        }

        response = requests.post(url, headers=headers, data=payload)
        
        if response.status_code == 200:
            audio_content = response.content
            
            temp_dir = os.path.join(os.getcwd(), 'temp_audio')
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            os.environ['TMPDIR'] = temp_dir
            
            self.audio_data = AudioSegment.from_file(io.BytesIO(audio_content), format="mp3")
            self.show_message("Conversion successful!")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    
    def play_audio(self):
        if self.audio_data:
            play(self.audio_data)
    
    def save_audio(self):
        if self.audio_data:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Audio", "", "MP3 Files (*.mp3);;All Files (*)", options=options)
            if file_name:
                self.audio_data.export(file_name, format="mp3")
    
    def show_message(self, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(message)
        msg_box.setWindowTitle("Information")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TTSApp()
    ex.show()
    sys.exit(app.exec_())
