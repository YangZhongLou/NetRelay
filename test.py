
from collections import defaultdict

def constant_factory(value):
    return lambda: value
d = defaultdict(constant_factory('hello'))
d.update(name='John', action='ran')

d["yang"] = "yang"

print(d)
print('%(name)s %(action)s to %(object)s' % d)

a = {
    "name" : "yang",
    "name1" : "yang1",
}
print(a)