"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const gitIntegration_1 = require("./gitIntegration");
const sessionManager_1 = require("./sessionManager");
const treeView_1 = require("./treeView");
const statusBar_1 = require("./statusBar");
const historyViewer_1 = require("./panels/historyViewer");
const conflictHelper_1 = require("./panels/conflictHelper");
function activate(context) {
    console.log('Claude Git Sync extension is now active');
    // Initialize managers
    const gitIntegration = new gitIntegration_1.GitIntegration();
    const sessionManager = new sessionManager_1.SessionManager();
    const statusBar = new statusBar_1.StatusBarManager();
    // Initialize tree view
    const treeProvider = new treeView_1.BranchTreeProvider(sessionManager);
    const treeView = vscode.window.createTreeView('claudeGitSyncBranches', {
        treeDataProvider: treeProvider,
        showCollapseAll: true
    });
    // Check if in git repository with claude-git-sync
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (!workspaceFolder) {
        return;
    }
    const isSetup = sessionManager.checkSetup(workspaceFolder.uri.fsPath);
    if (!isSetup) {
        vscode.window.showInformationMessage('Claude Git Sync is not set up in this repository. Run setup_integration.py to get started.');
        return;
    }
    // Update status bar
    updateStatusBar(statusBar, gitIntegration, sessionManager);
    // Register commands
    context.subscriptions.push(vscode.commands.registerCommand('claudeGitSync.syncCurrent', async () => {
        const result = await sessionManager.syncCurrent();
        if (result) {
            vscode.window.showInformationMessage('Chat session saved');
            treeProvider.refresh();
            updateStatusBar(statusBar, gitIntegration, sessionManager);
        }
    }));
    context.subscriptions.push(vscode.commands.registerCommand('claudeGitSync.switchBranch', async (branchName) => {
        if (!branchName) {
            const branches = await gitIntegration.getAllBranches();
            branchName = await vscode.window.showQuickPick(branches, {
                placeHolder: 'Select a branch to switch to'
            });
        }
        if (branchName) {
            const result = await sessionManager.switchToBranch(branchName);
            if (result) {
                vscode.window.showInformationMessage(`Switched to branch: ${branchName}`);
                treeProvider.refresh();
                updateStatusBar(statusBar, gitIntegration, sessionManager);
            }
        }
    }));
    context.subscriptions.push(vscode.commands.registerCommand('claudeGitSync.showHistory', async () => {
        const branch = await gitIntegration.getCurrentBranch();
        if (branch) {
            historyViewer_1.HistoryViewerPanel.createOrShow(context.extensionUri, sessionManager, branch);
        }
    }));
    context.subscriptions.push(vscode.commands.registerCommand('claudeGitSync.showConflicts', async () => {
        const hasConflicts = await gitIntegration.hasConflicts();
        if (hasConflicts) {
            conflictHelper_1.ConflictHelperPanel.createOrShow(context.extensionUri, sessionManager);
        }
        else {
            vscode.window.showInformationMessage('No merge conflicts detected');
        }
    }));
    context.subscriptions.push(vscode.commands.registerCommand('claudeGitSync.vacuum', async () => {
        const result = await sessionManager.vacuum();
        if (result) {
            vscode.window.showInformationMessage('Storage optimization complete');
        }
    }));
    context.subscriptions.push(vscode.commands.registerCommand('claudeGitSync.showStatus', async () => {
        const status = await sessionManager.getStatus();
        if (status) {
            vscode.window.showInformationMessage(status);
        }
    }));
    context.subscriptions.push(vscode.commands.registerCommand('claudeGitSync.refreshBranches', () => {
        treeProvider.refresh();
        updateStatusBar(statusBar, gitIntegration, sessionManager);
        vscode.window.showInformationMessage('Branches refreshed');
    }));
    // Watch for Git HEAD changes (branch switches)
    const gitHeadWatcher = vscode.workspace.createFileSystemWatcher('**/.git/HEAD');
    gitHeadWatcher.onDidChange(async () => {
        const config = vscode.workspace.getConfiguration('claudeGitSync');
        if (config.get('autoSync')) {
            await sessionManager.autoSwitch();
            treeProvider.refresh();
            updateStatusBar(statusBar, gitIntegration, sessionManager);
        }
    });
    context.subscriptions.push(gitHeadWatcher);
    // Add subscriptions
    context.subscriptions.push(treeView, statusBar);
    console.log('Claude Git Sync extension fully activated');
}
function updateStatusBar(statusBar, gitIntegration, sessionManager) {
    gitIntegration.getCurrentBranch().then(branch => {
        if (branch) {
            sessionManager.getMessageCount(branch).then(count => {
                statusBar.update(branch, count);
            });
        }
    });
}
function deactivate() {
    console.log('Claude Git Sync extension deactivated');
}
//# sourceMappingURL=extension.js.map