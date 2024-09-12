import random



class BoardException(Exception):
    pass

class BoardOutException(BoardException): #вышел за пределы

    def __str__(self):
        return "Атака за пределами игрового поля. Попробуй еще."

class CellAlreadyAttackedError(BoardException): #Ogon' v tu je tochku

    def __str__(self):
        return "Атака в занятую точку. Попробуй еще."

class ShipOverlapException(BoardException):

    def __str__(self):
        return "Корабль пересекается с другим. Попробуй еще"


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if not isinstance(other, Dot):
            return NotImplemented
        return self.x == other.x and self.y == other.y


class Ship:
    def __init__(self, length, bow, direction ):
        self.length = length
        self.bow = bow
        self.direction = direction
        self.lives = length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            cur_x, cur_y = self.bow.x, self.bow.y
            if self.direction == 0:
                cur_x += i
            else:
                cur_y += i
            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots


class Board:
    def __init__(self, hid=False, size=6):
        self.hid = hid
        self.size = size
        self.field = [['0'] * size for _ in range(size)]
        self.busy = []
        self.ships = []

    def add_ship(self, ship):
        for dot in ship.dots:
            if self.out(dot) or dot in self.busy:
                raise ShipOverlapException("Корабли не должны пересекаться или соприкасаться.")
        for dot in ship.dots:
            self.field[dot.x][dot.y] = '■'
            self.busy.append(dot)
        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near_ship = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for dot in ship.dots:
            for d_x, d_y in near_ship:
                cur = Dot(dot.x + d_x, dot.y + d_y)
                if not self.out(cur) and cur not in self.busy:
                    self.busy.append(cur)
                    if verb:
                        self.field[cur.x][cur.y] = '.'

    def out(self, dot):
        return not ( 0 <= dot.x < self.size and 0 <= dot.y < self.size)

    def shot(self, dot):
        if self.out(dot):
            raise BoardOutException()
        if dot in self.busy:
            raise CellAlreadyAttackedError()
        self.busy.append(dot)
        for ship in self.ships:
            if dot in ship.dots:
                ship.lives -=1
                self.field [dot.x][dot.y] = 'X'
                if ship.lives == 0:
                    self.contour(ship, verb=True)
                    self.ships.remove(ship)
                    print("Затопил!")
                    return True
                else:
                    print("Попал!")
                    return True
        self.field[dot.x][dot.y] = "T"
        print("Мимо!")
        return False

    def __str__(self):
        res = '|' + '|'.join(str(i + 1) for i in range(self.size)) + '|\n'
        for i, row  in enumerate(self.field):
            res += f'{i+1} |' + '|'.join(row) + '|\n'
        if self.hid:
            res = res.replace('■', '0')
        return res

    def clear_busy_point(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy_board):
        self.board = board
        self.enemy_board = enemy_board

    def ask(self):
        raise NotImplemented

    def move(self):
        while True:
            try:
                target = self.ask()
                again = self.enemy_board.shot(target)
                return again
            except BoardException as e:
                print(e)

class User(Player):
    def ask(self):
        while True:
            try:
                coordinate = input('Введите координаты  х у через прообел:').split()

                if len(coordinate) != 2 or not all(coord.isdigit() for coord in coordinate):
                    raise ValueError("Ввели чтото не то!")
                x, y = map(int, coordinate)
                if not ( 1 <= x <= self.board.size  and 1 <= y <= self.board.size):
                    raise ValueError('За пределами карты!')
                return Dot(x - 1, y - 1)
            except ValueError as e:
                print(e)

class AI(Player):
    def ask(self):
        x = random.randint(0, self.board.size - 1)
        y = random.randint(0, self.board.size - 1)
        print(f'AI атакует на {x + 1}, {y + 1}')
        return Dot(x, y)

class Game:
    def __init__(self, size=6):
        self.size = size
        self.user_board = self.random_board()
        self.ai_board = self.random_board(True)
        self.ai = AI(self.ai_board, self.user_board)
        self.user = User(self.user_board,self.ai_board)

    def random_board(self, hid=False):
        board = Board(hid=hid, size=self.size)
        ship_lives = [3, 2, 2, 1, 1, 1, 1]
        attemps = 0
        for lives in ship_lives:
            placed = False
            while not placed and attemps < 2000:
                ship = Ship(lives, Dot(random.randint(0, self.size - 1 ), random.randint(0, self.size - 1 )),
                            random.randint(0, 1))
                try:
                    board.add_ship(ship)
                    placed = True
                except ShipOverlapException:
                    attemps += 1
            if not placed:
                print('Невозможно разместить все корабли, давай заново')
                return self.random_board(hid)
        board.clear_busy_point()
        return board

    def greet(self):
        print('Приветствую на Битве Кораблей!')

    def loop(self):
        num = 0
        while True:
            print('Доска игрока')
            print(self.user.board)
            print('\nДоска АИ')
            print(self.ai.board)
            if num % 2 == 0:
                print('\nИдет игрок:')
                reapeat = self.user.move()
            else:
                print('\nИдет АИ:')
                reapeat = self.ai.move()
            if not reapeat:
                num += 1
            if len(self.ai.board.ships) == 0:
                print('Игрок Выиграл!')
                break
            if len(self.user.board.ships) == 0:
                print('АИ Выиграл!')
                break


    def start(self):
        self.greet()
        self.loop()

if  __name__  == '__main__':
    g = Game()
    g.start()





