import pytest

from symdiff import Constant, Variable, ONE, ZERO, Add, Multiply

x = Variable('x')
y = Variable('y')
TWO = Constant(2)


### Identity operations

@pytest.mark.identity
def test_add_identity():
    assert x + ZERO == x

@pytest.mark.identity
def test_mult_identity():
    assert x * ONE == x

@pytest.mark.identity
def test_mult_nullspace():
    assert x * ZERO == ZERO

### Combine constants

@pytest.mark.combine
def test_add_constants():
    assert ONE + TWO == Constant(3)

@pytest.mark.combine
def test_add_constants_and_variables():
    assert Add(ONE, x, TWO) == Add(3, x)

@pytest.mark.combine
def test_multiply_constants():
    assert TWO * TWO == Constant(4)

@pytest.mark.combine
def test_multiply_constants_and_variables():
    assert Multiply(TWO, x, TWO) == Multiply(4, x)

### Flatten nested operations

@pytest.mark.flatten
def test_flatten_add():
    assert Add(ONE, Add(x, y)) == Add(ONE, x, y)

@pytest.mark.flatten
def test_flatten_multiply():
    assert Multiply(TWO, Multiply(x, y)) == Multiply(TWO, x, y)

### Simplify with associativity

@pytest.mark.assoc
def test_associativity():
    assert 2 * x + 3 * x == 5 * x
