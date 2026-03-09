import * as vscode from 'vscode';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export class GitIntegration {
    private workspaceRoot: string;

    constructor() {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        this.workspaceRoot = workspaceFolder?.uri.fsPath || '';
    }

    async getCurrentBranch(): Promise<string | null> {
        try {
            const { stdout } = await execAsync('git branch --show-current', {
                cwd: this.workspaceRoot
            });
            return stdout.trim();
        } catch (error) {
            console.error('Error getting current branch:', error);
            return null;
        }
    }

    async getAllBranches(): Promise<string[]> {
        try {
            const { stdout } = await execAsync('git branch --format=%(refname:short)', {
                cwd: this.workspaceRoot
            });
            return stdout.trim().split('\n').filter(b => b.length > 0);
        } catch (error) {
            console.error('Error getting branches:', error);
            return [];
        }
    }

    async hasConflicts(): Promise<boolean> {
        try {
            const { stdout } = await execAsync('git diff --name-only --diff-filter=U', {
                cwd: this.workspaceRoot
            });
            return stdout.trim().length > 0;
        } catch (error) {
            return false;
        }
    }

    async switchBranch(branchName: string): Promise<boolean> {
        try {
            await execAsync(`git checkout "${branchName}"`, {
                cwd: this.workspaceRoot
            });
            return true;
        } catch (error) {
            console.error('Error switching branch:', error);
            return false;
        }
    }
}
