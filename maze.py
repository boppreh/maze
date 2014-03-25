# -*- coding: utf-8 -*-
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

    # Unicode character for a wall with other walls in the given directions.
    UNICODE_BY_CONNECTIONS = {'ensw': '┼',
                              'ens': '├',
                              'enw': '┴',
                              'esw': '┬',
                              'es': '┌',
                              'en': '└',
                              'ew': '─',
                              'e': '╶',
                              'nsw': '┤',
                              'ns': '│',
                              'nw': '┘',
                              'sw': '┐',
                              's': '╷',
                              'n': '╵',
                              'w': '╴'}

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

    def _to_str_matrix(self):
        """
        Returns a matrix with a pretty printed visual representation of this
        maze. Example 5x5:

        OOOOOOOOOOO
        O       O O
        OOO OOO O O
        O O   O   O
        O OOO OOO O
        O   O O   O
        OOO O O OOO
        O   O O O O
        O OOO O O O
        O     O   O
        OOOOOOOOOOO
        """
        str_matrix = [['O'] * (self.width * 2 + 1)
                      for i in range(self.height * 2 + 1)]

        for cell in self.cells:
            x = cell.x * 2 + 1
            y = cell.y * 2 + 1
            str_matrix[y][x] = ' '
            if N not in cell and y > 0:
                str_matrix[y - 1][x + 0] = ' '
            if S not in cell and y + 1 < self.width:
                str_matrix[y + 1][x + 0] = ' '
            if W not in cell and x > 0:
                str_matrix[y][x - 1] = ' '
            if E not in cell and x + 1 < self.width:
                str_matrix[y][x + 1] = ' '

        return str_matrix

    def __repr__(self):
        """
        Returns an Unicode representation of the maze. Size is doubled
        horizontally to avoid a stretched look. Example 5x5:

        ┌───┬───────┬───────┐
        │   │       │       │
        │   │   ╷   ╵   ╷   │
        │   │   │       │   │
        │   │   └───┬───┘   │
        │   │       │       │
        │   └───────┤   ┌───┤
        │           │   │   │
        │   ╷   ╶───┘   ╵   │
        │   │               │
        └───┴───────────────┘
        """
        # Starts with regular representation. Looks stretched because chars are
        # twice as high as they are wide (look at docs example in
        # `Maze._to_str_matrix`).
        skinny_matrix = self._to_str_matrix()

        # Simply duplicate each character in each line.
        double_wide_matrix = []
        for line in skinny_matrix:
            double_wide_matrix.append([])
            for char in line:
                double_wide_matrix[-1].append(char)
                double_wide_matrix[-1].append(char)

        # The last two chars of each line are walls, and we will need only one.
        # So we remove the last char of each line.
        matrix = [line[:-1] for line in double_wide_matrix]

        def g(x, y):
            """
            Returns True if there is a wall at (x, y). Values outside the valid
            range always return false.

            This is a temporary helper function.
            """
            if 0 <= x < len(matrix[0]) and 0 <= y < len(matrix):
                return matrix[y][x] != ' '
            else:
                return False

        # Fix double wide walls, finally giving the impression of a symmetric
        # maze.
        for y, line in enumerate(matrix):
            for x, char in enumerate(line):
                if not g(x, y) and g(x - 1, y):
                    matrix[y][x - 1] = ' '

        # Right now the maze has the correct aspect ratio, but is still using
        # 'O' to represent walls.

        # Finally we replace the walls with Unicode characters depending on
        # their context.
        for y, line in enumerate(matrix):
            for x, char in enumerate(line):
                if not g(x, y):
                    continue

                connections = set((N, S, E, W))
                if not g(x, y + 1): connections.remove(S)
                if not g(x, y - 1): connections.remove(N)
                if not g(x + 1, y): connections.remove(E)
                if not g(x - 1, y): connections.remove(W)

                str_connections = ''.join(sorted(connections))
                # Note we are changing the matrix we are reading. We need to be
                # careful as to not break the `g` function implementation.
                matrix[y][x] = Maze.UNICODE_BY_CONNECTIONS[str_connections]

        # Simple double join to transform list of lists into string.
        return '\n'.join(''.join(line) for line in matrix) + '\n'

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

    @staticmethod
    def generate(width=20, height=10):
        """
        Returns a new random perfect maze with the given sizes.
        """
        m = Maze(width, height)
        m.randomize()
        return m
                    

class MazeGame(object):
    """
    Class for interactively playing random maze games.
    """
    def __init__(self, maze):
        self.maze = maze or Maze.generate()

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
        # Double x position because displayed maze is double-wide.
        console.set_display(y * 2 + 1, x * 4 + 2, value)

    def play(self):
        """
        Starts an interactive game on this maze, with random starting and goal
        positions. Returns True if the user won, or False if she quit the game
        by pressing "q".
        """
        player = self._get_random_position()
        target = self._get_random_position()

        while player != target:
            console.display(str(self.maze))
            self._display(player, '@')
            self._display(target, '$')

            key = console.get_valid_key(['up', 'down', 'left', 'right', 'q'])

            if key == 'q':
                return False

            direction, difx, dify = {'up': (N, 0, -1),
                                     'down': (S, 0, 1),
                                     'left': (W, -1, 0),
                                     'right': (E, 1, 0)}[key]

            current_cell = self.maze[player]
            if direction not in current_cell:
                player = (player[0] + difx, player[1] + dify)

        console.display('You win!')
        console.get_key()
        return True

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        width = int(sys.argv[1])
        if len(sys.argv) > 2:
            height = int(sys.argv[2])
        else:
            height = width
    else:
        width = 20
        height = 10

    import console
    try:
        while MazeGame(Maze.generate(width, height)).play(): pass
    except:
        import traceback
        traceback.print_exc(file=open('error_log.txt', 'a'))
        
