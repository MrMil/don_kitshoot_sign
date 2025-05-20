import neopixel
import machine
import random
import time
from machine import Pin
import math
from collections import namedtuple
from animations import COLORS, ColorSweep, get_random_color, Animation, QuarterSpiralAnimation, DualColorSweep


# The shape of the physical led strips:
# Top:
#  Horizontal, on top
#  Left, right: Vertical, on the sides, each split up into two halves, and they meet at the bottom.
# So, they form a triangle together.
# The triangle is split into 4 quaters
#
# Drawing:
#
# [top top top top top top]
# ------------------------
# [L]        |        [R]
#  [L]       |       [R]
#   [L]      |      [R]
# ------------------------
#    [L]     |    [R]
#     [L]    |   [R]
#      [L]   |  [R]
#       [L]  | [R]
#        [L] |[R]
#         [L]|[R]




LEN_SIDE_TOP = 16
LEN_SIDE_BOTTOM = 17

LEN_SIDES = LEN_SIDE_TOP + LEN_SIDE_BOTTOM
LEN_TOP = 30

def main():
    physical_strand_left = neopixel.NeoPixel(
        machine.Pin(33, machine.Pin.OUT), LEN_SIDES
    )
    physical_strand_right = neopixel.NeoPixel(
        machine.Pin(26, machine.Pin.OUT), LEN_SIDES
    )
    physical_strand_top = neopixel.NeoPixel(machine.Pin(13, machine.Pin.OUT), LEN_TOP)

    color_sweep_top = ColorSweep(physical_strand_top, 80, get_random_color(), 'forward')
    dual_sweep = DualColorSweep(physical_strand_left, physical_strand_right, 80, get_random_color())
    quarter_spiral = QuarterSpiralAnimation(
        physical_strand_left,
        physical_strand_right,
        top_length=LEN_SIDE_TOP,
        bottom_length=LEN_SIDE_BOTTOM,
        initial_delay=30,
        acceleration_factor=0.15
    )
    
    cycles = 0
    current_animation = dual_sweep
    while True:
        #top anim
        color_sweep_top.make_step()

        #bottom anim
        if current_animation.make_step():
            cycles += 1
        if cycles > 4 and current_animation == dual_sweep:
            current_animation = quarter_spiral
            cycles = 0
        elif cycles > 2 and current_animation == quarter_spiral:
            current_animation = dual_sweep
            cycles = 0
        time.sleep(0.02)

if __name__ == "__main__":
    main()
