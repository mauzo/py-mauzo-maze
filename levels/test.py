# This is a level definition file. It is in python syntax, and should
# consist of exactly one dict.
{
    # All the colours we use.
    "colours": {
        "Blue":     (0, 0, 0.5),
        "Green":    (0, 0.5, 0),
        "Red":      (0.5, 0, 0),
        "Grey":     (0.5, 0.5, 0.5),
        "Purple":     (0.8, 0, 1),
        "White":    (1, 1, 1),
        "Yellow":   (0.8, 0.8, 0),
    },

    # The player's starting position
    "start":        (0, 0, 0),
    "start_angle":  (0, -10),

    # The lights.
    "lights":   [
        {   "type":         "directional",
            "direction":    (0.3, 1.2, 0.4),
            "ambient":      (0.5, 0.5, 0.5),
            "diffuse":      (0.9, 0.9, 0.9),
            "specular":     (1.0, 1.0, 1.0),
        },
    ],

    # A list of all the floors. Floors are horizontal rectangles. Each
    # floor has a dict with these keys:
    #   pos         The coordinates of one corner
    #   edges       The vectors along the two edges, X first, then Y.
    #   colour      A tuple of (red, green, blue)
    "floors": [
    ],

    # A list of the walls. Walls are parallelograms. The edges must be
    # given in anticlockwise order, looking at the side of the wall you
    # can see.
    "walls": [
         
        { "pos":        (-30, -30, -0.5),
          "edges":      ((60, 0, 0), (0, 60, 0), (0, 0, -0.5)),
          "colour":     "Red",
        },
    ],

    #"plan": "flashlight_drawing",

    "items": [
        {   "type":     "Portal",
            "pos":      (15, 0, 0),
            "angle":    0,
            "to":       "test",
        },
        {   "type":     "Spike",
            "pos":      (4, 0, -0.5),
            "angle":    0,
            "size":     1,
        },
    ],

    # We die if we fall this low.
    "doom_z":   -20,
}
