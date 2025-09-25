import axios from 'axios';
const watson = axios.create({
  baseURL: import.meta.env.VITE_WATSON_URL,
  headers: { 'Content-Type': 'application/json' },
  auth: { username: 'apikey', password: import.meta.env.VITE_WATSON_API_KEY }
});
export async function analyzeRisk(text) {
  const { data } = await watson.post('/v1/analyze?version=2021-08-01', {
    text, features: { categories: {}, sentiment: {} }
  });
  return data;
} 