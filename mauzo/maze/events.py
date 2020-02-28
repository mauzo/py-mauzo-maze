# events.py - Run the event loop

import  pygame
from    pygame.event        import Event
from    pygame.locals       import *

# Tell pygame we want to quit.
def event_post_quit ():
    pygame.event.post(Event(QUIT))

