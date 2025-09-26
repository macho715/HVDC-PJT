import * as tesseract from 'tesseract.js';
export async function runOCR(file) {
  const { data } = await tesseract.recognize(file, 'eng', { logger: m => console.debug(m) });
  const lines = data.text.split(/\n/).filter(Boolean);
  return lines.map((l) => {
    const [item, rate, qty] = l.match(/(\w+)\s+\$?(\d+(?:\.\d{1,2})?)\s+(\d+)/)?.slice(1) || [];
    return item ? { item, rate: parseFloat(rate), qty: parseInt(qty, 10) } : null;
  }).filter(Boolean);
} 