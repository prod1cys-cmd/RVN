"""Rasterize the supplied structural diagram for insertion into the editable report."""
from pathlib import Path

from cairosvg import svg2png


if __name__ == '__main__':
    source = Path(__file__).with_name('workplace.svg')
    svg2png(url=str(source), write_to=str(source.with_suffix('.png')), output_width=2200)
