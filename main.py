import neopixel
import machine
import random
import time

COLORS = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "purple": (255, 0, 255),
    "cyan": (0, 255, 255),
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "orange": (255, 165, 0),
    "pink": (255, 192, 203),
    "brown": (139, 69, 19),
    "gold": (255, 215, 0),
    "maroon": (128, 0, 0),
    "navy": (0, 0, 128),
    "olive": (128, 128, 0),
    "teal": (0, 128, 128),
    "indigo": (75, 0, 130),
    "violet": (238, 130, 238),
}


def main():
    strands = [
        neopixel.NeoPixel(machine.Pin(33, machine.Pin.OUT), 5),
        neopixel.NeoPixel(machine.Pin(26, machine.Pin.OUT), 5),
        neopixel.NeoPixel(machine.Pin(13, machine.Pin.OUT), 5)
    ]

    while True:
        for strand in strands:
            strand.fill(random.choice(list(COLORS.values())))
            strand.write()
        time.sleep(1)

if __name__ == "__main__":
    main()
