#---------------------------------------------------------------------#
# Warlight AI Challenge - Starter Bot                                 #
# ============                                                        #
#                                                                     #
# Last update: 20 Mar, 2014                                           #
#                                                                     #
# @author Jackie <jackie@starapple.nl>                                #
# @version 1.0                                                        #
# @license MIT License (http://opensource.org/licenses/MIT)           #
#---------------------------------------------------------------------#

from math import *
from sys import stderr, stdin, stdout
from time import clock

class Bot(object):
    '''
    Main bot class
    '''
    def __init__(self):
        '''
        Initializes a map instance and an empty dict for settings
        '''
        self.settings = {}
        self.map = Map()

    def run(self):
        '''
        Main loop

        Keeps running while being fed data from stdin.
        Writes output to stdout, remember to flush!
        '''
        while not stdin.closed:
            try:
                rawline = stdin.readline()

                # End of file check
                if len(rawline) == 0:
                    break

                line = rawline.strip()

                # Empty lines can be ignored
                if len(line) == 0:
                    continue

                parts = line.split()

                command = parts[0]

                # All different commands besides the opponents' moves
                if command == 'settings':
                    self.update_settings(parts[1:])

                elif command == 'setup_map':
                    self.setup_map(parts[1:])

                elif command == 'update_map':
                    self.update_map(parts[1:])

                elif command == 'pick_starting_regions':
                    stdout.write(self.pick_starting_regions(parts[2:]) + '\n')
                    stdout.flush()

                elif command == 'go':

                    sub_command = parts[1]

                    if sub_command == 'place_armies':

                        stdout.write(self.place_troops() + '\n')
                        stdout.flush()

                    elif sub_command == 'attack/transfer':

                        stdout.write(self.attack_transfer() + '\n')
                        stdout.flush()

                    else:
                        stderr.write('Unknown sub command: %s\n' % (sub_command))
                        stderr.flush()

                else:
                    stderr.write('Unknown command: %s\n' % (command))
                    stderr.flush()
            except EOFError:
                return

    def update_settings(self, options):
        '''
        Method to update game settings at the start of a new game.
        '''
        key, value = options
        self.settings[key] = value

    def setup_map(self, options):
        '''
        Method to set up essential map data given by the server.
        '''
        map_type = options[0]

        for i in range(1, len(options), 2):

            if map_type == 'super_regions':

                super_region = SuperRegion(options[i], int(options[i + 1]))
                self.map.super_regions.append(super_region)

            elif map_type == 'regions':

                super_region = self.map.get_super_region_by_id(options[i + 1])
                region = Region(options[i], super_region)

                self.map.regions.append(region)
                super_region.regions.append(region)

            elif map_type == 'neighbors':

                region = self.map.get_region_by_id(options[i])
                neighbours = [self.map.get_region_by_id(region_id) for region_id in options[i + 1].split(',')]

                for neighbour in neighbours:
                    region.neighbours.append(neighbour)
                    neighbour.neighbours.append(region)

        if map_type == 'neighbors':

            for region in self.map.regions:

                if region.is_on_super_region_border:
                    continue

                for neighbour in region.neighbours:

                    if neighbour.super_region.id != region.super_region.id:

                        region.is_on_super_region_border = True
                        neighbour.is_on_super_region_border = True

    def update_map(self, options):
        '''
        Method to update our map every round.
        '''
        for i in range(0, len(options), 3):

            region = self.map.get_region_by_id(options[i])
            region.owner = options[i + 1]
            region.troop_count = int(options[i + 2])

    def pick_starting_regions(self, options):
        '''
        Method to select our initial starting regions.

        Currently selects six random regions.
        '''
        shuffled_regions = Random.shuffle(Random.shuffle(options))

        return ' '.join(shuffled_regions[:6])

    def place_troops(self):
        '''
        Method to place our troops.

        Currently keeps places a maximum of two troops on random regions.
        '''
        placements = []
        region_index = 0
        troops_remaining = int(self.settings['starting_armies'])

        owned_regions = self.map.get_owned_regions(self.settings['your_bot'])
        shuffled_regions = Random.shuffle(owned_regions)

        attackers = int(troops_remaining/2)
        defenders = troops_remaining - attackers



        while attackers > 0:
            region = shuffled_regions[region_index]
            borders_enemy = 0

            for neighbour in list(region.neighbours):
                if neighbour.owner != region.owner:
                    borders_enemy = 1

            if borders_enemy == 1:
                    placements.append([region.id, 3])

                    region.troop_count += 3
                    attackers -= 3

            region_index += 1
            if region_index == len(shuffled_regions):
                region_index = 0

        while defenders > 0:
            region = shuffled_regions[region_index]
            if region.is_on_super_region_border and troops_remaining > 1:

                placements.append([region.id, 2])

                region.troop_count += 2
                defenders -= 2

            else:
                 placements.append([region.id, 1])

                 region.troop_count += 1
                 defenders -= 1

            region_index += 1
            if region_index == len(shuffled_regions):
                region_index = 0

        return ', '.join(['%s place_armies %s %d' % (self.settings['your_bot'], placement[0],
            placement[1]) for placement in placements])

    def attack_transfer(self):
        '''
        Method to attack another region or transfer troops to allied regions.

        Currently checks whether a region has more than six troops placed to attack,
        or transfers if more than 1 unit is available.
        '''
        attack_transfers = []
        enemies = []
        allies = []
        owned_regions = self.map.get_owned_regions(self.settings['your_bot'])

        for region in owned_regions:
            neighbours = list(region.neighbours)
            for neighbour in neighbours:
                if neighbour.owner != region.owner:
                    enemies.append(neighbour)
                else:
                    allies.append(neighbour)

            while len(enemies) > 0 or len(allies) > 0:
                if len(enemies) > 0:
                    target_region = enemies[Random.randrange(0, len(enemies))]

                    if target_region.troop_count * 1.2 <= region.troop_count:
                        attack_transfers.append([region.id, target_region.id, int((region.troop_count * .9)-.5)])
                        region.troop_count -= int((region.troop_count * .9)-.5)
                    else:
                        enemies.remove(target_region)

                if len(allies) > 0:
                    target_region = allies[Random.randrange(0, len(allies))]
                    if region.troop_count > 1 and target_region.is_on_super_region_border:
                        attack_transfers.append([region.id, target_region.id, region.troop_count - 1])
                        region.troop_count = 1
                    else:
                        allies.remove(target_region)

        if len(attack_transfers) == 0:
            return 'No moves'

        return ', '.join(['%s attack/transfer %s %s %s' % (self.settings['your_bot'], attack_transfer[0],
            attack_transfer[1], attack_transfer[2]) for attack_transfer in attack_transfers])

class Map(object):
    '''
    Map class
    '''
    def __init__(self):
        '''
        Initializes empty lists for regions and super regions.
        '''
        self.regions = []
        self.super_regions = []

    def get_region_by_id(self, region_id):
        '''
        Returns a region instance by id.
        '''
        return [region for region in self.regions if region.id == region_id][0]

    def get_super_region_by_id(self, super_region_id):
        '''
        Returns a super region instance by id.
        '''
        return [super_region for super_region in self.super_regions if super_region.id == super_region_id][0]

    def get_owned_regions(self, owner):
        '''
        Returns a list of region instances owned by `owner`.
        '''
        return [region for region in self.regions if region.owner == owner]

class SuperRegion(object):
    '''
    Super Region class
    '''
    def __init__(self, super_region_id, worth):
        '''
        Initializes with an id, the super region's worth and an empty lists for
        regions located inside this super region
        '''
        self.id = super_region_id
        self.worth = worth
        self.regions = []

class Region(object):
    '''
    Region class
    '''
    def __init__(self, region_id, super_region):
        '''
        '''
        self.id = region_id
        self.owner = 'neutral'
        self.neighbours = []
        self.troop_count = 2
        self.super_region = super_region
        self.is_on_super_region_border = False

class Random(object):
    '''
    Random class
    '''
    @staticmethod
    def randrange(min, max):
        '''
        A pseudo random number generator to replace random.randrange

        Works with an inclusive left bound and exclusive right bound.
        E.g. Random.randrange(0, 5) in [0, 1, 2, 3, 4] is always true
        '''
        return min + int(fmod(pow(clock() + pi, 2), 1.0) * (max - min))

    @staticmethod
    def shuffle(items):
        '''
        Method to shuffle a list of items
        '''
        i = len(items)
        while i > 1:
            i -= 1
            j = Random.randrange(0, i)
            items[j], items[i] = items[i], items[j]
        return items

if __name__ == '__main__':
    '''
    Not used as module, so run
    '''
    Bot().run()
