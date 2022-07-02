import numbers

class Operation:

    def partial(self, other):
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

    def __truediv__(self, other):
        return Multiply(self, Inverse(other))

    def __rtruediv__(self, other):
        return Multiply(other, Inverse(self))

    def __pow__(self, exp):
        if not isinstance(exp, int):
            raise ValueError("Only integer powers allowed.")
        if exp > 0:
            return Multiply(*[self for _ in xrange(exp)])
        if exp < 0:
            return Inverse(Multiply(*[self for _ in xrange(-exp)]))
        return ONE

    @staticmethod
    def make_op(a):
        if isinstance(a, Operation):
            return a
        return Constant(a)


class Constant(Operation):

    def __init__(self, value):
        if not isinstance(value, numbers.Number):
            raise TypeError(f'{value} is not a number')
        self.value = value

    def partial(self, other):
        return ZERO

    def __repr__(self):
        return repr(self.value)

    def __eq__(self, other):
        other = self.make_op(other)
        if not isinstance(other, Constant):
            return False
        return self.value == other.value


NEGONE = Constant(-1)
ZERO = Constant(0)
ONE = Constant(1)


class Variable(Operation):

    def __init__(self, name):
        if not isinstance(name, str):
            raise TypeError('name must be a string')
        self.name = name

    def partial(self, other):
        if other is self:
            return ONE
        return ZERO

    def __repr__(self):
        return self.name


class ArgOperation(Operation):

    def __init__(self, *args):
        self.args = [self.make_op(a) for a in args]

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.args == other.args


class Add(ArgOperation):

    def partial(self, other):
        return Add(*[a.partial(other) for a in self.args])

    def __repr__(self):
        return '( ' + ' + '.join(map(repr, self.args)) + ' )'


class Multiply(ArgOperation):

    def __new__(cls, *args):
        # Multiplication by zero may produce an array of zeros, which can
        # cause promotion of other things to arrays, unexpectedly.
        if ZERO in args:
            return ZERO
        return super(Multiply, cls).__new__(cls)

    def partial(self, other):
        return Add(*[Multiply(*[self.args[j] if i != j else self.args[j].partial(other)
                                for j in range(len(self.args))])
                     for i in range(len(self.args))])

    def __repr__(self):
        return '( ' + ' * '.join(map(repr, self.args)) + ' )'


class Inverse(Operation):

    def __init__(self, arg):
        self.arg = arg

    def partial(self, other):
        return Multiply(NEGONE, Inverse(Multiply(self.arg, self.arg)),
                        self.arg.partial(other))

    def __repr__(self):
        return '( 1 / ' + repr(self.arg) + ' )'
