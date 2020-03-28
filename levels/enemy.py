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
    "start":      (0, 0, 0),
    "start_angle": (0, -10),

    # The name of the next level
    "next_level":   "he real maze",

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
        { "pos":        (-2, -2, -1),
          "edges":      ((4, 0, 0), (0, 4, 0)),
          "colour":     "Red",
          "win":        False,
        },
        { "pos":        (13, -10, -7),
          "edges":      ((7, 0, 0), (0, 7, 0)),
          "colour":     "Blue",
          "win":        False,
        },
        { "pos":        (29, -2, -3),
          "edges":      ((4, 0, 0), (0, 4, 0)),
          "colour":     "White",
          "win":        True,
        },
        { "pos":        (22, -2, -5),
          "edges":      ((4, 0, 0), (0, 4, 0)),
          "colour":     "Yellow",
          "win":        False,
        },
        { "pos":        (14, 3, -5),
          "edges":      ((4, 0, 0), (0, 4, 0)),
          "colour":     "Yellow",
          "win":        False,
        }, 
    ],
    
    # A list of the walls. Walls are parallelograms. The edges must be
    # given in anticlockwise order, looking at the side of the wall you
    # can see.
    "walls": [],
    
    "collide": [],
    "keys":[
        {   "pos":      (16, 5, -4.8),
                    "colour":   "Green",
        },
    ],

    # We die if we fall this low.
    "doom_z":   -20,
}
