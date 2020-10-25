import pygame
from random import randint
import copy

import json
import paho.mqtt.client as mqtt

#
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

SCREEN_WIDTH = 700
SCREEN_HEIGHT = 500

PLAYER_WIDTH = 50
PLAYER_HEIGHT = 25

BLOCK_HEIGHT = 25

PATH_TIME = 5 # Seconds if movement is uninterrupted (approximate)
FRAME_RATE = 60 # frames per second

# Vertical movement of "player."  Player does not actually move up.  Instead,
# blocks move down toward the player.
SCROLL_SPEED = 3
MOV_SPEED = 3 # Left/right movement of player

BLOCK_CHANCE = 5 # Chance (out of 10) that a block will show up in its tile
TILE_CHANCE = 7 # Chance (out of 10) that a tile will spawn any blocks

players = 2 # Global variable initialization

class Client:
    """
    Prepares the client to connect to Mosquitto server and receive data through
    the MQTT protocol
    """

    def __init__(self, master, game):
        """
        Sets up client and connects to server
        """
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

    """
    def __init__(self, start_pos, x_limits, color):
        super(Player, self).__init__()
        self.image = pygame.Surface([PLAYER_WIDTH, PLAYER_HEIGHT], 5)
        self.image.fill(color)
        self.rect = self.image.get_rect()

        self.rect.x = start_pos[0]
        self.rect.y = start_pos[1]

        self.x_limits = x_limits

        self.x_speed = 0

        self.chosen = 'l'
        self.left_threshold = .7
        self.right_threshold = .7

    def update(self):
        if self.x_speed < 0 and self.rect.x > self.x_limits[0]:
            self.rect.x += self.x_speed
        if self.x_speed > 0 and self.rect.x < (self.x_limits[1] - PLAYER_WIDTH):
            self.rect.x += self.x_speed

    def command(self, probs):
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
        does not move (if both limits are .5, the player will always move, as
        one direction will always have a probability of over 50%).  It is not
        recommended to adjust threshold below .5, as a signal inaccuracy of that
        magnitude likely needs the classifier to be retrained.  Nevertheless,
        the thresholds will not go above 1.0 or below 0.0.

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

class Block(pygame.sprite.Sprite):
    def __init__(self, start_pos):
        super(Block, self).__init__()
        self.image = pygame.Surface([SCREEN_WIDTH / 6 + 1, BLOCK_HEIGHT], 5)
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()

        self.rect.x = start_pos[0]
        self.rect.y = start_pos[1]

        self.isScrolling = True

    def update(self):
        if self.isScrolling:
            self.rect.y += SCROLL_SPEED

class Tile:
    width = SCREEN_WIDTH / 2
    height = SCREEN_HEIGHT / 5
    space = SCREEN_HEIGHT / 10
    block0 = 0
    block1 = width / 3
    block2 = 2 * width / 3

    def __init__(self, game, num, base_tile = None):
        self.blocks = pygame.sprite.Group()
        self.game = game
        if base_tile == None:
            self.start_pos = [0, num * -(Tile.height + Tile.space)]
            self.num_blocks = 0

            self.generate_blocks(Tile.block0)
            self.generate_blocks(Tile.block1)
            self.generate_blocks(Tile.block2)

            self.game.path1_blocks.add(self.blocks)

        else:
            self.start_pos = copy.deepcopy(base_tile.start_pos)
            self.start_pos[0] = self.start_pos[0] + SCREEN_WIDTH / 2

            for block in base_tile.blocks:
                block = Block((block.rect.x + SCREEN_WIDTH / 2, block.rect.y))
                self.blocks.add(block)
                self.game.sprites.add(block)

            self.game.path2_blocks.add(self.blocks)


    def generate_blocks(self, pos):
        if randint(0,9) < TILE_CHANCE:
            if randint(0,9) < BLOCK_CHANCE and self.num_blocks < 2:
                block = Block((self.start_pos[0]+pos, self.start_pos[1]))
                self.blocks.add(block)
                self.game.sprites.add(block)
                self.num_blocks += 1


class Finish_Line(pygame.sprite.Sprite):
    def __init__(self, start_pos):
        super(Finish_Line, self).__init__()
        self.image = pygame.Surface([SCREEN_WIDTH / 2, BLOCK_HEIGHT], 5)
        self.image.fill(RED)
        self.rect = self.image.get_rect()

        self.rect.x = start_pos[0]
        self.rect.y = start_pos[1]

        self.isScrolling = True

    def update(self):
        if self.isScrolling:
            self.rect.y += SCROLL_SPEED

class Game:
    def __init__(self):
        self.isPlaying = True
        self.winner = 0

        self.sprites = pygame.sprite.Group()
        self.player1 = Player((SCREEN_WIDTH * .25 - PLAYER_WIDTH / 2,
            SCREEN_HEIGHT - PLAYER_HEIGHT - 25), (0, SCREEN_WIDTH * .5), BLUE)
        self.player2 = Player((SCREEN_WIDTH * .75 - PLAYER_WIDTH / 2, SCREEN_HEIGHT -
            PLAYER_HEIGHT - 25), (SCREEN_WIDTH * .5 + 1, SCREEN_WIDTH), GREEN)

        self.sprites.add(self.player1)
        self.sprites.add(self.player2)

        self.progress = [100, 100]

        self.path1 = []
        self.path2 = []

        self.path1_blocks = pygame.sprite.Group()
        self.path2_blocks = pygame.sprite.Group()

        self.path1_isScrolling = True
        self.path2_isScrolling = True

        self.generate_path()

        self.path_length = abs(self.finish_line1.rect.y - self.player1.rect.y)
        self.distance = [self.path_length, self.path_length]
        print self.path_length

    def generate_path(self):
        self.num_tiles = (MOV_SPEED * FRAME_RATE * PATH_TIME) / (SCREEN_HEIGHT / 3)

        for i in range(0, self.num_tiles):
            self.path1.append(Tile(self, i))

        for tile in self.path1:
            self.path2.append(Tile(self, 1, tile))

        self.finish_line1 = Finish_Line((0, (self.num_tiles + 1) *
                -(Tile.height + Tile.space)))
        self.path1_blocks.add(self.finish_line1)
        self.sprites.add(self.finish_line1)

        self.finish_line2 = Finish_Line((SCREEN_WIDTH / 2, (self.num_tiles + 1) *
                -(Tile.height + Tile.space)))
        self.path2_blocks.add(self.finish_line2)
        self.sprites.add(self.finish_line2)


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
                if event.key == pygame.K_w:
                    self.player1.adjust_threshold(True)
                elif event.key == pygame.K_s:
                    self.player1.adjust_threshold(False)
                elif event.key == pygame.K_d:
                    self.player1.chosen = 'r'
                elif event.key == pygame.K_a:
                    self.player1.chosen = 'l'

                # Manual controls
                if event.key == pygame.K_z or event.key == pygame.K_y:
                    self.player1.x_speed = -MOV_SPEED
                elif event.key == pygame.K_x:
                    self.player1.x_speed = MOV_SPEED
                if event.key == pygame.K_n:
                    self.player2.x_speed = -MOV_SPEED
                elif event.key == pygame.K_m:
                    self.player2.x_speed = MOV_SPEED

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_z or event.key == pygame.K_y:
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
        if self.isPlaying:
            self.sprites.update()

            self.p1_hit_list = pygame.sprite.spritecollide(self.player1, self.path1_blocks, False)

            if not self.p1_hit_list:
               self.path1_isScrolling = self.path_scroll(self.path1_blocks,
                    self.path1_isScrolling, True)
            else:
                if self.p1_hit_list[0].__class__.__name__ == "Finish_Line":
                    self.end_game(1)
                else:
                    self.correct_for_sides(self.player1, self.path1_blocks)
                    self.path1_isScrolling = self.path_scroll(self.path1_blocks,
                        self.path1_isScrolling, False)

            self.p2_hit_list = pygame.sprite.spritecollide(self.player2, self.path2_blocks, False)

            if not self.p2_hit_list:
                self.path2_isScrolling = self.path_scroll(self.path2_blocks,
                    self.path2_isScrolling, True)
            else:
                if self.p2_hit_list[0].__class__.__name__ == "Finish_Line":
                    self.end_game(2)
                else:
                    self.correct_for_sides(self.player2, self.path2_blocks)
                    self.path2_isScrolling = self.path_scroll(self.path2_blocks,
                        self.path2_isScrolling, False)

            self.distance[0] = abs(self.finish_line1.rect.y -self.player1.rect.y)
            self.progress[0] = 100 - (self.distance[0] * 100) / self.path_length

            self.distance[1] = abs(self.finish_line2.rect.y -self.player2.rect.y)
            self.progress[1] = 100 - (self.distance[1] * 100) / self.path_length


    def path_scroll(self, path, isScrolling, shouldScroll):
        if isScrolling:
            if not shouldScroll:
                for block in path:
                    block.isScrolling = False
                isScrolling = False
        else:
            if shouldScroll:
                for block in path:
                    block.isScrolling = True
                isScrolling = True
        return isScrolling

    def correct_for_sides(self, player, blocks):
        player.rect.x -= MOV_SPEED
        self.temp_hit_list = pygame.sprite.spritecollide(player, blocks, False)
        if self.temp_hit_list:
            player.rect.x += 2 * MOV_SPEED
        self.temp_hit_list = pygame.sprite.spritecollide(player, blocks, False)
        if self.temp_hit_list:
            player.rect.x -= MOV_SPEED

    def end_game(self, winner):
        global players
        self.isPlaying = False
        if self.distance[0] == self.distance[1]:
            self.winner = 0
        else:
            self.winner = winner
        if players == 1:
            self.winner = 1

    def display_frame(self, screen):
        screen.fill(BLACK)

        self.sprites.draw(screen)

        self.draw_thresholds(screen)
        self.draw_progress(screen)


        if not self.isPlaying:
            self.draw_end(screen)

        pygame.draw.line(screen, WHITE, (SCREEN_WIDTH / 2 - 1, 0),
            (SCREEN_WIDTH / 2 - 1, SCREEN_HEIGHT), 2)

        pygame.display.flip()

    def mqtt_command(self, command):
        player = self.player1 if command[0] == 1 else self.player2
        player.command((command[1], command[2]))

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
        screen.blit(text_l, (610, 10))
        screen.blit(text_r, (660, 10))

        text = font_small.render(str(self.player2.left_threshold) + " " +
            str(self.player2.right_threshold), 1, WHITE)
        screen.blit(text, (610, 40))

    def draw_progress(self, screen):
        font_large = pygame.font.Font(None, 48)

        text = font_large.render(str(self.progress[0]), 1, BLUE)
        screen.blit(text, (SCREEN_WIDTH / 2 - 50, 25))

        text = font_large.render(str(self.progress[1]), 1, GREEN)
        screen.blit(text, (SCREEN_WIDTH / 2 + 10, 25))

    def draw_end(self, screen):
        font_large = pygame.font.Font(None, 48)

        if self.winner == 1:
            text = font_large.render("You Won!", 1, BLUE)
            screen.blit(text, (90, 240))
        elif self.winner == 2:
            text = font_large.render("You Won!", 1, GREEN)
            screen.blit(text, (450, 240))
        else:
            text = font_large.render("TIE!", 1, RED)
            screen.blit(text, (130, 240))
            screen.blit(text, (500, 240))


def main():
    global players
    pygame.init()
    players = input("1 or 2 players? ")

    if players == 2:
        size = (SCREEN_WIDTH, SCREEN_HEIGHT)
    else:
        size = (SCREEN_WIDTH / 2, SCREEN_HEIGHT)
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

        clock.tick(FRAME_RATE)

    pygame.quit()
    client.loop_stop()
    client.disconnect()


if __name__ == "__main__":
    main()






