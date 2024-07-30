from explanations.expression_node import ExpressionNode

class ExpressionTree:
    def __init__(self):
        self.root = None

    def evaluate(self, missing_element: float) -> float:
        return self.root.evaluate(missing_element)

    def print_tree(self, node: ExpressionNode, depth=0) -> str:
        if not node:
            return ''

        result = ''
        indentation = ' ' * (depth * 4)
        if depth > 0:
            indentation += "|-- "

        result += f"{indentation}{node.value}\n"

        if node.left:
            result += self.print_tree(node.left, depth + 1)
        if node.right:
            result += self.print_tree(node.right, depth + 1)

        return result
