from imports import *


class Col(pg.sprite.Sprite):
    def __init__(self, x):
        super().__init__(col_sprites)
        self.image = pg.transform.scale(
            pg.image.load(choice([os.path.join('data', '1_wald-removebg-preview.png'),
                                  os.path.join('data', '2-wald-removebg-preview.png'),
                                  os.path.join('data', '3-wald-removebg-preview.png')])),
            (70, 100))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = 0
        self.rect.y -= 50
        self.mask = pg.mask.from_surface(self.image)

    def update(self):
        if self.rect.y >= race.height:  # убираем лишнее
            self.kill()
        else:  # движение
            self.rect.y += speed_col
            self.image = pg.transform.scale(self.image, (self.image.get_width() + 2, self.image.get_width() + 2))
            self.mask = pg.mask.from_surface(self.image)


class Player(pg.sprite.Sprite):  # игрок
    image = pg.transform.scale(pg.image.load(os.path.join('data', 'car.png')), (110, 75))

    def __init__(self):
        super().__init__(player_sprite_race)
        self.image = Player.image
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = race.height - self.image.get_height()
        self.speed = 5
        self.mask = pg.mask.from_surface(self.image)

    def move(self, step):
        if race.width - self.image.get_width() >= self.rect.x + step >= 0:
            self.rect.x += step

    def update(self):
        for enemy_mask in col_sprites:
            if pg.sprite.collide_mask(self, enemy_mask):  # столкновение
                if not race.end:
                    race.end = True
                    pg.mixer.Sound(os.path.join('sound', 'race_crash.mp3')).play(maxtime=800)


class Race:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.move = pg.USEREVENT + 1
        pg.time.set_timer(self.move, 10)
        self.new_tree = pg.USEREVENT + 2
        self.speed_tree_new = 1200
        pg.time.set_timer(self.new_tree, self.speed_tree_new)
        self.timer = pg.USEREVENT + 3
        pg.time.set_timer(self.timer, 100)
        self.end = False
        self.score = 0

    def render(self, screen):  # отображение очков
        f = pg.font.Font(None, 36)
        text = f.render(f'{self.score}', True,
                        (0, 0, 255))
        screen.blit(text, (10, 10))


def new_rec_race(score0):
    # Запись рекорда
    db = sqlite3.connect('records.db')
    cur = db.cursor()
    sql1 = f"""select rec from record where Game like '%raceInWald%'"""
    s = cur.execute(sql1).fetchone()[0]
    if int(score0) > int(s):
        sql = f"""update record set rec = {score0} where Game like '%raceInWald%'"""
        cur.execute(sql)
    db.commit()


def new_game():
    # перезапуск игры
    global score, col_sprites, player, player_sprite_race, race, speed_col, screen, clock, back_ground
    x0 = 600
    y0 = 400
    col_sprites = pg.sprite.Group()
    player_sprite_race = pg.sprite.Group()
    race = Race(x0, y0)
    player = Player()
    speed_col = 10
    clock = pg.time.Clock()
    back_ground = pg.transform.scale(pg.image.load(os.path.join('data', 'back_ground.jpg')),
                                     (race.width, race.height))


pg.init()
x0 = 600
y0 = 400
size = (x0, y0)
col_sprites = pg.sprite.Group()
player_sprite_race = pg.sprite.Group()
race = None
player = None
speed_col = 10
clock = pg.time.Clock()
back_ground = None


def race_start():
    global speed_col, race, player
    pg.display.set_caption('Зачем я решил срезать?')
    screen = pg.display.set_mode(size)
    race = Race(x0, y0)
    player = Player()
    race_prev = pg.image.load(os.path.join('prevs', 'race_img.png'))
    def race_pause():
        # Функция паузы
        pause = True
        screen.blit(race_prev, (0, 0))
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

    if race_pause():
        return
    running = True
    music_race = pg.mixer.Sound(os.path.join('sound', 'race_music.mp3'))
    new_game()
    music_flag = True
    music_race.play(-1)
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                running = False
            keys = pg.key.get_pressed()
            if not race.end:
                if event.type == race.new_tree:
                    Col((race.width * random() - player.rect.x // 4) % race.width)
                if event.type == race.timer:
                    race.score += 1
                if keys[pg.K_d]:
                    player.move(player.speed)
                if keys[pg.K_a]:
                    player.move(-player.speed)
            else:
                new_rec_race(race.score)
                if keys[pg.K_r]:
                    race.end = False
                    new_game()
            if event.type == pg.KEYDOWN and event.key == pg.K_TAB:
                pg.mixer.pause()
                if race_pause():
                    running = False
                else:
                    pg.mixer.unpause()
            if event.type == pg.KEYDOWN and event.key == pg.K_q:
                music_flag = not music_flag
                if music_flag:
                    music_race.set_volume(1)
                else:
                    music_race.set_volume(0)
        if race.score % 100 == 0 and race.score != 0:  # ускорение игры
            race.speed_tree_new = race.speed_tree_new - 50
            speed_col = round(speed_col * 1.10)
            pg.time.set_timer(race.new_tree, race.speed_tree_new)

        screen.fill((255, 255, 255))
        screen.blit(back_ground, (0, 0))
        race.render(screen)
        player_sprite_race.draw(screen)
        player_sprite_race.update()
        col_sprites.draw(screen)
        col_sprites.update()
        if race.end:
            f = pg.font.Font(None, 40)
            text = f.render(f"Вы проиграли! Нажмите R для новой игры.", True, (255, 255, 255))
            screen.blit(text, (10, 200))
        pg.display.flip()
        clock.tick(30)
    music_race.stop()