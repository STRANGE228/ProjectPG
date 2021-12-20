import os
import sqlite3
from random import random, randint

import pygame as pg

pg.init()
player_sprite = pg.sprite.Group()
sprites_1 = pg.sprite.Group()
sprites_2 = pg.sprite.Group()
ground_sprite = pg.sprite.Group()
check_sprite = pg.sprite.Group()
num = 1


class Player(pg.sprite.Sprite):
    image = pg.image.load(os.path.join('data', 'player_gleid.png'))
    def __init__(self):
        super().__init__(player_sprite)
        self.image = Player.image
        self.rect = self.image.get_rect()
        self.rect.x = 120
        self.rect.y = 500
        self.inJump = False
        self.jump = 20
        self.onGround = False
        self.score = 0
        self.live = True


    def update(self):
        self.score += 0.1
        if not(self.inJump):
            if pg.sprite.spritecollideany(self, ground_sprite) is None:
                if not(pg.sprite.spritecollideany(self, sprites_1) or pg.sprite.spritecollideany(self, sprites_2)):
                    self.rect.y += 4
                    if obstacle := (pg.sprite.spritecollideany(self, sprites_1) or
                                    pg.sprite.spritecollideany(self, sprites_2)):
                        if obstacle.typ != 1:
                            self.live = False
                        self.rect.y -= 4
                        self.rect.y = obstacle.rect.y - 30
                        self.onGround = True
                    elif ground := pg.sprite.spritecollideany(self, ground_sprite):
                        self.rect.y -= 4
                        self.rect.y = ground.rect.y - 30
                        self.onGround = True
                    else:
                        self.onGround = False
                else:
                    self.onGround = True

        if self.inJump:
            self.onGround = False
            if self.jump > -2:
                if self.jump > 0:
                    self.rect.y -= 4
                    if obstacle := (pg.sprite.spritecollideany(self, sprites_1) or
                                    pg.sprite.spritecollideany(self, sprites_2)):
                        self.rect.y += 4
                        self.rect.y = obstacle.rect.y + 30
                        self.jump = 0

                self.jump -= 1
            else:
                self.inJump = False
                self.jump = 20
        if pg.sprite.spritecollideany(self, ground_sprite):
            self.onGround = True

    def dead(self, t):
        if t < 50:
            if 35 > t > 5 :
                self.image = pg.image.load(os.path.join('data', f'player_gleid_dead{t // 5}.png'))


class Ground(pg.sprite.Sprite):
    image = pg.image.load(os.path.join('data', 'ground1.png'))
    def __init__(self):
        super().__init__(ground_sprite)
        self.image = Ground.image
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 540


class Obstacle(pg.sprite.Sprite):
    image_block = pg.image.load(os.path.join('data', 'brick.png'))
    image_spike = pg.image.load(os.path.join('data', 'spike.png'))
    def __init__(self, n, x, y, typ):
        if n == 1:
            super(Obstacle, self).__init__(sprites_1)
        else:
            super(Obstacle, self).__init__(sprites_2)
        if typ == 1:
            self.image = Obstacle.image_block
            self.typ = 1
        elif typ == 2:
            self.image = Obstacle.image_spike
            self.typ = 2
        elif typ == 3:
            self.image = pg.transform.flip(Obstacle.image_spike, False, True)
            self.typ = 3
        elif typ == 4:
            self.image = pg.transform.rotate(Obstacle.image_spike, 90)
            self.typ = 4
        elif typ == 5:
            self.image = pg.transform.rotate(Obstacle.image_spike, -90)
            self.typ = 5
        self.rect = self.image.get_rect()
        self.rect.x = x * 30 + 800
        self.rect.y = (y + 3) * 30

    def update(self):
        self.rect.x -= 5
        if self.rect.x < -30:
            self.kill()


class Check(pg.sprite.Sprite):
    def __init__(self, player):
        super().__init__(check_sprite)
        self.p = player
        self.image = pg.Surface([28, 28])
        self.rect = pg.Rect(self.p.rect.x + 3, self.p.rect.y + 1, 28, 28)

    def update(self):
        self.rect.x = self.p.rect.x + 3
        self.rect.y = self.p.rect.y + 1
        if  pg.sprite.spritecollideany(self, sprites_1) or pg.sprite.spritecollideany(self, sprites_2):
            self.p.live = False


def create_obstacle():
    global num
    if num == 1:
        num = 2
    else:
        num = 1
    with open('Obstacles.txt', 'r', encoding='utf8') as f:
        level = f.readlines()
        num_level = randint(0, round(len(level) / 18) - 1)
        level = level[num_level * 18:num_level * 18 + 15]
        for y, line in enumerate(level):
            for x, elem in enumerate(list(line.strip(' \n'))):
                if elem != '0':
                    Obstacle(num, x, y, int(elem))


def zap_rec(score):
    db = sqlite3.connect('records.db')
    cur = db.cursor()
    sql1 = f"""select rec from record where Game like '%Gleid%'"""
    last_rec = cur.execute(sql1).fetchone()[0]
    if str(score) > last_rec:
        sql = f"""update record set rec = {score} where Game like '%Gleid%'"""
        cur.execute(sql)
    db.commit()


def gleid_start():
    screen = pg.display.set_mode((800, 600))
    clock = pg.time.Clock()
    running = True
    player = Player()
    ground = Ground()
    check = Check(player)

    def new_game():
        nonlocal player, t, count, check
        player_sprite.empty()
        sprites_1.empty()
        sprites_2.empty()
        # ground_sprite.empty()
        check_sprite.empty()
        player = Player()
        t = 0
        count = 0
        check = Check(player)

    t = 0
    count = 0
    while running:
        screen.fill((150, 0, 150))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN or (event.type == pg.KEYDOWN and event.key == pg.K_SPACE):
                if player.onGround:
                    player.inJump = True
        if count <= 0:
            create_obstacle()
            count = 800
        count -= 3

        if player.live:
            player_sprite.update()
            sprites_1.update()
            sprites_2.update()
        else:
            t += 1
            if t < 50:
                player.dead(t)
            else:
                zap_rec(player.score)
                new_game()
        player_sprite.draw(screen)
        check_sprite.update()
        ground_sprite.draw(screen)
        sprites_1.draw(screen)
        sprites_2.draw(screen)
        f = pg.font.Font(None, 30)
        text_open = f.render(f'{round(player.score, 2)}', True,
                             (0, 240, 240))
        screen.blit(text_open, (10, 10))
        pg.display.flip()
        clock.tick(30)

    player_sprite.empty()
    sprites_1.empty()
    sprites_2.empty()
    ground_sprite.empty()
    check_sprite.empty()
