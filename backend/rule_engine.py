# backend/rule_engine.py

import re
import logging
from collections import Counter
from models import ASTNode, Rule, AttributeCatalog, db
from sqlalchemy.exc import IntegrityError

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class RuleEngine:
    def __init__(self):
        pass

    def tokenize(self, rule_str):
        """
        Tokenizes the rule string into a list of tokens using regex.
        """
        tokens = re.findall(r"\(|\)|AND|OR|>=|<=|>|<|=|!=|[\w']+", rule_str)
        logger.debug(f"Tokenized '{rule_str}' into tokens: {tokens}")
        return tokens

    def parse_expression(self, tokens):
        tokens = iter(tokens)
        current_token = None

        def next_token():
            nonlocal current_token
            try:
                current_token = next(tokens)
                logger.debug(f"Next token: {current_token}")
                return current_token
            except StopIteration:
                current_token = None
                return None

        def parse_operand():
            if current_token is None:
                raise ValueError("Unexpected end of input")
            attribute = current_token
            next_token()  # Move to the next token
            if current_token is None:
                # This means we have a constant without an operator, e.g., 'True' or 'False'
                if attribute.lower() in ['true', 'false']:
                    operand = {'constant': attribute.lower() == 'true'}
                    logger.debug(f"Parsed constant operand: {operand}")
                    next_token()
                    return operand
                else:
                    raise ValueError(f"Unexpected end of input after '{attribute}'")
            comparison = current_token
            if comparison not in [">", "<", ">=", "<=", "=", "!="]:
                raise ValueError(f"Invalid comparison operator: {comparison}")
            next_token()
            value = current_token
            if value is None:
                raise ValueError("Missing value for comparison")
            next_token()
            # Remove quotes from string values
            if value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            else:
                try:
                    value = int(value)
                except ValueError:
                    try:
                        value = float(value)
                    except ValueError:
                        pass
            operand = {'operand': {'attribute': attribute, 'comparison': comparison, 'value': value}}
            logger.debug(f"Parsed operand: {operand}")
            return operand

        def parse_expression_bp(min_bp):
            nonlocal current_token
            if current_token is None:
                next_token()
            token = current_token
            if token == '(':
                next_token()  # Consume '('
                left = parse_expression_bp(0)
                if current_token != ')':
                    raise ValueError("Missing closing parenthesis")
                next_token()  # Consume ')'
            elif token.lower() in ['true', 'false']:
                left = {'constant': token.lower() == 'true'}
                logger.debug(f"Parsed constant expression: {left}")
                next_token()
            else:
                left = parse_operand()
            while current_token and self.get_precedence(current_token) >= min_bp:
                op = current_token
                precedence = self.get_precedence(op)
                assoc = self.get_associativity(op)
                next_bp = precedence + 1 if assoc == 'left' else precedence
                next_token()
                right = parse_expression_bp(next_bp)
                left = {'operator': op, 'left': left, 'right': right}
            return left

        next_token()  # Initialize current_token
        expression = parse_expression_bp(0)
        logger.debug(f"Parsed expression: {expression}")
        return expression



    def get_precedence(self, operator):
        """
        Returns the precedence of the given operator.
        Higher number means higher precedence.
        """
        precedences = {
            'OR': 1,
            'AND': 2,
            '>': 3,
            '<': 3,
            '>=': 3,
            '<=': 3,
            '=': 3,
            '!=': 3
        }
        return precedences.get(operator.upper(), -1)

    def get_associativity(self, operator):
        """
        Returns the associativity of the given operator.
        """
        associativity = {
            'OR': 'left',
            'AND': 'left',
            '>': 'left',
            '<': 'left',
            '>=': 'left',
            '<=': 'left',
            '=': 'left',
            '!=': 'left'
        }
        return associativity.get(operator.upper(), 'left')

    

    def build_ast(self, expression, rule_id):
        """
        Recursively builds ASTNodes from the parsed expression.
        Implements rule simplification and handles operator precedence.
        """
        if 'operator' in expression:
            operator = expression['operator'].upper()
            node = ASTNode(
                rule_id=rule_id,
                node_type="operator",
                operator=operator
            )
            db.session.add(node)
            db.session.flush()  # To get node.id
            node.left_node = self.build_ast(expression['left'], rule_id).id
            node.right_node = self.build_ast(expression['right'], rule_id).id
            return node
        elif 'operand' in expression:
            operand = expression['operand']
            # Validate attribute
            data_type = self.validate_attribute(operand['attribute'])
            # Convert value to string for storage
            value_str = str(operand['value'])
            node = ASTNode(
                rule_id=rule_id,
                node_type="operand",
                attribute=operand['attribute'],
                comparison=operand['comparison'],
                value=value_str
            )
            db.session.add(node)
            db.session.flush()
            return node
        elif 'constant' in expression:
            # Handle constant expressions (True/False)
            constant_value = expression['constant']
            node = ASTNode(
                rule_id=rule_id,
                node_type="constant",
                value=str(constant_value)  # Store as string 'True' or 'False'
            )
            db.session.add(node)
            db.session.flush()
            return node
        else:
            raise ValueError("Invalid expression structure")


    def validate_attribute(self, attribute):
        """
        Validates that the attribute exists in the catalog.
        """
        catalog = AttributeCatalog.query.filter_by(attribute_name=attribute).first()
        if not catalog:
            raise ValueError(f"Attribute '{attribute}' is not in the catalog")
        return catalog.data_type

    def create_rule(self, name, rule_string):
        """
        Creates a new rule by parsing the rule string and building the AST.
        """
        try:
            tokens = self.tokenize(rule_string)
            expression = self.parse_expression(tokens)
            rule = Rule(name=name)
            db.session.add(rule)
            db.session.flush()  # To get rule.id

            # Build the AST for the rule
            root_node = self.build_ast(expression, rule.id)
            if not root_node:
                raise ValueError("Failed to build AST for the rule.")

            # Assign the root_node_id
            rule.root_node_id = root_node.id

            db.session.commit()
            logger.debug(f"Rule '{name}' created successfully with ID {rule.id}")
            return rule
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"IntegrityError when creating rule '{name}': {e.orig}")
            raise ValueError(f"Rule with name '{name}' already exists.")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Exception when creating rule '{name}': {str(e)}")
            raise ValueError(f"Failed to create rule: {str(e)}")

    def combine_rules(self, rule_strings, combined_rule_name="combined_rule", combine_operator="AND"):
        """
        Combines multiple rule strings into a single rule with an optimized AST.

        Parameters:
            - rule_strings (list of str): List of rule definitions as strings.
            - combined_rule_name (str): Name for the combined rule.
            - combine_operator (str): Operator to use when combining rules ('AND' or 'OR').

        Returns:
            - combined_rule (Rule): The newly created combined rule.
        """
        try:
            if not rule_strings:
                raise ValueError("No rules provided for combination.")
            if len(rule_strings) < 2:
                raise ValueError("At least two rules are required to combine.")

            parsed_expressions = []

            # Parse each rule string into expressions
            for rule_str in rule_strings:
                tokens = self.tokenize(rule_str)
                expression = self.parse_expression(tokens)
                parsed_expressions.append(expression)

            # Combine all expressions using the specified operator
            combined_expression = self.combine_expressions(parsed_expressions, combine_operator)

            # Simplify the combined expression
            simplified_expression = self.simplify_expression(combined_expression)

            # Build and store the combined AST
            combined_rule = Rule(name=combined_rule_name)
            db.session.add(combined_rule)
            db.session.flush()  # To get combined_rule.id

            root_node = self.build_ast(simplified_expression, combined_rule.id)
            if not root_node:
                raise ValueError("Failed to build AST for the combined rule.")

            combined_rule.root_node_id = root_node.id

            db.session.commit()
            logger.debug(f"Combined rule '{combined_rule_name}' created successfully with ID {combined_rule.id}")
            return combined_rule
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to combine rules: {str(e)}")
            raise ValueError(f"Failed to combine rules: {str(e)}")


    def combine_expressions(self, expressions, operator):
        """
        Combines multiple expressions using the specified operator, ensuring proper nesting and balancing.
        """
        if not expressions:
            return None
        elif len(expressions) == 1:
            return expressions[0]
        else:
            # Recursively combine expressions in a balanced manner
            mid = len(expressions) // 2
            left = self.combine_expressions(expressions[:mid], operator)
            right = self.combine_expressions(expressions[mid:], operator)
            return {'operator': operator, 'left': left, 'right': right}


    def handle_range_overlap(self, operand1, operand2, operator):
        """
        Handles overlapping range conditions for the same attribute and simplifies them.

        Parameters:
            - operand1, operand2: Operands to compare.
            - operator: The logical operator ('AND' or 'OR').

        Returns:
            - A simplified operand if possible, else None.
        """
        attr = operand1['attribute']
        comp1 = operand1['comparison']
        val1 = operand1['value']
        comp2 = operand2['comparison']
        val2 = operand2['value']

        # Ensure values are numeric
        try:
            val1 = float(val1)
            val2 = float(val2)
        except ValueError:
            # Cannot handle non-numeric values
            return None

        catalog = AttributeCatalog.query.filter_by(attribute_name=attr).first()
        if not catalog:
            # Cannot simplify if attribute is not in catalog
            return None
        data_type = catalog.data_type

        # Handle 'AND' operator
        if operator == 'AND':
            # Greater than comparisons
            if comp1 in ['>', '>='] and comp2 in ['>', '>=']:
                new_comp = '>' if comp1 == '>' or comp2 == '>' else '>='
                new_val = max(val1, val2)
            # Less than comparisons
            elif comp1 in ['<', '<='] and comp2 in ['<', '<=']:
                new_comp = '<' if comp1 == '<' or comp2 == '<' else '<='
                new_val = min(val1, val2)
            else:
                return None
        # Handle 'OR' operator
        elif operator == 'OR':
            # Greater than comparisons
            if comp1 in ['>', '>='] and comp2 in ['>', '>=']:
                new_comp = '>' if comp1 == '>' and comp2 == '>' else '>='
                new_val = min(val1, val2)
            # Less than comparisons
            elif comp1 in ['<', '<='] and comp2 in ['<', '<=']:
                new_comp = '<' if comp1 == '<' and comp2 == '<' else '<='
                new_val = max(val1, val2)
            else:
                return None
        else:
            return None

        # Convert new_val to appropriate type
        if data_type == 'int':
            new_val = int(new_val)
        elif data_type == 'float':
            new_val = float(new_val)
        else:
            # Cannot simplify non-numeric types
            return None

        return {'operand': {'attribute': attr, 'comparison': new_comp, 'value': new_val}}


    def simplify_expression(self, expression):
        if 'operator' in expression:
            operator = expression['operator'].upper()
            left = self.simplify_expression(expression['left'])
            right = self.simplify_expression(expression['right'])

            # Apply logical identities
            if operator == 'AND':
                # True AND A => A
                if left == {'constant': True}:
                    return right
                if right == {'constant': True}:
                    return left
                # False AND A => False
                if left == {'constant': False} or right == {'constant': False}:
                    return {'constant': False}
            elif operator == 'OR':
                # True OR A => True
                if left == {'constant': True} or right == {'constant': True}:
                    return {'constant': True}
                # False OR A => A
                if left == {'constant': False}:
                    return right
                if right == {'constant': False}:
                    return left

            # Handle range overlaps for operands (only for same attribute)
            if isinstance(left, dict) and 'operand' in left and isinstance(right, dict) and 'operand' in right:
                if left['operand']['attribute'] == right['operand']['attribute']:
                    simplified = self.handle_range_overlap(left['operand'], right['operand'], operator)
                    if simplified:
                        return simplified

            # Remove duplicate conditions
            if left == right:
                return left

            return {'operator': operator, 'left': left, 'right': right}
        elif 'operand' in expression:
            operand = expression['operand']
            # Check for constant conditions (e.g., always True or False)
            if operand['attribute'].lower() == 'true':
                return {'constant': True}
            if operand['attribute'].lower() == 'false':
                return {'constant': False}
            return expression
        elif 'constant' in expression:
            # Handle constant expressions
            return expression
        else:
            raise ValueError("Invalid expression structure during simplification")



    def extract_operators(self, expression):
        """
        Recursively extract all logical operators from an expression.
        """
        operators = []
        if 'operator' in expression:
            operators.append(expression['operator'].upper())
            operators.extend(self.extract_operators(expression['left']))
            operators.extend(self.extract_operators(expression['right']))
        return operators

    def ast_to_dict(self, node):
        """
        Converts an ASTNode to a nested dictionary representing the expression.
        """
        if node.node_type == "operator":
            left_node = ASTNode.query.get(node.left_node)
            right_node = ASTNode.query.get(node.right_node)
            return {
                'operator': node.operator,
                'left': self.ast_to_dict(left_node),
                'right': self.ast_to_dict(right_node)
            }
        elif node.node_type == "operand":
            return {
                'operand': {
                    'attribute': node.attribute,
                    'comparison': node.comparison,
                    'value': node.value
                }
            }
        elif node.node_type == "constant":
            constant_value = node.value.lower()
            if constant_value == 'true':
                return {'constant': True}
            elif constant_value == 'false':
                return {'constant': False}
            else:
                raise ValueError(f"Unknown constant value: {node.value}")
        else:
            raise ValueError("Unknown node type")

    def evaluate_ast(self, node, data):
        """
        Recursively evaluates the AST against the provided data.
        """
        if node.node_type == "constant":
            if node.value.lower() == "true":
                return True
            elif node.value.lower() == "false":
                return False
            else:
                raise ValueError(f"Unknown constant value: {node.value}")

        if node.node_type == "operator":
            left = self.evaluate_ast(ASTNode.query.get(node.left_node), data)
            right = self.evaluate_ast(ASTNode.query.get(node.right_node), data)
            if node.operator.upper() == "AND":
                return left and right
            elif node.operator.upper() == "OR":
                return left or right
            else:
                raise ValueError(f"Unknown operator: {node.operator}")
        elif node.node_type == "operand":
            attribute = node.attribute
            comparison = node.comparison
            value = node.value
            if attribute not in data:
                raise ValueError(f"Attribute '{attribute}' is not provided in data")
            data_value = data[attribute]
            # Get the data type from the catalog
            catalog = AttributeCatalog.query.filter_by(attribute_name=attribute).first()
            if not catalog:
                raise ValueError(f"Attribute '{attribute}' is not in the catalog")
            data_type = catalog.data_type
            # Convert value to appropriate type
            try:
                if data_type == "int":
                    value = int(value)
                    data_value = int(data_value)
                elif data_type == "float":
                    value = float(value)
                    data_value = float(data_value)
                elif data_type == "string":
                    value = str(value)
                    data_value = str(data_value)
                else:
                    raise ValueError(f"Unsupported data type '{data_type}' for attribute '{attribute}'")
            except ValueError:
                raise ValueError(f"Type mismatch for attribute '{attribute}'")

            if comparison == ">":
                return data_value > value
            elif comparison == "<":
                return data_value < value
            elif comparison == ">=":
                return data_value >= value
            elif comparison == "<=":
                return data_value <= value
            elif comparison == "=":
                return data_value == value
            elif comparison == "!=":
                return data_value != value
            else:
                raise ValueError(f"Unknown comparison operator: {comparison}")
        else:
            raise ValueError("Unknown node type")


    def evaluate_rule(self, rule_id, data):
        """
        Evaluates a rule against the provided data.
        """
        try:
            rule = Rule.query.get(rule_id)
            if not rule:
                raise ValueError("Rule not found")
            root_node = rule.root_node
            return self.evaluate_ast(root_node, data)
        except Exception as e:
            raise ValueError(f"Failed to evaluate rule: {str(e)}")

    def modify_rule(self, rule_id, modifications):
        """
        Modifies an existing rule's AST nodes.
        """
        try:
            rule = Rule.query.get(rule_id)
            if not rule:
                raise ValueError("Rule not found")
            node = ASTNode.query.get(modifications.get('node_id'))
            if not node:
                raise ValueError("Node not found")
            if node.rule_id != rule_id:
                raise ValueError("Node does not belong to the specified rule")

            # Update operator if provided
            if 'new_operator' in modifications:
                new_operator = modifications['new_operator'].upper()
                if new_operator not in ["AND", "OR"]:
                    raise ValueError("Invalid operator. Must be 'AND' or 'OR'.")
                node.operator = new_operator

            # Update attribute, comparison, and value if provided
            if 'new_attribute' in modifications:
                new_attribute = modifications['new_attribute']
                self.validate_attribute(new_attribute)
                node.attribute = new_attribute
            if 'new_comparison' in modifications:
                new_comparison = modifications['new_comparison']
                if new_comparison not in [">", "<", ">=", "<=", "=", "!="]:
                    raise ValueError("Invalid comparison operator.")
                node.comparison = new_comparison
            if 'new_value' in modifications:
                node.value = str(modifications['new_value'])

            db.session.commit()
            return rule
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Failed to modify rule: {str(e)}")
