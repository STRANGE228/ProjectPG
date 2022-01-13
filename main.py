from random import random

from Saper import *
from Gleid import *
from Survival import *
from FallGame import *

import pygame as pg


class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.scene = None
        self.rendering = True
        self.main_scene()
        self.x = 800
        self.y = 600
        self.size = self.x, self.y
        self.first_screen = pg.image.load(os.path.join('data', 'first_menu.jpg'))

    def main_scene(self):
        self.buttons = [(300, 100, '        Играть'),
                        (300, 200, '       Рекорды'),
                        (300, 300, '        Выход')]
        self.buttons_size = (200, 60)
        self.scene = 'main'

    def play_scene(self):
        self.buttons = [(10, 500, 'Назад'),
                        (50, 50, 'Gleid'),
                        (300, 50, 'Minesweeper'),
                        #(550, 50, 'Race in Wald'),
                        (50, 200, 'Zombie Survival'),
                        (300, 200, 'Spirt Fall')]
        self.buttons_size = (200, 100)
        self.scene = 'play'

    def record_scene(self):
        self.buttons = [(10, 500, 'Назад')]
        self.buttons_size = (100, 50)
        self.scene = 'record'

    def scene_begin_minesweeper(self):
        self.buttons = [(10, 500, 'Назад'),
                        (300, 50, 'Новичок'),
                        (300, 200, 'Средний'),
                        (300, 350, 'Эксперт')]
        self.buttons_size = (200, 100)
        self.scene = 'begin_minesweeper'

    def scene_raceInWald(self):
        self.scene = 'race_in_wald'

    def gleid(self):
        gleid_start()
        self.fix_screen()

    def race(self):
        pass
        self.play_scene()
        self.fix_screen()

    def minesweeper(self, x, y, bombs):
        saper_start(x, y, bombs)
        self.fix_screen()

    def zombie_game(self):
        zombie_start()
        self.fix_screen()

    def fall_game(self):
        fall_start()
        self.fix_screen()

    def exit_scene(self):
        pg.quit()
        exit(0)

    def fix_screen(self):
        pg.display.set_mode(self.size)
        pg.display.set_caption('Меню')
        pg.display.flip()


    def render(self, screen):
        if self.scene == 'main' or self.scene == 'record' or self.scene == 'play':
            screen.blit(self.first_screen, (0, 0))
        for button in self.buttons:
            pg.draw.rect(screen, (0, 200, 0), (button[0], button[1], self.buttons_size[0], self.buttons_size[1]))
            f = pg.font.Font(None, 36)
            text = f.render(f'{button[2]}', True,
                            (0, 0, 200))
            screen.blit(text, (button[0], button[1]))
        if self.scene == 'record':
            db = sqlite3.connect('records.db')
            cur = db.cursor()
            sql1 = f"""select * from record"""
            recs = cur.execute(sql1).fetchall()
            h = 20
            for rec in recs:
                f = pg.font.Font(None, 60)
                text = f.render(f'{rec[0]}', True,
                                (200, 0, 0))
                self.screen.blit(text, (140, h))
                text = f.render(f'{rec[1]}', True,
                                (200, 0, 0))
                self.screen.blit(text, (540, h))
                h += 80

    def click(self, mouse_pos):
        for button in self.buttons:
            if ((button[0] <= mouse_pos[0] < button[0] + self.buttons_size[0]) and
                    (button[1] <= mouse_pos[1] < button[1] + self.buttons_size[1])):
                if 'Назад' in button[2]:
                    self.main_scene()
                if self.scene == 'main':
                    if 'Играть' in button[2]:
                        self.play_scene()
                    elif 'Рекорды' in button[2]:
                        self.record_scene()
                    elif 'Выход' in button[2]:
                        self.exit_scene()
                elif self.scene == 'record':
                    if 'Назад' in button[2]:
                        self.main_scene()
                elif self.scene == 'play':
                    if 'Minesweeper' in button[2]:
                        self.scene_begin_minesweeper()
                    elif 'Race in Wald' in button[2]:
                        self.scene_raceInWald()
                        self.race()
                    elif 'Gleid' in button[2]:
                        self.gleid()
                    elif 'Zombie Survival' in button[2]:
                        self.zombie_game()
                    elif 'Spirt Fall' in button[2]:
                        self.fall_game()

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
    pg.init()
    size = (800, 600)
    screen = pg.display.set_mode(size)
    menu = Menu(screen)

    clock = pg.time.Clock()
    pg.display.set_caption('Меню')

    running = True

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                menu.click(event.pos)

        #screen.fill((200, 0, 200))
        menu.render(screen)
        pg.display.flip()
        clock.tick(50)
    pg.quit()


if __name__ == '__main__':
    main()



