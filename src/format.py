import pyqtgraph as pg
from pyqtgraph.Qt import QtCore

from psmon import config


SOLID_LINE_CHAR = '-'
DOTTED_LINE_CHAR = ':'
LINE_CONT_CHAR = ['-', '.']

COLOR_LIST = [
    'b', # blue
    'g', # green
    'r', # red
    'c', # cyan
    'm', # magenta
    'y', # yellow
    'k', # black
    'w', # white
]

MARKER_MAP = {
    '.': ('o', config.PYQT_MARK_SIZE_SMALL),
    'o': ('o', config.PYQT_MARK_SIZE),
    'v': ('t', config.PYQT_MARK_SIZE),
    '^': ('t', config.PYQT_MARK_SIZE),
    '<': ('t', config.PYQT_MARK_SIZE),
    '>': ('t', config.PYQT_MARK_SIZE),
    '1': ('t', config.PYQT_MARK_SIZE),
    '2': ('t', config.PYQT_MARK_SIZE),
    '3': ('t', config.PYQT_MARK_SIZE),
    '4': ('t', config.PYQT_MARK_SIZE),
    's': ('s', config.PYQT_MARK_SIZE),
    '+': ('+', config.PYQT_MARK_SIZE),
    'x': ('x', config.PYQT_MARK_SIZE),
    'd': ('d', config.PYQT_MARK_SIZE),
}

LINE_MAP = {
    ':':  QtCore.Qt.DotLine,
    '-':  QtCore.Qt.SolidLine,
    '--': QtCore.Qt.DashLine,
    '-.': QtCore.Qt.DashDotLine,
}


def parse_fmt_str(fmt_str, color_index):
    color = None
    line_style = None
    marker = None
    marker_size = None
    multi_char_seen = False

    for token in fmt_str:
        if multi_char_seen:
            multi_char_seen = False
            if token in LINE_CONT_CHAR:
                line_style = LINE_MAP.get(SOLID_LINE_CHAR + token)
                continue

        if token == SOLID_LINE_CHAR:
            if line_style is not None:
                raise ValueError('Illegal format string "%s"; two linestyle symbols' % fmt_str)
            line_style = LINE_MAP.get(SOLID_LINE_CHAR)
            multi_char_seen = True
        elif token == DOTTED_LINE_CHAR:
            if line_style is not None:
                raise ValueError('Illegal format string "%s"; two linestyle symbols' % fmt_str)
            line_style = QtCore.Qt.DotLine
        elif token in COLOR_LIST:
            if color is not None:
                raise ValueError('Illegal format string "%s"; two color symbols' % fmt_str)
            color = token
        elif token in MARKER_MAP:
            if marker is not None:
                raise ValueError('Illegal format string "%s"; two marker symbols' % fmt_str)
            marker, marker_size = MARKER_MAP.get(token)
        else:
            raise ValueError('Unrecognized character %s in format string "%s"' % (token, fmt_str))

    return color, line_style, marker, marker_size


def parse_fmt_xyplot(fmt_str, color_index=0):
    line = None
    fmt_dict = {}
    color, line_style, marker, marker_size = parse_fmt_str(fmt_str, color_index)

    # set color by rotating scheme if none is specified
    if color is None:
        color = (color_index, config.PYQT_AUTO_COLOR_MAX)

    # create a pen object for line if one is specified
    if line_style is not None:
        line = pg.mkPen(color, style=line_style)

    fmt_dict['pen'] = line

    # only pass add these entries if they are non-null
    if marker is not None:
        fmt_dict['symbol'] = marker
    if color is not None:
        fmt_dict['symbolBrush'] = color
    if marker_size is not None:
        fmt_dict['symbolSize'] = marker_size

    return fmt_dict