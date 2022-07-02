from symdiff import Constant, Variable, ONE, ZERO, Multiply

x = Variable('x')
y = Variable('y')


def test_const_equality():
    assert Constant(1) == Constant(1)

def test_const_equality_promotion():
    assert Constant(1) == 1

def test_const_inequality():
    assert Constant(1) != Constant(2)

def test_variable_equality():
    assert x == x

def test_variable_inequality():
    # Equality for variables is identity
    assert x != Variable('x')

def test_add_equality():
    assert x + y == x + y

def test_add_inequality():
    assert x + 0 != x + 1

def test_mult_equality():
    assert x * y == x * y

def test_mult_inequality():
    assert x * 1 != x * 2

def test_power_equality():
    assert x ** 2 == x ** 2

def test_power_inequality():
    assert x ** 2 != y ** 2

def test_partial_self():
    assert x.partial(x) == ONE

def test_partial_other():
    assert y.partial(x) == ZERO

def test_partial_add():
    assert (x + y).partial(x) == ONE + ZERO

def test_partial_add_both():
    assert (x + x).partial(x) == ONE + ONE

def test_partial_multiply():
    assert (x * y).partial(x) == ONE * y + ZERO

def test_partial_multiply_both():
    # Note that the order is important, since we don't account for
    # commutivity in equality checking yet.
    assert (x * x).partial(x) == ONE * x + x * ONE

def test_partial_power():
    assert (x**3).partial(x) == Multiply(3, x**2, ONE)

def test_partial_polynomial():
    #assert (3 * x**2 + 4 * x + 1).partial(x) == 6 * x + 4
    deriv = ZERO + 3 * Multiply(2, x**1, 1) + (ZERO + 4 * ONE) + ZERO
    assert (3 * x**2 + 4 * x + 1).partial(x) == deriv

def test_partial_power_of_polynomial():
    #assert ((3 * x + 1)**2).partial(x) == 18 * x + 2
    assert ((3 * x + 1)**2).partial(x) == Multiply(2, (3 * x + 1)**1, (ZERO + 3 * ONE) + ZERO)
