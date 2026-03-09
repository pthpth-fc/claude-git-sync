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
exports.BranchItem = exports.BranchTreeProvider = void 0;
const vscode = __importStar(require("vscode"));
class BranchTreeProvider {
    constructor(sessionManager) {
        this.sessionManager = sessionManager;
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
    }
    refresh() {
        this._onDidChangeTreeData.fire();
    }
    getTreeItem(element) {
        return element;
    }
    async getChildren(element) {
        if (element) {
            return [];
        }
        const branches = await this.sessionManager.getAllBranchesWithCounts();
        return branches.map(branch => new BranchItem(branch.name, branch.count, vscode.TreeItemCollapsibleState.None));
    }
}
exports.BranchTreeProvider = BranchTreeProvider;
class BranchItem extends vscode.TreeItem {
    constructor(branchName, messageCount, collapsibleState) {
        super(branchName, collapsibleState);
        this.branchName = branchName;
        this.messageCount = messageCount;
        this.collapsibleState = collapsibleState;
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
exports.BranchItem = BranchItem;
//# sourceMappingURL=treeView.js.map