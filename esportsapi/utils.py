import collections
import copy
import pprint as ppr

_printer = ppr.PrettyPrinter(indent=2)

def pprint(x):
    _printer.pprint(x)
    return x

def fmap(f, d):
    m = {}
    for k, v in d.items():
        m[k] = f(v)
    return m

def group_by(coll, f):
    d = {}
    for x in coll:
        k = f(x)
        lst = d.get(k, [])
        lst.append(x)
        d[k] = lst
    return d

def first(coll):
    return coll[0]

def last(coll):
    return coll[-1]

def getter(n):
    return lambda x: x[n]

def update(d, k, f, *args):
    nd = copy.deepcopy(d)
    nd[k] = f(d.get(k, None), *args)
    return nd

def assoc(d, k, v):
    nd = copy.deepcopy(d)
    nd[k] = v
    return nd

def zipmap(ks, vs):
    return {k: v for (k, v) in zip(ks, vs)}

def normal_dict(d):
    if isinstance(d, collections.OrderedDict):
        d = dict(d)
        for k, v in d.items():
            d[k] = normal_dict(v)
        return d
    elif isinstance(d, list):
        return list(map(normal_dict, d))
    else:
        return d
