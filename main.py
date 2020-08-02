import pygame
import configparser
import random

pygame.init()
configParser = configparser.RawConfigParser()
configParser.read("config.cfg")
clock = pygame.time.Clock()

# font styles
font_style = configParser.get("global constants", "font")
font_big = pygame.font.Font(font_style, 50)
font_small = pygame.font.Font(font_style, 26)

# colors
black_color = tuple(map(int, configParser.get("global constants", "black_color").split(",")))
white_color = tuple(map(int, configParser.get("global constants", "white_color").split(",")))

# global constants
x_max = configParser.getint("global constants", "x_max")
y_max = configParser.getint("global constants", "y_max")
max_time = configParser.getint("global constants", "max_level_time")

speed_of_player = configParser.getint("global constants", "speed_of_player")
max_speed_of_obstacle = 0
min_speed_of_obstacle = 0
number_of_fixed_obstacles = 0
number_of_left_moving_obstacles = 0
start_time = end_time = 0

# add background sounds
background_sound = pygame.mixer.music.load(configParser.get("sound files", "background_sound_file"))
level_up_sound = pygame.mixer.Sound(configParser.get("sound files", "level_up_sound_file"))
coin_sound = pygame.mixer.Sound(configParser.get("sound files", "coin_sound_file"))
death_sound = pygame.mixer.Sound(configParser.get("sound files", "death_sound_file"))
end_of_round_sound = pygame.mixer.Sound(configParser.get("sound files", "end_of_round_sound_file"))
quit_sound = pygame.mixer.Sound(configParser.get("sound files", "quit_sound_file"))

# create screen
screen = pygame.display.set_mode((x_max, y_max))
pygame.display.set_caption(configParser.get("global constants", "screen_caption"))
icon = pygame.image.load(configParser.get("images", "screen_icon"))
pygame.display.set_icon(icon)

river_background = pygame.image.load(configParser.get("images", "river_background_image")).convert()
river_background = pygame.transform.scale(river_background, (x_max, y_max))
land_background = pygame.image.load(configParser.get("images", "land_background_image")).convert()
land_background = pygame.transform.scale(land_background, (x_max, 60))
land_surface = pygame.Surface((x_max, 60))
land_surface.blit(land_background, (0, 0))

# coordinates required for calculating score
list_of_land_y_coordinates = list(map(int, configParser.get("lists", "list_of_land_y_coordinates").split(",")))
list_of_river_y_coordinates = list(map(int, configParser.get("lists", "list_of_river_y_coordinates").split(",")))
list_of_y_coordinates = list_of_land_y_coordinates + list_of_river_y_coordinates
list_of_y_coordinates.sort()

# global lists to calculate final winners
final_levels = list(map(int, configParser.get("lists", "zeroes_list").split(",")))
final_scores = list(map(int, configParser.get("lists", "zeroes_list").split(",")))
final_times = list(map(int, configParser.get("lists", "zeroes_list").split(",")))
final_coin_bonuses = list(map(int, configParser.get("lists", "zeroes_list").split(",")))
round_winners = list(map(int, configParser.get("lists", "zeroes_list").split(",")))

# stores the number of obstacles currently in each river or land strip
number_of_river_obstacles = {}
number_of_land_obstacles = {}
check_if_calculated = {}

# create sprite groups
players = []
all_obstacles = pygame.sprite.Group()
moving_obstacles = pygame.sprite.Group()
fixed_obstacles = pygame.sprite.Group()
coins = pygame.sprite.Group()


def drawInitialScreen():
    screen.blit(river_background, (0, 0))
    welcome_text = font_big.render("RIVER JUMP", True, black_color)
    welcome_text_rect = welcome_text.get_rect(center=(x_max / 2, y_max / 2))
    screen.blit(welcome_text, welcome_text_rect)

    info_text = font_small.render("Made using Pygame by Ashwin Rao", True, black_color)
    info_text_rect = info_text.get_rect(center=(x_max / 2, y_max / 2 + 50))
    screen.blit(info_text, info_text_rect)

    enter_text = font_small.render("Press Enter to start!", True, black_color)
    enter_text_rect = enter_text.get_rect(center=(x_max / 2, y_max / 2 + 100))
    screen.blit(enter_text, enter_text_rect)


def drawEndScreen(stop):
    screen.blit(river_background, (0, 0))
    game_over_text = font_big.render("END OF ROUND!", True, black_color)
    game_over_text_rect = game_over_text.get_rect(center=(x_max / 2, y_max / 2 - 200))
    screen.blit(game_over_text, game_over_text_rect)

    player_info = font_small.render(
        "Player: 1" + "    " + "Level: " + str(final_levels[0]) + "    " + "Score: " + str(
            final_scores[0]) + "    " + "Time Bonus: " + str(final_times[0]) + "    " + "Coins: " + str(
            final_coin_bonuses[0]) + "    " "Final Score: " + str(
            final_scores[0] + final_coin_bonuses[0] + final_times[0]), True,
        black_color)
    player_info_rect = player_info.get_rect(center=(x_max / 2, y_max / 2 - 100))
    screen.blit(player_info, player_info_rect)
    player_info = font_small.render(
        "Player: 2" + "    " + "Level: " + str(final_levels[1]) + "    " + "Score: " + str(
            final_scores[1]) + "    " + "Time Bonus: " + str(final_times[1]) + "    " + "Coins: " + str(
            final_coin_bonuses[1]) + "    " "Final Score: " + str(
            final_scores[1] + final_coin_bonuses[1] + final_times[1]), True,
        black_color)
    player_info_rect = player_info.get_rect(center=(x_max / 2, y_max / 2))
    screen.blit(player_info, player_info_rect)

    winner_text = font_small.render("Player " + str(round_winners[len(round_winners) - 1]) + " Wins!", True,
                                    black_color)
    winner_text_rect = winner_text.get_rect(center=(x_max / 2, y_max / 2 + 100))
    screen.blit(winner_text, winner_text_rect)

    enter_text = font_small.render("Next round: Enter, Quit: Q", True, black_color)
    enter_text_rect = enter_text.get_rect(center=(x_max / 2, y_max / 2 + 200))
    screen.blit(enter_text, enter_text_rect)

    if stop:
        if round_winners.count(1) == round_winners.count(2):
            winner_text = font_big.render("Players are Tied!", True, black_color)
        else:
            winner = 1 if round_winners.count(1) > round_winners.count(2) else 2
            winner_text = font_big.render("Player " + str(winner) + " Wins The Game!", True, black_color)
        winner_text_rect = winner_text.get_rect(center=(x_max / 2, y_max / 2 + 300))
        screen.blit(winner_text, winner_text_rect)


def drawBackground():
    screen.blit(river_background, (0, 0))
    for i in range(len(list_of_land_y_coordinates)):
        screen.blit(land_surface, (0, list_of_land_y_coordinates[i] - 18))


def displayStats(current_player):
    display_y = y_max - 32 if current_player.player_number else 0
    info = font_small.render("Player: " + str(current_player.player_number + 1), True, white_color)
    screen.blit(info, (0, display_y))
    info = font_small.render("Level: " + str(current_player.level), True, white_color)
    screen.blit(info, (150, display_y))
    info = font_small.render("Score: " + str(current_player.score), True, white_color)
    screen.blit(info, (300, display_y))
    info = font_small.render("Time Left: " + str(max_time - int((pygame.time.get_ticks() - start_time) / 1000)), True,
                             white_color)
    screen.blit(info, (500, display_y))
    info = font_small.render("Lives: " + str(current_player.lives), True, white_color)
    screen.blit(info, (700, display_y))
    info = font_small.render("Coins: " + str(current_player.coin_bonus), True, white_color)
    screen.blit(info, (850, display_y))
    info = font_small.render("FINISH", True, white_color)
    screen.blit(info, (x_max - 100, display_y))
    info = font_small.render("START", True, white_color)
    screen.blit(info, (x_max - 100, y_max - display_y - 32))


class CreatePlayer(pygame.sprite.Sprite):

    def __init__(self, img_name, speed_of_movement, player_number):
        super(CreatePlayer, self).__init__()
        self.img_name = img_name
        self.surface = pygame.image.load(self.img_name).convert()
        self.surface.set_colorkey(black_color)
        self.player_number = player_number
        self.rect = self.surface.get_rect(center=(x_max / 2, 0)) if self.player_number else self.surface.get_rect(
            center=(x_max / 2, y_max))
        self.speed_of_movement = speed_of_movement
        self.dead = False
        self.vertical_distance = 0

        self.max_vertical_distance = 0
        self.lives = 3
        self.level = 1
        self.score = 0
        self.coin_bonus = 0
        self.time_bonus = 0

    def movePlayerOnScreen(self):
        keys = pygame.key.get_pressed()
        if (not self.player_number and keys[pygame.K_LEFT]) or (self.player_number and keys[pygame.K_a]):
            self.rect.move_ip(-self.speed_of_movement, 0)
        if (not self.player_number and keys[pygame.K_RIGHT]) or (self.player_number and keys[pygame.K_d]):
            self.rect.move_ip(self.speed_of_movement, 0)
        if (not self.player_number and keys[pygame.K_UP]) or (self.player_number and keys[pygame.K_w]):
            self.rect.move_ip(0, -self.speed_of_movement)
        if (not self.player_number and keys[pygame.K_DOWN]) or (self.player_number and keys[pygame.K_s]):
            self.rect.move_ip(0, self.speed_of_movement)
        # Keep player on the screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > x_max:
            self.rect.right = x_max
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > y_max:
            self.rect.bottom = y_max

    def resetPlayer(self, time_elapsed, add_bonus, won):
        self.rect = self.surface.get_rect(center=(x_max / 2, 0)) if self.player_number else self.surface.get_rect(
            center=(x_max / 2, y_max))
        if won:
            self.level += 1
        self.vertical_distance = self.max_vertical_distance = 0
        if add_bonus:
            self.time_bonus += (max_time - time_elapsed)

    def calculateMaxVerticalDistance(self):
        self.vertical_distance = self.rect.bottom if self.player_number == 1 else abs(y_max - self.rect.top)
        self.max_vertical_distance = max(self.max_vertical_distance, self.vertical_distance)


class CreateMovingObstacles(pygame.sprite.Sprite):

    def __init__(self, img_name, right):
        super(CreateMovingObstacles, self).__init__()
        self.img_name = img_name
        self.speed_of_movement = random.uniform(min_speed_of_obstacle, max_speed_of_obstacle)
        self.direction = right
        self.surface = pygame.image.load(self.img_name).convert()
        self.surface = pygame.transform.scale(self.surface, (60, 60))
        self.surface.set_colorkey(white_color)
        self.random_river_number = random.choice(list_of_river_y_coordinates)
        self.rect = self.surface.get_rect(center=(
                -20, self.random_river_number + 15)) if self.direction else self.surface.get_rect(
            center=(x_max + 20, self.random_river_number + 15))
        number_of_river_obstacles[self.random_river_number] += 1

    def moveObstacleOnScreen(self):
        if self.direction:
            self.rect.move_ip(self.speed_of_movement, 0)
            # remove sprite when it passes out of the screen, and create a new sprite
            if self.rect.left > x_max:
                number_of_river_obstacles[self.random_river_number] -= 1
                obstacle = CreateMovingObstacles(configParser.get("images", "left_to_right_boat_image"), self.direction)
                self.kill()
                all_obstacles.add(obstacle)
                moving_obstacles.add(obstacle)
        else:
            self.rect.move_ip(-self.speed_of_movement, 0)
            # remove sprite when it passes out of the screen, and create a new sprite
            if self.rect.right < 0:
                number_of_river_obstacles[self.random_river_number] -= 1
                obstacle = CreateMovingObstacles(configParser.get("images", "right_to_left_boat_image"), self.direction)
                self.kill()
                all_obstacles.add(obstacle)
                moving_obstacles.add(obstacle)


class CreateFixedObstacles(pygame.sprite.Sprite):

    def __init__(self, img_name):
        super(CreateFixedObstacles, self).__init__()
        self.img_name = img_name
        self.surface = pygame.image.load(self.img_name).convert()
        self.surface = pygame.transform.scale(self.surface, (55, 55))
        self.surface.set_colorkey(white_color)
        self.random_land_number = random.choice(list_of_land_y_coordinates[1:len(list_of_land_y_coordinates) - 1])
        self.rect = self.surface.get_rect(
            center=(random.randrange(0, x_max),
                    self.random_land_number + 10))
        number_of_land_obstacles[self.random_land_number] += 1


class CreateCoins(pygame.sprite.Sprite):

    def __init__(self, img_name):
        super(CreateCoins, self).__init__()
        self.img_name = img_name
        self.surface = pygame.image.load(self.img_name).convert()
        self.surface = pygame.transform.scale(self.surface, (15, 15))
        self.surface.set_colorkey(black_color)
        self.rect = self.surface.get_rect(
            center=(random.randrange(0, x_max),
                    random.choice(list_of_river_y_coordinates) + 15))


def checkIfWon(current_player):
    if not current_player.player_number:
        if current_player.rect.top == 0:
            return True
        return False
    else:
        if current_player.rect.bottom == y_max:
            return True
        return False


def calculateScore(current_player):
    j = 0
    if current_player.vertical_distance < current_player.max_vertical_distance:
        return
    for j in range(0, len(list_of_y_coordinates)):
        if not check_if_calculated[list_of_y_coordinates[j]]:
            break
    if current_player.vertical_distance > list_of_y_coordinates[j] + 35:
        if j % 2 != 0:
            current_player.score += (number_of_river_obstacles[
                                         list_of_y_coordinates[j if current_player.player_number else 12 - j]] * 10)
        else:
            current_player.score += (number_of_land_obstacles[
                                         list_of_y_coordinates[j if current_player.player_number else 12 - j]] * 5)
        check_if_calculated[list_of_y_coordinates[j]] = True


def increaseLevel():
    global max_speed_of_obstacle
    global min_speed_of_obstacle
    max_speed_of_obstacle += 0.5
    min_speed_of_obstacle += 0.5

    for i in list_of_river_y_coordinates:
        number_of_river_obstacles[i] = 0
    for i in list_of_land_y_coordinates:
        number_of_land_obstacles[i] = 0

    # reset coins
    for coin in coins:
        coin.kill()
    for i in range(25):
        coin = CreateCoins(configParser.get("images", "coin_image"))
        all_obstacles.add(coin)
        coins.add(coin)

    # respawn fixed obstacles
    global number_of_fixed_obstacles
    for obstacle in fixed_obstacles:
        obstacle.kill()
    number_of_fixed_obstacles += 3
    for i in range(0, number_of_fixed_obstacles):
        obstacle = CreateFixedObstacles(configParser.get("images", "tree_image"))
        all_obstacles.add(obstacle)
        fixed_obstacles.add(obstacle)

    # respawn moving obstacles
    global number_of_left_moving_obstacles
    for obstacle in moving_obstacles:
        obstacle.kill()
    number_of_left_moving_obstacles += 1
    # add 1 more moving obstacle to the left
    for i in range(0, number_of_left_moving_obstacles):
        obstacle = CreateMovingObstacles(configParser.get("images", "left_to_right_boat_image"), True)
        all_obstacles.add(obstacle)
        moving_obstacles.add(obstacle)
    # add 1 more moving obstacle to the left
    for i in range(0, number_of_left_moving_obstacles):
        obstacle = CreateMovingObstacles(configParser.get("images", "right_to_left_boat_image"), False)
        all_obstacles.add(obstacle)
        moving_obstacles.add(obstacle)


def initialSetup():
    player = CreatePlayer(configParser.get("images", "player1_image"), speed_of_player, 0)
    players.append(player)
    player = CreatePlayer(configParser.get("images", "player2_image"), speed_of_player, 1)
    players.append(player)

    global max_speed_of_obstacle
    global min_speed_of_obstacle
    global number_of_left_moving_obstacles
    global number_of_fixed_obstacles
    global max_time
    max_speed_of_obstacle = configParser.getint("global constants", "initial_max_speed_of_obstacle")
    min_speed_of_obstacle = configParser.getint("global constants", "initial_min_speed_of_obstacle")
    number_of_left_moving_obstacles = configParser.getint("global constants", "initial_number_of_left_moving_obstacles")
    number_of_fixed_obstacles = configParser.getint("global constants", "initial_number_of_fixed_obstacles")
    max_time = configParser.getint("global constants", "max_level_time")

    final_levels[0] = final_levels[1] = 0
    final_scores[0] = final_scores[1] = 0
    final_times[0] = final_times[1] = 0
    final_coin_bonuses[0] = final_times[1] = 0

    for i in list_of_river_y_coordinates:
        number_of_river_obstacles[i] = 0
    for i in list_of_land_y_coordinates:
        number_of_land_obstacles[i] = 0


def reset():
    for i in list_of_y_coordinates:
        check_if_calculated[i] = False
    check_if_calculated[list_of_y_coordinates[0]] = check_if_calculated[list_of_y_coordinates[12]] = True
    global start_time
    start_time = pygame.time.get_ticks()


def findWinner():
    if (final_scores[0] + final_coin_bonuses[0] - final_times[0]) > (
            final_scores[1] + final_coin_bonuses[1] - final_times[1]):
        winner = 1
    elif (final_scores[0] + final_coin_bonuses[0] - final_times[0]) < (
            final_scores[1] + final_coin_bonuses[1] - final_times[1]):
        winner = 2
    else:
        if final_coin_bonuses[0] > final_coin_bonuses[1]:
            winner = 1
        elif final_coin_bonuses[0] < final_coin_bonuses[1]:
            winner = 2
        else:
            winner = 1 if final_times[0] > final_times[1] else 2
    round_winners.append(winner)


def increaseMaxLevelTime(current_player):
    global max_time, speed_of_player
    if current_player.level % 5 == 0:
        max_time += 5
    if current_player.level % 10 == 0:
        speed_of_player += 0.5


def mainloop():
    running = True
    start = False
    end = False
    stop = False
    current_player = None
    global start_time

    while running:

        for event in pygame.event.get():
            # check if quit button is pressed
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # start game
                if (event.key == pygame.K_RETURN and not stop and not start) or (event.key == pygame.K_r and start):
                    pygame.mixer.music.play(loops=-1)
                    start = True
                    end = False
                    initialSetup()
                    reset()
                    increaseLevel()
                    current_player = players[0]
                if event.key == pygame.K_q and end:
                    stop = True
                    quit_sound.play()
                    drawEndScreen(stop)

        if end and not stop:
            pygame.mixer.music.stop()
            start = False
            drawEndScreen(stop)

        elif not start and not stop:
            drawInitialScreen()

        elif start:
            drawBackground()
            displayStats(current_player)

            # find elapsed time since start of level
            time_elapsed = int((pygame.time.get_ticks() - start_time) / 1000)

            # move player based on arrow keys (when key is pressed)
            current_player.movePlayerOnScreen()

            # draw all obstacles on screen
            screen.blit(current_player.surface, current_player.rect)
            for sprite in all_obstacles:
                screen.blit(sprite.surface, sprite.rect)

            # move obstacles on screen
            for obstacle in moving_obstacles:
                obstacle.moveObstacleOnScreen()

            # check for collision with a coin
            if pygame.sprite.spritecollide(current_player, coins, True):
                current_player.coin_bonus += 1
                coin_sound.play()

            # calculate score
            current_player.calculateMaxVerticalDistance()
            calculateScore(current_player)

            # check if won
            if checkIfWon(current_player):
                level_up_sound.play()
                level_up_text = font_big.render(configParser.get("text", "level_up_text"), True, black_color)
                level_up_text_rect = level_up_text.get_rect(center=(x_max / 2, y_max / 2))
                screen.blit(level_up_text, level_up_text_rect)
                pygame.display.flip()
                current_player.resetPlayer(time_elapsed, True, True)
                pygame.time.delay(1000)
                reset()

                if (current_player == players[0] and players[1].dead) or (
                        current_player == players[1] and players[0].dead):
                    increaseLevel()
                    increaseMaxLevelTime(current_player)
                else:
                    current_player = players[0] if current_player == players[1] else players[1]
                    if current_player == players[0]:
                        increaseLevel()
                        increaseMaxLevelTime(current_player)

            # check for collision with an obstacle or time exceeded
            if pygame.sprite.spritecollideany(current_player, all_obstacles, collided=pygame.sprite.collide_rect_ratio(
                    0.75)) or time_elapsed >= max_time:
                death_sound.play()

                if time_elapsed >= max_time:
                    you_died_text = font_big.render(configParser.get("text", "time_up_text"), True, black_color)
                else:
                    you_died_text = font_big.render(configParser.get("text", "you_died_text"), True, black_color)
                you_died_text_rect = you_died_text.get_rect(center=(x_max / 2, y_max / 2))
                screen.blit(you_died_text, you_died_text_rect)
                pygame.display.flip()
                pygame.time.delay(1000)
                current_player.resetPlayer(time_elapsed, False, False)

                current_player.lives -= 1
                if not current_player.lives:
                    current_player.dead = True
                    final_scores[current_player.player_number] = current_player.score
                    final_levels[current_player.player_number] = current_player.level
                    final_coin_bonuses[current_player.player_number] = current_player.coin_bonus
                    final_times[current_player.player_number] = current_player.time_bonus
                    current_player = players[0] if current_player == players[1] else players[1]
                    if current_player == players[0]:
                        increaseLevel()

                reset()

                if players[0].dead and players[1].dead:
                    end_of_round_sound.play()
                    for sprite in all_obstacles:
                        sprite.kill()
                    findWinner()
                    end = True
                    players[0].kill()
                    players[1].kill()
                    players.clear()

        # flip(update) the display
        pygame.display.flip()

        # choose FPS rate
        clock.tick(60)

    pygame.quit()


mainloop()
