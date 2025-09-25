import { existsSync } from 'node:fs';
import { join } from 'node:path';

const viteBin = join('node_modules', '.bin', process.platform === 'win32' ? 'vite.cmd' : 'vite');
if (!existsSync(viteBin)) {
  console.error(`\u274C  vite binary not found at ${viteBin}. Installation failed.`);
  process.exit(1);
} else {
  console.log(`\u2705  vite binary verified at ${viteBin}`);
} 