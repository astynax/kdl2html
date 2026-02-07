import sys

import cuddle
from . import htmlize


def main():
    """Print the HTML made from the KDL document from the STDIN."""
    print(str(htmlize(cuddle.load(sys.stdin))))  # pyright: ignore[reportUnknownMemberType]


if __name__ == '__main__':
    main()
