// @ts-check
// Builds the offline web bundle from sources:
//   1. copies the single-source curriculum into apps/web,
//   2. regenerates apps/web/sw.js with a content-hashed cache name,
//   3. mirrors apps/web into the Android app's bundled assets (tests excluded).
// Run after any change under apps/web or packages/curriculum; CI fails on drift.
import {copyFile, cp, readFile, rm, writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';

const root = fileURLToPath(new URL('..', import.meta.url));
const webDir = `${root}apps/web`;
const curriculumSource = `${root}packages/curriculum/curriculum.json`;
const androidAssets = `${root}apps/android/app/src/main/assets/www`;

/** Files the service worker pre-caches for offline use (paths relative to apps/web). */
const CACHED_FILES = [
  'index.html', 'app.mjs', 'core.mjs', 'store.mjs', 'native.mjs', 'styles.css',
  'curriculum.json', 'manifest.webmanifest', 'icon.svg',
  'fonts/NotoSansDevanagari.ttf', 'fonts/OFL.txt',
];

/** @param {string} path */
const isTestFile = path => /\.test\.m?js$/.test(path);

/** @returns {Promise<string>} cache name derived from the cached files' bytes */
async function cacheName() {
  const hash = createHash('sha256');
  for (const file of CACHED_FILES) hash.update(await readFile(`${webDir}/${file}`));
  return `mentor-${hash.digest('hex').slice(0, 12)}`;
}

/** @param {string} cache */
function serviceWorker(cache) {
  const files = CACHED_FILES.map(f => `./${f}`);
  return `const CACHE=${JSON.stringify(cache)};const FILES=${JSON.stringify(files)};
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(FILES))));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k.startsWith('mentor-')&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{if(e.request.method!=='GET'||new URL(e.request.url).origin!==self.location.origin)return;e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request).catch(()=>e.request.mode==='navigate'?caches.match('./index.html'):Response.error())));});
`;
}

async function main() {
  await copyFile(curriculumSource, `${webDir}/curriculum.json`);
  await writeFile(`${webDir}/sw.js`, serviceWorker(await cacheName()));
  await rm(androidAssets, {recursive: true, force: true});
  await cp(webDir, androidAssets, {
    recursive: true,
    filter: src => !isTestFile(src) && !src.endsWith('.md'),
  });
  console.log('Synced curriculum, offline cache and Android assets.');
}

try {
  await main();
} catch (err) {
  console.error(`sync-assets failed: ${err instanceof Error ? err.message : String(err)}`);
  process.exitCode = 1;
}
