from collections import deque

def init():
    global  position, set_position

    position = deque([], 720)
    set_position = deque([0], 720)
