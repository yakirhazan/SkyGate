import React, { lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
const AuditPage = lazy(() => import('./pages/AuditPage'));
const ConsentPage = lazy(() => import('./pages/ConsentPage'));
const ChecklistPage = lazy(() => import('./pages/ChecklistPage'));

function App() {
  return (
    <Router>
      <Suspense fallback={<div>Loading...</div>}>
<Routes>
  <Route path="/audit" element={<AuditPage />} />
  <Route path="/consent" element={<ConsentPage />} />
  <Route path="/checklist" element={<ChecklistPage />} />
  <Route path="/" element={<div>Home</div>} />
</Routes>
      </Suspense>
    </Router>
  );
}

export default App;
