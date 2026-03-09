import * as vscode from 'vscode';

export class StatusBarManager {
    private statusBarItem: vscode.StatusBarItem;

    constructor() {
        this.statusBarItem = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Left,
            100
        );

        this.statusBarItem.command = 'claudeGitSync.showHistory';
        this.statusBarItem.show();
    }

    update(branch: string, messageCount: number): void {
        const config = vscode.workspace.getConfiguration('claudeGitSync');
        const showStatusBar = config.get('showStatusBar', true);

        if (!showStatusBar) {
            this.statusBarItem.hide();
            return;
        }

        this.statusBarItem.text = `$(comment-discussion) ${branch} (${messageCount})`;
        this.statusBarItem.tooltip = `Claude Chat: ${messageCount} messages on ${branch}\nClick to view history`;
        this.statusBarItem.show();
    }

    dispose(): void {
        this.statusBarItem.dispose();
    }
}
