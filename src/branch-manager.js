#!/usr/bin/env node
import { Storage } from './storage.js';
import { execSync } from 'child_process';

/**
 * Branch-Chat Manager
 * Handles the logic for syncing branches with chat sessions
 */

export class BranchManager {
  constructor(repoRoot) {
    this.storage = new Storage(repoRoot);
  }

  /**
   * Initialize a new branch with chat session
   * Creates hierarchical inheritance from parent branch
   */
  initBranch(branch, parentBranch = null) {
    const existingChatId = this.storage.getChatIdForBranch(branch);

    if (existingChatId) {
      console.log(`Branch "${branch}" already has chat session: ${existingChatId}`);
      return existingChatId;
    }

    // Determine parent branch
    const parent = parentBranch || this.storage.getCurrentBranch();

    // Create new chat ID
    const chatId = this.storage.generateChatId(branch);

    // Set up mappings
    this.storage.setBranchMapping(branch, chatId);

    if (parent && parent !== branch) {
      this.storage.setParentBranch(branch, parent);
    }

    // Initialize chat state with inherited context
    const inheritedContext = this.getInheritedContext(branch);
    this.storage.saveChatState(chatId, {
      branch,
      parentBranch: parent,
      inheritedContext,
      messages: [],
      created: new Date().toISOString()
    });

    console.log(`✓ Initialized chat session for branch "${branch}"`);
    console.log(`  Chat ID: ${chatId}`);
    if (parent && parent !== branch) {
      console.log(`  Inherits from: ${parent}`);
    }

    return chatId;
  }

  /**
   * Get inherited context from parent branches
   */
  getInheritedContext(branch) {
    const chain = this.storage.getInheritanceChain(branch);
    const contexts = [];

    for (const ancestor of chain) {
      if (ancestor === branch) continue;

      const chatId = this.storage.getChatIdForBranch(ancestor);
      if (chatId) {
        const chatState = this.storage.loadChatState(chatId);
        if (chatState) {
          contexts.push({
            branch: ancestor,
            chatId,
            summary: this.summarizeChat(chatState)
          });
        }
      }
    }

    return contexts;
  }

  /**
   * Summarize chat for inheritance
   */
  summarizeChat(chatState) {
    return {
      messageCount: chatState.messages?.length || 0,
      lastActivity: chatState.timestamp,
      topics: chatState.topics || []
    };
  }

  /**
   * Switch to a branch's chat session
   */
  switchToBranch(branch) {
    // Check if branch exists
    if (!this.storage.branchExists(branch)) {
      console.error(`Branch "${branch}" does not exist`);
      return null;
    }

    // Get or create chat session for branch
    let chatId = this.storage.getChatIdForBranch(branch);

    if (!chatId) {
      console.log(`No chat session found for "${branch}", creating new one...`);
      chatId = this.initBranch(branch);
    }

    const chatState = this.storage.loadChatState(chatId);

    console.log(`\n📝 Switched to chat session for branch: ${branch}`);
    console.log(`   Chat ID: ${chatId}`);

    const chain = this.storage.getInheritanceChain(branch);
    if (chain.length > 1) {
      console.log(`   Inheritance: ${chain.join(' → ')}`);
    }

    if (chatState?.messages) {
      console.log(`   Messages: ${chatState.messages.length}`);
    }

    return chatState;
  }

  /**
   * Save current chat state
   */
  saveCurrentChat(messages, metadata = {}) {
    const currentBranch = this.storage.getCurrentBranch();
    let chatId = this.storage.getChatIdForBranch(currentBranch);

    if (!chatId) {
      chatId = this.initBranch(currentBranch);
    }

    this.storage.saveChatState(chatId, {
      branch: currentBranch,
      messages,
      metadata,
      lastSaved: new Date().toISOString()
    });

    console.log(`✓ Saved chat state for branch "${currentBranch}"`);
  }

  /**
   * Create new branch with chat session
   */
  createBranch(newBranch, baseBranch = null) {
    const base = baseBranch || this.storage.getCurrentBranch();

    try {
      // Create Git branch
      execSync(`git checkout -b ${newBranch}`, {
        cwd: this.storage.repoRoot,
        stdio: 'inherit'
      });

      // Initialize chat session
      this.initBranch(newBranch, base);

      console.log(`\n✓ Created branch "${newBranch}" from "${base}"`);
      console.log(`  Chat session initialized with inherited context`);

    } catch (error) {
      console.error(`Failed to create branch: ${error.message}`);
    }
  }

  /**
   * Get status information
   */
  getStatus() {
    const currentBranch = this.storage.getCurrentBranch();
    const chatId = this.storage.getChatIdForBranch(currentBranch);
    const mappings = this.storage.getBranchMapping();

    return {
      currentBranch,
      currentChatId: chatId,
      totalBranches: Object.keys(mappings).length,
      mappings
    };
  }
}

export default BranchManager;
