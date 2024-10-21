// frontend/src/components/CombineRules.js

import React, { useState, useEffect } from 'react';
import axios from 'axios';

const CombineRules = () => {
  const [rules, setRules] = useState([]);
  const [selectedRules, setSelectedRules] = useState([]);
  const [combinedRuleName, setCombinedRuleName] = useState('');
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

  const handleCheckboxChange = (e) => {
    const ruleId = parseInt(e.target.value);
    if (e.target.checked) {
      setSelectedRules([...selectedRules, ruleId]);
    } else {
      setSelectedRules(selectedRules.filter((id) => id !== ruleId));
    }
  };

  const handleCombineRules = async (e) => {
    e.preventDefault();
    if (selectedRules.length < 2) {
      setMessage('Select at least two rules to combine.');
      return;
    }
    try {
      const response = await axios.post('http://localhost:5000/combine_rules', {
        rule_ids: selectedRules,
        combined_rule_name: combinedRuleName || 'combined_rule',
      });
      setMessage(`Combined Rule created with ID: ${response.data.combined_rule_id}`);
      setSelectedRules([]);
      setCombinedRuleName('');
      fetchRules();
    } catch (error) {
      setMessage(error.response?.data?.error || 'Error combining rules.');
    }
  };

  return (
    <div>
      <h3>Combine Rules</h3>
      <form onSubmit={handleCombineRules}>
        <div>
          <label>Combined Rule Name:</label>
          <input
            type="text"
            value={combinedRuleName}
            onChange={(e) => setCombinedRuleName(e.target.value)}
            placeholder="Optional: Default is 'combined_rule'"
          />
        </div>
        <div>
          <label>Select Rules to Combine:</label>
          <div style={{ maxHeight: '200px', overflowY: 'scroll', border: '1px solid #ccc', padding: '10px' }}>
            {rules.map((rule) => (
              <div key={rule.id}>
                <input
                  type="checkbox"
                  value={rule.id}
                  checked={selectedRules.includes(rule.id)}
                  onChange={handleCheckboxChange}
                />
                <label>{rule.name} (ID: {rule.id})</label>
              </div>
            ))}
          </div>
        </div>
        <button type="submit">Combine Rules</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
};

export default CombineRules;
