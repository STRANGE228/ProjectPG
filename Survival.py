from imports import *

enemies = pg.sprite.Group()
walls = pg.sprite.Group()
player_soldier = pg.sprite.Group()
bullets = pg.sprite.Group()
death = pg.sprite.Group()
score = 0
wins = 0
rec_zap = False


def create_map(x0, y0):
    # создание карты
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
        # добавление стен по краям, которые не ломаются
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


def new_rec(score0):
    # Запись рекорда
    db = sqlite3.connect('records.db')
    cur = db.cursor()
    sql1 = f"""select rec from record where Game like '%Survival%'"""
    s = cur.execute(sql1).fetchone()[0]
    if score0 > s:
        sql = f"""update record set rec = {score0} where Game like '%Survival%'"""
        cur.execute(sql)
    db.commit()


class Wall(pg.sprite.Sprite):
    image = pg.image.load(os.path.join('data', 'brick_z.png'))

    def __init__(self, x, y):
        super(Wall, self).__init__(walls)
        self.image = Wall.image
        self.rect = self.image.get_rect()
        self.rect.x = x * 70
        self.rect.y = y * 70


class Player(pg.sprite.Sprite):
    image0 = pg.image.load(os.path.join('data', 'soldier0.png'))
    image1 = pg.image.load(os.path.join('data', 'soldier1.png'))
    image_dead = pg.image.load(os.path.join('data', 'soldier_dead.png'))

    def __init__(self, x, y):
        super(Player, self).__init__(player_soldier)
        self.image = Player.image0
        self.rect = self.image.get_rect()
        self.rect.x = (x // 2) * 70
        self.rect.y = (y - 3) * 70
        self.speed = 4
        self.last_d = 1
        self.live = True
        self.reload = 10
        self.count = 0
        self.img = 1
        self.dead = pg.mixer.Sound(os.path.join('sound', 'survival_player_dead.mp3'))

    def move(self, d):
        if self.live:
            self.count += 1
            if self.count == 5:
                if self.img == 1:
                    self.image = Player.image1
                    self.img = 2
                else:
                    self.image = Player.image0
                    self.img = 1
                self.povorot(self.last_d)
                self.count = 0

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

    def povorot(self, d):
        # поворот картинки игрока при изменение направления движения
        if self.live:
            self.last_d = d
            if self.img == 1:
                image = Player.image0
            else:
                image = Player.image1
            if d == 1:
                self.image = image
            if d == 3:
                self.image = pg.transform.flip(image, False, True)
            if d == 2:
                self.image = pg.transform.rotate(image, -90)
            if d == 4:
                self.image = pg.transform.rotate(image, 90)

    def update(self):
        self.reload += 1
        if pg.sprite.spritecollideany(self, enemies):
            if self.live:
                self.dead.play(maxtime=500)
                if self.last_d == 1:
                    self.image = Player.image_dead
                elif self.last_d == 3:
                    self.image = pg.transform.flip(Player.image_dead, False, True)
                elif self.last_d == 2:
                    self.image = pg.transform.rotate(Player.image_dead, 90)
                else:
                    self.image = pg.transform.rotate(Player.image_dead, 90)
                self.live = False


class Enemy(pg.sprite.Sprite):
    image = pg.image.load(os.path.join('data', 'zombie0.png'))

    def __init__(self, x, y):
        super(Enemy, self).__init__(enemies)
        self.image = Enemy.image
        self.rect = self.image.get_rect()
        self.rect.x = x * 70
        self.rect.y = y * 70
        self.live = True
        self.d = 0
        self.count = 0

    def update(self):
        if self.live:
            # Выбор направления движения противников
            if self.count <= 0:
                self.count = randrange(10, 100)
                ds = []
                self.rect.y -= 2
                if not (pg.sprite.spritecollideany(self, walls)):
                    ds.append(1)
                self.rect.y += 5
                if not (pg.sprite.spritecollideany(self, walls)):
                    ds.append(3)
                self.rect.y -= 3
                self.rect.x += 3
                if not (pg.sprite.spritecollideany(self, walls)):
                    ds.append(2)
                self.rect.x -= 5
                if not (pg.sprite.spritecollideany(self, walls)):
                    ds.append(4)
                self.rect.x += 2
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
                self.rect.y -= 2
                if pg.sprite.spritecollideany(self, walls):
                    self.rect.y += 2
                    self.count = 0
            if self.d == 3:
                self.rect.y += 2
                if pg.sprite.spritecollideany(self, walls):
                    self.rect.y -= 2
                    self.count = 0
            if self.d == 2:
                self.rect.x += 2
                if pg.sprite.spritecollideany(self, walls):
                    self.rect.x -= 2
                    self.count = 0
            if self.d == 4:
                self.rect.x -= 2
                if pg.sprite.spritecollideany(self, walls):
                    self.rect.x += 2
                    self.count = 0
            self.count -= 1


class DeadZombie(pg.sprite.Sprite):
    image = pg.image.load(os.path.join('data', 'zombie_dead.png'))

    def __init__(self, x, y, d):
        super(DeadZombie, self).__init__(death)
        if d == 1:
            self.image = DeadZombie.image
        elif d == 3:
            self.image = pg.transform.flip(DeadZombie.image, False, True)
        elif d == 2:
            self.image = pg.transform.rotate(DeadZombie.image, 90)
        else:
            self.image = pg.transform.rotate(DeadZombie.image, 90)
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
            self.rect.x = x + 16
            self.rect.y = y - 6 + (d // 2) * 35
        else:
            self.rect.x = x + 35 - (d // 4) * 42
            self.rect.y = y + 16
        self.d = d

    def update(self):
        if self.d == 1:
            self.rect.y -= 6
        elif self.d == 3:
            self.rect.y += 6
        elif self.d == 2:
            self.rect.x += 6
        elif self.d == 4:
            self.rect.x -= 6
        if wall := pg.sprite.spritecollideany(self, walls):
            if not (((wall.rect.x / 70) and (wall.rect.y / 70 == 0)) or (
                    (wall.rect.x / 70 == 0) and (wall.rect.y / 70)) or
                    ((wall.rect.x / 70) and (wall.rect.y / 70 == 10)) or (
                            (wall.rect.x / 70 == 10) and (wall.rect.y / 70))):
                walls.remove(wall)
                pg.mixer.Sound(os.path.join('sound', 'survival_crash_wall.wav')).play()
            self.kill()
        elif z := pg.sprite.spritecollideany(self, enemies):
            DeadZombie(z.rect.x, z.rect.y, z.d)
            pg.mixer.Sound(os.path.join('sound', 'survival_zombie_dead.wav')).play(maxtime=500)
            z.kill()
            self.kill()


def new_game(wins0, player, score0):
    # перезапуск игры
    global score, rec_zap
    enemies.empty()
    walls.empty()
    death.empty()
    x = 11
    y = 11
    score = score0
    rec_zap = False
    player.image = Player.image0
    player.img = 1
    player.count = 0
    player.rect.x = (x // 2) * 70
    player.rect.y = (y - 3) * 70
    walls_pos, free_cell = create_map(x, y)
    for wall in walls_pos:
        Wall(*wall)
    cells = choices(free_cell, k=(min((x - 2) * (y - 2) // 8 + wins0 * 3, len(free_cell) - 4)))
    for enemy in cells:
        Enemy(*enemy)


def zombie_start():
    # начало игры
    global score, rec_zap
    x = 11
    y = 11
    size = (x * 70, y * 70)
    screen = pg.display.set_mode(size)
    clock = pg.time.Clock()
    pg.display.set_caption('Мега Супер Пупер Выживание Против Зомби Насмерть 18+')
    zombie_prev = pg.image.load(os.path.join('prevs', 'survival_img.png'))
    shot_survival = pg.mixer.Sound(os.path.join('sound', 'survival_shot.mp3'))
    music_survival = pg.mixer.Sound(os.path.join('sound', 'survival_music.mp3'))

    def clear_z():
        # отчистка групп спрайтов
        global enemies, walls, death, player_soldier, bullets
        enemies.empty()
        walls.empty()
        death.empty()
        player_soldier.empty()
        bullets.empty()
        music_survival.stop()

    def zombie_pause():
        # пауза
        pause = True
        screen.blit(zombie_prev, (0, 0))
        pg.display.flip()
        while pause:
            for event_p in pg.event.get():
                if event_p.type == pg.QUIT:
                    return True
                if event_p.type == pg.KEYDOWN:
                    if event_p.key == pg.K_ESCAPE:
                        return True
                    else:
                        pause = False
                if event_p.type == pg.MOUSEBUTTONDOWN:
                    pause = False

    if zombie_pause():
        clear_z()
        return

    walls_pos, free_cell = create_map(x, y)
    for wall in walls_pos:
        Wall(*wall)
    player = Player(x, y)
    cells = choices(free_cell, k=((x - 2) * (y - 2) // 8))
    for enemy in cells:
        Enemy(*enemy)
    score = 0
    wins1 = 0
    rec_zap = False
    running = True
    music_flag = True
    pg.key.set_repeat(200, 20)
    music_survival.play(-1)
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_s:
                    player.move(3)
                    player.povorot(3)
                if event.key == pg.K_w:
                    player.move(1)
                    player.povorot(1)
                if event.key == pg.K_d:
                    player.move(2)
                    player.povorot(2)
                if event.key == pg.K_a:
                    player.move(4)
                    player.povorot(4)
                if event.key == pg.K_SPACE:
                    if player.reload >= 40 and player.live:
                        Bullet(player.rect.x, player.rect.y, player.last_d)
                        player.reload = 0
                        shot_survival.play()
                if event.key == pg.K_r:
                    player.live = True
                    new_game(0, player, 0)
                    wins1 = 0
                if event.key == pg.K_TAB:
                    pg.mixer.pause()
                    if zombie_pause():
                        running = False
                    else:
                        pg.mixer.unpause()
                if event.key == pg.K_q:
                    music_flag = not music_flag
                    if music_flag:
                        music_survival.set_volume(1)
                    else:
                        music_survival.set_volume(0)

        if not player.live:
            if not rec_zap:
                rec_zap = True
                new_rec(score)

        if len(enemies) == 0:
            # переход на следуйщий уровень
            wins1 += 1
            score += len(death)
            new_game(wins1, player, score)
        screen.fill((0, 0, 0))
        death.draw(screen)
        death.update()
        player_soldier.draw(screen)
        player_soldier.update()
        walls.draw(screen)
        walls.update()
        enemies.draw(screen)
        enemies.update()
        bullets.draw(screen)
        bullets.update()
        f = pg.font.Font(None, 60)
        text_score = f.render(f'{score + len(death)}', True,
                              (0, 240, 240))
        screen.blit(text_score, (5, 5))
        if not player.live:
            f = pg.font.Font(None, 50)
            text = f.render(f"Вы проиграли! Нажмите R для новой игры.", True, (255, 0, 0))
            screen.blit(text, (10, 200))
        pg.display.flip()
        clock.tick(50)
    clear_z()
