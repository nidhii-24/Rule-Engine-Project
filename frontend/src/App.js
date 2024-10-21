// frontend/src/App.js

import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Navbar from './components/Navbar';
import CreateRule from './components/CreateRule';
import CombineRules from './components/CombineRules';
import EvaluateRule from './components/EvaluateRule';
import ModifyRule from './components/ModifyRule';
import AttributeCatalog from './components/AttributeCatalog';

function App() {
  return (
    <Router>
      <Navbar />
      <div className="container" style={{ padding: '20px' }}>
        <Routes>
          <Route path="/" element={<CreateRule />} />
          <Route path="/combine" element={<CombineRules />} />
          <Route path="/evaluate" element={<EvaluateRule />} />
          <Route path="/modify" element={<ModifyRule />} />
          <Route path="/attributes" element={<AttributeCatalog />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
