# backend/models.py

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Rule(db.Model):
    __tablename__ = 'rules'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    rule_string = db.Column(db.Text, nullable=False)  # Set nullable=True
    root_node_id = db.Column(db.Integer, db.ForeignKey('ast_nodes.id'))

    root_node = db.relationship('ASTNode', foreign_keys=[root_node_id])


    def __repr__(self):
        return f"<Rule {self.name}>"


class ASTNode(db.Model):
    __tablename__ = 'ast_nodes'
    id = db.Column(db.Integer, primary_key=True)
    rule_id = db.Column(db.Integer, db.ForeignKey('rules.id'), nullable=False)
    node_type = db.Column(db.String, nullable=False)  # "operator" or "operand"
    operator = db.Column(db.String, nullable=True)     # "AND", "OR"
    left_node = db.Column(db.Integer, db.ForeignKey('ast_nodes.id'), nullable=True)
    right_node = db.Column(db.Integer, db.ForeignKey('ast_nodes.id'), nullable=True)
    attribute = db.Column(db.String, nullable=True)
    comparison = db.Column(db.String, nullable=True)
    value = db.Column(db.String, nullable=True)
    
    # Relationships
    left = db.relationship('ASTNode', remote_side=[id], foreign_keys=[left_node], post_update=True)
    right = db.relationship('ASTNode', remote_side=[id], foreign_keys=[right_node], post_update=True)


class AttributeCatalog(db.Model):
    __tablename__ = 'attribute_catalog'
    id = db.Column(db.Integer, primary_key=True)
    attribute_name = db.Column(db.String, unique=True, nullable=False)
    data_type = db.Column(db.String, nullable=False)  # e.g., "int", "string", "float"
