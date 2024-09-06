def sane_repr(*attrs):
    if "id" not in attrs and "pk" not in attrs:
        attrs = ("id",) + attrs

    def _repr(self):
        cls = type(self).__name__

        pairs = (f"{a}={getattr(self, a, None)!r}" for a in attrs)

        return "<{} at 0x{:x}: {}>".format(cls, id(self), ", ".join(pairs))

    return _repr


def sane_str(*attrs):
    if "id" not in attrs and "pk" not in attrs:
        attrs = ("id",) + attrs

    def _str(self):
        cls = type(self).__name__

        pairs = (f"{a}={getattr(self, a, None)!r}" for a in attrs)

        return "{}({})".format(cls, ", ".join(pairs))

    return _str
