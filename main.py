import neopixel
import machine
import random
import time
from machine import Pin
import math

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


MAX_COLOR_GEN_ATTEMPTS = (
    20  # Keep this for attempts to find a *distinct* color from the list
)


def generate_random_rgb_color(existing_colors=None):
    """
    Selects a random RGB color from CURATED_COLORS.
    Tries to pick one not in existing_colors.
    """
    if existing_colors is None:
        existing_colors = []

    if not CURATED_COLORS:  # Should not happen if CURATED_COLORS is defined
        return (0, 0, 0)  # Fallback black

    available_colors = [c for c in CURATED_COLORS if c not in existing_colors]

    if available_colors:
        return random.choice(available_colors)
    else:
        # If all curated colors are already in existing_colors (e.g., asking for more distinct colors than available)
        # or if existing_colors is just very full, just pick any from CURATED_COLORS.
        return random.choice(CURATED_COLORS)


def get_distinct_colors(num_colors):
    if not CURATED_COLORS:
        return [(0, 0, 0)] * num_colors
    if num_colors <= 0:
        return []

    colors = list(CURATED_COLORS)
    random.shuffle(colors)
    result = colors[: min(num_colors, len(colors))]

    while len(result) < num_colors:
        result.append(random.choice(CURATED_COLORS))

    return result


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
    returns a strand where colors are random using the new generation logic
    """
    return [generate_random_rgb_color() for _ in range(strand_length)]


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
    colors = get_distinct_colors(5)  # Need 5 distinct colors
    return (
        add_noise(
            get_strand_state_in_color(LEN_TOP, colors[0]),
            NOICE_CHANCE_PER_LED,
            NOICE_CHANGE_PER_RGB,
        ),
        add_noise(
            get_strand_state_in_color(LEN_SIDE_TOP, colors[1]),
            NOICE_CHANCE_PER_LED,
            NOICE_CHANGE_PER_RGB,
        ),
        add_noise(
            get_strand_state_in_color(LEN_SIDE_TOP, colors[2]),
            NOICE_CHANCE_PER_LED,
            NOICE_CHANGE_PER_RGB,
        ),
        add_noise(
            get_strand_state_in_color(LEN_SIDE_BOTTOM, colors[3]),
            NOICE_CHANCE_PER_LED,
            NOICE_CHANGE_PER_RGB,
        ),
        add_noise(
            get_strand_state_in_color(LEN_SIDE_BOTTOM, colors[4]),
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
    def __init__(self, total_steps):
        self.total_steps = total_steps
        self.steps_already_made = 0

    def get_initial_states(self):
        """
        Returns (strand_states_tuple, current_step, total_steps)
        """
        return (None, 0, self.total_steps)

    def make_step(self, strand_states):
        """
        Converts StrandsStatesTuple into a new (StrandsStatesTuple, current_step, total_steps)
        """
        self.steps_already_made += 1
        return (None, self.steps_already_made, self.total_steps)


class WalkingNoiseAnimation(Animation):
    def __init__(self):
        super().__init__(0)  # No total steps for this animation

    def get_initial_states(self):
        return (get_noise_animation_initial_states(), 0, self.total_steps)

    def make_step(self, strand_states):
        return (
            get_noise_animation_step(strand_states),
            self.steps_already_made,
            self.total_steps,
        )


class WaveAnimation(Animation):
    def __init__(self):
        total_steps = LEN_SIDE_TOP + LEN_SIDE_BOTTOM  # One full wave cycle
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

        return (
            (
                top_state,
                top_left_state,
                top_right_state,
                bottom_left_state,
                bottom_right_state,
            ),
            self.wave_position,
            self.total_steps,
        )

    def make_step(self, strand_states):
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

        return (
            (
                new_top_state,
                new_top_left_state,
                new_top_right_state,
                new_bottom_left_state,
                new_bottom_right_state,
            ),
            self.wave_position,
            self.total_steps,
        )


class TopScrollAndQuartersAnimation(Animation):
    def __init__(self):
        self.block_size_top_scroll = 5
        # Add extra length for seamless looping of the scroll
        # Content needs to be long enough for left-to-right scroll where a piece disappears on left and new appears on right
        # So, if LEN_TOP is visible, and we shift, we need content of at least LEN_TOP + block_size_top_scroll for one new block to come in.
        # To make it loop smoothly, content should be ~2*LEN_TOP or some multiple of block_size that covers scrolling range.
        # Let's try (LEN_TOP rounded up to nearest block_size_multiple) + LEN_TOP for buffer.
        buffer_len_for_scroll = (
            (LEN_TOP + self.block_size_top_scroll - 1) // self.block_size_top_scroll
        ) * self.block_size_top_scroll
        self.top_scroll_content = get_block_pattern_strand_state(
            buffer_len_for_scroll + LEN_TOP, self.block_size_top_scroll
        )
        self.top_scroll_position = buffer_len_for_scroll  # Start by showing the 'end' part of the buffer, so first visible is start of 'real' content
        total_steps = buffer_len_for_scroll  # One full scroll cycle (buffer length)
        super().__init__(total_steps)

        colors = get_distinct_colors(2)
        self.base_color = colors[0]
        self.highlight_color = colors[1]

        self.highlighted_quarter_index = 0  # 0: TL, 1: TR, 2: BL, 3: BR
        self.steps_since_highlight_change = 0
        self.highlight_change_interval = 30  # Change highlighted quarter every 30 steps

    def get_initial_states(self):
        # Create new scroll content each time for variety
        buffer_len_for_scroll = (
            (LEN_TOP + self.block_size_top_scroll - 1) // self.block_size_top_scroll
        ) * self.block_size_top_scroll
        self.top_scroll_content = get_block_pattern_strand_state(
            buffer_len_for_scroll + LEN_TOP, self.block_size_top_scroll
        )
        self.top_scroll_position = buffer_len_for_scroll
        self.total_steps = (
            buffer_len_for_scroll  # Update total steps based on new buffer length
        )

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

        return (
            (current_top_state, quarters[0], quarters[1], quarters[2], quarters[3]),
            self.top_scroll_position,
            self.total_steps,
        )

    def make_step(self, strand_states):
        # Animate top scroll (LEFT to RIGHT, content moves right, so window moves left)
        self.top_scroll_position -= 1
        # The scroll content is like [BUFFER_FOR_RIGHT_APPEARANCE | ACTUAL_CONTENT_INITIALLY_VISIBLE]
        # Example: LEN_TOP=3, scroll_content = [b1,b2,b3, d1,d2,d3]. initial pos=3. shows [d1,d2,d3]
        # pos=2: shows [b3,d1,d2]. pos=1: shows [b2,b3,d1]. pos=0: shows [b1,b2,b3]
        # When pos < 0, it should wrap around to show the end of the content again.
        # To achieve smooth looping from left to right, the content needs to be conceptually circular.
        # A simple way is to have content like [A,B,C,D,E] and if LEN_TOP is 3:
        # show [A,B,C] (pos 0)
        # show [E,A,B] (pos -1, wrapped to pos 4, showing content[4], content[0], content[1] - needs specific slicing)
        # Or, simpler: top_scroll_content = get_block_pattern_strand_state(LEN_TOP, ...)
        # and then new_top_state = rotate(previous_top_state, -1) (for L-to-R) and fill in new element at [0]

        # Let's use the buffer approach: self.top_scroll_content = [buffer_for_new_elements | main_elements_to_loop]
        # total length of top_scroll_content is `buffer_len_for_scroll + LEN_TOP`
        # buffer_len_for_scroll is where "new" elements are taken from when scrolling right.
        # if self.top_scroll_position < 0:
        #    self.top_scroll_position = buffer_len_for_scroll -1 # This needs adjustment to make it loop correctly

        if self.top_scroll_position < 0:
            # If we scrolled past the beginning of the buffer, regenerate and reset position
            # This creates a continuous fresh stream of blocks from the right
            buffer_len_for_scroll = (
                (LEN_TOP + self.block_size_top_scroll - 1) // self.block_size_top_scroll
            ) * self.block_size_top_scroll
            self.top_scroll_content = get_block_pattern_strand_state(
                buffer_len_for_scroll + LEN_TOP, self.block_size_top_scroll
            )
            self.top_scroll_position = buffer_len_for_scroll
            self.total_steps = (
                buffer_len_for_scroll  # Update total steps based on new buffer length
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

        return (
            (
                new_top_state,
                new_quarters[0],
                new_quarters[1],
                new_quarters[2],
                new_quarters[3],
            ),
            self.top_scroll_position,
            self.total_steps,
        )


class BreathingQuartersAnimation(Animation):
    def __init__(self):
        self.cycles_for_color_change = 3  # Change colors every N breath cycles
        self.current_cycle_count = 0
        self._setup_colors_and_breath()

    def _setup_colors_and_breath(self):
        distinct_colors = get_distinct_colors(2)
        self.quarter_base_color = distinct_colors[0]
        self.top_bar_color = distinct_colors[1]

        self.breath_step = 0.0
        self.breath_speed = 0.1  # Adjust for faster/slower breathing
        self.min_brightness_factor = 0.2
        self.max_brightness_factor = 1.0
        self.breath_period_steps = (
            2 * math.pi
        ) / self.breath_speed  # Steps for one full sin wave cycle
        total_steps = (
            self.breath_period_steps * self.cycles_for_color_change
        )  # Total steps for color change
        super().__init__(total_steps)

    def _apply_brightness(self, color, factor):
        r, g, b = color
        # Ensure factor is clamped to avoid issues, though sin scaling should handle it
        factor = max(0.0, min(1.0, factor))
        return (int(r * factor), int(g * factor), int(b * factor))

    def get_initial_states(self):
        self._setup_colors_and_breath()  # Reset colors and breath cycle
        self.current_cycle_count = 0

        # Initial brightness (e.g., mid-point or min_brightness)
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

        return (
            (
                top_state,
                top_left_state,
                top_right_state,
                bottom_left_state,
                bottom_right_state,
            ),
            self.breath_step,
            self.total_steps,
        )

    def make_step(self, strand_states):
        self.breath_step += self.breath_speed

        # Scale sin output (-1 to 1) to (0 to 1), then to (min_factor to max_factor)
        sin_val = math.sin(self.breath_step)
        normalized_sin = (sin_val + 1) / 2  # Scale to 0-1 range
        current_brightness_factor = self.min_brightness_factor + normalized_sin * (
            self.max_brightness_factor - self.min_brightness_factor
        )

        breathing_quarter_color = self._apply_brightness(
            self.quarter_base_color, current_brightness_factor
        )

        new_top_state = [
            self.top_bar_color
        ] * LEN_TOP  # Top bar is static for this step
        new_top_left_state = [breathing_quarter_color] * LEN_SIDE_TOP
        new_top_right_state = [breathing_quarter_color] * LEN_SIDE_TOP
        new_bottom_left_state = [breathing_quarter_color] * LEN_SIDE_BOTTOM
        new_bottom_right_state = [breathing_quarter_color] * LEN_SIDE_BOTTOM

        # Check if a full breath cycle completed to count towards color change
        if self.breath_step >= (self.current_cycle_count + 1) * (
            2 * math.pi
        ):  # Check based on angle not just step count relative to period
            self.current_cycle_count += 1
            if self.current_cycle_count >= self.cycles_for_color_change:
                self._setup_colors_and_breath()  # Reset colors and breath phase
                self.current_cycle_count = 0
                # Update the colors immediately for the current step return values
                # Or it will take one more step with old color and new brightness phase
                breathing_quarter_color = self._apply_brightness(
                    self.quarter_base_color, self.min_brightness_factor
                )  # Start new cycle at min brightness
                new_top_left_state = [breathing_quarter_color] * LEN_SIDE_TOP
                new_top_right_state = [breathing_quarter_color] * LEN_SIDE_TOP
                new_bottom_left_state = [breathing_quarter_color] * LEN_SIDE_BOTTOM
                new_bottom_right_state = [breathing_quarter_color] * LEN_SIDE_BOTTOM
                new_top_state = [self.top_bar_color] * LEN_TOP

        return (
            (
                new_top_state,
                new_top_left_state,
                new_top_right_state,
                new_bottom_left_state,
                new_bottom_right_state,
            ),
            self.breath_step,
            self.total_steps,
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

    animations = [
        # WalkingNoiseAnimation(),
        WaveAnimation(),
        TopScrollAndQuartersAnimation(),
        BreathingQuartersAnimation(),
    ]
    current_animation_index = 0
    current_animation = animations[current_animation_index]
    strand_states_tuple, current_step, total_steps = (
        current_animation.get_initial_states()
    )

    while True:
        # Check if animation cycle is complete
        if current_step >= total_steps:
            current_animation_index = (current_animation_index + 1) % len(animations)
            current_animation = animations[current_animation_index]
            strand_states_tuple, current_step, total_steps = (
                current_animation.get_initial_states()
            )
        else:
            # Get next step from current animation
            strand_states_tuple, current_step, total_steps = (
                current_animation.make_step(strand_states_tuple)
            )

        # Apply the current state to the physical strands
        apply_states_to_strands_from_tuple(
            strand_states_tuple,
            physical_strand_left,
            physical_strand_right,
            physical_strand_top,
        )

        time.sleep(0.1)


if __name__ == "__main__":
    main()
