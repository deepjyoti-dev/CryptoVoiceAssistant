import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QComboBox
from PyQt5.QtGui import QFont
import speech_recognition as sr
import pyttsx3
import requests
from gtts import gTTS
import tempfile
import playsound
import joblib
import numpy as np

class CryptoVoiceAssistant(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Crypto Voice Assistant (Multilingual)")
        self.setGeometry(200, 200, 500, 350)
        self.language = "en"
        self.initUI()
        self.engine = pyttsx3.init()
        try:
            self.model = joblib.load("price_predictor.pkl")
        except:
            self.model = None

    def initUI(self):
        layout = QVBoxLayout()
        self.label = QLabel("Choose language and speak a command:")
        self.label.setFont(QFont("Arial", 12))
        layout.addWidget(self.label)

        self.lang_selector = QComboBox()
        self.lang_selector.addItem("English", "en")
        self.lang_selector.addItem("Hindi", "hi")
        self.lang_selector.currentIndexChanged.connect(self.set_language)
        layout.addWidget(self.lang_selector)

        self.listen_btn = QPushButton("🎤 Listen")
        self.listen_btn.clicked.connect(self.handle_voice_command)
        layout.addWidget(self.listen_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def set_language(self):
        self.language = self.lang_selector.currentData()

    def handle_voice_command(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.label.setText("Listening..." if self.language == "en" else "सुन रहा हूँ...")
            audio = recognizer.listen(source)
            try:
                command = recognizer.recognize_google(audio, language="en-IN" if self.language == "en" else "hi-IN")
                self.label.setText(f"You said: {command}" if self.language == "en" else f"आपने कहा: {command}")
                self.respond_to_command(command.lower())
            except sr.UnknownValueError:
                msg = "Sorry, I did not understand." if self.language == "en" else "माफ़ कीजिए, समझ नहीं पाया।"
                self.label.setText(msg)
            except sr.RequestError:
                msg = "Speech service error." if self.language == "en" else "स्पीच सेवा त्रुटि।"
                self.label.setText(msg)

    def respond_to_command(self, command):
        if "bitcoin" in command or "बिटकॉइन" in command:
            price = self.get_crypto_price("bitcoin")
            message = f"Bitcoin price is ${price}" if self.language == "en" else f"बिटकॉइन की कीमत है ₹{price * 83:.2f}"
        elif "ethereum" in command or "इथेरियम" in command:
            price = self.get_crypto_price("ethereum")
            message = f"Ethereum price is ${price}" if self.language == "en" else f"इथेरियम की कीमत है ₹{price * 83:.2f}"
        elif "predict bitcoin" in command or "अनुमान बिटकॉइन" in command:
            message = self.predict_price("bitcoin")
        elif "predict ethereum" in command or "अनुमान इथेरियम" in command:
            message = self.predict_price("ethereum")
        else:
            message = "Command not recognized." if self.language == "en" else "कमांड पहचानी नहीं गई।"
        self.label.setText(message)
        self.speak(message)

    def get_crypto_price(self, coin_id):
        try:
            response = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd")
            data = response.json()
            return data[coin_id]['usd']
        except:
            return 0

    def predict_price(self, coin):
        if not self.model:
            return "Prediction model not available." if self.language == "en" else "अनुमान मॉडल उपलब्ध नहीं है।"
        dummy_input = np.array([[1, 2, 3]])  # Dummy features
        predicted_price = self.model.predict(dummy_input)[0]
        if self.language == "en":
            return f"Predicted {coin} price is ${predicted_price:.2f}"
        else:
            return f"{coin} का अनुमानित मूल्य ₹{predicted_price * 83:.2f}"

    def speak(self, message):
        if self.language == "en":
            self.engine.say(message)
            self.engine.runAndWait()
        else:
            tts = gTTS(text=message, lang='hi')
            with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as fp:
                tts.save(fp.name)
                playsound.playsound(fp.name)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CryptoVoiceAssistant()
    window.show()
    sys.exit(app.exec_())