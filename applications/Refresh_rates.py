import pygame

BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400

FPS = 60


class Box(pygame.sprite.Sprite):
    """
    Box that blinks at the specified herz
    """

    def __init__(self, x, y, time):
        """

        """
        super(Box, self).__init__()
        self.image = pygame.Surface([100, 100], 5)
        self.image.fill(GREEN)
        self.shown = True
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y

        self.time = time
        self.count = 0

    def update(self):
        self.count += 1
        if self.count >= self.time:
            self.switch()
            self.count = 0

    def switch(self):
        if self.shown:
            self.image.fill(BLACK)
        else:
            self.image.fill(GREEN)

        self.shown = not self.shown

    def draw_frequency(self, screen):
        font = pygame.font.Font(None, 36)

        text = font.render(str(FPS / self.time), 1, WHITE)
        screen.blit(text, (self.rect.x+45, self.rect.y + 105))

pygame.init()
# Create screen
size = (SCREEN_WIDTH, SCREEN_HEIGHT)
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Gaming Display")

clock = pygame.time.Clock()
# Loop until user clicks close
done = False

count1 = 0
count2 = 0

box1 = Box(0, 0, 7)
box2 = Box(250, 0, 6)
box3 = Box(500, 0, 5)
box4 = Box(0, 250, 4)
box5 = Box(250, 250, 3)
box6 = Box(500, 250, 2)
# box7 = Box(202, 101, 17)
# box8 = Box(303, 101, 18)

sprites = pygame.sprite.Group()
sprites.add(box1)
sprites.add(box2)
sprites.add(box3)
sprites.add(box4)
sprites.add(box5)
sprites.add(box6)
# sprites.add(box7)
# sprites.add(box8)

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    sprites.update()

    screen.fill(BLACK)

    sprites.draw(screen)

    for box in sprites:
        box.draw_frequency(screen)

    pygame.display.flip()

    clock.tick(FPS)

pygame.quit()
