import neopixel
import machine
import random
import time
from machine import Pin
import math

# Define colors as a simple array of RGB tuples
COLORS = [
    (255, 0, 0),      # red
    (0, 255, 0),      # lime_green
    (0, 0, 255),      # blue
    (255, 255, 0),    # yellow
    (0, 255, 255),    # cyan
    (255, 0, 255),    # magenta
    (255, 128, 0),    # orange
    #(0, 200, 200),    # teal
    (128, 0, 255),    # purple
    (255, 0, 128),    # rose
    (50, 205, 50),    # lime_green_alt
    # (255, 215, 0),    # gold
    (75, 0, 130),     # indigo
    # (0, 128, 128),    # teal_alt
]

def interpolate_color(color1, color2, factor):
    """
    Interpolate between two colors.
    Args:
        color1: First color (r,g,b)
        color2: Second color (r,g,b)
        factor: Interpolation factor (0.0 to 1.0)
    Returns:
        Interpolated color (r,g,b)
    """
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    r = int(r1 + (r2 - r1) * factor)
    g = int(g1 + (g2 - g1) * factor)
    b = int(b1 + (b2 - b1) * factor)
    return (r, g, b)

def get_random_color():
    """Returns a random color from the COLORS array."""
    return random.choice(COLORS)

def get_different_random_color(current_color):
    """Returns a random color that is different from the current color."""
    available_colors = [color for color in COLORS if color != current_color]
    return random.choice(available_colors)

class Animation:
    def __init__(self):
        pass

    def make_step(self):
        """
        Advances the animation by one step.
        Returns True if animation is complete, False otherwise.
        """
        raise NotImplementedError("Subclasses must implement this method")

class BaseSweepAnimation(Animation):
    def __init__(self, steps, initial_color):
        """
        Base class for sweep animations.
        Args:
            steps: The number of steps in the animation
            initial_color: The initial color of the animation
        """
        super().__init__(total_steps=steps)
        self.steps = steps
        self.from_color = initial_color
        self.to_color = get_different_random_color(initial_color)
        self.position = 0
        self.fade_length = 5  # Number of LEDs for color fade

    def _update_colors(self):
        """Update colors when animation completes."""
        self.from_color, self.to_color = self.to_color, get_different_random_color(self.to_color)

    def _get_color_at_position(self, pos, total_length):
        """
        Get the interpolated color at a given position.
        Args:
            pos: Current position in the strand
            total_length: Total length of the strand
        Returns:
            Interpolated color for the position
        """
        if pos < self.fade_length:
            # Fade in at start
            factor = pos / self.fade_length
            return interpolate_color(self.from_color, self.to_color, factor)
        elif pos > total_length - self.fade_length:
            # Fade out at end
            factor = (total_length - pos) / self.fade_length
            return interpolate_color(self.to_color, self.from_color, factor)
        else:
            # Full color in middle
            return self.to_color

class ColorSweep(BaseSweepAnimation):
    def __init__(self, strand, steps, initial_color, direction):
        """
        Initialize the color sweep animation.
        Args:
            strand: The strand to animate
            steps: The number of steps in the animation
            initial_color: The initial color of the animation
            direction: The direction of the animation
        """
        super().__init__(steps, initial_color)
        self.strand = strand
        self.direction = direction
        self.led_count = len(strand)
        self.step_size = self.led_count / self.steps
        self.strand.fill(self.from_color)

    def make_step(self):
        # Calculate the exact position based on step
        exact_position = self.position * self.step_size
        
        # Get the LED indices that should be affected
        if self.direction == 'forward':
            start_led = int(exact_position)
            end_led = min(int(exact_position + self.step_size), self.led_count)
        else:
            end_led = self.led_count - int(exact_position)
            start_led = max(0, self.led_count - int(exact_position + self.step_size))

        # Update the LEDs in the affected range with interpolated colors
        for i in range(start_led, end_led):
            if self.direction == 'forward':
                self.strand[i] = self._get_color_at_position(i, self.led_count)
            else:
                self.strand[i] = self._get_color_at_position(self.led_count - i - 1, self.led_count)

        # Update position for next step
        if self.direction == 'forward':
            self.position += 1
            if self.position >= self.steps:
                self.position = 0
                self._update_colors()
                self.strand.write()
                return True  # Return True when reaching the end
        else:
            self.position += 1
            if self.position >= self.steps:
                self.position = 0
                self._update_colors()
                self.strand.write()
                return True  # Return True when reaching the end
        
        self.strand.write()
        return False

class DualColorSweep(BaseSweepAnimation):
    def __init__(self, strand1, strand2, steps, initial_color):
        """
        Initialize the dual color sweep animation.
        Args:
            strand1: First strand to animate
            strand2: Second strand to animate
            steps: The number of steps in the animation
            initial_color: The initial color of the animation
        """
        super().__init__(steps, initial_color)
        self.strand1 = strand1
        self.strand2 = strand2
        self.led_count = len(strand1)  # Assuming both strands are same length
        self.step_size = self.led_count / self.steps
        self.strand1.fill(self.from_color)
        self.strand2.fill(self.from_color)

    def make_step(self):
        # Calculate the exact position based on step
        exact_position = self.position * self.step_size
        
        # Get the LED indices that should be affected
        # Strand1 goes forward
        start_led1 = int(exact_position)
        end_led1 = min(int(exact_position + self.step_size), self.led_count)
        
        # Strand2 goes backward
        end_led2 = self.led_count - int(exact_position)
        start_led2 = max(0, self.led_count - int(exact_position + self.step_size))

        # Update the LEDs in the affected ranges with interpolated colors
        for i in range(start_led1, end_led1):
            self.strand1[i] = self._get_color_at_position(i, self.led_count)
        for i in range(start_led2, end_led2):
            self.strand2[i] = self._get_color_at_position(self.led_count - i - 1, self.led_count)

        # Update position for next step
        self.position += 1
        if self.position >= self.steps:
            self.position = 0
            self._update_colors()
            self.strand1.write()
            self.strand2.write()
            return True  # Return True when reaching the end
        
        self.strand1.write()
        self.strand2.write()
        return False

class QuarterSpiralAnimation(Animation):
    def __init__(self, left_strand, right_strand, top_length, bottom_length, initial_delay=20, acceleration_factor=0.04):
        """
        Initialize the quarter spiral animation.
        Args:
            left_strand: The left strand
            right_strand: The right strand
            top_length: Number of LEDs in top quarters (NW and NE)
            bottom_length: Number of LEDs in bottom quarters (SE and SW)
            initial_delay: Initial delay between quarters (in steps)
            acceleration_factor: How much to reduce delay each quarter (0.0 to 1.0)
        """
        super().__init__(total_steps=1000)  # Large number since we'll control our own completion
        self.left_strand = left_strand
        self.right_strand = right_strand
        self.initial_delay = initial_delay  # Set initial_delay first
        
        # Define quarter lengths from parameters
        self.quarter_lengths = {
            0: top_length,    # NW (left top)
            1: top_length,    # NE (right top)
            2: bottom_length, # SE (right bottom)
            3: bottom_length  # SW (left bottom)
        }
        
        # Animation state
        self.current_quarter = 0  # 0=NW, 1=NE, 2=SE, 3=SW
        self.current_color = get_random_color()
        self.next_color = get_different_random_color(self.current_color)
        self.delay = self.initial_delay  # Use self.initial_delay here
        self.current_step = 0
        self.acceleration_factor = acceleration_factor
        self.accelerating = True  # Track if we're speeding up or slowing down

    def _fill_quarter(self, quarter):
        """Fill a quarter with the current color."""
        start, end = self._get_quarter_range(quarter)
        strand = self.left_strand if quarter in [0, 3] else self.right_strand
        
        # Fill all LEDs in the quarter instantly
        for i in range(start, end):
            strand[i] = self.current_color

    def _get_quarter_range(self, quarter):
        """Get the LED range for a given quarter."""
        if quarter == 0:  # NW (left top)
            return (0, self.quarter_lengths[0])  # Start from beginning of left strand
        elif quarter == 1:  # NE (right top)
            return (0, self.quarter_lengths[1])  # Start from beginning of right strand
        elif quarter == 2:  # SE (right bottom)
            return (self.quarter_lengths[1], self.quarter_lengths[1] + self.quarter_lengths[2])  # Start after NE quarter
        else:  # SW (left bottom)
            return (self.quarter_lengths[0], self.quarter_lengths[0] + self.quarter_lengths[3])  # Start after NW quarter

    def make_step(self):
        # Normal animation
        self.current_step += 1
        
        # Check if it's time to move to next quarter
        if self.current_step >= self.delay:
            # Fill current quarter instantly
            self._fill_quarter(self.current_quarter)
            
            # Move to next quarter
            self.current_quarter += 1
            
            # Reset step counter
            self.current_step = 0
            # Check if all quarters are complete
            if self.current_quarter >= 4:
                self.current_quarter = 0
                self.current_color = self.next_color
                self.next_color = get_different_random_color(self.current_color)
                # Update delay after complete cycle
                reduction = (self.delay / self.initial_delay) ** (1/3) * self.acceleration_factor * 2
                if self.accelerating:
                    new_delay = max(2, self.delay * (1 - reduction))
                    if new_delay <= 2:
                        self.accelerating = False  # Start slowing down
                else:
                    new_delay = min(self.initial_delay, self.delay * (1 + reduction))
                self.delay = new_delay
        
        # Update strands
        self.left_strand.write()
        self.right_strand.write()
        
        # Return completion status
        # Animation is "done" when we complete a full cycle (reach initial delay again)
        if not self.accelerating and self.delay >= self.initial_delay:
            self.accelerating = True
            return True
        return False



