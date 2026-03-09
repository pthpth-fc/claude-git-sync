#!/usr/bin/env node
import { copyFileSync, chmodSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { execSync } from 'child_process';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log('🚀 Setting up Claude-Git Sync...\n');

try {
  // Find Git root
  const gitRoot = execSync('git rev-parse --show-toplevel', { encoding: 'utf8' }).trim();
  const hooksDir = join(gitRoot, '.git', 'hooks');
  const sourceHooksDir = join(dirname(__dirname), 'hooks');

  console.log(`Repository: ${gitRoot}`);
  console.log(`Installing Git hooks...\n`);

  // Install hooks
  const hooks = ['post-checkout', 'post-commit'];

  for (const hook of hooks) {
    const source = join(sourceHooksDir, hook);
    const dest = join(hooksDir, hook);

    if (!existsSync(source)) {
      console.log(`⚠️  Hook not found: ${hook}`);
      continue;
    }

    // Backup existing hook
    if (existsSync(dest)) {
      const backup = `${dest}.backup`;
      console.log(`  Backing up existing ${hook} to ${hook}.backup`);
      copyFileSync(dest, backup);
    }

    // Install new hook
    copyFileSync(source, dest);
    chmodSync(dest, 0o755);
    console.log(`  ✓ Installed ${hook}`);
  }

  // Initialize current branch
  const currentBranch = execSync('git branch --show-current', {
    encoding: 'utf8',
    cwd: gitRoot
  }).trim();

  console.log(`\n✓ Git hooks installed successfully`);
  console.log(`\nInitializing current branch: ${currentBranch}...`);

  execSync(`node ${join(__dirname, 'cli.js')} init "${currentBranch}"`, {
    stdio: 'inherit',
    cwd: gitRoot
  });

  console.log('\n' + '='.repeat(60));
  console.log('🎉 Claude-Git Sync setup complete!');
  console.log('='.repeat(60));
  console.log('\nNext steps:');
  console.log('  1. Switch branches with: git checkout <branch>');
  console.log('  2. Create new branch: node src/cli.js create <branch>');
  console.log('  3. Check status: node src/cli.js status');
  console.log('\nChat sessions will now sync automatically with your branches!');

} catch (error) {
  console.error(`\n❌ Setup failed: ${error.message}`);
  console.error('\nMake sure you are in a Git repository.');
  process.exit(1);
}
