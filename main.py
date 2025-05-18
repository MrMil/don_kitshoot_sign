import neopixel
import machine
import random
import time
from machine import Pin


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
# [top            letters] # I call this "top"
# [L]                 [R]
# [L]  (top left)     [R]  (top right)
# [L]                 [R]
#
# [L]  (bottom left)  [R]  (bottom right)
# [L]                 [R]
# [L]                 [R]

# We'll use a tuple to represent the state of all strands.
# StrandsStatesTuple
# (top_state, top_left_state, top_right_state, bottom_left_state, bottom_right_state)


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


def apply_states_to_strands_from_tuple(
    strands_state_tuple,
    physical_strand_left,
    physical_strand_right,
    physical_strand_top,
):
    (
        top_state,
        top_left_state,
        top_right_state,
        bottom_left_state,
        bottom_right_state,
    ) = strands_state_tuple
    apply_state_to_strands(
        physical_strand_left,
        physical_strand_right,
        physical_strand_top,
        top_state,
        top_left_state,
        top_right_state,
        bottom_left_state,
        bottom_right_state,
    )


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


NOICE_CHANCE_PER_LED = 0.1
NOICE_CHANGE_PER_RGB = 10


def get_noise_animation_initial_states():
    return (
        add_noise(
            get_strand_state_in_color(LEN_TOP, COLORS["purple"]),
            NOICE_CHANCE_PER_LED,
            NOICE_CHANGE_PER_RGB,
        ),
        add_noise(
            get_strand_state_in_color(LEN_SIDE_TOP, COLORS["red"]),
            NOICE_CHANCE_PER_LED,
            NOICE_CHANGE_PER_RGB,
        ),
        add_noise(
            get_strand_state_in_color(LEN_SIDE_TOP, COLORS["green"]),
            NOICE_CHANCE_PER_LED,
            NOICE_CHANGE_PER_RGB,
        ),
        add_noise(
            get_strand_state_in_color(LEN_SIDE_BOTTOM, COLORS["blue"]),
            NOICE_CHANCE_PER_LED,
            NOICE_CHANGE_PER_RGB,
        ),
        add_noise(
            get_strand_state_in_color(LEN_SIDE_BOTTOM, COLORS["orange"]),
            NOICE_CHANCE_PER_LED,
            NOICE_CHANGE_PER_RGB,
        ),
    )


def get_noise_animation_step(strand_states):
    return (
        rotate(strand_states[0], 1),
        rotate(strand_states[1], 1),
        rotate(strand_states[2], 1),
        rotate(strand_states[3], 1),
        rotate(strand_states[4], 1),
    )


class Animation:
    def get_initial_states(self):
        """
        Returns StrandsStatesTuple
        """
        pass

    def make_step(self, strand_states):
        """
        Converts StrandsStatesTuple into a new StrandsStatesTuple
        """
        pass


class WalkingNoiseAnimation(Animation):
    def get_initial_states(self):
        return get_noise_animation_initial_states()

    def make_step(self, strand_states):
        return get_noise_animation_step(strand_states)


class WaveAnimation(Animation):
    def __init__(self):
        self.wave_color = random.choice(list(COLORS.values()))
        self.background_color = random.choice(list(COLORS.values()))
        self.top_bar_color = random.choice(list(COLORS.values()))
        while self.background_color == self.wave_color:
            self.background_color = random.choice(list(COLORS.values()))
        while (
            self.top_bar_color == self.wave_color
            or self.top_bar_color == self.background_color
        ):
            self.top_bar_color = random.choice(list(COLORS.values()))

        self.wave_position = 0  # 0 to (LEN_SIDE_TOP + LEN_SIDE_BOTTOM - 1)
        self.wave_width = 8

    def get_initial_states(self):
        self.wave_position = 0
        # Initialize top bar to its static color
        top_state = [self.top_bar_color] * LEN_TOP

        # Initialize sides to background
        top_left_state = [self.background_color] * LEN_SIDE_TOP
        top_right_state = [self.background_color] * LEN_SIDE_TOP
        bottom_left_state = [self.background_color] * LEN_SIDE_BOTTOM
        bottom_right_state = [self.background_color] * LEN_SIDE_BOTTOM

        # Apply initial wave at the top of the side panels
        for i in range(self.wave_width):
            current_pos_in_wave = (
                self.wave_position + i
            )  # This is effectively just i for initial state
            if 0 <= current_pos_in_wave < LEN_SIDE_TOP:
                top_left_state[current_pos_in_wave] = self.wave_color
                top_right_state[current_pos_in_wave] = self.wave_color
            # N.B. Wave won't reach bottom_side initially if wave_width <= LEN_SIDE_TOP

        return (
            top_state,
            top_left_state,
            top_right_state,
            bottom_left_state,
            bottom_right_state,
        )

    def make_step(self, strand_states):
        self.wave_position += 1

        total_len_sides_vertical = LEN_SIDE_TOP + LEN_SIDE_BOTTOM
        if (
            self.wave_position >= total_len_sides_vertical
        ):  # Wave has completed a full pass down the sides
            self.wave_position = 0  # Reset wave to the top of sides
            # Change colors on reset
            self.wave_color = random.choice(list(COLORS.values()))
            self.background_color = random.choice(list(COLORS.values()))
            self.top_bar_color = random.choice(list(COLORS.values()))
            while self.background_color == self.wave_color:
                self.background_color = random.choice(list(COLORS.values()))
            while (
                self.top_bar_color == self.wave_color
                or self.top_bar_color == self.background_color
            ):
                self.top_bar_color = random.choice(list(COLORS.values()))

        # Top state remains constant
        new_top_state = [self.top_bar_color] * LEN_TOP

        # Create new side states, initialized to background
        new_top_left_state = [self.background_color] * LEN_SIDE_TOP
        new_top_right_state = [self.background_color] * LEN_SIDE_TOP
        new_bottom_left_state = [self.background_color] * LEN_SIDE_BOTTOM
        new_bottom_right_state = [self.background_color] * LEN_SIDE_BOTTOM

        # Apply wave to side panels
        for i in range(self.wave_width):
            current_led_index_in_sides = (
                self.wave_position + i
            )  # This is the 0-indexed position from the very top of side panels

            # Wave on Top_Sides (Left and Right are parallel)
            if current_led_index_in_sides < LEN_SIDE_TOP:
                # Check if the current segment of the wave is within the bounds of top_left/right_state
                actual_pos_in_top_side = current_led_index_in_sides
                if (
                    0 <= actual_pos_in_top_side < LEN_SIDE_TOP
                ):  # current_led_index_in_sides will always be >=0 here
                    new_top_left_state[actual_pos_in_top_side] = self.wave_color
                    new_top_right_state[actual_pos_in_top_side] = self.wave_color
            # Wave on Bottom_Sides (Left and Right are parallel)
            elif (
                current_led_index_in_sides < total_len_sides_vertical
            ):  # current_led_index_in_sides < LEN_SIDE_TOP + LEN_SIDE_BOTTOM
                # Calculate position relative to the start of bottom_left/right_state
                actual_pos_in_bottom_side = current_led_index_in_sides - LEN_SIDE_TOP
                if 0 <= actual_pos_in_bottom_side < LEN_SIDE_BOTTOM:
                    new_bottom_left_state[actual_pos_in_bottom_side] = self.wave_color
                    new_bottom_right_state[actual_pos_in_bottom_side] = self.wave_color

        return (
            new_top_state,
            new_top_left_state,
            new_top_right_state,
            new_bottom_left_state,
            new_bottom_right_state,
        )


def get_block_pattern_strand_state(strand_length, block_size):
    state = []
    while len(state) < strand_length:
        color = random.choice(list(COLORS.values()))
        for _ in range(block_size):
            if len(state) < strand_length:
                state.append(color)
            else:
                break
    return state


class TopScrollAndQuartersAnimation(Animation):
    def __init__(self):
        self.block_size_top_scroll = 5
        # Add extra length for seamless looping of the scroll
        self.top_scroll_content = get_block_pattern_strand_state(
            LEN_TOP + self.block_size_top_scroll * 2, self.block_size_top_scroll
        )
        self.top_scroll_position = 0

        self.base_color = random.choice(list(COLORS.values()))
        self.highlight_color = random.choice(list(COLORS.values()))
        while self.highlight_color == self.base_color:
            self.highlight_color = random.choice(list(COLORS.values()))

        self.highlighted_quarter_index = 0  # 0: TL, 1: TR, 2: BL, 3: BR
        self.steps_since_highlight_change = 0
        self.highlight_change_interval = 30  # Change highlighted quarter every 30 steps

    def get_initial_states(self):
        self.top_scroll_position = 0
        current_top_state = self.top_scroll_content[
            self.top_scroll_position : self.top_scroll_position + LEN_TOP
        ]

        self.base_color = random.choice(list(COLORS.values()))
        self.highlight_color = random.choice(list(COLORS.values()))
        while self.highlight_color == self.base_color:
            self.highlight_color = random.choice(list(COLORS.values()))
        self.highlighted_quarter_index = 0
        self.steps_since_highlight_change = 0

        quarters = []
        for i in range(4):
            color = (
                self.highlight_color
                if i == self.highlighted_quarter_index
                else self.base_color
            )
            if i < 2:  # Top quarters
                quarters.append([color] * LEN_SIDE_TOP)
            else:  # Bottom quarters
                quarters.append([color] * LEN_SIDE_BOTTOM)

        return (
            current_top_state,
            quarters[0],  # Top Left
            quarters[1],  # Top Right
            quarters[2],  # Bottom Left
            quarters[3],  # Bottom Right
        )

    def make_step(self, strand_states):
        # Animate top scroll (right to left)
        self.top_scroll_position += 1
        if self.top_scroll_position >= len(self.top_scroll_content) - LEN_TOP:
            self.top_scroll_position = 0
            # Regenerate scroll content for variety if desired, or let it loop
            self.top_scroll_content = get_block_pattern_strand_state(
                LEN_TOP + self.block_size_top_scroll * 2, self.block_size_top_scroll
            )

        new_top_state = self.top_scroll_content[
            self.top_scroll_position : self.top_scroll_position + LEN_TOP
        ]

        # Animate quarters highlight
        self.steps_since_highlight_change += 1
        if self.steps_since_highlight_change >= self.highlight_change_interval:
            self.steps_since_highlight_change = 0
            self.highlighted_quarter_index = (self.highlighted_quarter_index + 1) % 4
            # Optionally, change base and highlight colors when the cycle completes or at interval
            if self.highlighted_quarter_index == 0:  # Cycle completed
                self.base_color = random.choice(list(COLORS.values()))
                self.highlight_color = random.choice(list(COLORS.values()))
                while self.highlight_color == self.base_color:
                    self.highlight_color = random.choice(list(COLORS.values()))

        new_quarters = []
        for i in range(4):
            color = (
                self.highlight_color
                if i == self.highlighted_quarter_index
                else self.base_color
            )
            if i < 2:  # Top quarters (TL, TR)
                new_quarters.append([color] * LEN_SIDE_TOP)
            else:  # Bottom quarters (BL, BR)
                new_quarters.append([color] * LEN_SIDE_BOTTOM)

        return (
            new_top_state,
            new_quarters[0],  # Top Left
            new_quarters[1],  # Top Right
            new_quarters[2],  # Bottom Left
            new_quarters[3],  # Bottom Right
        )


def main():
    physical_strand_left = neopixel.NeoPixel(
        machine.Pin(33, machine.Pin.OUT), LEN_SIDES
    )
    physical_strand_right = neopixel.NeoPixel(
        machine.Pin(26, machine.Pin.OUT), LEN_SIDES
    )
    physical_strand_top = neopixel.NeoPixel(machine.Pin(13, machine.Pin.OUT), LEN_TOP)

    animations = [
        WaveAnimation(),
        TopScrollAndQuartersAnimation(),
    ]
    current_animation_index = 0
    current_animation = animations[current_animation_index]
    strand_states = current_animation.get_initial_states()

    step_count = 0
    steps_per_animation = 100  # Change animation every 100 steps

    while True:
        strand_states = current_animation.make_step(strand_states)
        apply_states_to_strands_from_tuple(
            strand_states,
            physical_strand_left,
            physical_strand_right,
            physical_strand_top,
        )

        time.sleep(0.1)
        step_count += 1

        if step_count >= steps_per_animation:
            step_count = 0
            current_animation_index = (current_animation_index + 1) % len(animations)
            current_animation = animations[current_animation_index]
            # Important: Re-initialize states for the new animation
            # If the new animation object was just created, get_initial_states might be redundant
            # but if we reuse animation objects that have internal state, it's crucial.
            # For classes like WaveAnimation with __init__, better to re-create or have a reset method.
            # Simplest for now: create new instances when switching
            if isinstance(
                current_animation, WalkingNoiseAnimation
            ):  # stateless, can reuse
                strand_states = current_animation.get_initial_states()
            elif isinstance(
                current_animation, WaveAnimation
            ):  # stateful due to __init__
                animations[current_animation_index] = WaveAnimation()  # Re-create
                current_animation = animations[current_animation_index]
                strand_states = current_animation.get_initial_states()
            elif isinstance(current_animation, TopScrollAndQuartersAnimation):
                animations[current_animation_index] = (
                    TopScrollAndQuartersAnimation()
                )  # Re-create
                current_animation = animations[current_animation_index]
                strand_states = current_animation.get_initial_states()


if __name__ == "__main__":
    main()
