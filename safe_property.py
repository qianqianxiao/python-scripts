__author__ = 'yoyo.Chen'


class SomeClass(object):
    def __init__(self):
        self._somevalue = 0

    def get_value(self):
        print "calling get"
        return self._somevalue

    def set_value(self, value):
        print "set value"
        self._somevalue = value

    def del_attr(self):
        print 'del value'

    x = property(get_value, set_value, del_attr, "ddd")

obj = SomeClass()
obj.x = 10
print obj.x + 2
del obj.x
print obj.x
