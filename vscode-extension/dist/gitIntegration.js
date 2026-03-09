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
exports.GitIntegration = void 0;
const vscode = __importStar(require("vscode"));
const child_process_1 = require("child_process");
const util_1 = require("util");
const execAsync = (0, util_1.promisify)(child_process_1.exec);
class GitIntegration {
    constructor() {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        this.workspaceRoot = workspaceFolder?.uri.fsPath || '';
    }
    async getCurrentBranch() {
        try {
            const { stdout } = await execAsync('git branch --show-current', {
                cwd: this.workspaceRoot
            });
            return stdout.trim();
        }
        catch (error) {
            console.error('Error getting current branch:', error);
            return null;
        }
    }
    async getAllBranches() {
        try {
            const { stdout } = await execAsync('git branch --format=%(refname:short)', {
                cwd: this.workspaceRoot
            });
            return stdout.trim().split('\n').filter(b => b.length > 0);
        }
        catch (error) {
            console.error('Error getting branches:', error);
            return [];
        }
    }
    async hasConflicts() {
        try {
            const { stdout } = await execAsync('git diff --name-only --diff-filter=U', {
                cwd: this.workspaceRoot
            });
            return stdout.trim().length > 0;
        }
        catch (error) {
            return false;
        }
    }
    async switchBranch(branchName) {
        try {
            await execAsync(`git checkout "${branchName}"`, {
                cwd: this.workspaceRoot
            });
            return true;
        }
        catch (error) {
            console.error('Error switching branch:', error);
            return false;
        }
    }
}
exports.GitIntegration = GitIntegration;
//# sourceMappingURL=gitIntegration.js.map