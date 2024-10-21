// frontend/src/components/CreateRule.js

import React, { useState } from 'react';
import axios from 'axios';

const CreateRule = () => {
  const [name, setName] = useState('');
  const [ruleString, setRuleString] = useState('');
  const [message, setMessage] = useState(null);

  const handleCreateRule = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:5000/create_rule', {
        name,
        rule_string: ruleString,
      });
      setMessage(`Rule created with ID: ${response.data.rule_id}`);
      setName('');
      setRuleString('');
    } catch (error) {
      setMessage(error.response?.data?.error || 'Error creating rule.');
    }
  };

  return (
    <div>
      <h3>Create Rule</h3>
      <form onSubmit={handleCreateRule}>
        <div>
          <label>Rule Name:</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Rule String:</label>
          <textarea
            value={ruleString}
            onChange={(e) => setRuleString(e.target.value)}
            required
            rows="4"
            cols="50"
            placeholder="e.g., ((age > 30 AND department = 'Sales') OR (age < 25 AND department = 'Marketing')) AND (salary > 50000 OR experience > 5)"
          ></textarea>
        </div>
        <button type="submit">Create Rule</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
};

export default CreateRule;
