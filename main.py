import base64
import sys

from Saper import *
from Gleid import *
from Survival import *
from FallGame import *
from RaceUnderRubble import *


def exit_scene():
    # Выход из pygame
    pg.quit()


class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.scene = None
        self.buttons = None
        self.buttons_size = (200, 60)
        self.rendering = True
        self.main_scene()
        self.count_easter = 0
        self.x = 800
        self.y = 600
        self.size = self.x, self.y
        self.first_menu = pg.image.load(os.path.join('data', 'first_main.jpg'))
        self.menu = pg.image.load(os.path.join('data', 'first_menu.jpg'))
        self.record_menu = pg.image.load(os.path.join('data', 'records.png'))
        self.game_menu = pg.image.load(os.path.join('data', 'game_select.png'))
        self.select_minesweeper = pg.image.load(os.path.join('data', 'minesweeper_difficulty_select.png'))
        self.names = {'Zombie_Survival': 'Zombie Survival',
                      'Super_hard': 'Сложный Сапёр',
                      'Saper_medium': 'Средний Сапёр',
                      'Saper_easy': 'Лёгкий Сапёр',
                      'Gleid': 'Gleid',
                      'spirte_fall': 'Spirte Fall',
                      'raceInWald': 'Опасная поездка'}

    def main_scene(self):
        # Главное меню
        self.buttons = [(300, 100, '        Играть'),
                        (300, 200, '       Рекорды'),
                        (300, 300, '        Выход')]
        self.buttons_size = (200, 60)
        self.scene = 'main'

    def play_scene(self):
        # Сцена выбора игры
        self.buttons = [(10, 500, 'Назад'),
                        (50, 50, 'Gleid'),
                        (300, 50, 'Minesweeper'),
                        (50, 200, 'Zombie Survival'),
                        (300, 200, 'Spirt Fall'),
                        (550, 50, 'easter'),
                        (300, 350, 'raceInWald')]
        self.buttons_size = (200, 100)
        self.scene = 'play'

    def record_scene(self):
        # Сцена рекордов игр
        self.buttons = [(10, 500, 'Назад')]
        self.buttons_size = (100, 50)
        self.scene = 'record'

    def scene_begin_minesweeper(self):
        # Сцена выбора сложности Сапёра
        self.buttons = [(10, 500, 'Назад'),
                        (300, 50, 'Новичок'),
                        (300, 200, 'Средний'),
                        (300, 350, 'Эксперт')]
        self.buttons_size = (200, 100)
        self.scene = 'begin_minesweeper'

    def gleid(self):
        # начало игры Gleid
        gleid_start()
        self.fix_screen()

    def minesweeper(self, x, y, bombs):
        # начало игры Сапёр
        saper_start(x, y, bombs)
        self.fix_screen()

    def zombie_game(self):
        # начало игры Zombie Survival
        zombie_start()
        self.fix_screen()

    def fall_game(self):
        # начало игры Spirt Fall
        fall_start()
        self.fix_screen()

    def race_in_wald(self):
        race_start()
        self.fix_screen()
        self.scene = 'play'

    def fix_screen(self):
        # возвращение размера окна в исходное состояние
        pg.display.set_mode(self.size)
        pg.display.set_caption('Меню')
        pg.display.flip()

    def render(self, screen):
        # отображение меню
        if self.scene == 'main':
            screen.blit(self.first_menu, (0, 0))
        elif self.scene == 'record':
            screen.blit(self.record_menu, (0, 0))
        elif self.scene == 'play':
            screen.blit(self.game_menu, (0, 0))
        elif self.scene == 'begin_minesweeper':
            screen.blit(self.select_minesweeper, (0, 0))
        if self.scene == 'record':
            db = sqlite3.connect('records.db')
            cur = db.cursor()
            sql1 = f"""select * from record"""
            recs = cur.execute(sql1).fetchall()
            h = 20
            for rec in recs:
                f = pg.font.Font(None, 60)
                text = f.render(f'{self.names[rec[0]]}', True,
                                (0, 228, 0))
                self.screen.blit(text, (140, h))
                text = f.render(f'{rec[1]}', True,
                                (0, 228, 0))
                self.screen.blit(text, (540, h))
                h += 80

    def easter_egg(self):
        # секретная пасхалка для команды 1 школы
        file_name_txt = os.path.join('data', 'img_s.txt')
        # расшифровка изображения из текстового файла
        with open(file_name_txt, 'rb') as f:
            img_data = base64.b64decode(f.read())
        # запись данных картинки в картинку
        with open('bs_s.jpg', 'wb') as f:
            f.write(img_data)
        # отображение картинки
        easter_image = pg.image.load('bs_s.jpg')
        self.screen.blit(easter_image, (0, 0))
        # удаление следов картинки, чтобы нельзя было найти её в файлах проекта
        os.remove('bs_s.jpg')
        # музыка для картинки
        music = pg.mixer.Sound(os.path.join('sound', 'easter_music.mp3'))
        # ...
        pg.display.set_caption('В перерывах между кодингом')
        pg.display.flip()
        music.play(-1)
        easter = True
        # возможность выйти из пасхалки
        while easter:
            for event_easter in pg.event.get():
                if event_easter.type == pg.QUIT:
                    easter = False
                if event_easter.type == pg.KEYDOWN:
                    easter = False
        music.stop()
        pg.display.set_caption('Меню')

    def click(self, mouse_pos):
        # Функция обработки нажатий кнопок
        for button in self.buttons:
            if ((button[0] <= mouse_pos[0] < button[0] + self.buttons_size[0]) and
                    (button[1] <= mouse_pos[1] < button[1] + self.buttons_size[1])):
                if 'Назад' in button[2]:
                    if self.scene == 'begin_minesweeper':
                        self.play_scene()
                    else:
                        self.main_scene()
                if self.scene == 'main':
                    if 'Играть' in button[2]:
                        self.play_scene()
                    elif 'Рекорды' in button[2]:
                        self.record_scene()
                    elif 'Выход' in button[2]:
                        exit_scene()
                elif self.scene == 'play':
                    if 'Minesweeper' in button[2]:
                        self.scene_begin_minesweeper()
                    elif 'Gleid' in button[2]:
                        self.gleid()
                    elif 'Zombie Survival' in button[2]:
                        self.zombie_game()
                    elif 'Spirt Fall' in button[2]:
                        self.fall_game()
                    elif 'easter' in button[2]:
                        self.count_easter += 1
                        if self.count_easter == 5:
                            self.easter_egg()
                            self.count_easter = 0
                    elif 'raceInWald' in button[2]:
                        self.race_in_wald()

                elif self.scene == 'begin_minesweeper':
                    x, y, bombs = 0, 0, 0
                    if 'Новичок' in button[2]:
                        x = 9
                        y = 9
                        bombs = 10
                    elif 'Средний' in button[2]:
                        x = 16
                        y = 16
                        bombs = 40
                    elif 'Эксперт' in button[2]:
                        x = 30
                        y = 16
                        bombs = 99
                    self.minesweeper(x, y, bombs)


def main():
    # Функция запуска приложения
    pg.mixer.pre_init(44100, -16, 4, 512)
    pg.init()

    size_menu = (800, 600)
    screen = pg.display.set_mode(size_menu)
    icon = pg.image.load(os.path.join('data', 'icon.png'))
    pg.display.set_icon(icon)
    menu = Menu(screen)
    clock_menu = pg.time.Clock()
    pg.display.set_caption('Меню')
    click = pg.mixer.Sound(os.path.join('sound', 'click.mp3'))

    running = True

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                running = False
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                click.play()
                menu.click(event.pos)

        menu.render(screen)
        pg.display.flip()
        clock_menu.tick(50)
    player_sprite_race.empty()
    col_sprites.empty()
    pg.display.quit()
    pg.quit()


if __name__ == '__main__':
    main()
