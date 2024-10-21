# backend/app.py

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db, Rule, ASTNode, AttributeCatalog
from rule_engine import RuleEngine
from flask_cors import CORS  # To handle CORS for frontend
import os
from flask_migrate import Migrate





app = Flask(__name__)
CORS(app)  # Enable CORS

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:postpass@localhost/rule_engine_db')  # Update with actual credentials or set via environment variable
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)

migrate = Migrate(app, db)

# Initialize RuleEngine
rule_engine = RuleEngine()

with app.app_context():
    db.create_all()

    # Initialize Attribute Catalog if empty
    if AttributeCatalog.query.count() == 0:
        sample_attributes = [
            {"attribute_name": "age", "data_type": "int"},
            {"attribute_name": "department", "data_type": "string"},
            {"attribute_name": "salary", "data_type": "float"},
            {"attribute_name": "experience", "data_type": "int"},
            # Add more attributes as needed
        ]
        for attr in sample_attributes:
            catalog_entry = AttributeCatalog(attribute_name=attr["attribute_name"], data_type=attr["data_type"])
            db.session.add(catalog_entry)
        db.session.commit()


# backend/app.py

import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/create_rule', methods=['POST'])
def create_rule():
    data = request.json
    name = data.get('name')
    rule_string = data.get('rule_string')
    logger.debug(f"Received create_rule request with name: {name}, rule_string: {rule_string}")
    if not name or not rule_string:
        logger.error("Missing 'name' or 'rule_string' in request")
        return jsonify({"error": "Missing 'name' or 'rule_string'"}), 400
    try:
        rule = rule_engine.create_rule(name, rule_string)
        logger.debug(f"Rule created with ID: {rule.id}, name: {rule.name}")
        return jsonify({"rule_id": rule.id, "name": rule.name}), 201
    except Exception as e:
        logger.error(f"Error creating rule: {str(e)}")
        return jsonify({"error": str(e)}), 400



@app.route('/combine_rules', methods=['POST'])
def combine_rules():
    data = request.json
    rule_ids = data.get('rule_ids')
    combined_rule_name = data.get('name', "combined_rule")
    combine_operator = data.get('operator', 'AND').upper()
    if not rule_ids or not isinstance(rule_ids, list):
        return jsonify({"error": "'rule_ids' must be a list"}), 400
    try:
        combined_rule = rule_engine.combine_rules(rule_ids, combined_rule_name, combine_operator)
        return jsonify({"combined_rule_id": combined_rule.id, "name": combined_rule.name}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400



@app.route('/evaluate_rule', methods=['POST'])
def evaluate_rule():
    data = request.json
    rule_id = data.get('rule_id')
    attributes = data.get('attributes')
    if not rule_id or not attributes:
        return jsonify({"error": "Missing 'rule_id' or 'attributes'"}), 400
    try:
        result = rule_engine.evaluate_rule(rule_id, attributes)
        return jsonify({"result": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/modify_rule', methods=['POST'])
def modify_rule():
    data = request.json
    rule_id = data.get('rule_id')
    modifications = data.get('modifications')
    if not rule_id or not modifications:
        return jsonify({"error": "Missing 'rule_id' or 'modifications'"}), 400
    try:
        rule = rule_engine.modify_rule(rule_id, modifications)
        return jsonify({"message": f"Rule '{rule.name}' modified successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/add_attribute', methods=['POST'])
def add_attribute():
    data = request.json
    attribute_name = data.get('attribute_name')
    data_type = data.get('data_type')
    if not attribute_name or not data_type:
        return jsonify({"error": "Missing 'attribute_name' or 'data_type'"}), 400
    if data_type not in ["int", "float", "string"]:
        return jsonify({"error": "Invalid 'data_type'. Must be 'int', 'float', or 'string'."}), 400
    try:
        new_attribute = AttributeCatalog(attribute_name=attribute_name, data_type=data_type)
        db.session.add(new_attribute)
        db.session.commit()
        return jsonify({"message": f"Attribute '{attribute_name}' added successfully."}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": f"Attribute '{attribute_name}' already exists."}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@app.route('/get_rules', methods=['GET'])
def get_rules():
    try:
        rules = Rule.query.all()
        rules_data = [{"id": rule.id, "name": rule.name} for rule in rules]
        return jsonify({"rules": rules_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/get_attributes', methods=['GET'])
def get_attributes():
    try:
        attributes = AttributeCatalog.query.all()
        attributes_data = [{"id": attr.id, "attribute_name": attr.attribute_name, "data_type": attr.data_type} for attr in attributes]
        return jsonify({"attributes": attributes_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/get_rule/<int:rule_id>', methods=['GET'])
def get_rule(rule_id):
    try:
        rule = Rule.query.get(rule_id)
        if not rule:
            return jsonify({"error": "Rule not found"}), 404
        # Fetch AST as nested dict
        ast_dict = rule_engine.ast_to_dict(rule.root_node)
        return jsonify({"id": rule.id, "name": rule.name, "ast": ast_dict}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True)
