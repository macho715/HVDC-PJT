# Logistics AI SPA
SPA integrating TF.js OCR, Brain.js heat‑stow, ML5.js forecast, Watson/Algorithmia HS risk.

## Quick Start (Windows Dev)
```powershell
winget install --id OpenJS.NodeJS.LTS
npm install --global pnpm   # optional
pnpm install                # or npm install
pnpm run dev
```

## Env Keys
Create `.env.local`:
```
VITE_WATSON_APIKEY="xxxx"
VITE_WATSON_URL="https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/..."
VITE_ALGO_KEY="sim_..."
```

## Tests
```
pnpm run test
```

---
> Generated via ChatGPT logistics‑ai blueprint v0.3.1