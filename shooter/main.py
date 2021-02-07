import os
import random
from random import randrange

import pygame

pygame.init()
pygame.font.init()
pygame.mixer.init()

BASE_PATH = os.path.dirname(__file__)
FPS = 60
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

BACKGROUND = pygame.transform.scale(
    pygame.image.load(os.path.join(BASE_PATH, 'assets', 'space.jpg')),
    (SCREEN_WIDTH, SCREEN_HEIGHT),
)

PLAYER_SPEED = 8
MAX_PLAYER_BULLET = 2
PLAYER_BULLET_SPEED = 8
PLAYER_HIT = pygame.USEREVENT + 1
PLAYER_POWERUP = pygame.USEREVENT + 3

BOSS_SPEED = 10
BOSS_BULLET_SPEED = 10
BOSS_HIT = pygame.USEREVENT + 2

HEALTH_FONT = pygame.font.SysFont('comicsans', 30)
END_GAME_TEXT = pygame.font.SysFont('comicsans', 100)

SOUND_PLAYER_FIRE = pygame.mixer.Sound(os.path.join(BASE_PATH, 'assets', 'player_fire.ogg'))
SOUND_PLAYER_HIT = pygame.mixer.Sound(os.path.join(BASE_PATH, 'assets', 'player_hit.oga'))
SOUND_BOSS_FIRE = pygame.mixer.Sound(os.path.join(BASE_PATH, 'assets', 'boss_fire.ogg'))
SOUND_BOSS_HIT = pygame.mixer.Sound(os.path.join(BASE_PATH, 'assets', 'boss_hit.ogg'))
SOUND_POWERUPS = pygame.mixer.Sound(os.path.join(BASE_PATH, 'assets', 'powerup.ogg'))


class BaseObject(object):
    def __init__(self):
        self.rep = None
        self.width = 0
        self.height = 0
        self.bullets = []
        self.power_ups = []

    def position(self):
        return (
            self.rep and self.rep.x or 0,
            self.rep and self.rep.y or 0,
        )


class Player(BaseObject):

    def __init__(self):
        self.image = pygame.transform.rotate(
            pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_PATH, 'assets', 'player.png')),
                (100, 100),
            ),
            270,
        )
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rep = pygame.Rect(
            10,
            SCREEN_HEIGHT / 2 - self.height / 2,
            self.width,
            self.height,
        )
        self.bullets = []
        self.life = 3
        self.max_bullets = MAX_PLAYER_BULLET


class Boss(BaseObject):

    def __init__(self):
        self.image = pygame.transform.rotate(
            pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_PATH, 'assets', 'boss.png')),
                (100, 75),
            ),
            90,
        )
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rep = pygame.Rect(
            SCREEN_WIDTH - self.image.get_width() - 10,
            SCREEN_HEIGHT / 2 - self.height / 2,
            self.width,
            self.height,
        )
        self.bullets = []
        self.power_ups = []
        self.life = 10


class Bullet(BaseObject):
    def __init__(self, x=0, y=0, width=10, height=10):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.rep = pygame.Rect(self.x, self.y, self.width, self.height)


class PowerUps(BaseObject):
    def __init__(self, x=0, y=0, width=20, height=20):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.rep = pygame.Rect(self.x, self.y, self.width, self.height)


def update_canvas(player, boss):
    # Fill the background with white
    SCREEN.fill((255, 255, 255))
    SCREEN.blit(BACKGROUND, (0, 0))
    SCREEN.blit(player.image, player.position())
    SCREEN.blit(boss.image, boss.position())

    for bullet in player.bullets:
        pygame.draw.rect(SCREEN, (0, 255, 0), bullet.rep)

    for bullet in boss.bullets:
        pygame.draw.rect(SCREEN, (255, 0, 0), bullet.rep)

    for power_up in boss.power_ups:
        pygame.draw.rect(SCREEN, (255, 255, 0), power_up.rep)

    player_health_text = HEALTH_FONT.render('Health: {}'.format(player.life), 1, (0, 255, 0))
    player_max_bullet = HEALTH_FONT.render('Max Bullets: {}'.format(player.max_bullets), 1, (0, 255, 0))
    boss_health_text = HEALTH_FONT.render('Health: {}'.format(boss.life), 1, (255, 0, 0))

    SCREEN.blit(player_health_text, (10, 10))
    SCREEN.blit(player_max_bullet, (40 + player_health_text.get_width(), 10))
    SCREEN.blit(boss_health_text, (SCREEN_WIDTH - boss_health_text.get_width() - 10, 10))

    pygame.display.update()


def handle_key_press(player, key_pressed):
    if key_pressed[pygame.K_w] and player.rep.y - PLAYER_SPEED > 0:
        player.rep.y -= PLAYER_SPEED
    if key_pressed[pygame.K_s] and player.rep.y + PLAYER_SPEED + player.height < SCREEN_HEIGHT:
        player.rep.y += PLAYER_SPEED


def handle_player_bullets(player, boss):
    for bullet in player.bullets:
        bullet.rep.x += PLAYER_BULLET_SPEED

        if boss.rep.colliderect(bullet.rep):
            pygame.event.post(pygame.event.Event(BOSS_HIT))
            player.bullets.remove(bullet)
        elif bullet.rep.x > SCREEN_WIDTH:
            player.bullets.remove(bullet)


def handle_boss_bullets(player, boss):
    for bullet in boss.bullets:
        bullet.rep.x -= BOSS_BULLET_SPEED

        if player.rep.colliderect(bullet.rep):
            pygame.event.post(pygame.event.Event(PLAYER_HIT))
            boss.bullets.remove(bullet)

        if bullet.rep.x < 0:
            boss.bullets.remove(bullet)

    for power_up in boss.power_ups:
        power_up.rep.x -= BOSS_BULLET_SPEED

        if player.rep.colliderect(power_up.rep):
            pygame.event.post(pygame.event.Event(PLAYER_POWERUP))
            boss.power_ups.remove(power_up)

        if power_up.rep.x < 0:
            boss.power_ups.remove(power_up)


def display_end_game_text(text, color):
    end_game_text = END_GAME_TEXT.render(text, 1, color)
    SCREEN.blit(
        end_game_text, (
            SCREEN_WIDTH / 2 - end_game_text.get_width() / 2,
            SCREEN_HEIGHT / 2 - end_game_text.get_height() / 2)
    )
    pygame.display.update()
    pygame.time.delay(5000)


def main():
    clock = pygame.time.Clock()
    running = True
    boss_bullet_timer = 0
    boss_move_timer = 0
    boss_bullet_freq = 45

    player = Player()
    boss = Boss()
    boss_move_bit = False

    while running:
        # Games Frames Per Second
        clock.tick(FPS)
        boss_bullet_timer += 1
        boss_move_timer += 1

        # Did the user click the window close button?
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and len(player.bullets) < player.max_bullets:
                    player.bullets.append(Bullet(x=player.width, y=player.rep.y + player.height / 2 - 8))
                    SOUND_PLAYER_FIRE.play()

            if event.type == PLAYER_HIT:
                player.life -= 1
                SOUND_PLAYER_HIT.play()

            if event.type == BOSS_HIT:
                boss.life -= 1
                boss_bullet_freq -= 2
                SOUND_BOSS_HIT.play()

            if event.type == PLAYER_POWERUP:
                player.max_bullets += 1
                SOUND_POWERUPS.play()

        if boss_move_timer >= 20:
            boss_move_timer = 0
            boss_move_bit = bool(random.getrandbits(1))

        if boss_move_bit and boss.rep.y - BOSS_SPEED > 0:
            boss.rep.y -= BOSS_SPEED
        elif not boss_move_bit and boss.rep.y + BOSS_SPEED + boss.height < SCREEN_HEIGHT:
            boss.rep.y += BOSS_SPEED

        if boss_bullet_timer >= boss_bullet_freq:
            boss_bullet_timer = 0
            fire = bool(random.getrandbits(1))
            if fire:
                boss.bullets.append(Bullet(x=boss.rep.x + 45, y=boss.rep.y + boss.height - 18, width=16, height=16))
                boss.bullets.append(Bullet(x=boss.rep.x, y=boss.rep.y + boss.height / 2 - 8, width=16, height=16))
                boss.bullets.append(Bullet(x=boss.rep.x + 45, y=boss.rep.y + 2, width=16, height=16))
                SOUND_BOSS_FIRE.play()
            elif not fire and randrange(10) == 7:
                boss.power_ups.append(PowerUps(x=boss.rep.x, y=boss.rep.y + boss.height / 2 - 10))

        key_pressed = pygame.key.get_pressed()
        handle_key_press(player, key_pressed)
        handle_player_bullets(player, boss)
        handle_boss_bullets(player, boss)

        update_canvas(player, boss)

        if player.life <= 0:
            display_end_game_text('You LOSS! :(', (255, 0, 0))
            break
        elif boss.life <= 0:
            display_end_game_text('You WIN! :)', (0, 255, 0))
            break

    # Done! Time to quit.
    pygame.quit()


if __name__ == '__main__':
    main()
