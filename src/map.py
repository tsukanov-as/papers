
class Machine:

    def __init__(self, cells):
        self.cells = cells
        self.state = {}
        self._state = {}
        for key in cells.keys():
            self.state[key] = 0b0000
        
    def step(self):
        for key, f in self.cells.items():
            if f is None:
                self._state[key] = self.state[key]
            else:
                self._state[key] = f(self.state)
        self.state, self._state = self._state, self.state

cells = {}

# матрица:
# n1    n2    n3
#    g1 g2 g3
# n8 g8 n0 g4 n4
#    g7 g6 g5
# n7    n6    n5

# размеры карты
h, w = 50, 50

# сигнал, указывающий что возбудился хотя бы один узел с меткой
# цикл эмулирует множество однотипных связей
def stop(s):
    res = 0b0000
    for x in range(1, w-1):
        for y in range(1, h-1):
            res = res | s[x, y, 'node', 'mark'] & s[x, y, 'node']
    return res & s['mode1']
cells['stop'] = stop

# режим поиска пути
cells['mode1'] = lambda s: s['mode1'] & ~s['stop']
# режим движения по построенному пути
cells['mode2'] = lambda s: s['mode2'] | s['stop']

# предварительное создание узлов, меток и ворот
for x in range(0, w):
    for y in range(0, h):
        cells[x, y, 'node'] = None    
        cells[x, y, 'node', 'mark'] = None    
        for i in range(1, 9):
            cells[x, y, 'gate', i] = None    
            cells[x, y, 'gate', i, 'mark'] = None   

def apply_matrix(x, y):
    # режимы
    m1 = 'mode1' # прямой ход
    m2 = 'mode2' # обратный ход
    m3 = 'stop'  # сигнал остановки поиска
    # ворота
    g1 = x, y, 'gate', 1 
    g2 = x, y, 'gate', 2
    g3 = x, y, 'gate', 3
    g4 = x, y, 'gate', 4
    g5 = x, y, 'gate', 5
    g6 = x, y, 'gate', 6
    g7 = x, y, 'gate', 7
    g8 = x, y, 'gate', 8
    # метки на воротах
    gm1 = x, y, 'gate', 1, 'mark' 
    gm2 = x, y, 'gate', 2, 'mark'
    gm3 = x, y, 'gate', 3, 'mark'
    gm4 = x, y, 'gate', 4, 'mark'
    gm5 = x, y, 'gate', 5, 'mark'
    gm6 = x, y, 'gate', 6, 'mark'
    gm7 = x, y, 'gate', 7, 'mark'
    gm8 = x, y, 'gate', 8, 'mark'
    # метки на воротах соседей
    _gm1 = x-1, y-1, 'gate', 5, 'mark'
    _gm2 = x+0, y-1, 'gate', 6, 'mark' 
    _gm3 = x+1, y-1, 'gate', 7, 'mark' 
    _gm4 = x+1, y+0, 'gate', 8, 'mark' 
    _gm5 = x+1, y+1, 'gate', 1, 'mark' 
    _gm6 = x+0, y+1, 'gate', 2, 'mark' 
    _gm7 = x-1, y+1, 'gate', 3, 'mark' 
    _gm8 = x-1, y+0, 'gate', 4, 'mark'
    # узел
    n0 = x, y, 'node'
    # пометка на узле
    nm0 = x, y, 'node', 'mark'
    # соседи
    n1 = x-1, y-1, 'node'
    n2 = x+0, y-1, 'node' 
    n3 = x+1, y-1, 'node' 
    n4 = x+1, y+0, 'node' 
    n5 = x+1, y+1, 'node' 
    n6 = x+0, y+1, 'node' 
    n7 = x-1, y+1, 'node' 
    n8 = x-1, y+0, 'node' 
    # узел будет активизирован если активны хотя бы одни ворота
    cells[n0] = lambda s: s[m3] & s[nm0] | ~s[m3] & (s[g1] | s[g2] | s[g3] | s[g4] | s[g5] | s[g6] | s[g7] | s[g8])
    # пометка ставится извне
    cells[nm0] = None
    
    # режим1: ворота активизируются если активен соответствующий этим воротам соседний узел
    # режим2: ворота активизируются если активен соответствующий этим воротам соседний узел и активна метка на соответствующих воротах соседа
    cells[g1] = lambda s: (s[m1] & s[n1]) | (s[m2] & s[n1] & s[_gm1])
    cells[g2] = lambda s: (s[m1] & s[n2]) | (s[m2] & s[n2] & s[_gm2])
    cells[g3] = lambda s: (s[m1] & s[n3]) | (s[m2] & s[n3] & s[_gm3])
    cells[g4] = lambda s: (s[m1] & s[n4]) | (s[m2] & s[n4] & s[_gm4])
    cells[g5] = lambda s: (s[m1] & s[n5]) | (s[m2] & s[n5] & s[_gm5])
    cells[g6] = lambda s: (s[m1] & s[n6]) | (s[m2] & s[n6] & s[_gm6])
    cells[g7] = lambda s: (s[m1] & s[n7]) | (s[m2] & s[n7] & s[_gm7])
    cells[g8] = lambda s: (s[m1] & s[n8]) | (s[m2] & s[n8] & s[_gm8])
    
    gm_ = lambda s: s[gm1] | s[gm2] | s[gm3] | s[gm4] | s[gm5] | s[gm6] | s[gm7] | s[gm8]
    
    # режим1: метка активизируется если активны соответствующие ворота и нет сигнала стоп;
    # выполняется упорядоченный выбор только одной метки (хвосты формул) если активны сразу несколько ворот;
    # метка остается активной после первой активации
    # режим2: метка остается активной, если была активна на момент включения режима
    cells[gm1] = lambda s: (s[m2] & s[gm1]) | (s[m1] & (s[gm1] | s[g1] & ~gm_(s) & ~s[m3] & ~s[g2] & ~s[g4] & ~s[g6] & ~s[g8] & ~s[g3] & ~s[g5] & ~s[g7]))
    cells[gm2] = lambda s: (s[m2] & s[gm2]) | (s[m1] & (s[gm2] | s[g2] & ~gm_(s) & ~s[m3] & ~s[g4] & ~s[g6] & ~s[g8]))
    cells[gm3] = lambda s: (s[m2] & s[gm3]) | (s[m1] & (s[gm3] | s[g3] & ~gm_(s) & ~s[m3] & ~s[g2] & ~s[g4] & ~s[g6] & ~s[g8] & ~s[g5] & ~s[g7]))
    cells[gm4] = lambda s: (s[m2] & s[gm4]) | (s[m1] & (s[gm4] | s[g4] & ~gm_(s) & ~s[m3] & ~s[g6] & ~s[g8]))
    cells[gm5] = lambda s: (s[m2] & s[gm5]) | (s[m1] & (s[gm5] | s[g5] & ~gm_(s) & ~s[m3] & ~s[g2] & ~s[g4] & ~s[g6] & ~s[g8] & ~s[g7]))
    cells[gm6] = lambda s: (s[m2] & s[gm6]) | (s[m1] & (s[gm6] | s[g6] & ~gm_(s) & ~s[m3] & ~s[g8]))
    cells[gm7] = lambda s: (s[m2] & s[gm7]) | (s[m1] & (s[gm7] | s[g7] & ~gm_(s) & ~s[m3] & ~s[g2] & ~s[g4] & ~s[g6] & ~s[g8]))
    cells[gm8] = lambda s: (s[m2] & s[gm8]) | (s[m1] & (s[gm8] | s[g8] & ~gm_(s) & ~s[m3]))
        
# построение карты
for x in range(1, w-1):
    for y in range(1, h-1):
        apply_matrix(x, y)

# ограничение на количество итераций для формирования gif
count = 81

# # дырка в сети
# hole_x, hole_y = (5, 45), (20, 40)
# for x in range(hole_x[0], hole_x[1]+1):
#     for y in range(hole_y[0], hole_y[1]+1):
#         cells[x, y, 'node'] = None
# count = 120
            
# создание машины
m = Machine(cells)          

# позиция существа на карте
self_x, self_y = 38, 5
# позиция цели на карте
target_x, target_y = 10, 45

# сигналы извне карты (режим поиска, метка позиции существа, позиция цели)
m.state['mode1'] = 0b0001
m.state['mode2'] = 0b0000
m.state[self_x, self_y, 'node', 'mark'] = 0b0001
m.state[target_x, target_y, 'node'] = 0b0001

from PIL import Image, ImageDraw

images = []

def draw_cell(draw, x, y, c):
    draw.rectangle([x*10, y*10, x*10+10, y*10+10], c)

def draw():
    im = Image.new("P", ((w-2)*10, (h-2)*10), 1)
    im.putpalette([
        0, 0, 0,
        255, 255, 255,
        255, 0, 0,
        0, 0, 255,
        100, 100, 100,
    ])
    images.append(im)
    draw = ImageDraw.Draw(im)
    # отрисовка активации одного канала карточек типа "узел"
    for x in range(1, w-1):
        for y in range(1, h-1):
            if m.state[x, y, 'node'] == 0b0001:
                draw_cell(draw, x-1, y-1, 0)
    # отрисовка позиции цели
    draw_cell(draw, target_x-1, target_y-1, 2)
    # отрисовка позиции существа
    draw_cell(draw, self_x-1, self_y-1, 3)
    # # отрисовка дырки (мертвых нейронов)
    # draw.rectangle([(hole_x[0]-1)*10, (hole_y[0]-1)*10, (hole_x[1]-1)*10+10, (hole_y[1]-1)*10+10], 4)

# итерации машины и выборочная отрисовка состояния одного канала в gif
for i in range(count):
    m.step()
    m.step()
    draw()
    
images[0].save("map.gif", save_all=True, append_images=images[1:], duration=100, loop=0)
