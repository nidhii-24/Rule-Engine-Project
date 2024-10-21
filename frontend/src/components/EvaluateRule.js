// frontend/src/components/EvaluateRule.js

import React, { useState, useEffect } from 'react';
import axios from 'axios';

const EvaluateRule = () => {
  const [rules, setRules] = useState([]);
  const [selectedRuleId, setSelectedRuleId] = useState('');
  const [attributes, setAttributes] = useState([]);
  const [attributeValues, setAttributeValues] = useState({});
  const [message, setMessage] = useState(null);

  useEffect(() => {
    fetchRules();
    fetchAttributes();
  }, []);

  const fetchRules = async () => {
    try {
      const response = await axios.get('http://localhost:5000/get_rules');
      setRules(response.data.rules);
    } catch (error) {
      console.error('Error fetching rules:', error);
    }
  };

  const fetchAttributes = async () => {
    try {
      const response = await axios.get('http://localhost:5000/get_attributes');
      setAttributes(response.data.attributes);
    } catch (error) {
      console.error('Error fetching attributes:', error);
    }
  };

  const handleInputChange = (e, attributeName) => {
    setAttributeValues({
      ...attributeValues,
      [attributeName]: e.target.value,
    });
  };

  const handleEvaluateRule = async (e) => {
    e.preventDefault();
    if (!selectedRuleId) {
      setMessage('Please select a rule to evaluate.');
      return;
    }
    try {
      const response = await axios.post('http://localhost:5000/evaluate_rule', {
        rule_id: selectedRuleId,
        attributes: attributeValues,
      });
      setMessage(`Evaluation Result: ${response.data.result}`);
    } catch (error) {
      setMessage(error.response?.data?.error || 'Error evaluating rule.');
    }
  };

  return (
    <div>
      <h3>Evaluate Rule</h3>
      <form onSubmit={handleEvaluateRule}>
        <div>
          <label>Select Rule:</label>
          <select value={selectedRuleId} onChange={(e) => setSelectedRuleId(e.target.value)} required>
            <option value="">--Select a Rule--</option>
            {rules.map((rule) => (
              <option key={rule.id} value={rule.id}>
                {rule.name} (ID: {rule.id})
              </option>
            ))}
          </select>
        </div>
        <div>
          <h4>Enter Attribute Values:</h4>
          {attributes.map((attr) => (
            <div key={attr.id}>
              <label>{attr.attribute_name} ({attr.data_type}):</label>
              <input
                type="text"
                value={attributeValues[attr.attribute_name] || ''}
                onChange={(e) => handleInputChange(e, attr.attribute_name)}
                required
              />
            </div>
          ))}
        </div>
        <button type="submit">Evaluate</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
};

export default EvaluateRule;
