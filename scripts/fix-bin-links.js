import { existsSync, mkdirSync, symlinkSync } from 'node:fs';
import { join, resolve } from 'node:path';

const projectRoot = resolve();
const binDir = join(projectRoot, 'node_modules', '.bin');
if (!existsSync(binDir)) {
  mkdirSync(binDir, { recursive: true });
}
const vitePath = join(projectRoot, 'node_modules', 'vite', 'bin', 'vite.js');
const viteLink = join(binDir, 'vite');
try {
  if (!existsSync(viteLink)) {
    symlinkSync(vitePath, viteLink, 'file');
    console.log('[postinstall] symlinked vite');
  }
} catch (e) {
  console.warn('[postinstall] symlink failed:', e.message);
} 