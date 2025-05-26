import speech_recognition as sr
import threading
import time

class VoiceListener:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.command = None
        self.listening = False

        # 🛠️ Calibrate for environment noise
        with self.microphone as source:
            print("📢 Calibrating... please stay quiet.")
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
            print(f"🔧 Calibrated energy threshold: {self.recognizer.energy_threshold}")

        # Optional: Lock it to that threshold
        self.recognizer.dynamic_energy_threshold = False

        self.thread = threading.Thread(target=self._listen_loop)
        self.thread.daemon = True
        self.thread.start()


    def _listen_loop(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("🎙️ VoiceListener is running... Speak any time.")

            while True:
                try:
                    print("👂 Waiting for speech...")
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    self.listening = True
                    print("🔊 Heard something... processing...")

                    command = self.recognizer.recognize_google(audio)
                    print(f"📝 You said: {command}")
                    self.command = command.lower()

                except sr.WaitTimeoutError:
                    print("⌛ No speech detected.")
                except sr.UnknownValueError:
                    print("❗ Didn't catch that. Please speak clearly.")
                except sr.RequestError as e:
                    print(f"❗ API error: {e}")
                except Exception as e:
                    print(f"❗ Error: {e}")
                finally:
                    self.listening = False
                    time.sleep(1.5)  # prevent immediate loop restart

    def get_command(self):
        cmd = self.command
        self.command = None
        return cmd
