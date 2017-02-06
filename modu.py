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
    3: set([(-y, -x) for x, y in BASIC_OFFSET]),
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
    grid = {}
    def __init__(self):
        self.build_grid()
        self.lawful_planes=copy.copy(ALL_PLANES)
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
        super(TargetBoard).__init__()
        self._lawful_flag = False
        if desc_tuples is not None:
            for item in desc_tuples:
                self.place(desc_tuples, item)

    def place(self, desc_tuple):
        plane = PLANES_DICT[desc_tuple]
        for cell in plane.cells:
            self.grid[cell]=CELL_BODY
        self.grid[plane.nose] = CELL_NOSE
        self._lawful_flag = False
        validation()

    def validation(self):
        self._lawful_flag = True

    def is_lawful(self):
        return self._lawful_flag

class UncertainBoard(Chessboard):

    def __init__(self,plane_nums=3,mode='auto'):
        super(UncertainBoard).__init__()
        self.history = []
        self.history.append(
            {
                'board': self.grid,
                'lawful_combines': self.lawful_combines,
            }
        )

    def build_grid(self):
        pass




    def move(self,coord,state):
        pass

    def stage_collapse(self):
        pass

    def re_compute(self):
        pass

    def rand_planes(self):
        pass

    def pick_a_plane(self):
        pass

    def change_mode(self,mode):
        pass

