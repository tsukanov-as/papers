# Пример использования кодирования (4+10 ячеек вместо 4*10) и нечеткой логики (позиция может быть зафиксирована произвольно точно)

import numpy as np
 
B = 4 # разрядность ячеек
 
# вектор с операциями нечеткой логики
class vector(np.ndarray):
    def __and__(x, y):
        return x * y
    def __or__(x, y):
        return (x + y) - (x * y)
    def __invert__(x):
        return 1 - x

# конструктор
def cell(v=None):
    a = vector(B, dtype=np.float32)
    if v is None:
        a.fill(0)
    else:
        for i in range(B):
            a[i] = v[i]
    return a

class Machine:
    def __init__(self, cells):
        self.cells = cells
        self.state = {}
        self._state = {}
        for key in cells.keys():
            self.state[key] = cell()
    def step(self):
        for key, f in self.cells.items():
            if f is None:
                self._state[key] = self.state[key]
            else:
                self._state[key] = f(self.state)
        self.state, self._state = self._state, self.state

# компас, имеющий очень высокую точность фиксации позиции (float32)
# и небольшую точность смещений позиций (4*10)
cells = {
    1: None, # немного налево
    2: None, # немного направо
    3: lambda s: (~s[8] & ~s[9] & s[3]) | (s[8] & s[6]) | (s[9] & s[4]), # Впереди
    4: lambda s: (~s[8] & ~s[9] & s[4]) | (s[8] & s[3]) | (s[9] & s[5]), # Справа
    5: lambda s: (~s[8] & ~s[9] & s[5]) | (s[8] & s[4]) | (s[9] & s[6]), # Сзади
    6: lambda s: (~s[8] & ~s[9] & s[6]) | (s[8] & s[5]) | (s[9] & s[3]), # Слева
    # сигналы переполнения:
    8: lambda s: s[1] & s[10], # Налево
    9: lambda s: s[2] & s[19], # Направо
    # смещение в пределах текущей стороны:
    10: lambda s: (~s[1] & ~s[2] & s[10]) | (s[1] & s[19]) | (s[2] & s[11]),
    11: lambda s: (~s[1] & ~s[2] & s[11]) | (s[1] & s[10]) | (s[2] & s[12]),
    12: lambda s: (~s[1] & ~s[2] & s[12]) | (s[1] & s[11]) | (s[2] & s[13]),
    13: lambda s: (~s[1] & ~s[2] & s[13]) | (s[1] & s[12]) | (s[2] & s[14]),
    14: lambda s: (~s[1] & ~s[2] & s[14]) | (s[1] & s[13]) | (s[2] & s[15]),
    15: lambda s: (~s[1] & ~s[2] & s[15]) | (s[1] & s[14]) | (s[2] & s[16]),
    16: lambda s: (~s[1] & ~s[2] & s[16]) | (s[1] & s[15]) | (s[2] & s[17]),
    17: lambda s: (~s[1] & ~s[2] & s[17]) | (s[1] & s[16]) | (s[2] & s[18]),
    18: lambda s: (~s[1] & ~s[2] & s[18]) | (s[1] & s[17]) | (s[2] & s[19]),
    19: lambda s: (~s[1] & ~s[2] & s[19]) | (s[1] & s[18]) | (s[2] & s[10]),
}

m = Machine(cells)

# нечеткая база, заданная с высокой точностью (float32)
# дефаззификация может быть выполнена методом центра тяжести: (0.7*справа + 0.5*сзади) / 1.2
m.state[4] = cell([0, 0, 0, 0.7]) # 0.7 справа
m.state[5] = cell([0, 0, 0, 0.5]) # 0.5 сзади
# смещение относительно базы
m.state[12] = cell([0, 0, 0, 1]) # смещение

# четкий сигнал о повороте
m.state[2] = cell([0, 0, 0, 1]) # немного направо

for i in range(100):
    z = []
    for k in m.state:
        z.append(m.state[k][3])
    print(z)
    m.step()
