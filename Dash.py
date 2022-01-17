import pygame as pg


class Dash:
    def __init__(self, x=56, y=19):
        self.width = x
        self.height = y
        self.board = [[0] * (y - 1) + [1] for _ in range(x)]
        self.cell_size = 30
        self.left, self.top = -22, 10
        self.move = pg.USEREVENT + 1
        self.player_x = 150
        self.player_y = 400
        self.player_width, self.player_height = 30, 30
        self.jump = 100
        self.fall = 2
        self.inJump = False
        self.onGround = False
        pg.time.set_timer(self.move, 20)
        self.score = 0

    def render(self, screen):
        for x in range(len(self.board)):
            for y in range(len(self.board[0])):
                if self.board[x][y] == 0:
                    pg.draw.rect(screen, pg.Color(255, 255, 255),
                                     (x * self.cell_size + self.left, y * self.cell_size + self.top,
                                      self.cell_size,
                                      self.cell_size), 1)
                else:
                    pg.draw.rect(screen, pg.Color(0, 255, 0),
                                 (x * self.cell_size + self.left, y * self.cell_size + self.top,
                                  self.cell_size,
                                  self.cell_size))
        pg.draw.rect(screen, (0, 0, 255), (self.player_x, self.player_y, self.player_width, self.player_height))
        f = pg.font.Font(None, 30)
        text_open = f.render(f'{self.score}', True,
                             (0, 240, 240))
        screen.blit(text_open, (10, 10))

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

    def get_fall(self, pos):
        x, y = self.get_cell(pos)
        if self.board[x][y] == 0:
            return True
        return False

    def get_block(self, pos):
        x, y = self.get_cell(pos)
        return (x * self.cell_size + self.left, y * self.cell_size + self.top)

    def map_plus(self):
        for _ in range(28):
            self.board.append([0] * 18 + [1])

    def moving(self):
        self.left -= 2
        if self.left == -52:
            self.left = -22
            self.score += 1
            self.board.pop(0)
            if len(self.board) == 28:
                self.map_plus();
        if not(self.inJump):
            if (self.get_fall((self.player_x, self.player_y + self.player_height)) and
                self.get_fall((self.player_x + self.player_width, self.player_y + self.player_height))):
                if (self.get_fall((self.player_x, self.player_y + self.player_height + self.fall)) and
                    self.get_fall((self.player_x + self.player_width, self.player_y + self.player_height + self.fall))):
                    self.player_y += 4
                else:
                    x, y = self.get_block((self.player_x,
                                           self.player_y + self.player_height + self.fall))
                    x1, y1 = self.get_block((self.player_x + self.player_width,
                                             self.player_y + self.player_height + self.fall))
                    if y > y1:
                        self.player_y = y - self.player_height
                    else:
                        self.player_y = y1 - self.player_height
            else:
                self.inJump = False
                self.jump = 30
                self.fall = 6
                self.onGround = True
        else:
            if self.jump > 0:
                self.player_y -= 4

            self.jump -= 1
            if self.jump == -3:
                self.inJump = False


    def jumping(self):
        if self.onGround:
            self.inJump = True
            self.onGround = False



def main():
    pg.init()
    x, y = 800, 600
    size = (x, y)
    screen = pg.display.set_mode(size)
    clock = pg.time.Clock()
    pg.display.set_caption('Dash')
    board = Dash()

    running = True

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                board.jumping()
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                board.jumping()
            if event.type == board.move:
                board.moving()


        screen.fill((255, 0, 0))
        board.render(screen)
        pg.display.flip()
        clock.tick(50)
    pg.quit()


if __name__ == '__main__':
    main()
