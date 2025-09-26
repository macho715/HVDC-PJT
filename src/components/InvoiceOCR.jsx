import { useState } from 'react';
import { runOCR } from '../utils/ocr_tfjs.js';
export default function InvoiceOCR() {
  const [rows, setRows] = useState([]);
  async function handleFile(e) {
    const file = e.target.files[0];
    if (file) setRows(await runOCR(file));
  }
  return (
    <section>
      <h1 className="text-2xl font-bold mb-4">Invoice OCR</h1>
      <input type="file" accept="image/*,application/pdf" onChange={handleFile} className="mb-4" />
      <table className="min-w-full border text-sm">
        <thead className="bg-gray-100">
          <tr><th>Item</th><th>Rate</th><th>Qty</th></tr>
        </thead>
        <tbody>
          {rows.map(r => (
            <tr key={r.item} className="border-t">
              <td>{r.item}</td><td>${r.rate.toFixed(2)}</td><td>{r.qty}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
} 