from os import path

level_dir = path.join(path.dirname(__file__), "assets", "levels")


class Level01(object):
    level = level_dir + "\map.tmx"

    wave_1 = [[0, 0, 0, 0]]
    wave_2 = [[0, 0, 1, 1, 1, 1]]
    wave_3 = [[1, 1, 1, 1, 1, 1]]

    wave_list = [wave_1, wave_2, wave_3]

    towers = [0, 1, 2, 3, 4, 5, 6]

    money = 1000


class Level02(object):
    level = level_dir + "\map2.tmx"

    wave_1 = [[0, 0, 0], [1, 1, 1]]
    wave_2 = [[2, 2, 1], [0, 0]]

    wave_list = [wave_1, wave_2]

    towers = [0, 1, 2, 3, 4]

    money = 1600


class Level03(object):
    level = level_dir + "\map3.tmx"

    wave_1 = [[0, 0, 0], [1, 1, 1], [2, 2, 2]]
    wave_2 = [[2, 2, 1], [0, 0], [0, 0, 0]]

    wave_list = [wave_1, wave_2]

    towers = [0, 1, 2, 3, 4, 5]

    money = 2400


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


