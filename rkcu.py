import argparse

from rkcu.config import get_base_config
from rkcu.utils import RKCU

# Python based Command Line wrapper for managing profiles on Royal Kludge RK 61 Keyboard
# author: Hardik Srivastava [oddlyspaced]

parser = argparse.ArgumentParser(
    prog = 'RK61 Config Utility',
    description = 'Utility to manage profiles on the Royal Kludge RK61 Keyboard.'
)

color_config = get_base_config()

def setup_arg_parser():
    global parser
    parser.add_argument('--speed', '-sp')
    parser.add_argument('--brightness', '-br')
    parser.add_argument('--sleep', '-sl')
    parser.add_argument('--animation', '-an')

    parser.add_argument('--rainbow', '-rb', action='store_true')

    parser.add_argument('--red', '-r')
    parser.add_argument('--green', '-g')
    parser.add_argument('--blue', '-b')

def read_args():
    args = parser.parse_args()
    var = vars(args)
    update_config(var)

def update_config(var: dict):
    color_config.update(var)

setup_arg_parser()
read_args()

rk = RKCU(0x258a, 0x00e0)
rk.apply_config(color_config)