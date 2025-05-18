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
    "white": (255, 255, 255),  # Not a good color, not pretty
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

# The shape is
#
# [top            letters]
# [L]                 [R]
# [L]  (top left)     [R]  (top right)
# [L]                 [R]
#
# [L]  (bottom left)  [R]  (bottom right)
# [L]                 [R]
# [L]                 [R]


def rotate(strand_state, step):
    """
    returns a strand where colors moved by step
    """
    new_strand_state = [None] * len(strand_state)
    for i in range(len(strand_state)):
        new_strand_state[i] = strand_state[i - step]
    return new_strand_state


def get_random_strand_state(strand_length):
    """
    returns a strand where colors are random
    """
    return [random.choice(list(COLORS.values())) for _ in range(strand_length)]


def apply_state(strand, strand_state):
    """
    applies a strand state to a strand
    """
    for i in range(len(strand)):
        strand[i] = strand_state[i]
    strand.write()


LEN_SIDE_TOP = 16
LEN_SIDE_BOTTOM = 17

LEN_SIDES = LEN_SIDE_TOP + LEN_SIDE_BOTTOM
LEN_TOP = 30


def apply_state_to_strands(
    physical_strand_left,
    physical_strand_right,
    physical_strand_top,
    state_top,
    state_top_left,
    state_top_right,
    state_bottom_left,
    state_bottom_right,
):
    assert len(state_top) == LEN_TOP
    assert len(state_top_left) == LEN_SIDE_TOP
    assert len(state_top_right) == LEN_SIDE_TOP
    assert len(state_bottom_left) == LEN_SIDE_BOTTOM
    assert len(state_bottom_right) == LEN_SIDE_BOTTOM
    assert len(physical_strand_left) == LEN_SIDES
    assert len(physical_strand_right) == LEN_SIDES
    assert len(physical_strand_top) == LEN_TOP

    state_left_combined = state_top_left + state_bottom_left
    state_right_combined = state_top_right + state_bottom_right

    apply_state(physical_strand_left, state_left_combined)
    apply_state(physical_strand_right, state_right_combined)
    apply_state(physical_strand_top, state_top)


def get_strand_state_in_color(strand_state_length, color):
    """
    returns a state where all colors are replaced with the given color
    """
    return [color for _ in range(strand_state_length)]


def add_noise(strand_state, noise_chance_per_led, change_per_rgb):
    """
    adds noise to a strand state
    """
    for i in range(len(strand_state)):
        if random.random() < noise_chance_per_led:
            strand_state[i] = (
                strand_state[i][0] + random.randint(-change_per_rgb, change_per_rgb),
                strand_state[i][1] + random.randint(-change_per_rgb, change_per_rgb),
                strand_state[i][2] + random.randint(-change_per_rgb, change_per_rgb),
            )
    return strand_state


def main():
    strand_left = neopixel.NeoPixel(machine.Pin(33, machine.Pin.OUT), LEN_SIDES)
    strand_right = neopixel.NeoPixel(machine.Pin(26, machine.Pin.OUT), LEN_SIDES)
    strand_top = neopixel.NeoPixel(machine.Pin(13, machine.Pin.OUT), 30)

    strand_left.fill(COLORS["red"])
    strand_left.write()
    strand_right.fill(COLORS["green"])
    strand_right.write()
    strand_top.fill(COLORS["blue"])
    strand_top.write()

    NOICE_CHANCE_PER_LED = 0.1
    NOICE_CHANGE_PER_RGB = 10

    top_left_state = add_noise(
        get_strand_state_in_color(LEN_SIDE_TOP, COLORS["red"]),
        NOICE_CHANCE_PER_LED,
        NOICE_CHANGE_PER_RGB,
    )
    top_right_state = add_noise(
        get_strand_state_in_color(LEN_SIDE_TOP, COLORS["green"]),
        NOICE_CHANCE_PER_LED,
        NOICE_CHANGE_PER_RGB,
    )
    bottom_left_state = add_noise(
        get_strand_state_in_color(LEN_SIDE_BOTTOM, COLORS["blue"]),
        NOICE_CHANCE_PER_LED,
        NOICE_CHANGE_PER_RGB,
    )
    bottom_right_state = add_noise(
        get_strand_state_in_color(LEN_SIDE_BOTTOM, COLORS["orange"]),
        NOICE_CHANCE_PER_LED,
        NOICE_CHANGE_PER_RGB,
    )
    top_state = add_noise(
        get_strand_state_in_color(LEN_TOP, COLORS["purple"]),
        NOICE_CHANCE_PER_LED,
        NOICE_CHANGE_PER_RGB,
    )

    while True:
        top_left_state = add_noise(
            rotate(top_left_state, 1), NOICE_CHANCE_PER_LED / 10.0, NOICE_CHANGE_PER_RGB
        )
        top_right_state = add_noise(
            rotate(top_right_state, 1),
            NOICE_CHANCE_PER_LED / 10.0,
            NOICE_CHANGE_PER_RGB,
        )
        bottom_left_state = add_noise(
            rotate(bottom_left_state, 1),
            NOICE_CHANCE_PER_LED / 10.0,
            NOICE_CHANGE_PER_RGB,
        )
        bottom_right_state = add_noise(
            rotate(bottom_right_state, 1),
            NOICE_CHANCE_PER_LED / 10.0,
            NOICE_CHANGE_PER_RGB,
        )
        top_state = rotate(top_state, 1)

        apply_state_to_strands(
            strand_left,
            strand_right,
            strand_top,
            top_state,
            top_left_state,
            top_right_state,
            bottom_left_state,
            bottom_right_state,
        )

        # for strand in strands:
        #     strand.fill(random.choice(list(COLORS.values())))
        #     strand.write()
        time.sleep(0.1)


if __name__ == "__main__":
    main()
