#!/usr/bin/env node
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { execSync } from 'child_process';

/**
 * Storage manager for Claude-Git sync
 * Handles branch-chat mappings and context inheritance
 */

export class Storage {
  constructor(repoRoot) {
    this.repoRoot = repoRoot || this.findGitRoot();
    this.claudeDir = join(this.repoRoot, '.claude');
    this.chatsDir = join(this.claudeDir, 'chats');
    this.mappingFile = join(this.claudeDir, 'branch-chats.json');
    this.contextFile = join(this.claudeDir, 'context-inheritance.json');

    this.ensureDirectories();
  }

  findGitRoot() {
    try {
      return execSync('git rev-parse --show-toplevel', { encoding: 'utf8' }).trim();
    } catch (error) {
      throw new Error('Not in a Git repository');
    }
  }

  ensureDirectories() {
    if (!existsSync(this.claudeDir)) {
      mkdirSync(this.claudeDir, { recursive: true });
    }
    if (!existsSync(this.chatsDir)) {
      mkdirSync(this.chatsDir, { recursive: true });
    }
  }

  readJSON(filepath, defaultValue = {}) {
    if (!existsSync(filepath)) {
      return defaultValue;
    }
    try {
      return JSON.parse(readFileSync(filepath, 'utf8'));
    } catch (error) {
      console.error(`Error reading ${filepath}:`, error.message);
      return defaultValue;
    }
  }

  writeJSON(filepath, data) {
    writeFileSync(filepath, JSON.stringify(data, null, 2), 'utf8');
  }

  // Branch-Chat Mappings
  getBranchMapping() {
    return this.readJSON(this.mappingFile, {});
  }

  setBranchMapping(branch, chatId) {
    const mappings = this.getBranchMapping();
    mappings[branch] = chatId;
    this.writeJSON(this.mappingFile, mappings);
  }

  getChatIdForBranch(branch) {
    const mappings = this.getBranchMapping();
    return mappings[branch];
  }

  // Context Inheritance
  getContextInheritance() {
    return this.readJSON(this.contextFile, {});
  }

  setParentBranch(childBranch, parentBranch) {
    const inheritance = this.getContextInheritance();
    inheritance[childBranch] = parentBranch;
    this.writeJSON(this.contextFile, inheritance);
  }

  getParentBranch(branch) {
    const inheritance = this.getContextInheritance();
    return inheritance[branch];
  }

  // Get inheritance chain (for hierarchical context loading)
  getInheritanceChain(branch) {
    const chain = [];
    let current = branch;
    const visited = new Set();

    while (current && !visited.has(current)) {
      chain.unshift(current);
      visited.add(current);
      current = this.getParentBranch(current);
    }

    return chain;
  }

  // Chat State Management
  getChatFile(chatId) {
    return join(this.chatsDir, `${chatId}.json`);
  }

  saveChatState(chatId, state) {
    const chatFile = this.getChatFile(chatId);
    this.writeJSON(chatFile, {
      chatId,
      timestamp: new Date().toISOString(),
      ...state
    });
  }

  loadChatState(chatId) {
    const chatFile = this.getChatFile(chatId);
    return this.readJSON(chatFile, null);
  }

  // Current branch helpers
  getCurrentBranch() {
    try {
      return execSync('git branch --show-current', {
        encoding: 'utf8',
        cwd: this.repoRoot
      }).trim();
    } catch (error) {
      throw new Error('Could not determine current branch');
    }
  }

  branchExists(branch) {
    try {
      execSync(`git rev-parse --verify ${branch}`, {
        encoding: 'utf8',
        cwd: this.repoRoot,
        stdio: 'pipe'
      });
      return true;
    } catch (error) {
      return false;
    }
  }

  // Generate unique chat ID
  generateChatId(branch) {
    const timestamp = Date.now();
    const sanitizedBranch = branch.replace(/[^a-zA-Z0-9-]/g, '-');
    return `${sanitizedBranch}-${timestamp}`;
  }
}

export default Storage;
