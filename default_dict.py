import collections


def add_anmail_in_family(species, animal, family):
    species[family].append(animal)


species = collections.defaultdict(list)
add_anmail_in_family(species, 'cat', 'felidea')