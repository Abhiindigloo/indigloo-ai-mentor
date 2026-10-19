// Guards the Android CI setup against the obsolete `tools` SDK package and
// against SDK packages drifting away from the app's compileSdk.
// Dependency-free on purpose; full workflow syntax is checked by actionlint in CI.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';

/** @param {string} relPath @returns {Promise<string>} */
async function readRepoFile(relPath) {
  try {
    return await readFile(new URL(`../${relPath}`, import.meta.url), 'utf8');
  } catch (err) {
    throw new Error(`Cannot read ${relPath}: ${err instanceof Error ? err.message : String(err)}`);
  }
}

/**
 * Returns the `packages` input of the android-actions/setup-android step,
 * or null when the step does not set it. Tolerates quoting and indentation.
 * @param {string} workflow
 * @returns {string[] | null}
 */
function setupAndroidPackages(workflow) {
  const lines = workflow.split(/\r?\n/);
  const start = lines.findIndex(l => /uses:\s*['"]?android-actions\/setup-android@/.test(l));
  assert.notEqual(start, -1, 'ci.yml must use android-actions/setup-android');

  for (let i = start + 1; i < lines.length; i++) {
    const line = lines[i];
    if (/^\s*-\s/.test(line)) break; // reached the next step
    const m = line.match(/^\s*packages:\s*(['"]?)(.+?)\1\s*(#.*)?$/);
    if (m) return m[2].trim().split(/\s+/);
  }
  return null;
}

const [workflow, gradle] = await Promise.all([
  readRepoFile('docs/ci/ci.yml'),
  readRepoFile('apps/android/app/build.gradle.kts'),
]);

const sdkMatch = gradle.match(/compileSdk\s*=\s*(\d+)/);
assert.ok(sdkMatch, 'apps/android/app/build.gradle.kts must declare compileSdk');
const sdk = sdkMatch[1];

const packages = setupAndroidPackages(workflow);
assert.ok(packages, "setup-android must set 'packages'; its default list requests the removed 'tools' package");
assert.ok(!packages.includes('tools'), "The removed 'tools' SDK package must not be requested");
assert.ok(packages.includes('platform-tools'), "'platform-tools' must be installed");
assert.ok(packages.includes(`platforms;android-${sdk}`), `'platforms;android-${sdk}' must match compileSdk ${sdk}`);
assert.ok(
  packages.some(p => new RegExp(`^build-tools;${sdk}\\.\\d+\\.\\d+$`).test(p)),
  `A 'build-tools;${sdk}.x.y' package must match compileSdk ${sdk}`,
);

console.log(`PASS: Android CI installs supported SDK packages for compileSdk ${sdk}.`);
