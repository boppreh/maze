import random

# Easy to read representation for each cardinal direction.
N, S, W, E = ('n', 's', 'w', 'e')

class Cell(object):
    """
    Class for each individual cell. Knows only its position and which walls are
    still standing.
    """
    def __init__(self, x, y, walls):
        self.x = x
        self.y = y
        self.walls = set(walls)

    def __repr__(self):
        # <15, 25 (es  )>
        return '<{}, {} ({:4})>'.format(self.x, self.y, ''.join(sorted(self.walls)))

    def __contains__(self, item):
        # N in cell
        return item in self.walls

    def is_full(self):
        """
        Returns True if all walls are still standing.
        """
        return len(self.walls) == 4

    def _wall_to(self, other):
        """
        Returns the direction to the given cell from the current one.
        Must be one cell away only.
        """
        assert abs(self.x - other.x) + abs(self.y - other.y) == 1, '{}, {}'.format(self, other)
        if other.y < self.y:
            return N
        elif other.y > self.y:
            return S
        elif other.x < self.x:
            return W
        elif other.x > self.x:
            return E
        else:
            assert False

    def connect(self, other):
        """
        Removes the wall between two adjacent cells.
        """
        other.walls.remove(other._wall_to(self))
        self.walls.remove(self._wall_to(other))

class Maze(object):
    """
    Maze class containing full board and maze generation algorithms.
    """
    def __init__(self, width=20, height=10):
        """
        Creates a new maze with the given sizes, with all walls standing.
        """
        self.width = width
        self.height = height
        self.cells = []
        for y in range(self.height):
            for x in range(self.width):
                self.cells.append(Cell(x, y, [N, S, E, W]))

    def __getitem__(self, index):
        """
        Returns the cell at index = (x, y).
        """
        x, y = index
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.cells[x + y * self.width]
        else:
            return None

    def neighbors(self, cell):
        """
        Returns the list of neighboring cells, not counting diagonals. Cells on
        borders or corners may have less than 4 neighbors.
        """
        x = cell.x
        y = cell.y
        for new_x, new_y in [(x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)]:
            neighbor = self[new_x, new_y]
            if neighbor is not None:
                yield neighbor

    def __repr__(self):
        """
        Returns a pretty printed visual representation of this maze. Example:

        OOOOOOOOOOOOOOOOOOOOO
        O O           O     O
        O O OOO O OOOOO OOO O
        O     O O O     O   O
        O OOOOO OOO OOOOO O O
        O O O O   O O   O O O
        O O O O O O O OOO O O
        O O O O O     O   O O
        O O O OOOOOOOOO OOO O
        O   O           O   O
        OOOOOOOOOOOOOOOOOOOOO
        """
        str_matrix = [['O'] * (self.width * 2 + 1)
                      for i in range(self.height * 2 + 1)]

        for cell in self.cells:
            x = cell.x * 2 + 1
            y = cell.y * 2 + 1
            str_matrix[y][x] = ' '
            if N not in cell and y > 0:
                str_matrix[y - 1][x] = ' '
            if S not in cell and y + 1 < self.width:
                str_matrix[y + 1][x] = ' '
            if W not in cell and x > 0:
                str_matrix[y][x - 1] = ' '
            if E not in cell and x + 1 < self.width:
                str_matrix[y][x + 1] = ' '

        return '\n'.join(''.join(line) for line in str_matrix) + '\n'

    def randomize(self):
        """
        Knocks down random walls to build a random perfect maze.

        Algorithm from http://mazeworks.com/mazegen/mazetut/index.htm
        """
        cell_stack = []
        cell = random.choice(self.cells)
        n_visited_cells = 1

        while n_visited_cells < len(self.cells):
            neighbors = [c for c in self.neighbors(cell) if c.is_full()]
            if len(neighbors):
                neighbor = random.choice(neighbors)
                cell.connect(neighbor)
                cell_stack.append(cell)
                cell = neighbor
                n_visited_cells += 1
            else:
                cell = cell_stack.pop()
                    

class MazeGame(object):
    """
    Class for interactively playing random maze games.
    """
    def __init__(self, width, height):
        self.maze = Maze(width, height)
        self.maze.randomize()

    def _get_random_position(self):
        """
        Returns a random position on the maze.
        """
        return (random.randrange(0, self.maze.width),
                random.randrange(0, self.maze.height))

    def _display(self, pos, value):
        """
        Displays a value on the screen from an x and y maze positions.
        """
        x, y = pos
        # position * 2 + 1 because that's how the maze is displayed.
        console.set_display(y * 2 + 1, x * 2 + 1, value)

    def play(self):
        """
        Starts an interactive game on this maze. Returns True if the user won,
        or False if she quit the game by pressing "q".
        """
        self.player = self._get_random_position()
        self.target = self._get_random_position()

        while self.player != self.target:
            console.display(str(self.maze))
            self._display(self.player, '!')
            self._display(self.target, '$')

            key = console.get_valid_key(['up', 'down', 'left', 'right', 'q'])

            if key == 'q':
                return False

            direction, difx, dify = {'up': (N, 0, -1),
                                     'down': (S, 0, 1),
                                     'left': (W, -1, 0),
                                     'right': (E, 1, 0)}[key]

            current_cell = self.maze[self.player]
            if direction not in current_cell:
                self.player = (self.player[0] + difx, self.player[1] + dify)

        console.display('You win!')
        console.get_key()
        return True

if __name__ == '__main__':
    import console
    try:
        while MazeGame(10, 10).play(): pass
    except:
        import traceback
        traceback.print_exc(file=open('error_log.txt', 'a'))
        
