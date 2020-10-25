import pygame
import json
import paho.mqtt.client as mqtt

# define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

CHOSEN_FONT = 36
NOT_CHOSEN_FONT = 28

SCREEN_WIDTH = 700
SCREEN_HEIGHT = 500


# Client to receive mqtt data
class Client:
    """
    Prepares the client to connect to Mosquitto server and receive data through
    the MQTT protocol
    """

    def __init__(self, master, game):
        self.game = game

        self.master = master
        self.master.on_connect = self.on_connect
        self.master.on_message = self.on_message
        # "localhost" is for an MQTT server on the same computer.  Change if
        # server exists on external device.
        self.master.connect("localhost", 1883, 60)


    def on_connect(self, master, userdata, flags, rc):
        """
        Confirms connection to server and subscribes to topic
        """
        print("Connected with result code " + str(rc))

        # Topic must match publisher script from OpenVibe.
        self.master.subscribe("topic/bci")

    def on_message(self, master, userdata, msg):
        """
        Unpackages message and sends to Game object for processing
        """
        self.game.mqtt_command(json.loads(msg.payload))


class Player(pygame.sprite.Sprite):
    """
    Red box on that is moved left and right by the bci data
    """

    def __init__(self):
        """
        Creates player as  a red box on screen
        """
        super(Player, self).__init__()
        self.image = pygame.Surface([100, 100], 5)
        self.image.fill(RED)
        self.rect = self.image.get_rect()

        self.rect.x = 300
        self.rect.y = 200

        self.x_speed = 0
        self.y_speed = 0

    def update(self):
        """
        Updates the position of the player based on current speed.
        """
        if self.rect.x > 0 and self.x_speed < 0:
            self.rect.x += self.x_speed
        elif self.rect.x < (SCREEN_WIDTH - 100) and self.x_speed > 0:
            self.rect.x += self.x_speed
        self.rect.y += self.y_speed

class Game:
    def __init__(self):
        """
        Creates objects for game
        """
        self.sprites = pygame.sprite.Group()
        self.player = Player()
        self.sprites.add(self.player)

        self.chosen = 'l'
        self.left_limit = .5
        self.right_limit = .5

    def process_events(self):
        """
        Process all pygame events (key presses and closing the window)
        :return: If the window is being closed
        """

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.adjust_limit(True)
                elif event.key == pygame.K_DOWN:
                    self.adjust_limit(False)
                elif event.key == pygame.K_RIGHT:
                    self.chosen = 'r'
                elif event.key == pygame.K_LEFT:
                    self.chosen = 'l'

        return False

    def run_logic(self):
        """
        Updates positions of sprites and would check for collisions if needed
        """
        self.sprites.update()

    def display_frame(self, screen):
        """
        Draws screen and updates display
        """
        screen.fill(BLACK)

        self.sprites.draw(screen)

        font = pygame.font.Font(None, 36)
        text = font.render(str(self.left_limit) + " " + str(self.right_limit), 1, WHITE)
        screen.blit(text, (25, 60))

        pygame.display.flip()

    def mqtt_command(self, probs):
        """
        Sets player speed based on whether values from openVibe are above the
        set limits.
        """
        if float(probs[0]) > self.left_limit:
            self.move_player(-1)
        elif float(probs[1]) > self.right_limit:
            self.move_player(1)

        else:
            self.move_player(0)

    def move_player(self, speed):
        """
        Changes speed of player
        """
        self.player.x = speed

    def adjust_limit(self, is_up):
        """
        Dynamically changes required probability of a direction to adjust for
        uneven signals.  The higher the limit, the stronger the signal needed to
        move in that direction.  If neither signal-limit is reached, the player
        does not move (if both limits are .5, the box will always move, as one
        direction will always have a probability of over 50%).  It is not
        recommended to go below .5, as a signal inaccuracy of that magnitude
        likely needs the classifier to be retrained.  Nevertheless, the limts
        will not go above 1.0 or below 0.0.
        :param is_up: Whether or not the limit is moving up (if not up,
                      it must be down).
        """
        if self.chosen == 'l':
            if is_up:
                self.left_limit += .10
                if self.left_limit > .9:
                    self.left_limit = 1.0
            else:
                self.left_limit += -.10
                if self.left_limit < .1:
                    self.left_limit = 0.0
        elif self.chosen == 'r':
            if is_up:
                self.right_limit += .10
                if self.right_limit > .9:
                    self.right_limit = 1.0
            else:
                self.right_limit += -.10
                if self.right_limit < .1:
                    self.right_limit = 0.0


def main():
    """
    Runs game and connects to Mosquitto server
    """
    pygame.init()
    # Create screen
    size = (SCREEN_WIDTH, SCREEN_HEIGHT)
    screen = pygame.display.set_mode(size)

    game = Game()

    client = mqtt.Client("", True, None, mqtt.MQTTv31)
    obj = Client(client, game)
    client.connect("localhost", 1883, 60)

    pygame.display.set_caption("Gaming Display")

    clock = pygame.time.Clock()
    # Loop until user clicks close
    done = False

    client.loop_start()

    while not done:
        done = game.process_events()

        game.run_logic()

        game.display_frame(screen)

        clock.tick(60)

    pygame.quit()
    client.loop_stop()
    client.disconnect()


if __name__ == "__main__":
    main()
