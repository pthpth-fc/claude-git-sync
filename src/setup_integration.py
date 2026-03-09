#!/usr/bin/env python3
"""
Setup script for Claude-Git Sync integration
Installs Git hooks and initializes current branch
"""

import os
import shutil
import subprocess
from pathlib import Path

print()
print("╔════════════════════════════════════════════════════════╗")
print("║   Claude-Git Sync - Installation                      ║")
print("╚════════════════════════════════════════════════════════╝")
print()

try:
    # Find Git root
    result = subprocess.run(
        ['git', 'rev-parse', '--show-toplevel'],
        capture_output=True,
        text=True,
        check=True
    )
    git_root = Path(result.stdout.strip())
    print(f"📁 Git Repository: {git_root}")

    # Get current branch
    result = subprocess.run(
        ['git', 'branch', '--show-current'],
        capture_output=True,
        text=True,
        check=True,
        cwd=git_root
    )
    current_branch = result.stdout.strip()
    print(f"🌿 Current Branch: {current_branch}")
    print()

    # Install Git hooks
    hooks_dir = git_root / '.git' / 'hooks'
    source_hooks_dir = Path(__file__).parent.parent / 'hooks'

    print("📦 Installing Git hooks...")
    print()

    hooks_to_install = ['post-checkout', 'post-commit']

    for hook_name in hooks_to_install:
        source = source_hooks_dir / hook_name
        dest = hooks_dir / hook_name

        if not source.exists():
            print(f"⚠️  Source hook not found: {hook_name}")
            continue

        # Backup existing hook
        if dest.exists():
            backup = dest.with_suffix('.backup')
            print(f"  📋 Backing up existing {hook_name}")
            shutil.copy2(dest, backup)

        # Copy new hook
        shutil.copy2(source, dest)
        os.chmod(dest, 0o755)
        print(f"  ✓ Installed {hook_name}")

    print()
    print("─" * 60)
    print()

    # Test the integration
    print("🧪 Testing integration...")
    print()

    test_script = Path(__file__).parent / 'git_sync.py'
    result = subprocess.run(
        ['python3', str(test_script), 'save'],
        cwd=git_root
    )

    if result.returncode == 0:
        print()
        print("✅ Integration test passed!")
    else:
        print()
        print("⚠️  Integration test had issues (may be normal if no active chat)")

    print()
    print("─" * 60)
    print()
    print("╔════════════════════════════════════════════════════════╗")
    print("║   ✅ Installation Complete!                            ║")
    print("╚════════════════════════════════════════════════════════╝")
    print()
    print("What's Next:")
    print()
    print("1. Start chatting with Claude Code as normal")
    print("2. Switch branches: git checkout <branch>")
    print("   → Chat history automatically switches!")
    print()
    print("3. Create new branch with context:")
    print("   → python3 src/git_sync.py create feature-new")
    print()
    print("4. Check status anytime:")
    print("   → python3 src/git_sync.py status")
    print()
    print("Your chat sessions are now synced with Git branches! 🎉")
    print()

except subprocess.CalledProcessError as e:
    print()
    print(f"❌ Error: {e}")
    print()
    print("Make sure you're in a Git repository")
    exit(1)
except Exception as e:
    print()
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
