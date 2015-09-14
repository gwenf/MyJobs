import re
address_line_1_terms = ['alley',
                        'alley',
                        'ally',
                        'aly',
                        'anex',
                        'annex',
                        'annx',
                        'anx',
                        'arcade',
                        'arcade',
                        'avenue',
                        'ave',
                        'aven',
                        'avenu',
                        'avenue',
                        'avn',
                        'avnue',
                        'bayou',
                        'bayou',
                        'beach',
                        'beach',
                        'bend',
                        'bnd',
                        'bluff',
                        'bluf',
                        'bluff',
                        'bluffs',
                        'bottom',
                        'btm',
                        'bottm',
                        'bottom',
                        'boulevard',
                        'boul',
                        'boulevard',
                        'boulv',
                        'branch',
                        'brnch',
                        'branch',
                        'bridge',
                        'brg',
                        'bridge',
                        'brook',
                        'brook',
                        'brooks',
                        'burg',
                        'burgs',
                        'bypass',
                        'bypa',
                        'bypas',
                        'bypass',
                        'byps',
                        'camp',
                        'cp',
                        'cmp',
                        'canyon',
                        'canyon',
                        'cnyn',
                        'cape',
                        'cpe',
                        'causeway',
                        'causwa',
                        'cswy',
                        'center',
                        'cent',
                        'center',
                        'centr',
                        'centre',
                        'cnter',
                        'cntr',
                        'ctr',
                        'centers',
                        'circle',
                        'circ',
                        'circl',
                        'circle',
                        'crcl',
                        'crcle',
                        'circles',
                        'cliff',
                        'cliff',
                        'cliffs',
                        'cliffs',
                        'club',
                        'club',
                        'common',
                        'commons',
                        'corner',
                        'corner',
                        'corners',
                        'cors',
                        'course',
                        'crse',
                        'court',
                        'ct',
                        'courts',
                        'cts',
                        'cove',
                        'cv',
                        'coves',
                        'creek',
                        'crk',
                        'crescent',
                        'cres',
                        'crsent',
                        'crsnt',
                        'crest',
                        'crossing',
                        'crssng',
                        'xing',
                        'crossroad',
                        'crossroads',
                        'curve',
                        'dale',
                        'dl',
                        'dam',
                        'dm',
                        'divide',
                        'divide',
                        'dv',
                        'dvd',
                        'drive',
                        'driv',
                        'drive',
                        'drv',
                        'drives',
                        'estate',
                        'estate',
                        'estates',
                        'ests',
                        'expressway',
                        'expr',
                        'express',
                        'expressway',
                        'expw',
                        'expy',
                        'extension',
                        'extension',
                        'extn',
                        'extnsn',
                        'extensions',
                        'fall',
                        'falls',
                        'fls',
                        'ferry',
                        'frry',
                        'fry',
                        'field',
                        'fld',
                        'fields',
                        'flds',
                        'flat',
                        'flt',
                        'flats',
                        'flts',
                        'ford',
                        'frd',
                        'fords',
                        'forest',
                        'forests',
                        'frst',
                        'forge',
                        'forge',
                        'frg',
                        'forges',
                        'fork',
                        'frk',
                        'forks',
                        'frks',
                        'fort',
                        'frt',
                        'ft',
                        'freeway',
                        'freewy',
                        'frway',
                        'frwy',
                        'fwy',
                        'garden',
                        'gardn',
                        'grden',
                        'grdn',
                        'gardens',
                        'gdns',
                        'grdns',
                        'gateway',
                        'gatewy',
                        'gatway',
                        'gtway',
                        'gtwy',
                        'glen',
                        'gln',
                        'glens',
                        'green',
                        'grn',
                        'greens',
                        'grove',
                        'grove',
                        'grv',
                        'groves',
                        'harbor',
                        'harbor',
                        'harbr',
                        'hbr',
                        'hrbor',
                        'harbors',
                        'haven',
                        'hvn',
                        'heights',
                        'hts',
                        'highway',
                        'highwy',
                        'hiway',
                        'hiwy',
                        'hway',
                        'hwy',
                        'hill',
                        'hl',
                        'hills',
                        'hls',
                        'hollow',
                        'hollow',
                        'hollows',
                        'holw',
                        'holws',
                        'inlet',
                        'island',
                        'island',
                        'islnd',
                        'islands',
                        'islnds',
                        'iss',
                        'isle',
                        'isles',
                        'junction',
                        'jction',
                        'jctn',
                        'junction',
                        'junctn',
                        'juncton',
                        'junctions',
                        'jcts',
                        'junctions',
                        'key',
                        'ky',
                        'keys',
                        'kys',
                        'knoll',
                        'knol',
                        'knoll',
                        'knolls',
                        'knolls',
                        'lake',
                        'lake',
                        'lakes',
                        'lakes',
                        'land',
                        'landing',
                        'lndg',
                        'lndng',
                        'lane',
                        'ln',
                        'light',
                        'light',
                        'lights',
                        'loaf',
                        'loaf',
                        'lock',
                        'lock',
                        'locks',
                        'locks',
                        'lodge',
                        'ldge',
                        'lodg',
                        'lodge',
                        'loop',
                        'loops',
                        'mall',
                        'manor',
                        'manor',
                        'manors',
                        'mnrs',
                        'meadow',
                        'meadows',
                        'mdws',
                        'meadows',
                        'medows',
                        'mews',
                        'mill',
                        'mills',
                        'mission',
                        'mssn',
                        'motorway',
                        'mount',
                        'mt',
                        'mount',
                        'mountain',
                        'mntn',
                        'mountain',
                        'mountin',
                        'mtin',
                        'mtn',
                        'mountains',
                        'mountains',
                        'neck',
                        'neck',
                        'orchard',
                        'orchard',
                        'orchrd',
                        'oval',
                        'ovl',
                        'overpass',
                        'park',
                        'prk',
                        'parks',
                        'parkway',
                        'parkwy',
                        'pkway',
                        'pkwy',
                        'pky',
                        'parkways',
                        'pkwys',
                        'pass',
                        'passage',
                        'path',
                        'paths',
                        'pike',
                        'pikes',
                        'pine',
                        'pines',
                        'pnes',
                        'place',
                        'plain',
                        'pln',
                        'plains',
                        'plns',
                        'plaza',
                        'plz',
                        'plza',
                        'point',
                        'pt',
                        'points',
                        'pts',
                        'port',
                        'prt',
                        'ports',
                        'prts',
                        'prairie',
                        'prairie',
                        'prr',
                        'radial',
                        'radial',
                        'radiel',
                        'radl',
                        'ramp',
                        'ranch',
                        'ranches',
                        'rnch',
                        'rnchs',
                        'rapid',
                        'rpd',
                        'rapids',
                        'rpds',
                        'rest',
                        'rst',
                        'ridge',
                        'rdge',
                        'ridge',
                        'ridges',
                        'ridges',
                        'river',
                        'river',
                        'rvr',
                        'rivr',
                        'road',
                        'road',
                        'roads',
                        'rds',
                        'route',
                        'row',
                        'rue',
                        'run',
                        'shoal',
                        'shoal',
                        'shoals',
                        'shoals',
                        'shore',
                        'shore',
                        'shr',
                        'shores',
                        'shores',
                        'shrs',
                        'skyway',
                        'spring',
                        'spng',
                        'spring',
                        'sprng',
                        'springs',
                        'spngs',
                        'springs',
                        'sprngs',
                        'spur',
                        'spurs',
                        'square',
                        'sqr',
                        'sqre',
                        'squ',
                        'square',
                        'squares',
                        'squares',
                        'station',
                        'station',
                        'statn',
                        'stn',
                        'stravenue',
                        'strav',
                        'straven',
                        'stravenue',
                        'stravn',
                        'strvn',
                        'strvnue',
                        'stream',
                        'streme',
                        'strm',
                        'street',
                        'strt',
                        'st',
                        'str',
                        'streets',
                        'summit',
                        'sumit',
                        'sumitt',
                        'summit',
                        'terrace',
                        'terr',
                        'terrace',
                        'throughway',
                        'trace',
                        'traces',
                        'trce',
                        'track',
                        'tracks',
                        'trak',
                        'trk',
                        'trks',
                        'trafficway',
                        'trail',
                        'trails',
                        'trl',
                        'trls',
                        'trailer',
                        'trlr',
                        'trlrs',
                        'tunnel',
                        'tunl',
                        'tunls',
                        'tunnel',
                        'tunnels',
                        'tunnl',
                        'turnpike',
                        'turnpike',
                        'turnpk',
                        'underpass',
                        'union',
                        'union',
                        'unions',
                        'valley',
                        'vally',
                        'vlly',
                        'vly',
                        'valleys',
                        'vlys',
                        'viaduct',
                        'via',
                        'viadct',
                        'viaduct',
                        'view',
                        'vw',
                        'views',
                        'vws',
                        'village',
                        'villag',
                        'village',
                        'villg',
                        'villiage',
                        'vlg',
                        'villages',
                        'vlgs',
                        'ville',
                        'vl',
                        'vista',
                        'vist',
                        'vista',
                        'vst',
                        'vsta',
                        'walk',
                        'walks',
                        'wall',
                        'way',
                        'way',
                        'ways',
                        'well',
                        'wells',
                        'wls',
                        'allee',
                        'anex',
                        'arc',
                        'av',
                        'bayoo',
                        'bch',
                        'bend',
                        'blf',
                        'bluffs',
                        'blvd',
                        'bot',
                        'br',
                        'brdge',
                        'brk',
                        'brooks',
                        'burg',
                        'burgs',
                        'byp',
                        'camp',
                        'canyn',
                        'cape',
                        'causeway',
                        'cen',
                        'centers',
                        'cir',
                        'circles',
                        'clb',
                        'clf',
                        'clfs',
                        'common',
                        'commons',
                        'cor',
                        'corners',
                        'course',
                        'court',
                        'courts',
                        'cove',
                        'coves',
                        'creek',
                        'crescent',
                        'crest',
                        'crossing',
                        'crossroad',
                        'crossroads',
                        'curve',
                        'dale',
                        'dam',
                        'div',
                        'dr',
                        'drives',
                        'est',
                        'estates',
                        'exp',
                        'ext',
                        'exts',
                        'fall',
                        'falls',
                        'ferry',
                        'field',
                        'fields',
                        'flat',
                        'flats',
                        'ford',
                        'fords',
                        'forest',
                        'forg',
                        'forges',
                        'fork',
                        'forks',
                        'fort',
                        'freeway',
                        'garden',
                        'gardens',
                        'gateway',
                        'glen',
                        'glens',
                        'green',
                        'greens',
                        'grov',
                        'groves',
                        'harb',
                        'harbors',
                        'haven',
                        'highway',
                        'hill',
                        'hills',
                        'hllw',
                        'ht',
                        'inlt',
                        'is',
                        'islands',
                        'isle',
                        'jct',
                        'jctns',
                        'key',
                        'keys',
                        'knl',
                        'knls',
                        'land',
                        'landing',
                        'lane',
                        'lck',
                        'lcks',
                        'ldg',
                        'lf',
                        'lgt',
                        'lights',
                        'lk',
                        'lks',
                        'loop',
                        'mall',
                        'manors',
                        'mdw',
                        'meadow',
                        'mews',
                        'mill',
                        'mills',
                        'missn',
                        'mnr',
                        'mnt',
                        'mntain',
                        'mntns',
                        'motorway',
                        'nck',
                        'orch',
                        'oval',
                        'overpass',
                        'park',
                        'parks',
                        'parkway',
                        'parkways',
                        'pass',
                        'passage',
                        'path',
                        'pike',
                        'pine',
                        'pines',
                        'pl',
                        'plain',
                        'plains',
                        'plaza',
                        'point',
                        'points',
                        'port',
                        'ports',
                        'pr',
                        'rad',
                        'ramp',
                        'ranch',
                        'rapid',
                        'rapids',
                        'rd',
                        'rdg',
                        'rdgs',
                        'rest',
                        'riv',
                        'roads',
                        'route',
                        'row',
                        'rue',
                        'run',
                        'shl',
                        'shls',
                        'shoar',
                        'shoars',
                        'skyway',
                        'smt',
                        'spg',
                        'spgs',
                        'spur',
                        'spurs',
                        'sq',
                        'sqrs',
                        'sta',
                        'stra',
                        'stream',
                        'street',
                        'streets',
                        'ter',
                        'throughway',
                        'trace',
                        'track',
                        'trafficway',
                        'trail',
                        'trailer',
                        'trnpk',
                        'tunel',
                        'un',
                        'underpass',
                        'unions',
                        'valley',
                        'valleys',
                        'vdct',
                        'view',
                        'views',
                        'vill',
                        'villages',
                        'ville',
                        'vis',
                        'walk',
                        'walks',
                        'wall',
                        'ways',
                        'well',
                        'wells',
                        'wy']

address_line_2_terms = ['apartment','apt',
                        'building','bldg',
                        'office','ofc',
                        'room','rm',
                        'suite','ste',
                        'trailer','trlr',
                        'lobby','lbby',
                        'hangar','hngr',
                        'floor','fl',
                        'basement','bsmt']

po_box_terms = ['po','p.o.', 'p o','po','p']

direction_terms = ['n',
                   'ne',
                   'nw',
                   's',
                   'se',
                   'sw',
                   'e',
                   'w',
                   'north',
                   'northeast',
                   'northwest',
                   'south',
                   'southeast',
                   'southwest',
                   'east',
                   'west']

re_address_1 = re.compile("(?P<stnum>(\d+))\s+((?P<direction>(%s))[,|.]?\s+)?([\w\s]+(?![%s]))(?P<sttype>(%s))?" % ("|".join(direction_terms),
                                                                         "|".join(address_line_1_terms),"|".join(address_line_1_terms)))

# re_address_1 = re.compile("(?P<stnum>(\d+)).*$")
#
# re_direction = re.compile("\s((?P<direction>(%s))[,|.])\s" % "|".join(direction_terms))
#
# re_street_tag = re.compile("\s(?P<sttype>(%s))\b" % "|".join(address_line_1_terms))

re_address_1_po = re.compile("(?P<pkey>(%s))(\s*[box|bo|b])?\s+(?P<ponum>(\d+))$" % "|".join(po_box_terms))

re_address_2 = re.compile("(?P<a2id>((%s[\s|,|.])|#))\s*(?P<a2string>(\w+))$" % "|".join(po_box_terms + address_line_2_terms))

def identify_address(input_string):
    properties = []
    input_string = input_string.strip().lower()
    match = re_address_1.search(input_string)
    if match:
        for i in range(10):
            try:
                print match.group(i)
            except:
                break
        print match.group('stnum')
        print match.group('direction')

        print match.group('sttype')
        properties.append('formatmatch')
    else:
        properties.append('noformat')

    match = re_address_1_po.search(input_string)
    if match:
        print match.group('pkey')
        print match.group('ponum')
        properties.append('formatpomatch')
    else:
        properties.append('nopoformat')

    match = re_address_2.search(input_string)
    if match:
        print match.group('a2id')
        print match.group('a2string')
        properties.append('format2match')
    else:
        properties.append('no2format')

    return properties

def