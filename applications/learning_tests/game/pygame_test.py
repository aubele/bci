import pygame
import paho.mqtt.client as mqtt

# define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)


def on_connect(client, userdata, flags, rc):
    print("Connected with result code" + str(rc))
    client.subscribe("topic/pygame")


def on_message(client, userdata, msg):
    global x_coord
    global y_coord
    global x_speed
    global y_speed
    global done

    if msg.payload == "quit":
        done = True
    elif msg.payload == "mv_up":
        y_speed += -3
    elif msg.payload == "mv_down":
        y_speed += 3
    elif msg.payload == "mv_left":
        x_speed += -3
    elif msg.payload == "mv_right":
        x_speed += 3
    elif msg.payload == "stp_horiz":
        x_speed = 0
    elif msg.payload == "stp_vert":
        y_speed = 0


def draw_square(screen, x, y):
    pygame.draw.rect(screen, RED, [x, y, 100, 100], 5)


client = mqtt.Client("", True, None, mqtt.MQTTv31)
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)

pygame.init()

clock = pygame.time.Clock()

# Create screen
size = (700, 500)
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Gaming Display")

# Loop until user clicks close
done = False

# Speed in pixels per frame
x_speed = 0
y_speed = 0

# Current position
x_coord = 30
y_coord = 30

client.loop_start()

while not done:
    global done

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
            # elif event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_LEFT:
            #         x_speed = -3
            #     elif event.key == pygame.K_RIGHT:
            #         x_speed = 3
            #     elif event.key == pygame.K_UP:
            #         y_speed = -3
            #     elif event.key == pygame.K_DOWN:
            #         y_speed = 3
            # elif event.type == pygame.KEYUP:
            #     if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
            #         x_speed = 0
            #     elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
            #         y_speed = 0

    x_coord += x_speed
    y_coord += y_speed

    screen.fill(WHITE)

    draw_square(screen, x_coord, y_coord)

    # Updates screen
    pygame.display.flip()

    # 60 fps
    clock.tick(60)

client.loop_stop()
client.disconnect()
pygame.quit()
