from temp_solution import *

import pytest

def test_factorial_sum():
    # Test with n = 0, should return 0 as there are no numbers to sum
    assert factorial_sum(0) == 0

    # Test with n = 1, should return 1 as 1! = 1
    assert factorial_sum(1) == 1

    # Test with n = 2, should return 1! + 2! = 1 + 2 = 3
    assert factorial_sum(2) == 3

    # Test with n = 3, should return 1! + 2! + 3! = 1 + 2 + 6 = 9
    assert factorial_sum(3) == 9

    # Test with n = 4, should return 1! + 2! + 3! + 4! = 1 + 2 + 6 + 24 = 33
    assert factorial_sum(4) == 33

    # Test with n = 5, should return 1! + 2! + 3! + 4! + 5! = 1 + 2 + 6 + 24 + 120 = 153
    assert factorial_sum(5) == 153

    # Test with a larger n, n = 10
    # 1! + 2! + 3! + 4! + 5! + 6! + 7! + 8! + 9! + 10!
    # = 1 + 2 + 6 + 24 + 120 + 720 + 5040 + 40320 + 362880 + 3628800 = 4037913
    assert factorial_sum(10) == 4037913

    # Test with a negative number, should return 0 as there are no numbers to sum
    assert factorial_sum(-5) == 0

    # Test with a large number to check performance, n = 20
    # This is more about ensuring the function handles larger inputs without error
    assert factorial_sum(20) == 2561327494111820313

# Run the tests
pytest.main()