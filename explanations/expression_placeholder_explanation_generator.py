# compiler/explanations/expression_placeholder_explanation_generator.py

from explanations.expression_node import ExpressionNode

class PlaceholderExpressionExplanationGenerator:
    """
    Generates two sets of explanations for an ExpressionNode tree:
      1) Placeholder steps (like "STEP 0: <x1> = 3"), showing how placeholders (x1, x2, etc.) 
         are assigned for literals or computed for sub-expressions.
      2) Real (numeric) steps (like "STEP 0: 3 = 3.0"), showing the actual arithmetic.

    Also tracks:
      - A placeholder map (placeholder -> numeric_value) 
      - Snapshots of the map after each step,
      - Final placeholder and final numeric value.

    Typical Usage:
      1. Construct an ExpressionNode-based AST:
         root = ExpressionNode("*",
                    ExpressionNode("+", ExpressionNode("3"), ExpressionNode("5")),
                    ExpressionNode("-", ExpressionNode("10"), ExpressionNode("4")))
      2. Pass the root to PlaceholderExpressionExplanationGenerator(...).
      3. Call generate_explanation(missing_element=0) to produce the dictionary of results.
    """

    def __init__(self, root: ExpressionNode):
        """
        :param root: The root ExpressionNode of the expression tree.
        """
        self.root = root
        
        # Placeholder steps, e.g. STEP 0: <x1> = 3
        self.placeholder_steps = []
        
        # Real steps, e.g. STEP 0: 3 = 3.0
        self.real_steps = []
        
        # Current map: { 'x1': 3.0, 'x2': 5.0, ... }
        self.placeholder_map = {}
        
        # List of dict snapshots after each step
        self.placeholder_map_snapshots = []
        
        # Generates unique placeholder labels: x1, x2, x3, ...
        self.placeholder_counter = 1

    def generate_explanation(self, missing_element: float):
        """
        Evaluates the entire expression tree while building explanations
        in both placeholder and real value forms.

        :param missing_element: The numeric value to substitute for any ExpressionNode
                                where value='?'.
        :return: A dictionary containing:
            {
                "placeholder_steps": [list of str],
                "real_steps": [list of str],
                "placeholder_map": {str: float},
                "placeholder_map_snapshots": [list of dict],
                "final_placeholder": str,
                "final_value": float
            }
        """
        # Reset all tracking variables (useful if the same instance is reused)
        self.placeholder_steps = []
        self.real_steps = []
        self.placeholder_map = {}
        self.placeholder_map_snapshots = []
        self.placeholder_counter = 1
        
        # Recursively compute placeholders & numeric values from the root
        final_placeholder, final_value = self._evaluate_with_placeholders(self.root, missing_element)
        
        return {
            "placeholder_steps": self.placeholder_steps,
            "real_steps": self.real_steps,
            "placeholder_map": self.placeholder_map,
            "placeholder_map_snapshots": self.placeholder_map_snapshots,
            "final_placeholder": final_placeholder,
            "final_value": final_value
        }

    def _evaluate_with_placeholders(self, node: ExpressionNode, missing_element: float):
        """
        Recursively traverse the tree. For each node:
          - If node.value == '?', assign a new placeholder and use `missing_element`.
          - If node is a literal, assign a new placeholder for that value.
          - If node is an operator, recursively evaluate children, 
            then assign a new placeholder for the resulting value.

        Returns: (placeholder_label, numeric_value)
        """
        # 1) Special case: node.value == '?' (missing element)
        if node.value == '?':
            placeholder_label = self._assign_placeholder()
            self.placeholder_map[placeholder_label] = missing_element
            
            # Placeholder step
            step_count_p = len(self.placeholder_steps)
            self.placeholder_steps.append(
                f"STEP {step_count_p}: <{placeholder_label}> = ?"
            )
            
            # Real step
            step_count_r = len(self.real_steps)
            self.real_steps.append(
                f"STEP {step_count_r}: ? = {missing_element}"
            )
            
            self._snapshot_placeholder_map()
            return placeholder_label, missing_element

        # 2) If node is a leaf literal (e.g. '3')
        if node.left is None and node.right is None:
            placeholder_label = self._assign_placeholder()
            numeric_value = float(node.value)  # Convert string to float
            self.placeholder_map[placeholder_label] = numeric_value
            
            # Show each literal introduction
            step_count_p = len(self.placeholder_steps)
            self.placeholder_steps.append(
                f"STEP {step_count_p}: <{placeholder_label}> = {node.value}"
            )
            step_count_r = len(self.real_steps)
            self.real_steps.append(
                f"STEP {step_count_r}: {node.value} = {numeric_value}"
            )
            
            self._snapshot_placeholder_map()
            return placeholder_label, numeric_value

        # 3) Otherwise, it's an operator with left/right children
        operator = node.value
        
        # Recursively handle the left child
        left_placeholder, left_value = self._evaluate_with_placeholders(node.left, missing_element)
        # Recursively handle the right child
        right_placeholder, right_value = self._evaluate_with_placeholders(node.right, missing_element)
        
        # Perform the numeric operation
        result_value = self._perform_calculation(operator, left_value, right_value)
        
        # Create a placeholder for this result
        result_placeholder = self._assign_placeholder()
        self.placeholder_map[result_placeholder] = result_value
        
        # Placeholder step
        step_count_p = len(self.placeholder_steps)
        self.placeholder_steps.append(
            f"STEP {step_count_p}: (<{left_placeholder}> {operator} <{right_placeholder}>) = <{result_placeholder}>"
        )
        
        # Real step
        step_count_r = len(self.real_steps)
        left_str = self._format_number_for_display(left_value)
        right_str = self._format_number_for_display(right_value)
        result_str = self._format_number_for_display(result_value)
        self.real_steps.append(
            f"STEP {step_count_r}: ({left_str} {operator} {right_str}) = {result_str}"
        )
        
        self._snapshot_placeholder_map()
        return result_placeholder, result_value

    def _assign_placeholder(self) -> str:
        """
        Generate a unique placeholder label like x1, x2, x3, ...
        """
        label = f"x{self.placeholder_counter}"
        self.placeholder_counter += 1
        return label

    def _perform_calculation(self, operator: str, left: float, right: float) -> float:
        """
        Perform the math operation given the operator and operand values.
        Supports +, -, *, /.
        """
        if operator == '+':
            return left + right
        elif operator == '-':
            return left - right
        elif operator == '*':
            return left * right
        elif operator == '/':
            # If needed, handle divide-by-zero gracefully
            return left / right
        else:
            raise ValueError(f"Unknown operator: {operator}")

    def _format_number_for_display(self, num: float) -> str:
        """
        Helper to produce a more readable string for the numeric steps.
        Rounds to 4 decimals and removes trailing .0 if integer.
        """
        rounded = round(num, 4)
        if rounded.is_integer():
            return str(int(rounded))
        return str(rounded)

    def _snapshot_placeholder_map(self):
        """
        Capture the current state of the placeholder map (dict) 
        and store it as a snapshot. Each snapshot is a shallow copy.
        """
        self.placeholder_map_snapshots.append(self.placeholder_map.copy())