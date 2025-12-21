from chuk_math_gym.expression_generator.utilities.random_number_generator import (
    generate_random_number,
)
from chuk_math_gym.expression_generator.utilities.random_operator_generator import (
    generate_random_operator,
)
from chuk_math_gym.expression_generator.arithmetic_expression_generator import (
    ArithmeticExpressionGenerator,
)


def test_generate_random_number_integer():
    result = generate_random_number(1, 10, allow_negative=False, allow_decimals=False)
    assert isinstance(result, int)
    assert 1 <= result <= 10


def test_generate_random_number_negative():
    result = generate_random_number(1, 10, allow_negative=True, allow_decimals=False)
    assert isinstance(result, int)
    assert -10 <= result <= 10


def test_generate_random_number_decimal():
    result = generate_random_number(
        1, 10, allow_negative=False, allow_decimals=True, decimal_places=3
    )
    assert isinstance(result, float)
    assert 1 <= result <= 10
    assert round(result, 3) == result  # Ensures proper decimal precision


def test_generate_random_operator_basic():
    operators = {"+", "-", "*", "/"}
    result = generate_random_operator(include_advanced_operators=False, allow_division=True)
    assert result in operators


def test_generate_random_operator_no_division():
    operators = {"+", "-", "*"}
    result = generate_random_operator(include_advanced_operators=False, allow_division=False)
    assert result in operators


def test_generate_random_operator_advanced():
    operators = {"+", "-", "*", "/", "%", "**"}
    result = generate_random_operator(include_advanced_operators=True, allow_division=True)
    assert result in operators


def test_generate_expression_very_easy():
    eg = ArithmeticExpressionGenerator()
    expression = eg.generate_random_expression("very easy")
    assert isinstance(expression, str)
    # For very easy, expressions should be simple, check that it does not contain advanced operators
    assert not any(op in expression for op in ["%", "**"])


def test_generate_expression_easy():
    eg = ArithmeticExpressionGenerator()
    expression = eg.generate_random_expression("easy")
    assert isinstance(expression, str)
    assert not any(op in expression for op in ["%", "**"])


def test_generate_expression_medium():
    eg = ArithmeticExpressionGenerator()
    expression = eg.generate_random_expression("medium")
    assert isinstance(expression, str)


def test_generate_expression_hard():
    eg = ArithmeticExpressionGenerator()
    expression = eg.generate_random_expression("hard")
    assert isinstance(expression, str)
    assert any(op in expression for op in ["+", "-", "*", "/"])


def test_generate_expression_very_hard():
    eg = ArithmeticExpressionGenerator()
    expression = eg.generate_random_expression("very hard")
    assert isinstance(expression, str)
    # Verify inclusion of possible advanced operators
    assert any(op in expression for op in ["%", "**", "+", "-", "*", "/"])


def test_generate_expression_pretty_easy():
    """Test pretty easy difficulty level."""
    eg = ArithmeticExpressionGenerator()
    expression = eg.generate_random_expression("pretty easy")
    assert isinstance(expression, str)


def test_generate_expression_pretty_hard():
    """Test pretty hard difficulty level."""
    eg = ArithmeticExpressionGenerator()
    expression = eg.generate_random_expression("pretty hard")
    assert isinstance(expression, str)


def test_generate_expression_unknown_difficulty():
    """Test unknown difficulty raises error."""
    import pytest

    eg = ArithmeticExpressionGenerator()
    with pytest.raises(ValueError, match="Unknown difficulty"):
        eg.generate_random_expression("impossible")


def test_needs_parens_with_operators():
    """Test needs_parens with expressions containing operators."""
    from chuk_math_gym.expression_generator.arithmetic_expression_generator import (
        needs_parens,
    )

    assert needs_parens("3 + 5")
    assert needs_parens("3 * 5")
    assert needs_parens("3 - 5")
    assert needs_parens("3 / 5")


def test_needs_parens_simple_number():
    """Test needs_parens with simple numbers."""
    from chuk_math_gym.expression_generator.arithmetic_expression_generator import (
        needs_parens,
    )

    assert not needs_parens("42")
    assert not needs_parens("-42")
    assert not needs_parens("3.14")


def test_needs_parens_negative_with_operator():
    """Test needs_parens with negative number containing operator."""
    from chuk_math_gym.expression_generator.arithmetic_expression_generator import (
        needs_parens,
    )

    # Negative with operator should need parens
    assert needs_parens("-3 + 5")
    assert needs_parens("-3 - 5")


def test_needs_parens_with_spaces():
    """Test needs_parens with expression containing spaces."""
    from chuk_math_gym.expression_generator.arithmetic_expression_generator import (
        needs_parens,
    )

    # Spaces indicate compound expression
    assert needs_parens("3 5")  # has space


def test_format_number_integer():
    """Test format_number with integer (0 decimal places)."""
    from chuk_math_gym.expression_generator.arithmetic_expression_generator import (
        format_number,
    )

    result = format_number(42.7, decimal_places=0)
    assert result == "43"

    result = format_number(-5.4, decimal_places=0)
    assert result == "-5"


def test_format_number_decimal():
    """Test format_number with decimal places."""
    from chuk_math_gym.expression_generator.arithmetic_expression_generator import (
        format_number,
    )

    result = format_number(3.14159, decimal_places=2)
    assert result == "3.14"

    result = format_number(-12.999, decimal_places=2)
    assert result == "-13.00"


def test_maybe_wrap_wraps_with_chance():
    """Test maybe_wrap with high chance."""
    import random

    from chuk_math_gym.expression_generator.arithmetic_expression_generator import (
        maybe_wrap,
    )

    random.seed(42)
    # With chance=1.0, should always wrap complex expressions
    result = maybe_wrap("3 + 5", chance=1.0)
    assert result == "(3 + 5)"


def test_maybe_wrap_no_wrap_simple():
    """Test maybe_wrap doesn't wrap simple numbers."""
    from chuk_math_gym.expression_generator.arithmetic_expression_generator import (
        maybe_wrap,
    )

    # Simple number shouldn't need parens regardless of chance
    result = maybe_wrap("42", chance=1.0)
    assert result == "42"


def test_generate_expression_deep():
    """Test generate_expression with high max_depth."""
    import random

    random.seed(42)

    eg = ArithmeticExpressionGenerator()
    # Force deep recursion by setting depth=0 and high max_depth
    expression = eg.generate_expression(
        depth=0,
        max_depth=5,
        allow_negative=True,
        allow_decimals=True,
        min_number=1,
        max_number=10,
        include_advanced_operators=False,
        allow_division=True,
        decimal_places=2,
    )
    assert isinstance(expression, str)


def test_generate_expression_with_division():
    """Test generate_expression with division operator."""
    import random

    random.seed(100)

    eg = ArithmeticExpressionGenerator()
    # Generate many times to hit division paths
    for i in range(50):
        random.seed(i * 7)  # Different seeds
        expression = eg.generate_expression(
            depth=0,
            max_depth=3,
            allow_negative=True,
            allow_decimals=True,
            min_number=1,
            max_number=10,
            include_advanced_operators=False,
            allow_division=True,
            decimal_places=2,
        )
        assert isinstance(expression, str)


def test_generate_expression_force_recursion():
    """Test generate_expression forcing deep recursion."""
    import random

    eg = ArithmeticExpressionGenerator()

    # Generate many expressions with high max_depth and low probability of leaf
    # This forces the else branch (lines 100-144)
    for seed in range(100):
        random.seed(seed)
        expression = eg.generate_expression(
            depth=0,
            max_depth=10,  # High max_depth forces recursion
            allow_negative=True,
            allow_decimals=True,
            min_number=1,
            max_number=10,
            include_advanced_operators=False,
            allow_division=True,
            decimal_places=2,
        )
        assert isinstance(expression, str)


def test_generate_expression_division_path():
    """Test generate_expression specifically hitting division code path."""
    import random
    from unittest.mock import patch

    eg = ArithmeticExpressionGenerator()

    # Force division operator to be selected
    with patch(
        "chuk_math_gym.expression_generator.arithmetic_expression_generator.generate_random_operator",
        return_value="/",
    ):
        random.seed(999)
        expression = eg.generate_expression(
            depth=0,
            max_depth=3,
            allow_negative=True,
            allow_decimals=True,
            min_number=1,
            max_number=10,
            include_advanced_operators=False,
            allow_division=True,
            decimal_places=2,
        )
        assert isinstance(expression, str)


def test_generate_expression_division_by_zero_avoidance():
    """Test that division by zero is avoided."""
    import random
    from unittest.mock import patch

    eg = ArithmeticExpressionGenerator()

    # Force division operator and zero for the right operand
    call_count = [0]

    def mock_generate_number(*args, **kwargs):
        call_count[0] += 1
        # Return 0 on first call (right operand), then 5
        if call_count[0] <= 2:
            return 0
        return 5

    with patch(
        "chuk_math_gym.expression_generator.arithmetic_expression_generator.generate_random_operator",
        return_value="/",
    ):
        with patch(
            "chuk_math_gym.expression_generator.arithmetic_expression_generator.generate_random_number",
            side_effect=mock_generate_number,
        ):
            random.seed(42)
            expression = eg.generate_expression(
                depth=0,
                max_depth=3,
                allow_negative=True,
                allow_decimals=False,
                min_number=1,
                max_number=10,
                include_advanced_operators=False,
                allow_division=True,
                decimal_places=0,
            )
            assert isinstance(expression, str)


def test_generate_expression_non_division_operator():
    """Test generate_expression with non-division operators hitting else branch."""
    import random
    from unittest.mock import patch

    eg = ArithmeticExpressionGenerator()

    # Force + operator (not division) - this tests the else branch at line 106
    with patch(
        "chuk_math_gym.expression_generator.arithmetic_expression_generator.generate_random_operator",
        return_value="+",
    ):
        # Force random.random() to return high value to enter else branch
        with patch("random.random", return_value=0.99):
            random.seed(42)
            expression = eg.generate_expression(
                depth=0,
                max_depth=5,
                allow_negative=True,
                allow_decimals=True,
                min_number=1,
                max_number=10,
                include_advanced_operators=False,
                allow_division=True,
                decimal_places=2,
            )
            assert isinstance(expression, str)
            # Expression should contain the + operator
            assert "+" in expression or expression.replace(".", "").replace("-", "").isdigit()


def test_generate_expression_else_branch_decimals():
    """Test generate_expression else branch with decimals enabled."""
    from unittest.mock import patch

    eg = ArithmeticExpressionGenerator()

    # Force high random value to enter else branch, with multiplication
    with patch(
        "chuk_math_gym.expression_generator.arithmetic_expression_generator.generate_random_operator",
        return_value="*",
    ):
        with patch("random.random", return_value=0.99):
            expression = eg.generate_expression(
                depth=0,
                max_depth=5,
                allow_negative=True,
                allow_decimals=True,  # This tests line 106 else path
                min_number=1,
                max_number=10,
                include_advanced_operators=False,
                allow_division=True,
                decimal_places=3,
            )
            assert isinstance(expression, str)


def test_generate_expression_else_branch_direct():
    """Test generate_expression forcing else branch by patching random at module level."""
    from unittest.mock import patch

    eg = ArithmeticExpressionGenerator()

    # Create a counter to control random behavior
    call_count = [0]

    def mock_random():
        call_count[0] += 1
        # First call: return high value to enter else branch (line 99)
        # Subsequent calls: return low value to wrap expressions
        if call_count[0] == 1:
            return 0.99  # Enter else branch
        return 0.1  # Low value for maybe_wrap calls

    # Patch random.random at the module level
    with patch(
        "chuk_math_gym.expression_generator.arithmetic_expression_generator.random.random",
        side_effect=mock_random,
    ):
        with patch(
            "chuk_math_gym.expression_generator.arithmetic_expression_generator.generate_random_operator",
            return_value="+",
        ):
            expression = eg.generate_expression(
                depth=1,  # depth > 0 so threshold < 1.0
                max_depth=3,
                allow_negative=True,
                allow_decimals=True,
                min_number=1,
                max_number=10,
                include_advanced_operators=False,
                allow_division=True,
                decimal_places=2,
            )
            assert isinstance(expression, str)
            # Should contain + operator from the else branch
            assert (
                "+" in expression
                or expression.replace(".", "").replace("-", "").lstrip("(").rstrip(")").isdigit()
            )


def test_generate_expression_else_branch_division_zero():
    """Test the division by zero avoidance path in else branch."""
    from unittest.mock import patch

    eg = ArithmeticExpressionGenerator()

    call_count = [0]

    def mock_random():
        call_count[0] += 1
        if call_count[0] == 1:
            return 0.99  # Enter else branch
        return 0.1

    number_call_count = [0]

    def mock_generate_number(*args, **kwargs):
        number_call_count[0] += 1
        # Return 0 for the right_val first time to trigger line 128-131
        if number_call_count[0] == 2:
            return 0
        if number_call_count[0] == 3:
            return 5  # Replacement for zero
        return 3

    with patch(
        "chuk_math_gym.expression_generator.arithmetic_expression_generator.random.random",
        side_effect=mock_random,
    ):
        with patch(
            "chuk_math_gym.expression_generator.arithmetic_expression_generator.generate_random_operator",
            return_value="/",
        ):
            with patch(
                "chuk_math_gym.expression_generator.arithmetic_expression_generator.generate_random_number",
                side_effect=mock_generate_number,
            ):
                expression = eg.generate_expression(
                    depth=1,
                    max_depth=3,
                    allow_negative=True,
                    allow_decimals=True,
                    min_number=1,
                    max_number=10,
                    include_advanced_operators=False,
                    allow_division=True,
                    decimal_places=2,
                )
                assert isinstance(expression, str)


def test_generate_expression_else_branch_all_paths():
    """Test all paths in else branch including maybe_wrap."""
    from unittest.mock import patch

    eg = ArithmeticExpressionGenerator()

    # Need many random values: first high to enter else, rest for maybe_wrap calls
    random_values = [0.99] + [0.1] * 20  # Enough for all maybe_wrap calls
    call_idx = [0]

    def mock_random():
        idx = call_idx[0]
        call_idx[0] += 1
        if idx < len(random_values):
            return random_values[idx]
        return 0.1  # Default fallback

    with patch(
        "chuk_math_gym.expression_generator.arithmetic_expression_generator.random.random",
        side_effect=mock_random,
    ):
        with patch(
            "chuk_math_gym.expression_generator.arithmetic_expression_generator.generate_random_operator",
            return_value="-",
        ):
            expression = eg.generate_expression(
                depth=1,
                max_depth=2,
                allow_negative=False,
                allow_decimals=False,
                min_number=1,
                max_number=10,
                include_advanced_operators=False,
                allow_division=False,
                decimal_places=0,
            )
            assert isinstance(expression, str)
