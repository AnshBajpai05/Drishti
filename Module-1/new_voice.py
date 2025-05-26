import pygame
import time
from gtts import gTTS
import os

def voice(myText):
    language = 'en'
    tts = gTTS(text=myText, lang=language, slow=False)
    filename = "output.mp3"
    tts.save(filename)
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.5)

    pygame.mixer.quit()
    os.remove(filename)

