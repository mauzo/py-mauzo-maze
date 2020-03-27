# This is a level definition file. It is in python syntax, and should
# consist of exactly one dict.
{
    # All the colours we use.
    "colours": {
        "Blue":     (0, 0, 0.5),
        "Green":    (0, 0.5, 0),
        "Red":      (0.5, 0, 0),
        "Grey":     (0.5, 0.5, 0.5),
        "Pink":     (0.8, 0, 1),
        "White":    (1, 1, 1),
        "Yellow":   (0.8, 0.8, 0),
    },

    # The player's starting position
    "start":      (-2, -2, -0.49),
    "start_angle": (70, -10),

    # The lights.
    "lights":   [
        {   "type":         "directional",
            "direction":    (0.3, -1.2, 0.4),
            "ambient":      (0.3, 0.3, 0.3),
            "diffuse":      (0.7, 0.7, 0.7),
            "specular":     (0.7, 0.7, 0.7),
        },
    ],

    # A list of all the floors. Floors are horizontal rectangles. Each
    # floor has a dict with these keys:
    #   pos         The coordinates of one corner
    #   edges       The vectors along the two edges, X first, then Y.
    #   colour      A tuple of (red, green, blue)
    #   win         True if this is a winning platform, False otherwise
    "floors": [
        { "pos":        (-10, -10, -1),
          "edges":      ((20, 0, 0), (0, 20, 0)),
          "colour":     "Red",
          "win":        False,
        },
        { "pos":        (-10, 10, -1),
          "edges":      ((10, 0, 0), (0, 5, 0)),
          "colour":     "Green",
          "win":        False,
        },
        { "pos":        (0, 10, -1),
          "edges":      ((10, 0, 0), (0, 5, 0)),
          "colour":     "Blue",
          "win":        False,
        },
        { "pos":        (-7, 0, 1),
          "edges":      ((3, 0, 0), (0, 5, 0)),
          "colour":     "Green",
          "win":        False,
        },
        { "pos":        (0, 0, 2),
          "edges":      ((5, 0, 0), (0, 5, 0)),
          "colour":     "Yellow",
          "win":        False,
        },
        { "pos":        (0, 6, 4),
          "edges":      ((5, 0, 0), (0, 5, 0)),
          "colour":     "Pink",
          "win":        False,
        },
        { "pos":        (6, 6, 6),
          "edges":      ((6, 0, 0), (0, 5, 0)),
          "colour":     "White",
          "win":        True,
        },
        { "pos":        (-10, 10, 3),
          "edges":      ((15, 0, 0), (0, 5, 0)),
          "colour":     "Grey",
          "win":        False,
        },
        { "pos":        (-13, -13, -5),
          "edges":      ((10, 0, 0), (0, 15, 0)),
          "colour":     "Pink",
          "win":        False,
        },
        { "pos":        (1, -13, -3),
          "edges":      ((8, 0, 0), (0, 2, 0)),
          "colour":     "Blue",
          "win":        False,
        },
        { "pos":        (8, -14, -3),
          "edges":      ((1, 0, 0), (0, 1, 0)),
          "colour":     "Blue",
          "win":        False,
        }
    ],

    # A list of the walls. Walls are parallelograms. The edges must be
    # given in anticlockwise order, looking at the side of the wall you
    # can see.
    "walls": [
        {   "pos":      (-9, -10, -1),
            "edges":    ((0, 0, 2), (17, 0, 0), (0, -0.5, 0)),
            "colour":   "Blue",
        },
        {   "pos":      (9, -10, -1),
            "edges":    ((0, 0, 5), (1, 0, 0), (0, -0.5, 0)),
            "colour":   "Blue",
        },
        {   "pos":      (-10, -10, -1),
            "edges":    ((0, 20, 0), (0, 0, 5), (-0.5, 0, 0)),
            "colour":   "Blue",
        },
        {   "pos":      (10, -10, -1),
            "edges":    ((0, 0, 5), (0, 20, 0), (0.5, 0, 0)),
            "colour":   "Blue",
        },
        {   "pos":      (-10, 10, -1),
            "edges":    ((0, 5, 0), (0, 0, 5), (-0.5, 0, 0)),
            "colour":   "Red",
        },
        {   "pos":      (-10, 15, -1),
            "edges":    ((10, 0, 0), (0, 0, 5), (0, 0.5, 0)),
            "colour":   "Red",
        },
        {   "pos":      (10, 10, -1),
            "edges":    ((0, 0, 5), (0, 5, 0), (0.5, 0, 0)),
            "colour":   "Green",
        },
        {   "pos":      (0, 15, -1),
            "edges":    ((10, 0, 0), (0, 0, 5), (0, 0.5, 0)),
            "colour":   "Green",
        },
    ],

    "keys": [
        {   "pos":      (-5, -5, -4.8),
            "colour":   "Green",
        },
    ],

    "collide": [
        {   "pos":      (0, 0, 0),
            "edges":    ((2, 0, 0), (0, 2, 0), (0, 0, -2)),
        },
    ],

    # We die if we fall this low.
    "doom_z":   -20,
}
