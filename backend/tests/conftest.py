# backend/tests/conftest.py

import pytest
from flask import Flask
from models import db, AttributeCatalog
from rule_engine import RuleEngine

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory DB for tests
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
            catalog_entry = AttributeCatalog(
                attribute_name=attr["attribute_name"], 
                data_type=attr["data_type"]
            )
            db.session.add(catalog_entry)
        db.session.commit()

        yield app  # Tests run here

        # Teardown: drop all tables after each test
        db.session.remove()
        db.drop_all()
