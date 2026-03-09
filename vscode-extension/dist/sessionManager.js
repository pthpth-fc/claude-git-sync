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
exports.SessionManager = void 0;
const vscode = __importStar(require("vscode"));
const child_process_1 = require("child_process");
const util_1 = require("util");
const path = __importStar(require("path"));
const fs = __importStar(require("fs"));
const execAsync = (0, util_1.promisify)(child_process_1.exec);
class SessionManager {
    constructor() {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        this.workspaceRoot = workspaceFolder?.uri.fsPath || '';
        const config = vscode.workspace.getConfiguration('claudeGitSync');
        this.pythonPath = config.get('pythonPath') || 'python3';
        this.scriptPath = path.join(this.workspaceRoot, 'src', 'git_sync.py');
    }
    checkSetup(workspacePath) {
        const syncDir = path.join(workspacePath, '.claude-git-sync');
        return fs.existsSync(syncDir);
    }
    async runCommand(command, args = []) {
        try {
            const fullCommand = `${this.pythonPath} "${this.scriptPath}" ${command} ${args.join(' ')}`;
            const { stdout, stderr } = await execAsync(fullCommand, {
                cwd: this.workspaceRoot
            });
            if (stderr && !stderr.includes('Warning')) {
                console.error('Command stderr:', stderr);
            }
            return stdout;
        }
        catch (error) {
            console.error('Error running command:', error);
            vscode.window.showErrorMessage(`Claude Git Sync error: ${error.message}`);
            throw error;
        }
    }
    async syncCurrent() {
        try {
            await this.runCommand('save');
            return true;
        }
        catch (error) {
            return false;
        }
    }
    async switchToBranch(branchName) {
        try {
            await this.runCommand('switch', [branchName]);
            return true;
        }
        catch (error) {
            return false;
        }
    }
    async autoSwitch() {
        try {
            await this.runCommand('auto');
            return true;
        }
        catch (error) {
            return false;
        }
    }
    async vacuum() {
        try {
            await this.runCommand('vacuum', ['--full']);
            return true;
        }
        catch (error) {
            return false;
        }
    }
    async getStatus() {
        try {
            const output = await this.runCommand('status');
            return output;
        }
        catch (error) {
            return null;
        }
    }
    async getMessageCount(branch) {
        try {
            const metadataPath = path.join(this.workspaceRoot, '.claude-git-sync', 'metadata.json');
            if (!fs.existsSync(metadataPath)) {
                return 0;
            }
            const metadata = JSON.parse(fs.readFileSync(metadataPath, 'utf-8'));
            const branchInfo = metadata.branches?.[branch];
            return branchInfo?.messageCount || 0;
        }
        catch (error) {
            return 0;
        }
    }
    async getAllBranchesWithCounts() {
        try {
            const metadataPath = path.join(this.workspaceRoot, '.claude-git-sync', 'metadata.json');
            if (!fs.existsSync(metadataPath)) {
                return [];
            }
            const metadata = JSON.parse(fs.readFileSync(metadataPath, 'utf-8'));
            const branches = metadata.branches || {};
            return Object.entries(branches).map(([name, info]) => ({
                name,
                count: info.messageCount || 0
            }));
        }
        catch (error) {
            return [];
        }
    }
    async getHistory(branch, limit = 20) {
        try {
            const output = await this.runCommand('history', [branch, '--limit', limit.toString()]);
            // Parse output - this is a simplified version
            return [];
        }
        catch (error) {
            return [];
        }
    }
    async getConflicts() {
        try {
            const output = await this.runCommand('conflicts');
            return output;
        }
        catch (error) {
            return 'No conflicts detected';
        }
    }
}
exports.SessionManager = SessionManager;
//# sourceMappingURL=sessionManager.js.map