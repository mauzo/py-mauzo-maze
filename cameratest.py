from math           import radians, sin, cos, fmod
import pygame
from pygame.locals  import *
from pygame.event   import Event
from OpenGL.GL      import *
from OpenGL.GLU     import *

Display = {
    "winsize":  (600, 600),
    "fps":      80,
}

Camera = {
    "angle":    [0, 0],
    "pos":      [0, 0, 0],
}

# Draw a coloured cube around the origin. Not used; for checking on
# camera positioning.
def draw_cube_10():
    glBegin(GL_QUADS)
    glColor3f(1, 0, 0)
    glVertex3f(10, -10, -10)
    glVertex3f(10, 10, -10)
    glVertex3f(10, 10, 10)
    glVertex3f(10, -10, 10)

    glColor3f(0.5, 0, 0)
    glVertex3f(-10, -10, -10)
    glVertex3f(-10, 10, -10)
    glVertex3f(-10, 10, 10)
    glVertex3f(-10, -10, 10)

    glColor3f(0, 1, 0)
    glVertex3f(-10, 10, -10)
    glVertex3f(10, 10, -10)
    glVertex3f(10, 10, 10)
    glVertex3f(-10, 10, 10)

    glColor3f(0, 0.5, 0)
    glVertex3f(-10, -10, -10)
    glVertex3f(10, -10, -10)
    glVertex3f(10, -10, 10)
    glVertex3f(-10, -10, 10)
    
    glColor3f(0, 0, 1)
    glVertex3f(-10, -10, 10)
    glVertex3f(10, -10, 10)
    glVertex3f(10, 10, 10)
    glVertex3f(-10, 10, 10)

    glColor3f(0, 0, 0.5)
    glVertex3f(-10, -10, -10)
    glVertex3f(10, -10, -10)
    glVertex3f(10, 10, -10)
    glVertex3f(-10, 10, -10)
    glEnd()

# Draw a marker at the origin so we can see where it is.
def draw_origin_marker():
    glColor3f(1, 1, 1)

    glBegin(GL_POINTS)
    glVertex3f(0, 0, 0)
    glEnd()

    glBegin(GL_LINES)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, 1)
    glEnd()

# Start up pygame and open the window.
def init_display():
    pygame.init()
    pygame.display.set_mode(Display["winsize"], OPENGL|DOUBLEBUF)

# Set up the initial OpenGL state, including the projection matrix.
def init_opengl():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LINE_SMOOTH)
    glEnable(GL_POINT_SMOOTH)

    glPointSize(5)

    winsize = Display["winsize"]
    aspect  = winsize[0]/winsize[1]

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(100.0, aspect, 0.1, 100.0)

    glMatrixMode(GL_MODELVIEW)

# Clear the screen to remove the previous frame.
def render_clear():
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

# Position the camera based on the player's current position. We put
# the camera 1 unit above the player's position.
def render_camera():
    pos     = Camera["pos"]
    angle   = Camera["angle"]
    
    # Clear the previous camera position
    glLoadIdentity()
    # Annoyingly, the camera starts pointing down (-Z).
    # Rotate so we are pointing down +X with +Y upwards.
    glRotatef(90, 0, 0, 1)
    glRotatef(90, 0, 1, 0)

    # Set the new camera position for this frame. Everything has to be
    # done backwards because we are moving the world rather than moving
    # the camera. This is why we rotate before we translate rather than
    # the other way round.
    
    # Vertical rotation. We are pointing down +X so we would expect a
    # CCW rotation about -Y to make +ve angles turn upwards, but as
    # everthing is backwards we need to turn the other way.
    glRotatef(angle[1], 0, 1, 0)
    # Horizontal rotation. Again we rotate about -Z rather than +Z.
    glRotatef(angle[0], 0, 0, -1)
    # Move to the camera position. These need to be negative because we
    # are moving the world rather than moving the camera.
    glTranslatef(-pos[0], -pos[1], -pos[2])

def render ():
    render_clear()
    render_camera()
    draw_cube_10()

# Handle a key-up or key-down event. k is the keycode, down is True or False.
def handle_key(k, down):
    if k == K_q:
        pygame.event.post(Event(QUIT))
    elif k == K_j:
        Camera["angle"][0] += 5
    elif k == K_l:
        Camera["angle"][0] -= 5
    elif k == K_k:
        Camera["angle"][1] -= 5
    elif k == K_i:
        Camera["angle"][1] += 5
    elif k == K_a:
        Camera["pos"][0] -= 1
    elif k == K_d:
        Camera["pos"][0] += 1
    elif k == K_s:
        Camera["pos"][1] -= 1
    elif k == K_w:
        Camera["pos"][1] += 1
    elif k == K_f:
        Camera["pos"][2] -= 1
    elif k == K_r:
        Camera["pos"][2] += 1
    print("New camera pos", Camera)
    

# This is the main loop that runs the whole game. We wait for events
# and handle them as we need to.
def mainloop():
    # Set up a clock to keep track of the framerate.
    clock   = pygame.time.Clock()    
    fps     = Display["fps"]
    
    while True:
        # Check for events and deal with them.
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                print("FPS: ", clock.get_fps())
                return

            elif event.type == KEYDOWN:
                handle_key(event.key, True)

        # Draw the frame. We draw on the 'back of the page' and then
        # flip the page over so we don't see a half-drawn picture.        
        render()
        pygame.display.flip()

        # Wait if necessary so that we don't draw more frames per second
        # than we want. Any more is just wasting processor time.
        clock.tick(fps)

# Main

def main():
    # Open the window and setup pygame
    init_display()

    # This try: block catches errors and makes sure the finally: block
    # runs even if there's an error. Otherwise the window doesn't go away.
    try:
        # Run the other initialisation
        init_opengl()

        # Go into the main loop, which doesn't return until we quit the game.
        mainloop()
    finally:
        # Make sure the window is closed when we finish.
        pygame.display.quit()

main()

