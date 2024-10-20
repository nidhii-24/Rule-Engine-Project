# backend/tests/test_combine_rules.py

import pytest
from rule_engine import RuleEngine
from models import db, Rule, ASTNode, AttributeCatalog
from flask import Flask

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    db.init_app(app)
    with app.app_context():
        db.create_all()
        # Initialize Attribute Catalog
        sample_attributes = [
            {"attribute_name": "age", "data_type": "int"},
            {"attribute_name": "department", "data_type": "string"},
            {"attribute_name": "salary", "data_type": "float"},
            {"attribute_name": "experience", "data_type": "int"},
        ]
        for attr in sample_attributes:
            catalog_entry = AttributeCatalog(attribute_name=attr["attribute_name"], data_type=attr["data_type"])
            db.session.add(catalog_entry)
        db.session.commit()
        yield app



def test_combine_rules(app):
    with app.app_context():
        engine = RuleEngine()
        # Define multiple rule strings with varying operators and nested logic
        rule_strings = [
            "age > 20 AND age > 30",  # Should simplify to age > 30
            "salary > 50000 OR salary > 60000",  # Should simplify to salary > 60000
            "True OR department = 'HR'",  # Should simplify to True
            "False AND experience >= 5",  # Should simplify to False
            "age < 25 OR age < 30",  # Should simplify to age < 25
            "department = 'Sales' AND department = 'Sales'"  # Should simplify to department = 'Sales'
        ]
        combined_rule_name = "combined_rule_test"
        combined_rule = engine.combine_rules(rule_strings, combined_rule_name)
        
        assert combined_rule.id is not None
        assert combined_rule.name == combined_rule_name
        assert combined_rule.root_node is not None
        
        # Fetch the combined rule's AST for verification
        combined_ast = engine.ast_to_dict(combined_rule.root_node)
        assert combined_ast is not None

        # Expected simplifications:
        # - age > 20 AND age > 30 => age > 30
        # - salary > 50000 OR salary > 60000 => salary > 60000
        # - True OR department = 'HR' => True
        # - False AND experience >= 5 => False
        # - age < 25 OR age < 30 => age < 25
        # - department = 'Sales' AND department = 'Sales' => department = 'Sales'
        # Combined using 'AND' as per operator precedence and simplification

        # The combined expression after simplification should logically be:
        # True AND False AND age > 30 AND salary > 60000 AND age < 25 AND department = 'Sales'
        # Which further simplifies to False due to the presence of 'False'

        # Evaluate with sample data that should result in False
        sample_data = {
            "age": 35,
            "department": "Sales",
            "salary": 70000,
            "experience": 6
        }
        result = engine.evaluate_rule(combined_rule.id, sample_data)
        assert result == False  # Because one of the combined conditions is False

        # Another sample data
        sample_data_true = {
            "age": 24,
            "department": "Sales",
            "salary": 60000,
            "experience": 5
        }
        result_true = engine.evaluate_rule(combined_rule.id, sample_data_true)
        assert result_true == False  # Still False due to presence of 'False' in combined conditions

        # Modify rules to remove 'False' condition and test again
        # Re-define rule_strings without 'False AND experience >= 5'
        rule_strings_updated = [
            "age > 20 AND age > 30",  # Simplifies to age > 30
            "salary > 50000 OR salary > 60000",  # Simplifies to salary > 60000
            "True OR department = 'HR'",  # Simplifies to True
            "age < 25 OR age < 30",  # Simplifies to age < 25
            "department = 'Sales' AND department = 'Sales'"  # Simplifies to department = 'Sales'
        ]
        combined_rule_updated_name = "combined_rule_updated_test"
        combined_rule_updated = engine.combine_rules(rule_strings_updated, combined_rule_updated_name)

        assert combined_rule_updated.id is not None
        assert combined_rule_updated.name == combined_rule_updated_name
        assert combined_rule_updated.root_node is not None

        # The combined expression after simplification should logically be:
        # True AND age > 30 AND salary > 60000 AND age < 25 AND department = 'Sales'
        # Which simplifies to False due to 'True AND ... AND ...' but 'age > 30 AND age < 25' is impossible

        # Evaluate with sample data that satisfies age > 30 AND age < 25 (impossible)
        sample_data_conflict = {
            "age": 28,
            "department": "Sales",
            "salary": 70000,
            "experience": 4
        }
        result_conflict = engine.evaluate_rule(combined_rule_updated.id, sample_data_conflict)
        assert result_conflict == False  # age > 30 AND age < 25 is impossible

        # Evaluate with sample data that satisfies all conditions except age < 25
        sample_data_partial = {
            "age": 35,
            "department": "Sales",
            "salary": 70000,
            "experience": 4
        }
        result_partial = engine.evaluate_rule(combined_rule_updated.id, sample_data_partial)
        assert result_partial == False  # age < 25 not satisfied

        # Evaluate with sample data that satisfies all conditions
        # Note: age > 30 AND age < 25 is impossible, so ensure data does not violate
        # For testing, remove conflicting conditions by simplifying further
        # Adjust rule_strings to make a valid combined rule
        valid_rule_strings = [
            "age > 20 AND age > 30",  # Simplifies to age > 30
            "salary > 50000 OR salary > 60000",  # Simplifies to salary > 60000
            "department = 'Sales' AND department = 'Sales'"  # Simplifies to department = 'Sales'
        ]
        combined_rule_valid_name = "combined_rule_valid_test"
        combined_rule_valid = engine.combine_rules(valid_rule_strings, combined_rule_valid_name, combine_operator="AND")


        assert combined_rule_valid.id is not None
        assert combined_rule_valid.name == combined_rule_valid_name
        assert combined_rule_valid.root_node is not None

        # The combined expression after simplification should be:
        # age > 30 AND salary > 60000 AND department = 'Sales'

        # Evaluate with sample data that satisfies all conditions
        sample_data_valid = {
            "age": 35,
            "department": "Sales",
            "salary": 70000,
            "experience": 6
        }
        result_valid = engine.evaluate_rule(combined_rule_valid.id, sample_data_valid)
        assert result_valid == True

        # Evaluate with sample data that fails one condition
        sample_data_invalid = {
            "age": 35,
            "department": "Marketing",
            "salary": 70000,
            "experience": 6
        }
        result_invalid = engine.evaluate_rule(combined_rule_valid.id, sample_data_invalid)
        assert result_invalid == False
