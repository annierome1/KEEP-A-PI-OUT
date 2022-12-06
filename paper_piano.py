import RPi.GPIO as GPIO
from time import sleep, time
import pygame
from array import array
from math import sin, pi

MIXER_FREQ = 44100
MIXER_SIZE = -16
MIXER_CHANS = 1
MIXER_BUFF = 1024

class Note(pygame.mixer.Sound):
    def __init__(self, frequency, volume, wave):
        self.frequency = frequency
        self.wave = wave
        if (wave == "square"):
            pygame.mixer.Sound.__init__(self, buffer = self.square())
        elif (wave == "triangle"):
            pygame.mixer.Sound.__init__(self, buffer = self.triangle())
        elif (wave == "sawtooth"):
            pygame.mixer.Sound.__init__(self, buffer = self.sawtooth())
        elif (wave == "sinsudonial"):
            pygame.mixer.Sound.__init__(self, buffer = self.sinsudonial())
        self.set_volume(volume)
        
    def square(self):
        period = int(round(MIXER_FREQ/ self.frequency))
        amplitude = 2 ** (abs(MIXER_SIZE) -1) -1
        samples = array("h", [0] * period)
        # square wave 
        for t in range(period):
            if (t < period/2):
                samples[t] = amplitude
            else:
                samples[t] = -amplitude
        return samples
    
    def triangle(self):
        period = int(round(MIXER_FREQ/ self.frequency))
        amplitude = 2 ** (abs(MIXER_SIZE) -1) -1
        samples = array("h", [0] * period)
        for t in range(period):
            if (t < period / 4):
                samples[t] = samples[t -1] + 780
            elif (t >= period / 4 and t < int(round(period * 3 / 4))):
                samples[t] = samples [t-1] - 780
            elif(t > int(round(period * 3 / 4))):
                samples[t] = samples [t -1] + 780
        return samples

     
    def sawtooth(self):
        period = int(round(MIXER_FREQ/ self.frequency))
        amplitude = 2 ** (abs(MIXER_SIZE) -1) -1
        samples = array("h", [0] * period)
        for t in range(period):
            if (t < period / 2):
                samples[t] = samples[t-1] + 390
            else:
                samples[t] = samples[t-85] -32767
        return samples
    def sinsudonial(self):
        period = int(round(MIXER_FREQ/ self.frequency))
        amplitude = 2 ** (abs(MIXER_SIZE) -1) -1
        samples = array("h", [0] * period)
        for t in range(period):
            if(t < period):
                samples[t] = int(amplitude * sin(((2 * pi / 169) * t)))
        return samples 
        
       
                    
def wait_for_note_start():
    while (True):
        for key in range(len(keys)):
            if(GPIO.input(keys[key])):
                return key
        if(GPIO.input(play)):
            sleep(0.01)
            return "play"
        if(GPIO.input(record)):
            while (GPIO.input(record)):
                sleep(0.01)
            return "record"
        sleep(0.01)
        
            
def wait_for_note_stop(key):
    while (GPIO.input(key)):
        sleep(0.1)
        
def play_song():
    for part in song:
        note, duration = part
        if (note == "SILENCE)"):
            sleep(duration)
        else:
            notes[note].play(-1)
            sleep(duration)
            notes[note].stop()

pygame.mixer.pre_init(MIXER_FREQ, MIXER_SIZE, MIXER_CHANS, MIXER_BUFF)
pygame.init()

GPIO.setmode(GPIO.BCM)
keys = [20, 16, 12, 26]
wave = ["square", "triangle", "sawtooth", "sinsudonial"] # when this is in array, I get an error that says backend has terminated.
notes = []




play = 19
record = 21

red = 27
green = 18
blue = 17

GPIO.setup(keys, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(play, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(record, GPIO.IN, GPIO.PUD_DOWN)

GPIO.setup(red, GPIO.OUT)
GPIO.setup(green, GPIO.OUT)
GPIO.setup(blue, GPIO.OUT)

for n in wave:
    notes.append(Note(262.6, 1, n))
    
recording = False
song = []

print("Welcome to Paper Piano!")
print("Press Ctrl+C to exit...")

try:
    while(True):
        start = time()
        key = wait_for_note_start()
        duration = time() - start
        if(recording):
            song.append(["SILENCE", duration])
        if (key == "record"):
            if(not recording):
                song = []
            recording = not recording
            GPIO.output(red, recording)
        elif (key == "play"):
            if (recording):
                recording = False
                GPIO.output(red, False)
            GPIO.output(green, True)
            play_song()
            GPIO.output(green, False)
        else:
            start = time()
            notes[key].play(-1)
            wait_for_note_stop(keys[key])
            notes[key].stop()
            duration = time() - start
            if(recording):
               song.append([key, duration]) 
            
except KeyboardInterrupt:
    GPIO.cleanup()