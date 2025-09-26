const { existsSync, mkdirSync, symlinkSync } = require('node:fs');
const { join, resolve } = require('node:path');

const projectRoot = resolve();
const binDir = join(projectRoot, 'node_modules', '.bin');
if (!existsSync(binDir)) {
  mkdirSync(binDir, { recursive: true });
  console.log('[fix-bin-links] Created .bin directory');
}
const vitePath = join(projectRoot, 'node_modules', 'vite', 'bin', 'vite.js');
const viteLink = join(binDir, 'vite');
try {
  if (!existsSync(viteLink)) {
    symlinkSync(vitePath, viteLink, 'file');
    console.log('[fix-bin-links] symlinked vite');
  } else {
    console.log('[fix-bin-links] vite link already exists');
  }
} catch (e) {
  console.warn('[fix-bin-links] symlink failed:', e.message);
} 