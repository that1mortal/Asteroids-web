import pygame
import os
import random
from itertools import repeat

pygame.init()
pygame.font.init()
pygame.mixer.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (170, 115, 55)
BLUE = (0, 0, 255)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 500

HEALTH_PACK_MIN = 75
HEALTH_PACK_CHANCE = 1200
HEAL_MIN = 15
HEAL_MAX = 35

FPS = 60

HIT_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'hit.wav'))
WALL_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'wall.wav'))
DEATH_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'death.wav'))

LOSE_FONT = pygame.font.SysFont('framd', 100)
SUB_TEXT = pygame.font.SysFont('framd', 20)
HEALTH_TEXT = pygame.font.SysFont('framd', 40)
SCORE_TEXT = pygame.font.SysFont('famd', 30)

trail = []
mini_trail = []
bouncer_trails = []
bouncers_vel = []
health_packs = []

hit_on_bounce = 0

MAX_MINI_SQUARES = 3

BOUNCER_VEL_X = 5
BOUNCER_VEL_Y = 0
BOUNCER_WIDTH = 15
BOUNCER_HEIGHT = 15
BOUNCER_TRAIL_LEN = 40
BOUNCER_TRAIL_REMOVE = 0.7
BOUNCER_MIN_DMG = 10
BOUNCER_MAX_DMG = 25

MINI_SQUARE_WIDTH = 10
MINI_SQUARE_HEIGHT = 10
MINI_SQUARE_TRAIL_LEN = 2000
MINI_SQUARE_TRAIL_REMOVE = 0.5
MINI_SQUARE_SPEED = 2
MINI_SQUARE_MIN_DMG = 20
MINI_SQUARE_MAX_DMG = 40

TRAIL_LENGTH = 50
SIZE_REMOVE_AMOUNT = 1
PLAYER_WIDTH = 20
PLAYER_HEIGHT = 20
PLAYER_VEL = 8

health_img = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'health.png')), (25, 25))

shake_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen = shake_screen.copy()
pygame.display.set_caption("Dodge shit")

bounce_multiplier = 3

offset = repeat((0, 0))

def draw_window(player, mini_square):
    global trail, mini_trail, health, bouncer_trails, bouncers, offset, health_packs

    screen.fill(BLACK)

    health_text = HEALTH_TEXT.render("Health: " + str(health), 1, WHITE)
    screen.blit(health_text, (SCREEN_WIDTH/2 - health_text.get_width()/2, 20))

    score_text = SCORE_TEXT.render("Score: " + str(bounces_survived), 1, WHITE)
    screen.blit(score_text, (20, 20))

    pygame.draw.rect(screen, ORANGE, mini_square)

    pygame.draw.rect(screen, RED, player)

    if len(health_packs) > 0:
        for pack in health_packs:
            screen.blit(health_img, (pack.x, pack.y))

    for bouncer in bouncers:
        pygame.draw.rect(screen, BLUE, bouncer)
    
    trail_remove = 0
    i = 0
    #[0[[543, 543], [535, 5343]]]
    for bouncer in bouncer_trails:
        trail_remove = 0
        for t in bouncer:
            pygame.draw.rect(screen, BLUE, (t[0]+trail_remove/2, t[1]+trail_remove/2, BOUNCER_WIDTH - trail_remove, BOUNCER_HEIGHT - trail_remove))
            trail_remove += BOUNCER_TRAIL_REMOVE
        i += 1

    size_remove = 0
    for t in trail:
        pygame.draw.rect(screen, RED, (t[0]+size_remove/2, t[1]+size_remove/2, PLAYER_WIDTH - size_remove, PLAYER_HEIGHT - size_remove))
        size_remove += SIZE_REMOVE_AMOUNT
    
    trail_remove = 0
    for t in mini_trail:
        pygame.draw.rect(screen, ORANGE, (t[0]+trail_remove/2, t[1]+trail_remove/2, MINI_SQUARE_WIDTH - trail_remove/2, MINI_SQUARE_HEIGHT - trail_remove))
        trail_remove += MINI_SQUARE_TRAIL_REMOVE

    shake_screen.blit(screen, next(offset))

    pygame.display.update()

def screen_shake(intensity, amplitude):
    s = -1
    for i in range(0, 3):
        for x in range(0, amplitude, intensity):
            yield x * s, 0
        for x in range(amplitude, 0, intensity):
            yield x * s, 0
        s *= -1
    while True:
        yield 0, 0


def player_movement(player, keys_pressed):
    global PLAYER_VEL, trail, offset

    if keys_pressed[pygame.K_w]:
        if player.y - PLAYER_VEL > 0:
            player.y -= PLAYER_VEL
        else:
            if not trail[1][1] == player.y:
                WALL_SOUND.play()
                offset = screen_shake(3, 10)
    if keys_pressed[pygame.K_s]:
        if player.y + PLAYER_VEL + PLAYER_HEIGHT < SCREEN_HEIGHT:
            player.y += PLAYER_VEL
        else:
            if not trail[1][1] == player.y:
                WALL_SOUND.play()
                offset = screen_shake(3, 10)
    if keys_pressed[pygame.K_a]:
        if player.x - PLAYER_VEL > 0:
            player.x -= PLAYER_VEL
        else:
            if not trail[1][0] == player.x:
                WALL_SOUND.play()
                offset = screen_shake(3, 10)
    if keys_pressed[pygame.K_d]:
        if player.x + PLAYER_VEL + PLAYER_WIDTH < SCREEN_WIDTH:
            player.x += PLAYER_VEL
        else:
            if not trail[1][0] == player.x:
                WALL_SOUND.play()
                offset = screen_shake(3, 10)


def mini_square_movement(player, mini_square):
    global health, offset, MINI_SQUARE_MIN_DMG, MINI_SQUARE_MAX_DMG

    if player.x + PLAYER_WIDTH/4 - mini_square.x < 0 and not player.x + PLAYER_WIDTH/4 - mini_square.x == 0:
        mini_square.x -= MINI_SQUARE_SPEED
    else:
        mini_square.x += MINI_SQUARE_SPEED
    if player.y + PLAYER_HEIGHT/4 - mini_square.y < 0 and not player.y + PLAYER_HEIGHT/4 - mini_square.y == 0:
        mini_square.y -= MINI_SQUARE_SPEED
    else:
        mini_square.y += MINI_SQUARE_SPEED

    if mini_square.colliderect(player):
        health -= random.randint(MINI_SQUARE_MIN_DMG, MINI_SQUARE_MAX_DMG)
        HIT_SOUND.play()
        offset = screen_shake(5, 20)
        mini_square.x = random.randint(0, SCREEN_WIDTH)
        mini_square.y = random.randint(0, SCREEN_HEIGHT)

def lose_screen():
    global run, bounces_survived

    lose_text = LOSE_FONT.render("You Died!", 1, RED)
    sub_text = SUB_TEXT.render("Restarting in 5 seconds", 1, WHITE)
    score_text = SCORE_TEXT.render("Score: " + str(bounces_survived), 1, WHITE)

    screen.fill(BLACK)
    screen.blit(lose_text, (SCREEN_WIDTH/2 - lose_text.get_width()/2, SCREEN_HEIGHT/2 - lose_text.get_height()/2))
    screen.blit(sub_text, (SCREEN_WIDTH/2 - sub_text.get_width()/2, SCREEN_HEIGHT/2 - sub_text.get_height()/2 + 80))
    screen.blit(score_text, (SCREEN_WIDTH/2 - score_text.get_width()/2, SCREEN_HEIGHT/2 - score_text.get_height()/2 - 80))
    shake_screen.blit(screen, (0, 0))
    pygame.display.update()
    pygame.time.delay(5000)
    run = False

def bouncer_movement(player):
    global bouncers, BOUNCER_VEL_X, BOUNCER_VEL_Y, bounces_survived, bouncers_vel, health, can_dmg, hit_on_bounce, offset, BOUNCER_MIN_DMG, BOUNCER_MAX_DMG

    index = 0
    for bouncer in bouncers:
        bouncer.x += bouncers_vel[index][0]
        bouncer.y += bouncers_vel[index][1]
        if bouncer.x >= SCREEN_WIDTH:
            bouncers_vel[index][0] *= -1
            bouncers_vel[index][0] += random.randint(-4, 0)
            bouncers_vel[index][1] += random.randint(-4, 0)
            bounces_survived += 1
        elif bouncer.x <= 0:
            bouncers_vel[index][0] *= -1
            bouncers_vel[index][0] += random.randint(0, 4)
            bouncers_vel[index][1] += random.randint(-4, 0)
            bounces_survived += 1
        if bouncer.y >= SCREEN_HEIGHT:
            bouncers_vel[index][1] *= -1
            bouncers_vel[index][1] += random.randint(-4, 0)
            bounces_survived += 1
        elif bouncer.y <= 0:
            bouncers_vel[index][1]*= -1
            bouncers_vel[index][1] += random.randint(0, 4)
            bounces_survived += 1
        if bouncers_vel[index][0] > 7:
            bouncers_vel[index][0] = 7
        if bouncers_vel[index][1] > 7:
            bouncers_vel[index][1] = 7
        if bouncer.colliderect(player):
            if hit_on_bounce < bounces_survived:
                health -= random.randint(BOUNCER_MIN_DMG, BOUNCER_MAX_DMG)
                HIT_SOUND.play()
                offset = screen_shake(5, 20)
                hit_on_bounce = bounces_survived
        index += 1

def difficulty_handler(keys_pressed):
    global bounce_multiplier, PLAYER_VEL, MINI_SQUARE_MIN_DMG, MINI_SQUARE_MAX_DMG, BOUNCER_MIN_DMG, BOUNCER_MAX_DMG, MINI_SQUARE_SPEED, HEALTH_PACK_MIN, HEALTH_PACK_CHANCE, HEAL_MIN, HEAL_MAX

    if keys_pressed[pygame.K_1]:
        bounce_multiplier = 4
        PLAYER_VEL = 10
        MINI_SQUARE_MIN_DMG = 10
        MINI_SQUARE_MAX_DMG = 25
        MINI_SQUARE_SPEED = 1
        HEALTH_PACK_MIN = 90
        HEAL_MIN = 25
        HEAL_MAX = 50
        HEALTH_PACK_CHANCE = 8000
    if keys_pressed[pygame.K_2]:
        bounce_multiplier = 3
        PLAYER_VEL = 7
        MINI_SQUARE_MIN_DMG = 20
        MINI_SQUARE_MAX_DMG = 30
        MINI_SQUARE_SPEED = 2
        HEAL_MIN = 15
        HEAL_MAX = 30
        HEALTH_PACK_MIN = 75
        HEALTH_PACK_CHANCE = 1200
    if keys_pressed[pygame.K_3]:
        bounce_multiplier = 2
        MINI_SQUARE_MIN_DMG = 30
        MINI_SQUARE_MAX_DMG = 45
        MINI_SQUARE_SPEED = 3
        HEALTH_PACK_MIN = 45
        HEAL_MIN = 10
        HEAL_MAX = 20
        PLAYER_VEL = 5
        HEALTH_PACK_CHANCE = 2400

def health_handler(player):
    global health, health_packs 

    index = 0
    for pack in health_packs:
        if pack.colliderect(player):
            health += random.randint(HEAL_MIN, HEAL_MAX)
            health_packs.pop(index)
            if health > 100:
                health = 100
        
        index += 1

def main():

    global trail, bounces_survived, mini_trail, health, run, bouncer_trails, bouncers, bouncers_vel, hit_on_bounce, easy_button, med_button, hard_button, health_packs

    health = 100

    run = True

    health_packs = []

    diff_text = HEALTH_TEXT.render("1: Easy 2: Medium 3: Hard", 1,  WHITE)
    sub_text = SUB_TEXT.render("You can select the difficulty when the game starts", 1, WHITE)

    shake_screen.fill(BLACK)
    shake_screen.blit(diff_text, (SCREEN_WIDTH/2 - diff_text.get_width()/2, SCREEN_HEIGHT/2 - diff_text.get_height()/2))
    shake_screen.blit(sub_text, (SCREEN_WIDTH/2 - sub_text.get_width()/2, SCREEN_HEIGHT/2 - sub_text.get_height()/2 + 50))
    pygame.display.update()
    pygame.time.delay(5000)

    trail = []
    mini_trail = []
    bouncer_trails = []
    bouncers_vel = []

    hit_on_bounce = 0

    clock = pygame.time.Clock()

    bounces_survived = 0
    bounce_limit = 5

    player = pygame.Rect(SCREEN_WIDTH/2 - PLAYER_WIDTH/2, SCREEN_HEIGHT/2 - PLAYER_HEIGHT/2, PLAYER_WIDTH, PLAYER_HEIGHT)

    randx = random.randint(0, SCREEN_WIDTH)
    randy = random.randint(0, SCREEN_HEIGHT)

    mini_square = pygame.Rect(randx - MINI_SQUARE_WIDTH/2, randy - MINI_SQUARE_HEIGHT/2, MINI_SQUARE_WIDTH, MINI_SQUARE_HEIGHT)

    randx = random.randint(0, SCREEN_WIDTH)
    randy = random.randint(0, SCREEN_HEIGHT)
    bouncers = [pygame.Rect(randx - BOUNCER_WIDTH/2, randy - BOUNCER_WIDTH/2, BOUNCER_WIDTH, BOUNCER_HEIGHT)]
    bouncers_vel = [[BOUNCER_VEL_X, BOUNCER_VEL_Y]]
    bouncer_trails.append([[randx, randy]])
    bounce_multiplier = 3

    while run:

        clock.tick(FPS)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                exit()
        
        trail.insert(0, [player.x, player.y])
        if len(trail) > TRAIL_LENGTH:
            trail.pop(TRAIL_LENGTH)

        i = 0
        for bouncer in bouncers:
            bouncer_trails[i].insert(0, [bouncer.x, bouncer.y])
            if len(bouncer_trails[i]) > BOUNCER_TRAIL_LEN:
                bouncer_trails[i].pop(BOUNCER_TRAIL_LEN)
            i += 1
        
        mini_trail.insert(0, [mini_square.x, mini_square.y])
        if len(mini_trail) > MINI_SQUARE_TRAIL_LEN:
            mini_trail.pop(MINI_SQUARE_TRAIL_LEN)

        if health <= 0:
            health = 0
            DEATH_SOUND.play()
            lose_screen()

        if bounces_survived > bounce_limit:
            randx = random.randint(0, SCREEN_WIDTH)
            randy = random.randint(0, SCREEN_HEIGHT)
            bouncers.append(pygame.Rect(randx - BOUNCER_WIDTH/2, randy - BOUNCER_WIDTH/2, BOUNCER_WIDTH, BOUNCER_HEIGHT))
            bouncers_vel.append([BOUNCER_VEL_X, BOUNCER_VEL_Y])
            bouncer_trails.append([[randx, randy]])
            bounce_limit *= bounce_multiplier

        if health < HEALTH_PACK_MIN:
            if random.randint(1, HEALTH_PACK_CHANCE) == 300:
                health_packs.append(pygame.Rect(random.randint(15, SCREEN_WIDTH - 15), random.randint(15, SCREEN_HEIGHT - 15), 15, 15))

        keys_pressed = pygame.key.get_pressed()
        player_movement(player, keys_pressed)
        difficulty_handler(keys_pressed)
        mini_square_movement(player, mini_square)
        bouncer_movement(player)
        health_handler(player)
        draw_window(player, mini_square)
    
    main()
    

if __name__ == "__main__":
    main()