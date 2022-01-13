import os
import sqlite3
from random import randint
from math import atan2, cos, sin, degrees

import pygame as pg

pg.init()
player_sprite = pg.sprite.Group()
enemy_sprite = pg.sprite.Group()
bullet_sprite = pg.sprite.Group()
spawn_bul = pg.sprite.Group()


def zap_record(score):
    db = sqlite3.connect('records.db')
    cur = db.cursor()
    sql1 = f"""select rec from record where Game like '%spirte%'"""
    last_rec = cur.execute(sql1).fetchone()[0]
    if score > int(last_rec):
        sql = f"""update record set rec = {score} where Game like '%spirte%'"""
        cur.execute(sql)
    db.commit()


class PlayerFall(pg.sprite.Sprite):
    image = pg.image.load(os.path.join('data', 'spirte2.png'))

    def __init__(self):
        super().__init__(player_sprite)
        self.image = PlayerFall.image
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = 200
        self.bullets = 3
        self.score = 0
        self.live = True
        self.dx, self.dy = 0, 0

    def update(self):
        self.rect = self.rect.move(self.dx, self.dy)
        if self.dy < 5:
            self.dy += 0.1
        if self.dx > 0:
            self.dx -= 0.01
        elif self.dx < 0:
            self.dx += 0.01
        if self.rect.y <= 0:
            self.rect.y = 1
            self.dy = 1
        if self.rect.x <= -self.image.get_width():
            self.rect.x = 800
        if self.rect.x > 800 + self.image.get_width():
            self.rect.x = -self.image.get_width()
        if self.rect.y >= 600:
            self.live = False
        if bul := pg.sprite.spritecollideany(self, spawn_bul):
            bul.kill()
            self.bullets += 1
            self.score += 1
        if pg.sprite.spritecollideany(self, enemy_sprite):
            self.live = False


class GunFall(pg.sprite.Sprite):
    image = pg.image.load(os.path.join('data', 'spirte1.png'))

    def __init__(self, player):
        super().__init__(player_sprite)
        self.image = GunFall.image
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = 200
        self.pl = player
        self.angle = 0

    def update(self):
        self.image = pg.transform.rotate(GunFall.image, -degrees(self.angle) - 90)
        self.rect.x = self.pl.rect.x + self.image.get_width() * cos(self.angle) // 2
        self.rect.y = self.pl.rect.y + 25 + self.image.get_height() * sin(self.angle) // 2


class BulletFall(pg.sprite.Sprite):
    image = pg.image.load(os.path.join('data', 'spirte0.png'))

    def __init__(self, x, y, dx, dy, angle):
        super().__init__(bullet_sprite)
        self.image = pg.transform.rotate(BulletFall.image, -degrees(angle) - 90)
        self.rect = self.image.get_rect()
        self.rect.x = x + self.image.get_width() * cos(angle) // 2
        self.rect.y = y + self.image.get_height() * sin(angle) // 2
        self.dx = dx
        self.dy = dy

    def update(self):
        self.rect = self.rect.move(self.dx, self.dy)
        if not(-self.image.get_width() <= self.rect.x < 800 + self.image.get_width()):
            self.kill()
        if not(-self.image.get_height() <= self.rect.y < 600 + self.image.get_height()):
            self.kill()


class EnemyFall(pg.sprite.Sprite):
    image = pg.image.load(os.path.join('data', 'Fantaser0.png'))

    def __init__(self, x, y):
        super().__init__(enemy_sprite)
        self.image = EnemyFall.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        if self.rect.y > 600 + self.image.get_height():
            self.kill()
        self.rect.y += 5


class SpawnBullet(pg.sprite.Sprite):
    image = pg.image.load(os.path.join('data', 'spirte0.png'))

    def __init__(self, x, y):
        super().__init__(spawn_bul)
        self.image = SpawnBullet.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


def fall_start():
    screen = pg.display.set_mode((800, 600))
    clock = pg.time.Clock()
    running = True
    arrow = pg.image.load(os.path.join('data', 'arrow.png'))
    player, gun = None, None

    def new_game():
        nonlocal player, gun
        player_sprite.empty()
        enemy_sprite.empty()
        bullet_sprite.empty()
        spawn_bul.empty()
        player = PlayerFall()
        gun = GunFall(player)
    new_game()
    coord = 0, 0
    count = 0
    pg.mouse.set_visible(False)
    while running:
        screen.fill((240, 250, 240))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if player.live:
                if event.type == pg.MOUSEBUTTONDOWN:
                    if player.bullets:
                        angle = atan2((event.pos[1] - gun.rect.y), (event.pos[0] - gun.rect.x))
                        player.dx = -cos(angle) * 10
                        player.dy = -sin(angle) * 10
                        player.bullets -= 1
                        BulletFall(player.rect.x + GunFall.image.get_width() * cos(angle) // 2,
                                   player.rect.y + 25 + GunFall.image.get_height() * sin(angle) // 2,
                                   cos(angle) * 7, sin(angle) * 7, angle)
            if event.type == pg.MOUSEMOTION:
                coord = event.pos
                angle = atan2((event.pos[1] - gun.rect.y), (event.pos[0] - gun.rect.x))
                gun.angle = angle
        if player.live:
            if len(spawn_bul) < 2:
                for _ in range(2 - len(spawn_bul)):
                    SpawnBullet(randint(0, 800,), randint(0, 400))
            if len(enemy_sprite) < randint(1, 3):
                EnemyFall(randint(1, 799), -EnemyFall.image.get_height() - randint(10, 400))
        f = pg.font.Font(None, 60)
        text_bul = f.render(f'{round(player.bullets, 2)}', True, (0, 240, 240))
        screen.blit(text_bul, (10, 10))
        f = pg.font.Font(None, 260)
        text_score = f.render(f'{round(player.score, 2)}', True, (150, 150, 150))
        screen.blit(text_score, (380, 200))
        player_sprite.draw(screen)
        enemy_sprite.draw(screen)
        bullet_sprite.draw(screen)
        spawn_bul.draw(screen)
        if player.live:
            player_sprite.update()
            enemy_sprite.update()
            bullet_sprite.update()
        if coord and pg.mouse.get_focused():
            screen.blit(arrow, (coord[0] - arrow.get_width() // 2, coord[1] - arrow.get_height() // 2))
        if not player.live:
            if count < 20:
                count += 1
            else:
                count = 0
                zap_record(player.score)
                new_game()
        pg.display.flip()
        clock.tick(30)
    player_sprite.empty()
    enemy_sprite.empty()
    bullet_sprite.empty()
    spawn_bul.empty()
    pg.mouse.set_visible(True)
