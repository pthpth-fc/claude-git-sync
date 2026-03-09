import * as vscode from 'vscode';
import { GitIntegration } from './gitIntegration';
import { SessionManager } from './sessionManager';
import { BranchTreeProvider } from './treeView';
import { StatusBarManager } from './statusBar';
import { HistoryViewerPanel } from './panels/historyViewer';
import { ConflictHelperPanel } from './panels/conflictHelper';

export function activate(context: vscode.ExtensionContext) {
    console.log('Claude Git Sync extension is now active');

    // Initialize managers
    const gitIntegration = new GitIntegration();
    const sessionManager = new SessionManager();
    const statusBar = new StatusBarManager();

    // Initialize tree view
    const treeProvider = new BranchTreeProvider(sessionManager);
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
        vscode.window.showInformationMessage(
            'Claude Git Sync is not set up in this repository. Run setup_integration.py to get started.'
        );
        return;
    }

    // Update status bar
    updateStatusBar(statusBar, gitIntegration, sessionManager);

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('claudeGitSync.syncCurrent', async () => {
            const result = await sessionManager.syncCurrent();
            if (result) {
                vscode.window.showInformationMessage('Chat session saved');
                treeProvider.refresh();
                updateStatusBar(statusBar, gitIntegration, sessionManager);
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('claudeGitSync.switchBranch', async (branchName?: string) => {
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
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('claudeGitSync.showHistory', async () => {
            const branch = await gitIntegration.getCurrentBranch();
            if (branch) {
                HistoryViewerPanel.createOrShow(context.extensionUri, sessionManager, branch);
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('claudeGitSync.showConflicts', async () => {
            const hasConflicts = await gitIntegration.hasConflicts();
            if (hasConflicts) {
                ConflictHelperPanel.createOrShow(context.extensionUri, sessionManager);
            } else {
                vscode.window.showInformationMessage('No merge conflicts detected');
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('claudeGitSync.vacuum', async () => {
            const result = await sessionManager.vacuum();
            if (result) {
                vscode.window.showInformationMessage('Storage optimization complete');
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('claudeGitSync.showStatus', async () => {
            const status = await sessionManager.getStatus();
            if (status) {
                vscode.window.showInformationMessage(status);
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('claudeGitSync.refreshBranches', () => {
            treeProvider.refresh();
            updateStatusBar(statusBar, gitIntegration, sessionManager);
            vscode.window.showInformationMessage('Branches refreshed');
        })
    );

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

function updateStatusBar(
    statusBar: StatusBarManager,
    gitIntegration: GitIntegration,
    sessionManager: SessionManager
) {
    gitIntegration.getCurrentBranch().then(branch => {
        if (branch) {
            sessionManager.getMessageCount(branch).then(count => {
                statusBar.update(branch, count);
            });
        }
    });
}

export function deactivate() {
    console.log('Claude Git Sync extension deactivated');
}
