# backend/tests/test_evaluate_rule.py

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

def test_evaluate_rule(app):
    with app.app_context():
        engine = RuleEngine()
        rule_string = "age > 30 AND department = 'Sales'"
        unique_rule_name = "rule_evaluate_unique_1"
        rule = engine.create_rule(unique_rule_name, rule_string)
        data = {"age": 35, "department": "Sales", "salary": 60000, "experience": 3}
        result = engine.evaluate_rule(rule.id, data)
        assert result == True
        data = {"age": 25, "department": "Marketing", "salary": 40000, "experience": 2}
        result = engine.evaluate_rule(rule.id, data)
        assert result == False