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
        return Multiply(self, Power(other, NEGONE))

    def __rtruediv__(self, other):
        return Multiply(other, Power(self, NEGONE))

    def __pow__(self, other):
        return Power(self, other)

    def __rpow__(self, other):
        return Power(other, self)

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


class Power(Operation):

    def __init__(self, base, exponent):
        self.base = self.make_op(base)
        self.exponent = self.make_op(exponent)
        if not isinstance(self.exponent, Constant):
            raise NotImplementedError('Only constant exponents currently supported')

    def partial(self, other):
        return Multiply(self.exponent,
                        Power(self.base, Constant(self.exponent.value - 1)),
                        self.base.partial(other))

    def __eq__(self, other):
        if not isinstance(other, Power):
            return False
        return self.base == other.base and self.exponent == other.exponent

    def __repr__(self):
        return f'{self.base} ^ {self.exponent}'
