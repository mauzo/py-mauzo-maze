# This is a level definition file. It is in python syntax, and should
# consist of exactly one dict.
{
    # All the colours we use.
    "colours": {
        "Blue":     (0, 0, 0.5),
        "Green":    (0, 0.5, 0),
        "Red":      (0.5, 0, 0),
        "Grey":     (0.5, 0.5, 0.5),
        "Purple":   (0.8, 0, 1),
        "White":    (1, 1, 1),
        "Yellow":   (0.8, 0.8, 0),
    },

    # The player's starting position
    "start":      (0, 2, 0),
    "start_angle": (0, -10),

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
    "floors": [
        { "pos":        (-2, 2, -1),
          "edges":      ((4, 0, 0), (0, 4, 0)),
          "colour":     "Yellow",
        },
        { "pos":        (13, -5, -6),
          "edges":      ((20, 0, 0), (0, 20, 0)),
          "colour":     "Purple",
        },
        { "pos":        (36, -2, -5),
          "edges":      ((20, 0, 0), (0, 3, 0)),
          "colour":     "White",
        },
        { "pos":        (60, 1, -4),
          "edges":      ((4, 0, 0), (0, 4, 0)),
          "colour":     "Green",
        },
        { "pos":        (50, -2, -2.5),
          "edges":      ((4, 0, 0), (0, 4, 0)),
          "colour":     "Blue",
        },
        { "pos":        (57, -5, -1),
          "edges":      ((4, 0, 0), (0, 4, 0)),
          "colour":     "Red",
        },
        { "pos":        (60, 1, 0.5),
          "edges":      ((4, 0, 0), (0, 4, 0)),
          "colour":     "Green",
        },
        { "pos":        (53, -2, 2),
          "edges":      ((4, 0, 0), (0, 4, 0)),
          "colour":     "Blue",
        },
        { "pos":        (57, -5, 3.5),
          "edges":      ((4, 0, 0), (0, 4, 0)),
          "colour":     "Red",
        },
        { "pos":        (65, -5, 5),
          "edges":      ((10, 0, 0), (0, 10, 0)),
          "colour":     "Yellow",
        },
    ],
    
    # A list of the walls. Walls are parallelograms. The edges must be
    # given in anticlockwise order, looking at the side of the wall you
    # can see.
    "walls": [],
    
    "items": [
        {   "type":     "Portal",
            "pos":      (70, 0, 6),
            "to":       "test",
            "angle":    0
        },
    ],

    # We die if we fall this low.
    "doom_z":   -20,
}
