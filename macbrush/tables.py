from collections import OrderedDict

class TableField(object):

    def __init__(self, idx, name="TableField_", decoder=lambda I:I):
        if isinstance(idx, (tuple, list)): idx = ".".join(map(str, idx))
        self.index = idx
        if not isinstance(self.index, tuple): self.index = (self.index,)
        self.name = name
        self.decoder = decoder

    def value(self, v):
        return self.decoder(v)

class TableIntegerField(TableField):

    def __init__(self, idx, **kw):
        kw['decoder'] = int
        super(TableIntegerField, self).__init__(idx, **kw)

class TableMACField(TableField):

    def __init__(self, idx, **kw):
        super(TableMACField, self).__init__(idx, **kw)

    def value(self, v):
        return "".join(map(lambda b: "%02X" % ord(b), v))

class BasicTableIndex(object):

    def decode_index(self, oid):
        return ".".join(map(str, oid[-self._IndexSize:]))

class IntegerTableIndex(object):

    def decode_index(self, oid):
        return int(oid[-1])

class MACTableIndex(object):

    def decode_index(self, oid):
        return "".join(map(lambda x: "%02X" % x, oid[-6:]))


def get_class_attributes_dict (listname, bases, attrs, ofinstance):
    """
    This function, used in a metaclass, looks for all attributes of given instance within the
    class currently being created and all its superclasses. Next it sorts the found attributes
    on their '_creation_counter' attribute (if defined), removes them from the attribute dictionary
    and returns them as an OrderedDict.

    This allows us to define TLV structures in an elegant fashion.

    This code is based on the way Django project's ORM Model classes are defined.
    """
    attrs = [ (attrname, attrs.pop(attrname)) for (attrname, obj) in attrs.items() if isinstance (attrs[attrname], ofinstance) ]

    try:
        attrs.sort ( lambda x,y : cmp(x[1]._creation_counter, y[1]._creation_counter) )
    except AttributeError:
        pass

    for base in bases[::-1]:
        if hasattr(base, listname):
            attrs = getattr(base, listname).items() + attrs

    return OrderedDict(attrs)

def get_class_attribute (attrname, bases, attrs):
    """
    Get a class attribute from the current class or from its superclasses.
    """
    if attrname in attrs: return attrs[attrname]
    for base in bases[::-1]:
        if hasattr(base, attrname): return getattr(base, attrname)
    return None


class TableMeta(type):

    def __new__(cls,  name, bases, attrs):

        attrs['table_index_decoder'] = lambda x:x;
        fields = get_class_attributes_dict( 'fields', bases, attrs, TableField)

        tfi = {}
        for n, f in fields.items():
            f.name = n
            tfi[f.index] = f

        attrs['table_field_index'] = tfi
        return type.__new__(cls, name, bases, attrs)

class Table(object):
    __metaclass__ = TableMeta

    _IndexSize = 1

    def __init__(self, root):
        self.root = root
        self.results = {}
        root = self._ensure_tuple_oid(root)

    def _ensure_tuple_oid(self, oid):
        if isinstance(oid, str):
            oid = tuple(oid.split("."))
        return oid

    def __contains__(self, oid):
        oid = self._ensure_tuple_oid(oid)
        return oid[0:len(self.root)] == self.root

    def field_name(self, idx):
        if idx in self.table_field_index:
            return self.table_field_index[idx].name
        return ".".join(map(str,idx))

    def field_value(self, idx, value):
        if idx in self.table_field_index:
            try:
                return self.table_field_index[idx].value(value)
            except TypeError:
                return None
        return value

    def insert(self, oid, value):
        index = self.decode_index(oid)
        field_index = oid[len(self.root):-self._IndexSize]
        self.results.setdefault(index, {})
        self.results[index][self.field_name(field_index)] = self.field_value(field_index,value)

