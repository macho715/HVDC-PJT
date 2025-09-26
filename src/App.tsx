import React from 'react';
import { Routes, Route, NavLink } from 'react-router-dom';
import InvoiceOCR from '@/components/InvoiceOCR';
import HeatStow from '@/components/HeatStow';
import WarehouseForecast from '@/components/WarehouseForecast';

export default function App() {
  return (
    <div className="flex h-screen">
      <aside className="w-52 bg-slate-800 text-white p-4 space-y-4">
        <NavLink to="/ocr" className={({ isActive }) => isActive ? 'font-bold' : ''}>Invoice OCR</NavLink>
        <NavLink to="/heat" className={({ isActive }) => isActive ? 'font-bold' : ''}>Deck Heat-Stow</NavLink>
        <NavLink to="/forecast" className={({ isActive }) => isActive ? 'font-bold' : ''}>Warehouse Forecast</NavLink>
      </aside>
      <main className="flex-1 p-6 overflow-auto">
        <Routes>
          <Route path="/ocr" element={<InvoiceOCR />} />
          <Route path="/heat" element={<HeatStow />} />
          <Route path="/forecast" element={<WarehouseForecast />} />
          <Route path="*" element={<div>Select a module on the left.</div>} />
        </Routes>
      </main>
    </div>
  );
} 