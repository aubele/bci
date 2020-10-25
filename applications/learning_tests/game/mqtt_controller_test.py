import pygame
import paho.mqtt.client as mqtt

# This is the publisher
client = mqtt.Client("", True, None, mqtt.MQTTv31)
client.connect("localhost", 1883, 60)

pygame.init()

clock = pygame.time.Clock()

screen = pygame.display.set_mode((100, 100))

pygame.display.set_caption("Gaming Control")

done = False

while not done:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            client.publish("topic/pygame", "quit")
            done = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                client.publish("topic/pygame", "mv_right")
            elif event.key == pygame.K_LEFT:
                client.publish("topic/pygame", "mv_left")
            elif event.key == pygame.K_UP:
                client.publish("topic/pygame", "mv_up")
            elif event.key == pygame.K_DOWN:
                client.publish("topic/pygame", "mv_down")
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                client.publish("topic/pygame", "stp_horiz")
            elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                client.publish("topic/pygame", "stp_vert")

    clock.tick(60)

client.disconnect();
pygame.quit()
