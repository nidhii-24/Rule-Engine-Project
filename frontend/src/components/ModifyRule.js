// frontend/src/components/ModifyRule.js

import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ModifyRule = () => {
  const [rules, setRules] = useState([]);
  const [selectedRuleId, setSelectedRuleId] = useState('');
  const [ruleDetails, setRuleDetails] = useState(null);
  const [modifications, setModifications] = useState({});
  const [message, setMessage] = useState(null);

  useEffect(() => {
    fetchRules();
  }, []);

  const fetchRules = async () => {
    try {
      const response = await axios.get('http://localhost:5000/get_rules');
      setRules(response.data.rules);
    } catch (error) {
      console.error('Error fetching rules:', error);
    }
  };

  const fetchRuleDetails = async (ruleId) => {
    try {
      const response = await axios.get(`http://localhost:5000/get_rule/${ruleId}`);
      setRuleDetails(response.data.ast);
    } catch (error) {
      console.error('Error fetching rule details:', error);
      setRuleDetails(null);
    }
  };

  const handleRuleSelection = (e) => {
    const ruleId = e.target.value;
    setSelectedRuleId(ruleId);
    if (ruleId) {
      fetchRuleDetails(ruleId);
    } else {
      setRuleDetails(null);
    }
    setModifications({});
    setMessage(null);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setModifications({
      ...modifications,
      [name]: value,
    });
  };

  const handleModifyRule = async (e) => {
    e.preventDefault();
    if (!selectedRuleId) {
      setMessage('Please select a rule to modify.');
      return;
    }
    if (!modifications.node_id) {
      setMessage('Please specify the node ID to modify.');
      return;
    }
    try {
      const response = await axios.post('http://localhost:5000/modify_rule', {
        rule_id: parseInt(selectedRuleId),
        modifications,
      });
      setMessage(response.data.message);
      fetchRuleDetails(selectedRuleId);
      setModifications({});
    } catch (error) {
      setMessage(error.response?.data?.error || 'Error modifying rule.');
    }
  };

  const renderAST = (node, depth = 0) => {
    if (!node) return null;
    return (
      <div style={{ marginLeft: depth * 20 + 'px' }}>
        {node.operator ? (
          <div>
            <strong>Operator:</strong> {node.operator}
            {node.left && renderAST(node.left, depth + 1)}
            {node.right && renderAST(node.right, depth + 1)}
          </div>
        ) : (
          <div>
            <strong>Operand:</strong> {node.attribute} {node.comparison} {node.value}
          </div>
        )}
      </div>
    );
  };

  return (
    <div>
      <h3>Modify Rule</h3>
      <form onSubmit={handleModifyRule}>
        <div>
          <label>Select Rule:</label>
          <select value={selectedRuleId} onChange={handleRuleSelection} required>
            <option value="">--Select a Rule--</option>
            {rules.map((rule) => (
              <option key={rule.id} value={rule.id}>
                {rule.name} (ID: {rule.id})
              </option>
            ))}
          </select>
        </div>
        {ruleDetails && (
          <div>
            <h4>Rule AST:</h4>
            {renderAST(ruleDetails)}
            <h4>Modifications:</h4>
            <div>
              <label>Node ID:</label>
              <input
                type="number"
                name="node_id"
                value={modifications.node_id || ''}
                onChange={handleInputChange}
                required
              />
            </div>
            <div>
              <label>New Operator (if modifying operator node):</label>
              <select name="new_operator" value={modifications.new_operator || ''} onChange={handleInputChange}>
                <option value="">--Select Operator--</option>
                <option value="AND">AND</option>
                <option value="OR">OR</option>
              </select>
            </div>
            <div>
              <label>New Attribute (if modifying operand node):</label>
              <input
                type="text"
                name="new_attribute"
                value={modifications.new_attribute || ''}
                onChange={handleInputChange}
                placeholder="e.g., age"
              />
            </div>
            <div>
              <label>New Comparison:</label>
              <select name="new_comparison" value={modifications.new_comparison || ''} onChange={handleInputChange}>
                <option value="">--Select Comparison--</option>
                <option value=">">></option>
                <option value="<">&lt;</option>
                <option value=">=">&gt;=</option>
                <option value="<=">&lt;=</option>
                <option value="=">=</option>
                <option value="!=">!=</option>
              </select>
            </div>
            <div>
              <label>New Value:</label>
              <input
                type="text"
                name="new_value"
                value={modifications.new_value || ''}
                onChange={handleInputChange}
                placeholder="e.g., 30"
              />
            </div>
            <button type="submit">Apply Modifications</button>
          </div>
        )}
      </form>
      {message && <p>{message}</p>}
    </div>
  );
};

export default ModifyRule;
