import collections


def add_anmail_in_family(species, animal, family):
    species[family].append(animal)


species = collections.defaultdict(list)
add_anmail_in_family(species, 'cat', 'felidea')

# 通过命名属性获取元组元素而不是通过索引
Foobar = collections.namedtuple('Foobar', ['x', 'y'])
a = Foobar(33, 22)
print a.x