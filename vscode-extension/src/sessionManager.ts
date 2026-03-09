import * as vscode from 'vscode';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as path from 'path';
import * as fs from 'fs';

const execAsync = promisify(exec);

export class SessionManager {
    private workspaceRoot: string;
    private pythonPath: string;
    private scriptPath: string;

    constructor() {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        this.workspaceRoot = workspaceFolder?.uri.fsPath || '';

        const config = vscode.workspace.getConfiguration('claudeGitSync');
        this.pythonPath = config.get('pythonPath') || 'python3';

        this.scriptPath = path.join(this.workspaceRoot, 'src', 'git_sync.py');
    }

    checkSetup(workspacePath: string): boolean {
        const syncDir = path.join(workspacePath, '.claude-git-sync');
        return fs.existsSync(syncDir);
    }

    async runCommand(command: string, args: string[] = []): Promise<string> {
        try {
            const fullCommand = `${this.pythonPath} "${this.scriptPath}" ${command} ${args.join(' ')}`;
            const { stdout, stderr } = await execAsync(fullCommand, {
                cwd: this.workspaceRoot
            });

            if (stderr && !stderr.includes('Warning')) {
                console.error('Command stderr:', stderr);
            }

            return stdout;
        } catch (error: any) {
            console.error('Error running command:', error);
            vscode.window.showErrorMessage(`Claude Git Sync error: ${error.message}`);
            throw error;
        }
    }

    async syncCurrent(): Promise<boolean> {
        try {
            await this.runCommand('save');
            return true;
        } catch (error) {
            return false;
        }
    }

    async switchToBranch(branchName: string): Promise<boolean> {
        try {
            await this.runCommand('switch', [branchName]);
            return true;
        } catch (error) {
            return false;
        }
    }

    async autoSwitch(): Promise<boolean> {
        try {
            await this.runCommand('auto');
            return true;
        } catch (error) {
            return false;
        }
    }

    async vacuum(): Promise<boolean> {
        try {
            await this.runCommand('vacuum', ['--full']);
            return true;
        } catch (error) {
            return false;
        }
    }

    async getStatus(): Promise<string | null> {
        try {
            const output = await this.runCommand('status');
            return output;
        } catch (error) {
            return null;
        }
    }

    async getMessageCount(branch: string): Promise<number> {
        try {
            const metadataPath = path.join(this.workspaceRoot, '.claude-git-sync', 'metadata.json');
            if (!fs.existsSync(metadataPath)) {
                return 0;
            }

            const metadata = JSON.parse(fs.readFileSync(metadataPath, 'utf-8'));
            const branchInfo = metadata.branches?.[branch];
            return branchInfo?.messageCount || 0;
        } catch (error) {
            return 0;
        }
    }

    async getAllBranchesWithCounts(): Promise<Array<{ name: string; count: number }>> {
        try {
            const metadataPath = path.join(this.workspaceRoot, '.claude-git-sync', 'metadata.json');
            if (!fs.existsSync(metadataPath)) {
                return [];
            }

            const metadata = JSON.parse(fs.readFileSync(metadataPath, 'utf-8'));
            const branches = metadata.branches || {};

            return Object.entries(branches).map(([name, info]: [string, any]) => ({
                name,
                count: info.messageCount || 0
            }));
        } catch (error) {
            return [];
        }
    }

    async getHistory(branch: string, limit: number = 20): Promise<any[]> {
        try {
            const output = await this.runCommand('history', [branch, '--limit', limit.toString()]);
            // Parse output - this is a simplified version
            return [];
        } catch (error) {
            return [];
        }
    }

    async getConflicts(): Promise<string> {
        try {
            const output = await this.runCommand('conflicts');
            return output;
        } catch (error) {
            return 'No conflicts detected';
        }
    }
}
