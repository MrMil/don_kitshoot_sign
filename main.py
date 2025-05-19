import neopixel
import machine
import random
import time
from machine import Pin
import math
from collections import namedtuple


# New curated list of vibrant colors
CURATED_COLORS = [
    (255, 0, 0),  # Red
    (0, 255, 0),  # Lime Green
    (0, 0, 255),  # Blue
    (255, 255, 0),  # Yellow
    (0, 255, 255),  # Cyan
    (255, 0, 255),  # Magenta
    (255, 128, 0),  # Orange
    (0, 200, 200),  # Teal
    (128, 0, 255),  # Purple
    (255, 0, 128),  # Rose
    (50, 205, 50),  # LimeGreen (alternative, less harsh)
    # (30, 144, 255),  # DodgerBlue
    # (255, 128, 128),  # HotPink
    (255, 215, 0),  # Gold
    (75, 0, 130),  # Indigo
    (0, 128, 128),  # Teal (another shade)
    # (135, 206, 235),  # SkyBlue
]


def generate_random_rgb_color(existing_colors=None):
    return random.choice(CURATED_COLORS)


def get_distinct_colors(num_colors):
    colors_left = set({})
    result = []
    while len(result) < num_colors:
        if len(colors_left) == 0:
            colors_left = set(CURATED_COLORS)

        result.append(random.choice(list(colors_left)))
        colors_left.remove(result[-1])

    return result


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

# We'll use a tuple to represent the state of all strands.
StrandsStates = namedtuple(
    "StrandsStatesTuple",
    [
        "top_state",
        "top_left_state",
        "top_right_state",
        "bottom_left_state",
        "bottom_right_state",
    ],
)


def rotate(strand_state, step):
    new_strand_state = [None] * len(strand_state)
    for i in range(len(strand_state)):
        new_strand_state[i] = strand_state[i - step]
    return new_strand_state


def get_random_strand_state(strand_length):
    return [generate_random_rgb_color() for _ in range(strand_length)]


def apply_state(strand, strand_state):
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
    return [color for _ in range(strand_state_length)]


class Animation:
    def __init__(self, total_steps):
        self.total_steps = total_steps
        self.steps_already_made = 0

    def get_initial_states(self):
        """
        Child class should implement this to return the initial StrandsStates instance.
        """
        # Child needs to implement this
        pass

    def make_step(self, strand_states):
        """
        Advances the animation by one step.
        Returns the new StrandsStatesTuple.
        """
        self.steps_already_made += 1
        return self._child_make_step(strand_states)

    def _child_make_step(self, strand_states):
        """
        Child class should implement this to calculate and return the next StrandsStatesTuple.
        """
        # Child needs to implement this
        pass


class WaveAnimation(Animation):
    def __init__(self, total_steps):
        super().__init__(total_steps)
        colors = get_distinct_colors(3)
        self.wave_color = colors[0]
        self.background_color = colors[1]
        self.top_bar_color = colors[2]

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

        return StrandsStates(
            top_state=top_state,
            top_left_state=top_left_state,
            top_right_state=top_right_state,
            bottom_left_state=bottom_left_state,
            bottom_right_state=bottom_right_state,
        )

    def _child_make_step(self, strand_states):
        self.wave_position += 1

        total_len_sides_vertical = LEN_SIDE_TOP + LEN_SIDE_BOTTOM
        if (
            self.wave_position >= total_len_sides_vertical
        ):  # Wave has completed a full pass down the sides
            self.wave_position = 0  # Reset wave to the top of sides
            # Change colors on reset
            new_colors = get_distinct_colors(3)
            self.wave_color = new_colors[0]
            self.background_color = new_colors[1]
            self.top_bar_color = new_colors[2]

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

        return StrandsStates(
            top_state=new_top_state,
            top_left_state=new_top_left_state,
            top_right_state=new_top_right_state,
            bottom_left_state=new_bottom_left_state,
            bottom_right_state=new_bottom_right_state,
        )


class TopScrollAndQuartersAnimation(Animation):
    def __init__(self, total_steps):
        super().__init__(total_steps)

        self.block_size_top_scroll = 5
        self.buffer_len_for_scroll = (
            (LEN_TOP + self.block_size_top_scroll - 1) // self.block_size_top_scroll
        ) * self.block_size_top_scroll

        self.top_scroll_content = get_block_pattern_strand_state(
            self.buffer_len_for_scroll + LEN_TOP, self.block_size_top_scroll
        )
        self.top_scroll_position = self.buffer_len_for_scroll

        colors = get_distinct_colors(2)
        self.base_color = colors[0]
        self.highlight_color = colors[1]

        self.highlighted_quarter_index = 0  # 0: TL, 1: TR, 2: BL, 3: BR
        self.steps_since_highlight_change = 0
        self.highlight_change_interval = 30  # Change highlighted quarter every 30 steps

    def get_initial_states(self):
        self.top_scroll_content = get_block_pattern_strand_state(
            self.buffer_len_for_scroll + LEN_TOP, self.block_size_top_scroll
        )
        self.top_scroll_position = self.buffer_len_for_scroll

        current_top_state = self.top_scroll_content[
            self.top_scroll_position : self.top_scroll_position + LEN_TOP
        ]

        new_colors_quarters = get_distinct_colors(2)
        self.base_color = new_colors_quarters[0]
        self.highlight_color = new_colors_quarters[1]
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

        return StrandsStates(
            top_state=current_top_state,
            top_left_state=quarters[0],
            top_right_state=quarters[1],
            bottom_left_state=quarters[2],
            bottom_right_state=quarters[3],
        )

    def _child_make_step(self, strand_states):
        self.top_scroll_position -= 1

        if self.top_scroll_position < 0:
            buffer_len_for_scroll = (
                (LEN_TOP + self.block_size_top_scroll - 1) // self.block_size_top_scroll
            ) * self.block_size_top_scroll
            self.top_scroll_content = get_block_pattern_strand_state(
                buffer_len_for_scroll + LEN_TOP, self.block_size_top_scroll
            )
            self.top_scroll_position = buffer_len_for_scroll

        new_top_state = self.top_scroll_content[
            self.top_scroll_position : self.top_scroll_position + LEN_TOP
        ]

        self.steps_since_highlight_change += 1
        if self.steps_since_highlight_change >= self.highlight_change_interval:
            self.steps_since_highlight_change = 0
            self.highlighted_quarter_index = (self.highlighted_quarter_index + 1) % 4
            if self.highlighted_quarter_index == 0:
                new_cycle_colors = get_distinct_colors(2)
                self.base_color = new_cycle_colors[0]
                self.highlight_color = new_cycle_colors[1]

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

        return StrandsStates(
            top_state=new_top_state,
            top_left_state=new_quarters[0],
            top_right_state=new_quarters[1],
            bottom_left_state=new_quarters[2],
            bottom_right_state=new_quarters[3],
        )


class BreathingQuartersAnimation(Animation):
    def __init__(self, total_steps):
        super().__init__(total_steps)
        self.cycles_for_color_change = 3  # Change colors every N breath cycles
        self.breath_speed = 0.1  # Adjust for faster/slower breathing
        self.min_brightness_factor = 0.2
        self.max_brightness_factor = 1.0

        self._reset_cycle_state()  # Initialize colors and breath step

    def _reset_cycle_state(self):
        """Resets colors, breath step, and cycle count for a new color cycle."""
        distinct_colors = get_distinct_colors(2)
        self.quarter_base_color = distinct_colors[0]
        self.top_bar_color = distinct_colors[1]
        self.breath_step = 0.0
        self.current_cycle_count = 0

    def _apply_brightness(self, color, factor):
        r, g, b = color
        factor = max(0.0, min(1.0, factor))
        return (int(r * factor), int(g * factor), int(b * factor))

    def get_initial_states(self):
        self._reset_cycle_state()  # Reset colors and breath cycle for a fresh start

        initial_sin_val = math.sin(self.breath_step)
        brightness_factor = self.min_brightness_factor + ((initial_sin_val + 1) / 2) * (
            self.max_brightness_factor - self.min_brightness_factor
        )

        current_quarter_color = self._apply_brightness(
            self.quarter_base_color, brightness_factor
        )

        top_state = [self.top_bar_color] * LEN_TOP
        top_left_state = [current_quarter_color] * LEN_SIDE_TOP
        top_right_state = [current_quarter_color] * LEN_SIDE_TOP
        bottom_left_state = [current_quarter_color] * LEN_SIDE_BOTTOM
        bottom_right_state = [current_quarter_color] * LEN_SIDE_BOTTOM

        return StrandsStates(
            top_state=top_state,
            top_left_state=top_left_state,
            top_right_state=top_right_state,
            bottom_left_state=bottom_left_state,
            bottom_right_state=bottom_right_state,
        )

    def _child_make_step(self, strand_states):
        self.breath_step += self.breath_speed

        sin_val = math.sin(self.breath_step)
        normalized_sin = (sin_val + 1) / 2
        current_brightness_factor = self.min_brightness_factor + normalized_sin * (
            self.max_brightness_factor - self.min_brightness_factor
        )

        breathing_quarter_color = self._apply_brightness(
            self.quarter_base_color, current_brightness_factor
        )

        new_top_state = [self.top_bar_color] * LEN_TOP
        new_top_left_state = [breathing_quarter_color] * LEN_SIDE_TOP
        new_top_right_state = [breathing_quarter_color] * LEN_SIDE_TOP
        new_bottom_left_state = [breathing_quarter_color] * LEN_SIDE_BOTTOM
        new_bottom_right_state = [breathing_quarter_color] * LEN_SIDE_BOTTOM

        # Check if enough full breath cycles completed to trigger a color/state reset
        # A full 2*pi cycle for self.breath_step means one breath cycle.
        # current_cycle_count tracks how many such 2*pi cycles we've intended to complete for the color change.
        if self.breath_step >= (self.current_cycle_count + 1) * (2 * math.pi):
            self.current_cycle_count += 1
            if self.current_cycle_count >= self.cycles_for_color_change:
                self._reset_cycle_state()  # Reset colors and breath phase for a new color cycle
                # Update colors for the current step with the new state
                # Start new cycle at min brightness (or initial brightness from _reset_cycle_state)
                initial_sin_val_reset = math.sin(
                    self.breath_step
                )  # breath_step is now 0.0
                brightness_factor_reset = self.min_brightness_factor + (
                    (initial_sin_val_reset + 1) / 2
                ) * (self.max_brightness_factor - self.min_brightness_factor)
                breathing_quarter_color = self._apply_brightness(
                    self.quarter_base_color, brightness_factor_reset
                )
                new_top_left_state = [breathing_quarter_color] * LEN_SIDE_TOP
                new_top_right_state = [breathing_quarter_color] * LEN_SIDE_TOP
                new_bottom_left_state = [breathing_quarter_color] * LEN_SIDE_BOTTOM
                new_bottom_right_state = [breathing_quarter_color] * LEN_SIDE_BOTTOM
                new_top_state = [self.top_bar_color] * LEN_TOP

        return StrandsStates(
            top_state=new_top_state,
            top_left_state=new_top_left_state,
            top_right_state=new_top_right_state,
            bottom_left_state=new_bottom_left_state,
            bottom_right_state=new_bottom_right_state,
        )


def get_block_pattern_strand_state(strand_length, block_size):
    state = []
    current_block_color = generate_random_rgb_color()
    color_count_in_block = 0
    for _ in range(strand_length):
        if color_count_in_block >= block_size:
            current_block_color = generate_random_rgb_color(
                existing_colors=[state[-1] if state else None]
            )  # Try to avoid same as last block
            color_count_in_block = 0
        state.append(current_block_color)
        color_count_in_block += 1
    return state


def main():
    physical_strand_left = neopixel.NeoPixel(
        machine.Pin(33, machine.Pin.OUT), LEN_SIDES
    )
    physical_strand_right = neopixel.NeoPixel(
        machine.Pin(26, machine.Pin.OUT), LEN_SIDES
    )
    physical_strand_top = neopixel.NeoPixel(machine.Pin(13, machine.Pin.OUT), LEN_TOP)

    STEPS_PER_ANIMATION = 100

    animations = [
        WaveAnimation(STEPS_PER_ANIMATION),
        TopScrollAndQuartersAnimation(STEPS_PER_ANIMATION),
        BreathingQuartersAnimation(STEPS_PER_ANIMATION),
    ]
    current_animation_index = 0
    current_animation = animations[current_animation_index]
    current_strand_states = current_animation.get_initial_states()

    steps_took_in_current_animation = 0

    while True:
        steps_took_in_current_animation += 1

        # Time to change animation?
        if steps_took_in_current_animation > STEPS_PER_ANIMATION:
            # Initialize new animation
            steps_took_in_current_animation = 0
            current_animation_index = (current_animation_index + 1) % len(animations)
            current_animation = animations[current_animation_index]
            current_strand_states = current_animation.get_initial_states()

        # Make step
        current_strand_states = current_animation.make_step(current_strand_states)

        apply_states_to_strands_from_tuple(
            current_strand_states,
            physical_strand_left,
            physical_strand_right,
            physical_strand_top,
        )

        time.sleep(0.1)


if __name__ == "__main__":
    main()
