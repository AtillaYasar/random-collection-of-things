import pygame, time, random
from abc import ABC, abstractmethod

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

class MyRectangle:
    def __init__(self, topleft, bottomright, color):
        self.topleft = topleft
        self.bottomright = bottomright
        self.width = self.bottomright[0] - self.topleft[0]
        self.height = self.bottomright[1] - self.topleft[1]
        self.color = color

    def draw(self):
        pygame.draw.rect(screen, self.color, [*self.topleft, self.width, self.height])

class TimeBar(MyRectangle):
    def __init__(self, topleft, bottomright, timeloop_object):
        super().__init__(topleft, bottomright, WHITE)
        self.topleft = topleft
        self.bottomright = bottomright

        self.timeloop_object = timeloop_object

    def _draw_rect(self):
        pygame.draw.rect(screen, self.color, [*self.topleft, self.width, self.height])

    def _draw_line(self, fraction_x):
        abs_x = self.topleft[0] + fraction_x * (self.bottomright[0]-self.topleft[0])
        pygame.draw.line(screen, BLACK, (abs_x,self.bottomright[1]), (abs_x,self.topleft[1]), 3)

    def draw(self):
        """This is called by the main loop."""

        self._draw_rect()
        self._draw_line(self.timeloop_object.get_fraction())

class ContinuousLoop:
    """
    Example of a continuous loop:
        a clock. There is absolute time, but also a relative time within the 24h cycle.
    """

    def __init__(self, start_value, chunk_size):
        self.start_value = start_value
        self.chunk_size = chunk_size
        print(f'start_value:{start_value}, chunk_size:{chunk_size}')

    # has super_, so i can use get_rel in classes that inherit from this one
    def super_get_rel(self, cur_value):
        abs_value = cur_value - self.start_value
        rel_value = abs_value % self.chunk_size
        return rel_value

    def super_get_fraction(self, cur_value):
        return self.super_get_rel(cur_value) / self.chunk_size

class Timeloop(ContinuousLoop):
    """Can tell you the time relative to the current block of {duration} seconds."""

    def __init__(self, duration, on_reset=None):
        starttime = time.time()
        self.duration = duration
        super().__init__(starttime, duration)
        
        self.last_fraction = 0
        self.on_reset = on_reset

    def get_rel(self):
        return self.super_get_rel(time.time())

    def get_fraction(self):
        f = self.super_get_fraction(time.time())

        # only way current fraction is smaller is if the loop just reset.
        if f > self.last_fraction:
            self.last_fraction = f
        else:
            self.last_fraction = f
            self._on_reset()

        return f

    def _on_reset(self):
        if callable(self.on_reset):
            self.on_reset()
        else:
            pass

class Text:
    def __init__(self, y_coord):
        self.string = ''
        self.set_text(self.string)
        self.y = y_coord

    def set_text(self, new_string):
        self.img = font.render(new_string, True, RED)

    def draw(self):
        screen.blit(self.img, (20, self.y))

class AnimatedObjectABC(ABC):
    """
    Basically, an animation can be derived from a `time-->image` mapping.
    And if you use a function that maps time to *arguments* for drawing something, you can get an animation.
    """

    def __init__(self, timeloop_object):
        self.timeloop_object = timeloop_object

    @abstractmethod
    def fraction_to_args(self):
        pass

    @abstractmethod
    def args_to_drawing(self, args):
        # example:
        #   pygame.draw.rect(screen, self.color, [*self.topleft, self.width, self.height])
        pass

    def draw(self):
        f = self.timeloop_object.get_fraction()
        args = self.fraction_to_args(f)
        self.args_to_drawing(args)

def animation_factory(topleft, dims, color):
    class GrowingRectangle(AnimatedObjectABC):
        def __init__(self, topleft, dims, color):
            super().__init__(timeloop_object)

            self.topleft = topleft
            self.dims = dims
            self.color = color

        def fraction_to_args(self, frac):
            total_width = self.dims[0]
            total_height = self.dims[1]
            return total_width*frac, total_height*frac

        def args_to_drawing(self, args):
            pygame.draw.rect(screen, self.color, [*self.topleft, *args])
    
    obj = GrowingRectangle(
        topleft,
        dims,
        color,
    )
    return obj

def moving_dot_factory(startloc, endloc, starttime, endtime, color):
    class MovingDot(AnimatedObjectABC):
        def __init__(self, startloc, endloc, starttime, endtime, color):

            super().__init__(timeloop_object)  # timeloop_object is a global variable
            
            assert endtime > starttime
            assert starttime <= timeloop_object.duration
            assert endtime <= timeloop_object.duration

            self.startloc = startloc
            self.endloc = endloc
            self.starttime = starttime
            self.endtime = endtime
            self.color = color

            self.active_range = [starttime / timeloop_object.duration, endtime / timeloop_object.duration]
            self.movement_fraction = timeloop_object.duration / (endtime - starttime)
            self.timeloop_duration = timeloop_object.duration

        def fraction_to_args(self, frac):
            """
            pygame.draw.circle(surface, color, center, radius)
            """
            if frac > self.active_range[0] and frac < self.active_range[1]:
                # calculate location
                vector_total = (
                    self.endloc[0]-self.startloc[0],
                    self.endloc[1]-self.startloc[1],
                )
                movement_in_range = frac - self.active_range[0]
                relative_fraction = movement_in_range / self.movement_fraction  # if this is 1, you go the full distance
                vector_current = (
                    vector_total[0] * relative_fraction,
                    vector_total[1] * relative_fraction,
                )
                new_location = (
                    self.startloc[0] + vector_current[0],
                    self.startloc[1] + vector_current[1],
                )

                return (screen, self.color, new_location, 3)
            else:
                return None

        def args_to_drawing(self, args):
            if args == None:
                pass
            else:
                pygame.draw.circle(*args)
    obj = MovingDot(
        startloc,
        endloc,
        starttime,
        endtime,
        color,
    )
    return obj

def new_rect():
    # randomly generate some parameters
    locx = random.randint(0, 100)
    locy = random.randint(0, 100)
    width = random.randint(20, 60)
    height = random.randint(20, 60)

    r,g,b = [random.randint(0,255) for _ in range(3)]

    rect = animation_factory(
        (locx, locy),
        (width,height),
        (r,g,b),
    )
    things_to_draw.append(rect)

loop_length = 2

timeloop_object = Timeloop(loop_length)
time_bar = TimeBar(
    (50,200),
    (500,240),
    timeloop_object,
)

pygame.init()

fontsize = 30
font = pygame.font.SysFont(None, fontsize)
line1 = Text(20)
line2 = Text(50)
line3 = Text(80)

moving_dot = moving_dot_factory(
    (50, 50),
    (300, 200),
    0,
    2,
    RED,
)

# will call .draw on these during the loop
things_to_draw = [
    time_bar,
    moving_dot,
]

# Set the width and height of the screen [width, height]
size = (700, 500)
screen = pygame.display.set_mode(size)

pygame.display.set_caption("music shapes")
 
# Loop until the user clicks the close button.
done = False
 
# Used to manage how fast the screen updates
clock = pygame.time.Clock()



# -------- Main Program Loop -----------
while not done:
    # --- Main event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                new_rect()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pass

    # --- Game logic should go here

    # --- Screen-clearing code goes here

    # If you want a background image, replace this clear with blit'ing the
    # background image.
    screen.fill(BLACK)

    # --- Drawing code should go here
    for drawable in things_to_draw:
        drawable.draw()

    # --- Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

    # --- Limit to 60 frames per second
    clock.tick(60)

# Close the window and quit.
pygame.quit()
