import * as vscode from 'vscode';
import { SessionManager } from './sessionManager';

export class BranchTreeProvider implements vscode.TreeDataProvider<BranchItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<BranchItem | undefined | null | void> = new vscode.EventEmitter<BranchItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<BranchItem | undefined | null | void> = this._onDidChangeTreeData.event;

    constructor(private sessionManager: SessionManager) {}

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: BranchItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: BranchItem): Promise<BranchItem[]> {
        if (element) {
            return [];
        }

        const branches = await this.sessionManager.getAllBranchesWithCounts();
        return branches.map(branch => new BranchItem(
            branch.name,
            branch.count,
            vscode.TreeItemCollapsibleState.None
        ));
    }
}

export class BranchItem extends vscode.TreeItem {
    constructor(
        public readonly branchName: string,
        public readonly messageCount: number,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState
    ) {
        super(branchName, collapsibleState);

        this.tooltip = `${branchName}: ${messageCount} messages`;
        this.description = `${messageCount} messages`;
        this.iconPath = new vscode.ThemeIcon('git-branch');
        this.contextValue = 'branchItem';

        // Make it clickable
        this.command = {
            command: 'claudeGitSync.switchBranch',
            title: 'Switch to Branch',
            arguments: [branchName]
        };
    }
}
