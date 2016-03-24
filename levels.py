from os import path

level_dir = path.join(path.dirname(__file__), "assets", "levels")


class Level01(object):
    name = "Level01"

    level = level_dir + "\map.tmx"

    wave_1 = [[0, 0, 0, 0]]
    wave_2 = [[0, 0, 1, 1, 1, 1]]
    wave_3 = [[1, 1, 1, 1, 1, 1]]

    wave_list = [wave_1]

    towers = [0, 1, 2]
    traps = [0]

    money = 1000


class Level02(object):
    name = "Level02"

    level = level_dir + "\map2.tmx"

    wave_1 = [[0], [1]]
    wave_2 = [[2, 2, 1], [0, 0]]

    wave_list = [wave_1]

    towers = [0, 1, 2, 3, 4]
    traps = [0]

    money = 1600


class Level03(object):
    name = "Level03"

    level = level_dir + "\map3.tmx"

    wave_1 = [[0, 0, 0, 0], [1, 1, 1, 0, 0], [1, 1, 1, 1, 2]]
    wave_2 = [[3, 3, 0, 0], [2, 3, 1, 0, 0], [1, 3, 3, 1, 2]]

    wave_list = [wave_1, wave_2]

    towers = [0, 1, 2, 3, 4, 5, 6, 7]
    traps = [0]

    money = 5000

class Level04(object):
    name = "Level04"

    level = level_dir + "\map.tmx"

    wave_1 = [[0]]
    wave_2 = [[0, 0, 1, 1, 1, 1]]
    wave_3 = [[1, 1, 1, 1, 1, 1]]

    wave_list = [wave_1]

    towers = [0, 1, 2, 3, 4, 5, 6, 7]
    traps = [0]

    money = 1000

class Level05(object):
    name = "Level05"

    level = level_dir + "\map.tmx"

    wave_1 = [[0]]
    wave_2 = [[0, 0, 1, 1, 1, 1]]
    wave_3 = [[1, 1, 1, 1, 1, 1]]

    wave_list = [wave_1]

    towers = [0, 1, 2, 3, 4, 5, 6, 7]
    traps = [0]

    money = 1000


"""
level_list = [level_dir + "\map.tmx", level_dir + "\map2.tmx"]
wave_list = [[ [[0, 0], [1, 1, 1, 1, 1, 1, 1], [2] ],
                      [ [1, 1], [2, 2], [2, 2] ],
                      [ [1, 1], [2, 2], [2, 2] ],
                      [ [1, 1], [2, 2], [2, 2] ],
                      [ [1, 1], [2, 2], [2, 2] ]
                      ],
                      [ [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [1, 1]], [[1, 2], [2, 2]] ]
                     ]

money_list = [1000, 2000]
"""


