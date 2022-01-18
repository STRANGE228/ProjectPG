from imports import *


class Board:
    def __init__(self, width, height, left=10, top=10, cell_size=30):
        self.width = width
        self.height = height
        self.board = [[-1] * width for _ in range(height)]
        self.left = 0
        self.top = 0
        self.cell_size = 0
        self.set_view(left, top, cell_size)

    def render(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                pg.draw.rect(screen, pg.Color(255, 255, 255),
                             (x * self.cell_size + self.left, y * self.cell_size + self.top,
                              self.cell_size,
                              self.cell_size), 1)

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def on_click(self, cell):
        pass

    def get_cell(self, mouse_pos):
        cell_x = (mouse_pos[0] - self.left) // self.cell_size
        cell_y = (mouse_pos[1] - self.top) // self.cell_size
        if cell_x < 0 or cell_x >= self.width or cell_y < 0 or cell_y >= self.height:
            return None
        return cell_x, cell_y

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell:
            self.on_click(cell)


class Minesweeper(Board):
    def __init__(self, x, y, bombs, screen):
        super(Minesweeper, self).__init__(x, y, 20, 60, 30)
        self.bombs = bombs
        self.timer = pg.USEREVENT + 1
        pg.time.set_timer(self.timer, 1000)
        self.music_saper = pg.mixer.Sound(os.path.join('sound', 'saper_music.mp3'))
        self.boom = pg.mixer.Sound(os.path.join('sound', 'saper_boom.mp3'))
        self.win = pg.mixer.Sound(os.path.join('sound', 'saper_win.mp3'))
        self.end = False
        self.status_end = None
        self.first_step = None
        self.flags = None
        self.count = None
        self.time = None
        self.new_game(screen)

    def render(self, screen):
        super(Minesweeper, self).render(screen)
        f = pg.font.Font(None, 36)
        for col in range(self.width):
            for row in range(self.height):
                if self.board[col][row] == -10:
                    if self.end:
                        pg.draw.rect(screen, (255, 0, 0), (self.left + col * self.cell_size + 1,
                                                           self.top + row * self.cell_size + 1,
                                                           self.cell_size - 2, self.cell_size - 2))
                elif self.board[col][row] != -1:
                    text = f.render(f'{self.board[col][row]}', True,
                                    (0, 255, 0))
                    screen.blit(text, (self.left + col * self.cell_size + 1,
                                       self.top + row * self.cell_size + 1))
        for pos in self.flags:
            if self.board[pos[0]][pos[1]] != -10 and self.board[pos[0]][pos[1]] != -1:
                self.flags.remove(pos)
                continue
            text = f.render('F', True,
                            (0, 0, 255))
            screen.blit(text, (self.left + pos[0] * self.cell_size + 1,
                               self.top + pos[1] * self.cell_size + 1))

        f = pg.font.Font(None, 25)
        text_open = f.render(f'Открыто {self.count}/{self.width * self.height - self.bombs}', True,
                             (0, 240, 240))
        screen.blit(text_open, (self.left // 2, 10))

        text_time = f.render(f'Время: {self.time // 60}:{self.time % 60}', True,
                             (0, 240, 240))
        screen.blit(text_time, (self.left * 9.5, 10))
        if self.end:
            if self.status_end == 'lose':
                text_end = 'Вы проиграли! Нажмите R для новой игры.'
            else:
                text_end = 'Вы выйграли! Нажмите R для новой игры.'
            f = pg.font.Font(None, 20)
            text_open = f.render(f'{text_end}', True,
                                 (0, 240, 240))
            screen.blit(text_open, (self.width // 2 * (self.width - 9) + 10, 30))

    def open_cell(self, cell):
        if self.board[cell[0]][cell[1]] == -1:
            if cell in self.flags:
                self.flags.remove(cell)
            summa = 0
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if 0 <= (cell[0] + dx) < self.width and 0 <= (cell[1] + dy) < self.height:
                        if dx == 0 and dy == 0:
                            continue
                        if self.board[cell[0] + dx][cell[1] + dy] == -10:
                            summa += 1
            self.board[cell[0]][cell[1]] = summa
            if summa == 0:
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        if 0 <= (cell[0] + dx) < self.width and 0 <= (cell[1] + dy) < self.height:
                            if dx == 0 and dy == 0:
                                continue
                            self.open_cell((cell[0] + dx, cell[1] + dy))
            sp = [1 if self.board[x][y] == -1 else 0 for y in range(self.height) for x in range(self.width)]
            self.count = self.width * self.height - self.bombs - sum(sp)
            if self.count == self.width * self.height - self.bombs:
                self.end = True
                self.status_end = 'win'
                self.music_saper.stop()
                self.win.play()
                db = sqlite3.connect('records.db')
                cur = db.cursor()
                if self.width == 9:
                    mode = 'easy'
                elif self.width == 16:
                    mode = 'medium'
                else:
                    mode = 'hard'
                sql1 = f"""select rec from record where Game like '%Saper_{mode}%'"""
                t = cur.execute(sql1).fetchone()[0]
                if (self.time // 60 < int(t.split(':')[0])) or (self.time // 60 == int(t.split(':')[0]) and
                                                                self.time % 60 < int(t.split(':')[1])):
                    sql = f"""update record set rec = '{self.time // 60}:{self.time % 60}' 
                    where Game like '%Saper_{mode}%'"""
                    cur.execute(sql)
                db.commit()

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell:
            if self.first_step:
                self.create_map(cell[0], cell[1])
                self.first_step = False
            if cell in self.flags:
                self.flags.remove(cell)
            if self.board[cell[0]][cell[1]] == -1:
                self.open_cell(cell)
            elif self.board[cell[0]][cell[1]] == -10:
                self.end = True
                self.status_end = 'lose'
                self.music_saper.stop()
                self.boom.play(fade_ms=2)

    def get_flag(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell:
            if self.board[cell[0]][cell[1]] == -1 or self.board[cell[0]][cell[1]] == -10:
                self.flags.append(cell)

    def new_game(self, screen):
        self.flags = []
        self.end = False
        self.count = 0
        self.time = 0
        self.status_end = None
        self.first_step = True
        self.board = [[-1] * self.height for _ in range(self.width)]
        self.render(screen)
        self.music_saper.play(-1)
        pg.display.flip()

    def create_map(self, x1, y1):
        mines = [(x, y) for y in range(self.height) for x in range(self.width)]
        mines.remove((x1, y1))
        for pos in choices(mines, k=self.bombs):
            self.board[pos[0]][pos[1]] = -10


def saper_start(x, y, bombs):
    x = x
    y = y
    size = (20 * 2 + x * 30, 60 + 10 * 2 + y * 30)
    screen = pg.display.set_mode(size)
    pg.display.set_caption('Сапёр')
    clock = pg.time.Clock()
    pg.display.set_caption('Сапер')

    prev = True
    screen.fill((0, 0, 0))
    screen.blit(pg.image.load(os.path.join('prevs', 'saper_img.png')), (0, 0))
    pg.display.flip()
    board = Minesweeper(x, y, bombs, screen)
    while prev:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                board.music_saper.stop()
                return
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    board.music_saper.stop()
                    return
                else:
                    prev = False
            if event.type == pg.MOUSEBUTTONDOWN:
                prev = False
    music_flag = True
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                board.music_saper.stop()
                running = False
            if not board.end:
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    board.get_click(event.pos)
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
                    board.get_flag(event.pos)
                if event.type == board.timer:
                    board.time += 1
            if event.type == pg.KEYDOWN and event.key == pg.K_r:
                board.new_game(screen)
            if event.type == pg.KEYDOWN and event.key == pg.K_q:
                music_flag = not music_flag
                if music_flag:
                    board.music_saper.set_volume(1)
                else:
                    board.music_saper.set_volume(0)
        screen.fill((0, 0, 0))
        board.render(screen)
        pg.display.flip()
        clock.tick(50)
