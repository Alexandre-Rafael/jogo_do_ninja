import json
import pygame

AUTOTILE_MAP = {
    tuple(sorted([(1, 0), (0, 1)])): 0,
    tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,
    tuple(sorted([(-1, 0), (0, 1)])): 2,
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 3,
    tuple(sorted([(-1, 0), (0, -1)])): 4,
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5,
    tuple(sorted([(1, 0), (0, -1)])): 6,
    tuple(sorted([(1, 0), (0, -1), (0, 1)])): 7,
    tuple(sorted([(1, 0), (-1, 0), (0, 1), (0, -1)])): 8,
}

NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]
PHYSICS_TILES = {'grass', 'stone'}
AUTOTILE_TYPES = {'grass', 'stone'}


class Tilemap:
    def __init__(self, game, tile_size=16):
        self._game = game
        self._tile_size = tile_size
        self._tilemap = {}
        self._offgrid_tiles = []

    def get_game(self):
        return self._game

    def set_game(self, game):
        self._game = game

    def get_tile_size(self):
        return self._tile_size

    def set_tile_size(self, tile_size):
        self._tile_size = tile_size

    def get_tilemap(self):
        return self._tilemap

    def set_tilemap(self, tilemap):
        self._tilemap = tilemap

    def get_offgrid_tiles(self):
        return self._offgrid_tiles

    def set_offgrid_tiles(self, offgrid_tiles):
        self._offgrid_tiles = offgrid_tiles

    def get_map_height(self):
        max_y = 0
        for loc in self._tilemap:
            y = int(loc.split(';')[1])
            if y > max_y:
                max_y = y
        return (max_y + 1) * self._tile_size

    def extract(self, id_pairs, keep=False):
        matches = []
        for tile in self._offgrid_tiles.copy():
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                if not keep:
                    self._offgrid_tiles.remove(tile)

        for loc in self._tilemap:
            tile = self._tilemap[loc]
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                matches[-1]['pos'] = matches[-1]['pos'].copy()
                matches[-1]['pos'][0] *= self._tile_size
                matches[-1]['pos'][1] *= self._tile_size
                if not keep:
                    del self._tilemap[loc]

        return matches

    def tiles_around(self, pos):
        tiles = []
        tile_loc = (int(pos[0] // self._tile_size), int(pos[1] // self._tile_size))
        for offset in NEIGHBOR_OFFSETS:
            check_loc = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if check_loc in self._tilemap:
                tiles.append(self._tilemap[check_loc])
        return tiles

    def save(self, path):
        f = open(path, 'w')
        json.dump({'tilemap': self._tilemap, 'tile_size': self._tile_size, 'offgrid': self._offgrid_tiles}, f)
        f.close()

    def load(self, path):
        f = open(path, 'r')
        map_data = json.load(f)
        f.close()

        self._tilemap = map_data['tilemap']
        self._tile_size = map_data['tile_size']
        self._offgrid_tiles = map_data['offgrid']

    def solid_check(self, pos):
        tile_loc = str(int(pos[0] // self._tile_size)) + ';' + str(int(pos[1] // self._tile_size))
        if tile_loc in self._tilemap:
            if self._tilemap[tile_loc]['type'] in PHYSICS_TILES:
                return self._tilemap[tile_loc]

    def physics_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            if tile['type'] in PHYSICS_TILES:
                rects.append(
                    pygame.Rect(tile['pos'][0] * self._tile_size, tile['pos'][1] * self._tile_size, self._tile_size,
                                self._tile_size))
        return rects

    def autotile(self):
        for loc in self._tilemap:
            tile = self._tilemap[loc]
            neighbors = set()
            for shift in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
                check_loc = str(tile['pos'][0] + shift[0]) + ';' + str(tile['pos'][1] + shift[1])
                if check_loc in self._tilemap:
                    if self._tilemap[check_loc]['type'] == tile['type']:
                        neighbors.add(shift)
            neighbors = tuple(sorted(neighbors))
            if (tile['type'] in AUTOTILE_TYPES) and (neighbors in AUTOTILE_MAP):
                tile['variant'] = AUTOTILE_MAP[neighbors]

    def render(self, surf, offset=(0, 0)):
        for tile in self._offgrid_tiles:
            surf.blit(self._game.get_assets()[tile['type']][tile['variant']],
                      (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))

        for x in range(offset[0] // self._tile_size, (offset[0] + surf.get_width()) // self._tile_size + 1):
            for y in range(offset[1] // self._tile_size, (offset[1] + surf.get_height()) // self._tile_size + 1):
                loc = str(x) + ';' + str(y)
                if loc in self._tilemap:
                    tile = self._tilemap[loc]
                    surf.blit(self._game.get_assets()[tile['type']][tile['variant']], (
                    tile['pos'][0] * self._tile_size - offset[0], tile['pos'][1] * self._tile_size - offset[1]))
