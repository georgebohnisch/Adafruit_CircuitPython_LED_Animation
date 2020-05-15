# The MIT License (MIT)
#
# Copyright (c) 2019-2020 Roy Hooper
# Copyright (c) 2020 Kattni Rembor for Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`adafruit_led_animation.sparkle`
================================================================================

Sparkle animations for CircuitPython helper library for LED animations.


* Author(s): Roy Hooper, Kattni Rembor

Implementation Notes
--------------------

**Hardware:**

* `Adafruit NeoPixels <https://www.adafruit.com/category/168>`_
* `Adafruit DotStars <https://www.adafruit.com/category/885>`_

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

"""

import random
from adafruit_led_animation.animation import Animation
from . import NANOS_PER_SECOND, monotonic_ns

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_LED_Animation.git"


class Sparkle(Animation):
    """
    Sparkle animation of a single color.

    :param pixel_object: The initialised LED object.
    :param float speed: Animation speed in seconds, e.g. ``0.1``.
    :param color: Animation color in ``(r, g, b)`` tuple, or ``0x000000`` hex format.
    :param num_sparkles: Number of sparkles to generate per animation cycle.
    """

    # pylint: disable=too-many-arguments
    def __init__(self, pixel_object, speed, color, num_sparkles=1, name=None):
        if len(pixel_object) < 2:
            raise ValueError("Sparkle needs at least 2 pixels")
        self._half_color = None
        self._dim_color = None
        self._num_sparkles = num_sparkles
        super().__init__(pixel_object, speed, color, name=name)

    def _recompute_color(self, color):
        half_color = tuple(color[rgb] // 4 for rgb in range(len(color)))
        dim_color = tuple(color[rgb] // 10 for rgb in range(len(color)))
        for pixel in range(len(self.pixel_object)):
            if self.pixel_object[pixel] == self._half_color:
                self.pixel_object[pixel] = half_color
            elif self.pixel_object[pixel] == self._dim_color:
                self.pixel_object[pixel] = dim_color
        self._half_color = half_color
        self._dim_color = dim_color

    def draw(self):
        pixels = [
            random.randint(0, (len(self.pixel_object) - 2))
            for n in range(self._num_sparkles)
        ]
        for pixel in pixels:
            self.pixel_object[pixel] = self._color
        self.show()
        for pixel in pixels:
            self.pixel_object[pixel] = self._half_color
            self.pixel_object[pixel + 1] = self._dim_color
        self.show()


class SparklePulse(Animation):
    """
    Combination of the Spark and Pulse animations.

    :param pixel_object: The initialised LED object.
    :param int speed: Animation refresh rate in seconds, e.g. ``0.1``.
    :param color: Animation color in ``(r, g, b)`` tuple, or ``0x000000`` hex format.
    :param period: Period to pulse the LEDs over.  Default 5.
    :param max_intensity: The maximum intensity to pulse, between 0 and 1.0.  Default 1.
    :param min_intensity: The minimum intensity to pulse, between 0 and 1.0.  Default 0.
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self, pixel_object, speed, color, period=5, max_intensity=1, min_intensity=0
    ):
        if len(pixel_object) < 2:
            raise ValueError("Sparkle needs at least 2 pixels")
        self.max_intensity = max_intensity
        self.min_intensity = min_intensity
        self._period = period
        self._intensity_delta = max_intensity - min_intensity
        self._half_period = period / 2
        self._position_factor = 1 / self._half_period
        self._bpp = len(pixel_object[0])
        self._last_update = monotonic_ns()
        self._cycle_position = 0
        self._half_color = None
        self._dim_color = None
        super().__init__(pixel_object, speed, color)

    def _recompute_color(self, color):
        half_color = tuple(color[rgb] // 4 for rgb in range(len(color)))
        dim_color = tuple(color[rgb] // 10 for rgb in range(len(color)))
        for pixel in range(len(self.pixel_object)):
            if self.pixel_object[pixel] == self._half_color:
                self.pixel_object[pixel] = half_color
            elif self.pixel_object[pixel] == self._dim_color:
                self.pixel_object[pixel] = dim_color
        self._half_color = half_color
        self._dim_color = dim_color

    def draw(self):
        pixel = random.randint(0, (len(self.pixel_object) - 2))

        now = monotonic_ns()
        time_since_last_draw = (now - self._last_update) / NANOS_PER_SECOND
        self._last_update = now
        pos = self._cycle_position = (
            self._cycle_position + time_since_last_draw
        ) % self._period
        if pos > self._half_period:
            pos = self._period - pos
        intensity = self.min_intensity + (
            pos * self._intensity_delta * self._position_factor
        )
        color = [int(self.color[n] * intensity) for n in range(self._bpp)]
        self.pixel_object[pixel] = color
        self.show()
