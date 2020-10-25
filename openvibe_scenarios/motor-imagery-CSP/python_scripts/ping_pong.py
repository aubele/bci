import pygame
import random

import json
import paho.mqtt.client as mqtt

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

SCREEN_WIDTH = 700
SCREEN_HEIGHT = 500

BALL_WIDTH = 15
BALL_HEIGHT = 15

MOV_SPEED = 3


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
        Unpacks message with json and passes to Game object.
        """
        self.game.mqtt_command(json.loads(msg.payload))


class Player(pygame.sprite.Sprite):
    """
    The paddle controlled by each player
    """
    def __init__(self, x, y):
        """
        Creates the paddle at the specified positions and sets initial control
        threshold levels to .5
        :param x: Starting x position
        :param y: Starting y position
        """
        super(Player, self).__init__()
        self.image = pygame.Surface([100, 20], 5)
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y

        self.x_speed = 0

        self.chosen = 'l'
        self.left_threshold = .5
        self.right_threshold = .5

    def update(self):
        """
        Updates position of paddle based on current speed.  Paddles will not
        go off-screen.
        """
        if self.rect.x > 0 and self.x_speed < 0:
            self.rect.x += self.x_speed
        elif self.rect.x < (SCREEN_WIDTH - 100) and self.x_speed > 0:
            self.rect.x += self.x_speed

    def mqtt_command(self, probs):
        """
        Sets player speed based on whether values from openVibe are above the
        set limits.
        """
        if float(probs[0]) > self.left_threshold:
            self.x_speed = -MOV_SPEED
        elif float(probs[1]) > self.right_threshold:
            self.x_speed = MOV_SPEED

        else:
            self.x_speed = 0

    def adjust_threshold(self, is_up):
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
                self.left_threshold += .10
                if self.left_threshold > .9:
                    self.left_threshold = 1.0
            else:
                self.left_threshold += -.10
                if self.left_threshold < .1:
                    self.left_threshold = 0.0
        elif self.chosen == 'r':
            if is_up:
                self.right_threshold += .10
                if self.right_threshold > .9:
                    self.right_threshold = 1.0
            else:
                self.right_threshold += -.10
                if self.right_threshold < .1:
                    self.right_threshold = 0.0


class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super(Ball, self).__init__()
        self.image = pygame.Surface([BALL_WIDTH, BALL_HEIGHT], 5)
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()

        self.rect.x = SCREEN_WIDTH / 2
        self.rect.y = SCREEN_HEIGHT / 2

        self.speed = [random.randint(-2, 2), random.randint(-2, 2)]
        while self.speed[0] == 0:
            self.speed[0] = random.randint(-2, 2)
        while self.speed[1] == 0:
            self.speed[1] = random.randint(-2, 2)

    def update(self):
        self.rect.x += self.speed[0]
        self.rect.y += self.speed[1]

    def bounce(self, dim):
        self.speed[dim] *= -1
        while self.speed[dim] == 0:
            self.speed[dim] = random.randint(-2, 2)

        if self.speed[dim] > 0:
            self.speed[dim] += 1
        elif self.speed[dim] < 0:
            self.speed[dim] -= 1


class Game:
    def __init__(self):
        self.sprites = pygame.sprite.Group()
        self.player1 = Player(300, 20)
        self.player2 = Player(300, 460)
        self.ball = Ball()

        self.score = [0, 0]

        self.sprites.add(self.player1)
        self.sprites.add(self.player2)
        self.sprites.add(self.ball)

        self.players = [self.player1, self.player2]

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            elif event.type == pygame.KEYDOWN:
                # Reset game
                if event.key == pygame.K_BACKSPACE:
                    self.__init__()

                # Adjusting player1 thresholds
                if event.key == pygame.K_UP:
                    self.player2.adjust_threshold(True)
                elif event.key == pygame.K_DOWN:
                    self.player2.adjust_threshold(False)
                elif event.key == pygame.K_RIGHT:
                    self.player2.chosen = 'r'
                elif event.key == pygame.K_LEFT:
                    self.player2.chosen = 'l'
                # Adjusting player2 thresholds
                elif event.key == pygame.K_w:
                    self.player1.adjust_threshold(True)
                elif event.key == pygame.K_s:
                    self.player1.adjust_threshold(False)
                elif event.key == pygame.K_d:
                    self.player1.chosen = 'r'
                elif event.key == pygame.K_a:
                    self.player1.chosen = 'l'

                # Manual controls
                if event.key == pygame.K_z:
                    self.player1.x_speed = -MOV_SPEED
                elif event.key == pygame.K_x:
                    self.player1.x_speed = MOV_SPEED
                if event.key == pygame.K_n:
                    self.player2.x_speed = -MOV_SPEED
                elif event.key == pygame.K_m:
                    self.player2.x_speed = MOV_SPEED

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_z:
                    self.player1.x_speed = 0
                elif event.key == pygame.K_x:
                    self.player1.x_speed = 0
                if event.key == pygame.K_n:
                    self.player2.x_speed = 0
                elif event.key == pygame.K_m:
                    self.player2.x_speed = 0

        return False

    def run_logic(self):
        """
        This method is run each time through the frame.
        It updates positions and checks for collisions.
        """
        self.sprites.update()

        # Check for collision with players
        if pygame.sprite.spritecollide(self.ball, self.players, False):
            self.ball.bounce(1)

        # Check for collision with side walls
        if self.ball.rect.x <= 0 or self.ball.rect.x >= SCREEN_WIDTH - BALL_WIDTH:
            self.ball.bounce(0)

        # Check for scoring
        if self.ball.rect.y < 0 - BALL_HEIGHT:
            self.player_score(1)
        elif self.ball.rect.y > SCREEN_HEIGHT:
            self.player_score(0)

    def player_score(self, player):
        self.score[player] += 1
        self.ball.kill()
        self.ball = Ball()
        self.sprites.add(self.ball)

    def display_frame(self, screen):
        screen.fill(BLACK)

        self.sprites.draw(screen)

        self.draw_score(screen)
        self.draw_thresholds(screen)

        pygame.draw.line(screen, WHITE, (0, SCREEN_HEIGHT / 2), (SCREEN_WIDTH,
            SCREEN_HEIGHT / 2))

        pygame.display.flip()

    def mqtt_command(self, command):
        player = self.player1 if command[0] == 1 else self.player2
        player.mqtt_command((command[1], command[2]))

    def draw_score(self, screen):
        font = pygame.font.Font(None, 48)

        text = font.render(str(self.score[0]), 1, WHITE)
        screen.blit(text, (15, 200))

        text = font.render(str(self.score[1]), 1, WHITE)
        screen.blit(text, (665, 260))

    def draw_thresholds(self, screen):
        font_small = pygame.font.Font(None, 36)
        font_large = pygame.font.Font(None, 48)

        if self.player1.chosen == 'l':
            text_l = font_large.render("L", 1, WHITE)
            text_r = font_small.render("R", 1, WHITE)
        else:
            text_l = font_small.render("L", 1, WHITE)
            text_r = font_large.render("R", 1, WHITE)
        screen.blit(text_l, (15, 10))
        screen.blit(text_r, (65, 10))

        text = font_small.render(str(self.player1.left_threshold) + " " +
            str(self.player1.right_threshold), 1, WHITE)
        screen.blit(text, (15, 40))

        if self.player2.chosen == 'l':
            text_l = font_large.render("L", 1, WHITE)
            text_r = font_small.render("R", 1, WHITE)
        else:
            text_l = font_small.render("L", 1, WHITE)
            text_r = font_large.render("R", 1, WHITE)
        screen.blit(text_l, (610, 430))
        screen.blit(text_r, (660, 430))

        text = font_small.render(str(self.player2.left_threshold) + " " +
            str(self.player2.right_threshold), 1, WHITE)
        screen.blit(text, (610, 460))


def main():
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
