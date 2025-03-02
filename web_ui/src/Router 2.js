import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import App from './App';
import Dashboard from './Dashboard';

const AppRouter = () => (
    <Router>
        <Routes>
            <Route path="/" element={<App />} />
            <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
    </Router>
);

export default AppRouter;