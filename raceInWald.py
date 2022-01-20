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

    def update(self):
        if pg.sprite.spritecollideany(self, player_sprite): # столкновение
            race.end = True
        elif self.rect.y >= race.height: # убираем лишнее
            self.kill()
        else: # движение
            self.rect.y += speed_col
            self.image = pg.transform.scale(self.image, (self.image.get_width() + 2, self.image.get_width() + 2))


class Player(pg.sprite.Sprite): # игрок
    image = pg.transform.scale(pg.image.load(os.path.join('data', 'car.png')), (110, 75))

    def __init__(self):
        super().__init__(player_sprite)
        self.image = Player.image
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = race.height - self.image.get_height()
        self.speed = 5

    def move(self, step):
        if self.rect.x + step <= race.width - self.image.get_width() and self.rect.x + step >= 0:
            self.rect.x += step


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

    def render(self, screen): # отображение очков
        f = pg.font.Font(None, 36)
        text = f.render(f'{self.score}', True,
                        (0, 0, 255))
        screen.blit(text, (10, 10))

def new_rec(score0):
    # Запись рекорда
    db = sqlite3.connect('records.db')
    cur = db.cursor()
    sql1 = f"""select rec from record where Game like '%raceInWald%'"""
    s = cur.execute(sql1).fetchone()[0]
    if score0 > s:
        sql = f"""update record set rec = {score0} where Game like '%raceInWald%'"""
        cur.execute(sql)
    db.commit()

def new_game():
    # перезапуск игры
    global score, rec_zap, col_sprites, player, player_sprite, race, speed_col, screen, clock, back_ground
    x = 600
    y = 400
    size = (x, y)
    col_sprites = pg.sprite.Group()
    player_sprite = pg.sprite.Group()
    race = Race(x, y)
    player = Player()
    speed_col = 10
    screen = pg.display.set_mode(size)
    clock = pg.time.Clock()
    pg.display.set_caption('Зачем я решил срезать?')
    back_ground = pg.transform.scale(pg.image.load(os.path.join('data', 'back_ground.jpg')),
                                     (race.width, race.height))


pg.init()
x = 600
y = 400
size = (x, y)
col_sprites = pg.sprite.Group()
player_sprite = pg.sprite.Group()
race = Race(x, y)
player = Player()
speed_col = 10
screen = pg.display.set_mode(size)
clock = pg.time.Clock()
pg.display.set_caption('Зачем я решил срезать?')
back_ground = None


def race_start():
    global speed_col
    running = True
    new_game()
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
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
                new_rec(race.score)
                f = pg.font.Font(None, 50)
                text = f.render(f"Вы проиграли! Нажмите R для новой игры.", True, (255, 0, 0))
                screen.blit(text, (10, 200))
                if keys[pg.K_r]:
                    race.end = False
                    new_game()
        if race.score % 100 == 0 and race.score != 0: # ускорение игры
            race.speed_tree_new = race.speed_tree_new - 50
            speed_col = round(speed_col * 1.10)
            pg.time.set_timer(race.new_tree, race.speed_tree_new)

        screen.fill((255, 255, 255))
        screen.blit(back_ground, (0, 0))
        race.render(screen)
        player_sprite.draw(screen)
        col_sprites.draw(screen)
        col_sprites.update()
        pg.display.flip()
        clock.tick(30)
