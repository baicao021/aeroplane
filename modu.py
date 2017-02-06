import copy
import random

CELL_NOSE = 2
CELL_BODY = 1
CELL_BLANK = 0
BASIC_OFFSET = [(0, 0), (1, -2), (1, -1), (1, 0), (1, 1), (1, 2), (2, 0), (3, -1), (3, 0), (3, 1)]
OFFSET = {
    0: set([(x, y) for x, y in BASIC_OFFSET]),
    1: set([(y, -x) for x, y in BASIC_OFFSET]),
    2: set([(-x, y) for x, y in BASIC_OFFSET]),
    3: set([(y,  x) for x, y in BASIC_OFFSET]),
}
BOARD_SIZE = 10
PLANE_NUMS = 3


class Plane():
    _lawful_flag = False
    nose = (-1, -1)
    cells = set([])

    def __init__(self, desc_tuple):
        self.desc_tuple = desc_tuple
        self.build_cell()
        self.validation()

    def build_cell(self):
        x, y, k = self.desc_tuple
        self.nose = (x, y)
        self.cells = set([(x+a, y+b) for a, b in OFFSET[k]])

    def validation(self):
        self._lawful_flag =\
            min([min(x, y) for x, y in self.cells]) >= 0 and max([max(x, y) for x, y in self.cells]) < BOARD_SIZE

    def is_lawful(self):
        return self._lawful_flag

    def is_conflict(self, other_plane):
        return self.cells.intersection(other_plane.cells) != set({})


ALL_PLANES = set([plane for plane in
                  [Plane((i,j,k)) for i in range(BOARD_SIZE) for j in range(BOARD_SIZE) for k in range(4)]
                  if plane.is_lawful()])
PLANES_DICT = {plane.desc_tuple:plane for plane in ALL_PLANES}

CELL_TO_PLANE = {(x, y):set([]) for x in range(BOARD_SIZE) for y in range(BOARD_SIZE)}
for plane in ALL_PLANES:
    for x, y in plane.cells:
        CELL_TO_PLANE[(x, y)].add(plane.desc_tuple)

CONFLICT_PLANES = {}
for i in ALL_PLANES:
    for j in ALL_PLANES:
        if i.desc_tuple < j.desc_tuple and i.is_conflict(j):
            CONFLICT_PLANES[i.desc_tuple] = CONFLICT_PLANES.get(i.desc_tuple, []) + [j.desc_tuple]
            CONFLICT_PLANES[j.desc_tuple] = CONFLICT_PLANES.get(j.desc_tuple, []) + [i.desc_tuple]

ALL_COMBINES = []

for i in ALL_PLANES:
    possible_planes = copy.copy(ALL_PLANES)
    possible_planes = possible_planes.difference(CONFLICT_PLANES[i.desc_tuple])
    possible_planes = set([plane for plane in possible_planes if i.desc_tuple < plane.desc_tuple])
    for j in possible_planes:
        possible_planes_2nd = copy.copy(possible_planes)
        possible_planes_2nd = possible_planes_2nd.difference(CONFLICT_PLANES[j.desc_tuple])
        possible_planes_2nd = set([plane for plane in possible_planes_2nd if j.desc_tuple < plane.desc_tuple])
        for k in possible_planes_2nd:
            ALL_COMBINES.append([i.desc_tuple,j.desc_tuple,k.desc_tuple])


class Chessboard(object):
    def __init__(self):
        self.lawful_planes = copy.copy(ALL_PLANES)
        self.lawful_combines = copy.copy(ALL_COMBINES)
        self.grid = {(i, j): CELL_BLANK for i in range(BOARD_SIZE) for j in range(BOARD_SIZE)}

    def get_cell_state(self, cord):
        return self.grid[cord]

    def weave(self,idx=-1):
        pass

    def reset(self):
        self.__init__()

    def cell_color(self):
        return 255, 255, 255


class TargetBoard(Chessboard):

    def __init__(self,desc_tuples=None):
        super(TargetBoard,self).__init__()
        self.planes = {}
        self._lawful_flag = False
        if desc_tuples is None:
            desc_tuples = random.choice(self.lawful_combines)
        for item in desc_tuples:
            self.place(item)

    def place(self, desc_tuple):
        plane = PLANES_DICT[desc_tuple]
        self.planes[desc_tuple] = plane
        for cell in plane.cells:
            self.grid[cell]=CELL_BODY
        self.grid[plane.nose] = CELL_NOSE
        self._lawful_flag = False
        self.validation()

    def validation(self):
        self._lawful_flag = True

    def is_lawful(self):
        return self._lawful_flag


class UncertainBoard(Chessboard):

    def __init__(self, plane_nums=3, mode='auto', desc_tuples = None):
        super(UncertainBoard, self).__init__()
        self.history = []
        self.history.append(
            {
                'board': self._combines_to_cell_prob(self.lawful_combines),
                'lawful_combines': self.lawful_combines,
                'move': (-1, -1)
            }
        )
        if mode == 'auto':
            self.is_auto =True
            self.target = TargetBoard(desc_tuples)

    def _combines_to_cell_prob(self, lawful_combines):
        grid = {
            (x, y):{
                CELL_NOSE: 0,
                CELL_BODY: 0
            }
        for x in range(10) for y in range(10)}
        n = float(len(lawful_combines))
        for combine in lawful_combines:
            for desc_tuple in combine:
                for cord in PLANES_DICT[desc_tuple].cells:
                    grid[cord][CELL_BODY]+=1
                grid[PLANES_DICT[desc_tuple].nose][CELL_BODY] -= 1
                grid[PLANES_DICT[desc_tuple].nose][CELL_NOSE] += 1

        prob_grid = {
            cord:{
                CELL_NOSE:grid[cord][CELL_NOSE]/n,
                CELL_BODY:grid[cord][CELL_BODY]/n,
            }
        for cord in grid.keys()}

        return prob_grid

    def compute_entropy(cls, combines):
        return 0.0

    def predict(self):
        return []

    def move(self, cord, cell_state, is_probe = True):
        if cell_state == CELL_NOSE:
            temp_set = set([(*cord,i) for i in range(4)])
            lawful_combines = set([combine for combine in self.lawful_combines
                                   if len(combine.intersection(temp_set)) > 0])
        if cell_state == CELL_BLANK:
            temp_set = CELL_TO_PLANE[cord]
            lawful_combines = set([combine for combine in self.lawful_combines
                                   if len(combine.intersection(temp_set)) == 0])
        if cell_state == CELL_BODY:
            temp_set = CELL_TO_PLANE[cord]
            lawful_combines = set([combine for combine in self.lawful_combines
                                   if len(combine.intersection(temp_set)) == 0])
    def play(self):
        pass

    def next(self):
        card = random.choice(self.predict())
        state = self.target.get_cell_state(card)
        self.lawful_combines = self.move(card, state)
        self.history.append(
            {
                board:
            }
        )