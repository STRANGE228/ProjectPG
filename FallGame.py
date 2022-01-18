from imports import *

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
            pg.mixer.Sound(os.path.join('sound', 'fallgame_ammo.mp3')).play()
            self.bullets += 1
            self.score += 1
        if pg.sprite.spritecollideany(self, enemy_sprite):
            pg.mixer.Sound(os.path.join('sound', 'fallgame_dead.wav')).play()
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
    screen = pg.display.set_mode((800, 600), pg.FULLSCREEN)
    clock = pg.time.Clock()
    running = True
    arrow = pg.image.load(os.path.join('data', 'arrow.png'))
    player, gun = None, None
    music_fallgame = pg.mixer.Sound(os.path.join('sound', 'fallgame_music.mp3'))
    fallgame_prev = pg.image.load(os.path.join('prevs', 'spirte_fall_img.png'))

    def fallgame_clear():
        player_sprite.empty()
        enemy_sprite.empty()
        bullet_sprite.empty()
        spawn_bul.empty()
        pg.mouse.set_visible(True)
        music_fallgame.stop()

    def fallgame_pause():
        pause = True
        screen.blit(fallgame_prev, (0, 0))
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

    if fallgame_pause():
        fallgame_clear()
        return

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
    music_fallgame.play(-1)
    pg.mouse.set_visible(False)
    music_flag = True
    while running:
        screen.fill((240, 250, 240))
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
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
                        pg.mixer.Sound(os.path.join('sound', 'fallgame_shot.wav')).play(maxtime=500)
            if event.type == pg.MOUSEMOTION:
                coord = event.pos
                angle = atan2((event.pos[1] - gun.rect.y), (event.pos[0] - gun.rect.x))
                gun.angle = angle
            if event.type == pg.KEYDOWN and event.key == pg.K_TAB:
                music_fallgame.stop()
                if fallgame_pause():
                    running = False
                else:
                    music_fallgame.play(-1)
            if event.type == pg.KEYDOWN and event.key == pg.K_q:
                music_flag = not music_flag
                if music_flag:
                    music_fallgame.set_volume(1)
                else:
                    music_fallgame.set_volume(0)
        if player.live:
            if len(spawn_bul) < 2:
                for _ in range(2 - len(spawn_bul)):
                    SpawnBullet(randint(0, 800,), randint(100, 400))
            if len(enemy_sprite) < 3:
                EnemyFall(randint(20, 779), -EnemyFall.image.get_height() - randint(10, 400))
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
    fallgame_clear()
