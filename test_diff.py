from symdiff import Constant, Variable, ONE, ZERO

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
