// frontend/src/components/AttributeCatalog.js

import React, { useState, useEffect } from 'react';
import axios from 'axios';

const AttributeCatalog = () => {
  const [attributes, setAttributes] = useState([]);
  const [attributeName, setAttributeName] = useState('');
  const [dataType, setDataType] = useState('int');
  const [message, setMessage] = useState(null);

  useEffect(() => {
    fetchAttributes();
  }, []);

  const fetchAttributes = async () => {
    try {
      const response = await axios.get('http://localhost:5000/get_attributes');
      setAttributes(response.data.attributes);
    } catch (error) {
      console.error('Error fetching attributes:', error);
    }
  };

  const handleAddAttribute = async (e) => {
    e.preventDefault();
    if (!attributeName) {
      setMessage('Attribute name is required.');
      return;
    }
    try {
      const response = await axios.post('http://localhost:5000/add_attribute', {
        attribute_name: attributeName,
        data_type: dataType,
      });
      setMessage(response.data.message);
      setAttributeName('');
      setDataType('int');
      fetchAttributes();
    } catch (error) {
      setMessage(error.response?.data?.error || 'Error adding attribute.');
    }
  };

  return (
    <div>
      <h3>Attribute Catalog</h3>
      <h4>Existing Attributes:</h4>
      <table border="1" cellPadding="5">
        <thead>
          <tr>
            <th>ID</th>
            <th>Attribute Name</th>
            <th>Data Type</th>
          </tr>
        </thead>
        <tbody>
          {attributes.map((attr) => (
            <tr key={attr.id}>
              <td>{attr.id}</td>
              <td>{attr.attribute_name}</td>
              <td>{attr.data_type}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <h4>Add New Attribute:</h4>
      <form onSubmit={handleAddAttribute}>
        <div>
          <label>Attribute Name:</label>
          <input
            type="text"
            value={attributeName}
            onChange={(e) => setAttributeName(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Data Type:</label>
          <select value={dataType} onChange={(e) => setDataType(e.target.value)}>
            <option value="int">Int</option>
            <option value="float">Float</option>
            <option value="string">String</option>
          </select>
        </div>
        <button type="submit">Add Attribute</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
};

export default AttributeCatalog;
