# pylint: disable=all

import random


digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
chars = [chr(ord('a') + i) for i in range(26)]
seeds = chars + digits


def random_id():
    s = []
    for i in range(32):
        idx = random.randint(0, len(seeds) - 1)
        s.append(seeds[idx])
    return ''.join(s)
