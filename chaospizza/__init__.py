"""Contains a set of django applications for the chaospizza backend."""
__version__ = '0.1.0'
__version_info__ = tuple([int(num) if num.isdigit() else num for num in __version__.replace('-', '.', 1).split('.')])
