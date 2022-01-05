import os
import sqlite3

import pygame as pg
from random import choices, choice, randrange

pg.init()
enemies = pg.sprite.Group()
walls = pg.sprite.Group()
player_soldier = pg.sprite.Group()
bullets = pg.sprite.Group()
death = pg.sprite.Group()
score = 0
wins = 0
rec_zap = False


def create_map(x0, y0):
    coords = ([(x, y) for y in range(1, y0) for x in range(1, x0)])
    walls_map = []
    for i in range(-1, 2):
        for j in range(-1, 2):
            if j == -1:
                walls_map.append((x0 // 2 + i, y0 - 3 + j))
            elif j == 0 and i != 0:
                walls_map.append((x0 // 2 + i, y0 - 3 + j))
            else:
                coords.remove((x0 // 2 + i, y0 - 3 + j))
    for i in range(0, 11):
        walls_map.append((0, i))
        walls_map.append((i, 0))
        walls_map.append((10, i))
        walls_map.append((i, 10))
    wall = choices(coords, k=((x0 - 2) * (y0 - 2) // 3))
    walls_map.extend(wall)
    for w in walls_map:
        if w in coords:
            coords.remove(w)
    return walls_map, coords


def new_rec(score):
    db = sqlite3.connect('records.db')
    cur = db.cursor()
    sql1 = f"""select rec from record where Game like '%Survival%'"""
    s = cur.execute(sql1).fetchone()[0]
    if score > s:
        sql = f"""update record set rec = {score} where Game like '%Survival%'"""
        cur.execute(sql)
    db.commit()


class Wall(pg.sprite.Sprite):
    image = pg.image.load(os.path.join('data', 'brick.png'))

    def __init__(self, x, y):
        super(Wall, self).__init__(walls)
        self.image = Wall.image
        self.rect = self.image.get_rect()
        self.rect.x = x * 30
        self.rect.y = y * 30


class Player(pg.sprite.Sprite):
    image = pg.image.load(os.path.join('data', 'soldier1.png'))

    def __init__(self, x, y):
        super(Player, self).__init__(player_soldier)
        self.image = Player.image
        self.rect = self.image.get_rect()
        self.rect.x = (x // 2) * 30
        self.rect.y = (y - 3) * 30
        self.speed = 3
        self.last_d = 1
        self.live = True
        self.reload = 10

    def move(self, d):
        if self.live:
            if d == 1:
                self.rect.y -= self.speed
                if pg.sprite.spritecollideany(self, walls):
                    self.rect.y += self.speed
            if d == 3:
                self.rect.y += self.speed
                if pg.sprite.spritecollideany(self, walls):
                    self.rect.y -= self.speed
            if d == 2:
                self.rect.x += self.speed
                if pg.sprite.spritecollideany(self, walls):
                    self.rect.x -= self.speed
            if d == 4:
                self.rect.x -= self.speed
                if pg.sprite.spritecollideany(self, walls):
                    self.rect.x += self.speed
            if pg.sprite.spritecollideany(self, enemies):
                self.live = False

    def povorot(self, d):
        if self.live:
            self.last_d = d
            if d == 1:
                self.image = Player.image
            if d == 3:
                self.image = pg.transform.flip(Player.image, False, True)
            if d == 2:
                self.image = pg.transform.rotate(Player.image, -90)
            if d == 4:
                self.image = pg.transform.rotate(Player.image, 90)

    def update(self):
        self.reload += 1


class Enemy(pg.sprite.Sprite):
    image = pg.image.load(os.path.join('data', 'zombie1.png'))

    def __init__(self, x, y):
        super(Enemy, self).__init__(enemies)
        self.image = Enemy.image
        self.rect = self.image.get_rect()
        self.rect.x = x * 30
        self.rect.y = y * 30
        self.live = True
        self.d = 0
        self.count = 0

    def update(self):
        if self.live:
            if self.count <= 0:
                self.count = randrange(10, 100)
                ds = []
                self.rect.y -= 1
                if not (pg.sprite.spritecollideany(self, walls)):
                    ds.append(1)
                self.rect.y += 3
                if not (pg.sprite.spritecollideany(self, walls)):
                    ds.append(3)
                self.rect.y -= 2
                self.rect.x += 2
                if not (pg.sprite.spritecollideany(self, walls)):
                    ds.append(2)
                self.rect.x -= 3
                if not (pg.sprite.spritecollideany(self, walls)):
                    ds.append(4)
                self.rect.x += 1
                if ds:
                    self.d = choice(ds)
                    if self.d == 1:
                        self.image = Enemy.image
                    if self.d == 3:
                        self.image = pg.transform.flip(Enemy.image, False, True)
                    if self.d == 2:
                        self.image = pg.transform.rotate(Enemy.image, -90)
                    if self.d == 4:
                        self.image = pg.transform.rotate(Enemy.image, 90)
                else:
                    self.d = 0
            if self.d == 1:
                self.rect.y -= 1
                if pg.sprite.spritecollideany(self, walls):
                    self.rect.y += 1
                    self.count = 0
            if self.d == 3:
                self.rect.y += 1
                if pg.sprite.spritecollideany(self, walls):
                    self.rect.y -= 1
                    self.count = 0
            if self.d == 2:
                self.rect.x += 1
                if pg.sprite.spritecollideany(self, walls):
                    self.rect.x -= 1
                    self.count = 0
            if self.d == 4:
                self.rect.x -= 1
                if pg.sprite.spritecollideany(self, walls):
                    self.rect.x += 1
                    self.count = 0
            self.count -= 1


class DeadZombie(pg.sprite.Sprite):
    image = pg.image.load(os.path.join('data', 'zombie_dead.png'))

    def __init__(self, x, y):
        super(DeadZombie, self).__init__(death)
        self.image = DeadZombie.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Bullet(pg.sprite.Sprite):
    image = pg.image.load(os.path.join('data', 'bullet.png'))

    def __init__(self, x, y, d):
        super(Bullet, self).__init__(bullets)
        if d == 1:
            self.image = Bullet.image
        if d == 3:
            self.image = pg.transform.flip(Bullet.image, False, True)
        if d == 2:
            self.image = pg.transform.rotate(Bullet.image, -90)
        if d == 4:
            self.image = pg.transform.rotate(Bullet.image, 90)
        self.rect = self.image.get_rect()
        if d % 2:
            self.rect.x = x + 6
            self.rect.y = y - 9 + (d // 2) * 25
        else:
            self.rect.x = x + 16 - (d // 4) * 30
            self.rect.y = y + 6
        self.d = d

    def update(self):
        if self.d == 1:
            self.rect.y -= 3
        elif self.d == 3:
            self.rect.y += 3
        elif self.d == 2:
            self.rect.x += 3
        elif self.d == 4:
            self.rect.x -= 3
        if wall := pg.sprite.spritecollideany(self, walls):
            if not (((wall.rect.x / 30) and (wall.rect.y / 30 == 0)) or (
                    (wall.rect.x / 30 == 0) and (wall.rect.y / 30)) or
                    ((wall.rect.x / 30) and (wall.rect.y / 30 == 10)) or (
                            (wall.rect.x / 30 == 10) and (wall.rect.y / 30))):
                walls.remove(wall)
            self.kill()
        elif z := pg.sprite.spritecollideany(self, enemies):
            z.kill()
            DeadZombie(z.rect.x, z.rect.y)
            self.kill()


def new_game(wins, player):
    global score, rec_zap
    enemies.empty()
    walls.empty()
    death.empty()
    x = 11
    y = 11
    score = 0
    rec_zap = False
    player.rect.x = (x // 2) * 30
    player.rect.y = (y - 3) * 30
    pg.display.set_caption('Мега Супер Пупер Выживание Против Зомби Насмерть 18+')
    walls_pos, free_cell = create_map(x, y)
    for wall in walls_pos:
        Wall(*wall)
    cells = choices(free_cell, k=(min((x - 2) * (y - 2) // 8 + wins * 3, len(free_cell) - 4)))
    for enemy in cells:
        Enemy(*enemy)


def zombie_start():
    global score, rec_zap
    pg.init()
    x = 11
    y = 11
    size = (x * 30, y * 30)
    screen = pg.display.set_mode(size)
    clock = pg.time.Clock()
    pg.display.set_caption('Мега Супер Пупер Выживание Против Зомби Насмерть 18+')
    walls_pos, free_cell = create_map(x, y)
    for wall in walls_pos:
        Wall(*wall)
    player = Player(x, y)
    cells = choices(free_cell, k=((x - 2) * (y - 2) // 8))
    for enemy in cells:
        Enemy(*enemy)
    score = 0
    wins = 0
    rec_zap = False
    running = True
    pg.key.set_repeat(200, 60)

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_DOWN:
                    player.move(3)
                    player.povorot(3)
                if event.key == pg.K_UP:
                    player.move(1)
                    player.povorot(1)
                if event.key == pg.K_RIGHT:
                    player.move(2)
                    player.povorot(2)
                if event.key == pg.K_LEFT:
                    player.move(4)
                    player.povorot(4)
            if event.type == pg.MOUSEBUTTONDOWN or (event.type == pg.KEYDOWN and event.key == pg.K_SPACE):
                if player.reload >= 20:
                    if player.live:
                        Bullet(player.rect.x, player.rect.y, player.last_d)
                        player.reload = 0
            if event.type == pg.KEYDOWN and event.key == pg.K_r:
                player.live = True
                new_game(0, player)
                wins = 0
        if not player.live:
            if not rec_zap:
                rec_zap = True
                new_rec(score)

        if len(enemies) == 0:
            wins += 1
            score += len(death)
            new_game(wins, player)
        screen.fill((0, 0, 0))
        death.draw(screen)
        death.update()
        walls.draw(screen)
        walls.update()
        enemies.draw(screen)
        enemies.update()
        player_soldier.draw(screen)
        player_soldier.update()
        bullets.draw(screen)
        bullets.update()
        f = pg.font.Font(None, 20)
        text_score = f.render(f'{score + len(death)}', True,
                              (0, 240, 240))
        screen.blit(text_score, (5, 5))
        if not player.live:
            f = pg.font.Font(None, 20)
            text_score = f.render(f"Вы проиграли! Нажмите R для новой игры.", True,
                                  (255, 0, 0))
            screen.blit(text_score, (20, 100))
        pg.display.flip()
        clock.tick(50)
    enemies.empty()
    walls.empty()
    death.empty()
    player_soldier.empty()
    bullets.empty()
