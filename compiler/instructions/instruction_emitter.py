import os
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any, Dict, List
from jinja2 import Environment, FileSystemLoader
from langchain_ollama.llms import OllamaLLM
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate

from compiler.instructions.output_emitters.json_emitter import emit_json
from compiler.instructions.output_emitters.jsonl_emitter import emit_jsonl
from compiler.instructions.output_emitters.chat_emitter import emit_chat
from compiler.instructions.output_emitters.llama2_emitter import emit_llama2
from compiler.instructions.output_emitters.qa_emitter import emit_qa

class IInstructionEmitter(ABC):
    @abstractmethod
    def emit_instruction(self) -> Dict[str, Any]:
        pass

class InstructionEmitter(IInstructionEmitter):
    def __init__(self, ast: Dict[str, Any] = None, tokens: List[Any] = None, llm: str = None):
        self.ast = ast
        self.tokens = tokens or []
        self.expression = ""  # Ensure this is set

        # Set up the LLM client using LangChain
        if llm:
            self.llm = OllamaLLM(model=llm)
        else:
            self.llm = None

    def emit_instruction(self, step_by_step_template_name = "math_stepbystep_template.jinja") -> Dict[str, Any]:
        # Extract the expression from the ast
        self.expression = self.extract_expression_from_ast(self.ast)

        # Simplify the tokens
        simplified_tokens = self.simplify_tokens(self.tokens)

        # Get the question
        question = self.get_random_instruction()

        # Evaluate the expression
        answer = self.evaluate_expression()

        # Generate the explanation
        explanation = self.generate_explanation()

        # Generate LLM responses only if an LLM is provided
        if self.llm:
            pretty_result = self.get_pretty_result(question, answer)
            step_by_step_result = self.get_step_by_step_explanation(question, answer, explanation, step_by_step_template_name)
        else:
            pretty_result = step_by_step_result = None

        # Build the final instruction dict
        instruction = {
            "instruction": question,
            "expression": self.expression,
            "tokens": simplified_tokens,
            "ast": self.ast,
            "result": answer,
            "explanation": explanation,
            "llm_pretty_result": pretty_result,
            "llm_step_by_step_result": step_by_step_result
        }

        return instruction

    def simplify_tokens(self, tokens: List[Any]) -> List[Dict[str, Any]]:
        """Converts tokens into a simplified representation."""
        return [{'type': token.type, 'value': token.value} for token in tokens]

    def emit_json(self):
        """Emit JSON."""
        return emit_json(self.emit_instruction())

    def emit_jsonl(self):
        """Emit JSON Lines."""
        return emit_jsonl(self.emit_instruction())
    
    def emit_chat(self, step_by_step_template_name = "math_stepbystep_template.jinja"):
        """Emit chat format."""
        return emit_chat(self.emit_instruction(step_by_step_template_name))

    def emit_llama2(self):
        """Emit llama2 format."""
        return emit_llama2(self.emit_instruction())

    def emit_qa(self):
        """Emit Q&A format."""
        return emit_qa(self.emit_instruction())

    def extract_expression_from_ast(self, node: Dict[str, Any]) -> str:
        """
        Extracts a string representation of the expression from the AST
        with minimal parentheses.
        """
        if not node or not isinstance(node, dict):
            return ""

        node_type = node.get("type")

        # 1. Handle unary expression (e.g. -42)
        if node_type == "UnaryExpression":
            # e.g. operator = '-'
            op = node.get("operator", {}).get("value", "")
            operand_str = self.extract_expression_from_ast(node.get("operand"))
            # Typically: '-(3)' or just '-3'; choose your style
            return f"{op}{operand_str}"

        # 2. Handle binary expression (left, operator, right)
        if node_type == "BinaryExpression" or ("operator" in node and "left" in node and "right" in node):
            op = node["operator"]["value"]
            left_node = node.get("left")
            right_node = node.get("right")

            left_expr = self.extract_expression_from_ast(left_node)
            right_expr = self.extract_expression_from_ast(right_node)

            # Determine if parentheses are needed
            left_needs_paren = self._needs_parentheses(left_node, op)
            right_needs_paren = self._needs_parentheses(right_node, op)

            if left_needs_paren:
                left_expr = f"({left_expr})"
            if right_needs_paren:
                right_expr = f"({right_expr})"

            return f"{left_expr} {op} {right_expr}"

        # 3. Handle literal
        if node_type == "Literal" or "value" in node:
            val = node.get("value", "")
            # Convert floats that are whole numbers to int
            if isinstance(val, float) and val.is_integer():
                val = int(val)
            return str(val)

        # Fallback if no recognised node type
        return ""

    def _needs_parentheses(self, sub_ast: Dict[str, Any], parent_op: str) -> bool:
        """Determines if the sub-expression needs parentheses based on the parent operator."""
        if not sub_ast or not isinstance(sub_ast, dict):
            return False
        
        # If it's unary, skip parentheses logic
        if sub_ast.get("type") == "UnaryExpression":
            return False

        # If there's no operator, it might just be a literal
        if "operator" not in sub_ast:
            return False

        child_op = sub_ast["operator"]["value"]
        # Precedence rules
        precedence = {
            '+': 1, '-': 1,
            '*': 2, '/': 2,
            '^': 3
        }

        return precedence.get(child_op, 0) < precedence.get(parent_op, 0)

    def evaluate_expression(self) -> str:
        """Evaluates the expression and returns the result as a string."""
        try:
            result = self.safe_eval(self.expression)
            return str(result)
        except ValueError as error:
            return str(error)

    def get_pretty_result(self, question, answer):
        """Generate a natural language response using the question and answer."""
        response_template = """For the question "{question}" and it's associated expression "{expression}", the result is "{answer}".  Now create a highly readable version of the answer, keep it simple, not LATEX.  Just provide the answer response, no premable, do not change the values for the question or expression."""

        # call the llm
        return self.get_llm_response(response_template.format(expression=self.expression, answer=answer, question=question))

    def get_step_by_step_explanation(self, question, answer, explanation, template_name = "math_stepbystep_template.jinja") -> str:
        """Generate a step-by-step explanation using the Jinja template."""
        #template_name = "math_stepbystep_reflection_template.jinja"
        template_name = "math_stepbystep_template.jinja"

        # Locate the folder containing your template files
        templates_dir = os.path.join(os.path.dirname(__file__), 'prompt_templates')

        # Create a Jinja environment pointing to that folder
        env = Environment(loader=FileSystemLoader(templates_dir))

        # Load the specific template file dynamically based on the template_name parameter
        template = env.get_template(template_name)

        # Render the template, injecting your variables
        rendered_output = template.render(
            question=question,
            expression=self.expression,
            answer=answer,
            explanation=explanation
        )

        # If you still wish to pass the rendered output to your LLM, do so here
        return self.get_llm_response(rendered_output)


    def get_llm_response(self, input_text: str) -> str:
        """Get a response from the LLM."""
        if self.llm:
            try:
                prompt = PromptTemplate(input_variables=["input_text"], template="{input_text}")
                chain = prompt | self.llm | StrOutputParser()
                response = chain.invoke({"input_text": input_text})
                return response
            except Exception as e:
                return f"Error generating response from LLM: {e}"
        else:
            return input_text  # Fallback to the raw text if no LLM is available