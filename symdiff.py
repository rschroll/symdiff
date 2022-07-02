class Operation(object):

    def run(self, feed_dict=None):
        if feed_dict and self in feed_dict:
            return feed_dict[self]
        return self._run(feed_dict)

    def _run(self, feed_dict):
        raise NotImplementedError

    def grad(self, other):
        if self is other:
            return ONE
        return self._grad(other)

    def _grad(self, other):
        raise NotImplementedError

    def __add__(self, other):
        return Add(self, other)

    def __radd__(self, other):
        return Add(other, self)

    def __mul__(self, other):
        return Multiply(self, other)

    def __rmul__(self, other):
        return Multiply(other, self)

    def __neg__(self):
        return Multiply(NEGONE, self)

    def __sub__(self, other):
        return Add(self, -other)

    def __rsub__(self, other):
        return Add(other, -self)

    def __div__(self, other):
        return Multiply(self, Inverse(other))

    def __truediv__(self, other):
        return self.__div__(other)

    def __rdiv__(self, other):
        return Multiply(other, Inverse(self))

    def __rtruediv__(self, other):
        return self.__rdiv__(other)

    def __pow__(self, exp):
        if not isinstance(exp, int):
            raise ValueError("Only integer powers allowed.")
        if exp > 0:
            return Multiply(*[self for _ in xrange(exp)])
        if exp < 0:
            return Inverse(Multiply(*[self for _ in xrange(-exp)]))
        return ONE


class Constant(Operation):

    def __init__(self, value, name=None):
        self.default = value
        self.name = name

    def _run(self, feed_dict):
        return self.default

    def _grad(self, other):
        return ZERO

    def __repr__(self):
        if self.name:
            return self.name
        return '<' + hex(id(self)) + '>'


NEGONE = Constant(-1, '-1')
ZERO = Constant(0, '0')
ONE = Constant(1, '1')


class ArgOperation(Operation):

    def __init__(self, *args):
        self.args = [self.make_op(a) for a in args]

    @staticmethod
    def make_op(a):
        if isinstance(a, Operation):
            return a
        return Constant(a)


class Add(ArgOperation):

    def _run(self, feed_dict):
        return sum(a.run(feed_dict) for a in self.args)

    def _grad(self, other):
        return Add(*[a.grad(other) for a in self.args])

    def __repr__(self):
        return '( ' + ' + '.join(map(repr, self.args)) + ' )'


class Multiply(ArgOperation):

    def __new__(cls, *args):
        # Multiplication by zero may produce an array of zeros, which can
        # cause promotion of other things to arrays, unexpectedly.
        if ZERO in args:
            return ZERO
        return super(Multiply, cls).__new__(cls)

    def _run(self, feed_dict):
        return reduce(lambda x,y: x*y, (a.run(feed_dict) for a in self.args))

    def _grad(self, other):
        return Add(*[Multiply(*[self.args[j] if i != j else self.args[j].grad(other)
                                for j in xrange(len(self.args))])
                     for i in xrange(len(self.args))])

    def __repr__(self):
        return '( ' + ' * '.join(map(repr, self.args)) + ' )'


class Inverse(Operation):

    def __init__(self, arg):
        self.arg = arg

    def _run(self, feed_dict):
        return ONE / self.arg.run(feed_dict)

    def _grad(self, other):
        return Multiply(NEGONE, Inverse(Multiply(self.arg, self.arg)),
                        self.arg.grad(other))

    def __repr__(self):
        return '( 1 / ' + repr(self.arg) + ' )'
