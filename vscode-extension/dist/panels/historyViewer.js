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
exports.HistoryViewerPanel = void 0;
const vscode = __importStar(require("vscode"));
class HistoryViewerPanel {
    constructor(panel, extensionUri, sessionManager, branch) {
        this.sessionManager = sessionManager;
        this.branch = branch;
        this._disposables = [];
        this._panel = panel;
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
        this._update();
    }
    static createOrShow(extensionUri, sessionManager, branch) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;
        if (HistoryViewerPanel.currentPanel) {
            HistoryViewerPanel.currentPanel._panel.reveal(column);
            HistoryViewerPanel.currentPanel.branch = branch;
            HistoryViewerPanel.currentPanel._update();
            return;
        }
        const panel = vscode.window.createWebviewPanel('claudeHistoryViewer', `Chat History: ${branch}`, column || vscode.ViewColumn.One, {
            enableScripts: true,
            localResourceRoots: [extensionUri]
        });
        HistoryViewerPanel.currentPanel = new HistoryViewerPanel(panel, extensionUri, sessionManager, branch);
    }
    async _update() {
        this._panel.title = `Chat History: ${this.branch}`;
        this._panel.webview.html = await this._getHtmlForWebview();
    }
    async _getHtmlForWebview() {
        const messageCount = await this.sessionManager.getMessageCount(this.branch);
        // Get actual messages
        let messagesHtml = '';
        try {
            const output = await this.sessionManager.runCommand('history', [this.branch, '--limit', '50']);
            // Parse the output to extract messages
            // This is a simple implementation - could be enhanced
            messagesHtml = '<div class="messages-list">';
            if (messageCount > 0) {
                messagesHtml += `<p><strong>Showing last 50 messages (${messageCount} total)</strong></p>`;
                messagesHtml += '<p>For detailed view with full content, use CLI:</p>';
                messagesHtml += `<code>git-claude history ${this.branch}</code><br><br>`;
                // Show that messages exist
                const sessionPath = `${this.sessionManager['workspaceRoot']}/.claude-git-sync/sessions/${this.branch}.jsonl`;
                messagesHtml += `<div class="info">Session file: ${sessionPath}</div>`;
                messagesHtml += `<div class="info">Messages available via CLI commands</div>`;
            }
            else {
                messagesHtml += '<p>No messages in this branch yet.</p>';
            }
            messagesHtml += '</div>';
        }
        catch (error) {
            messagesHtml = `<p>Error loading messages: ${error}</p>`;
        }
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Chat History</title>
            <style>
                body {
                    padding: 20px;
                    font-family: var(--vscode-font-family);
                    color: var(--vscode-foreground);
                    background-color: var(--vscode-editor-background);
                }
                .header {
                    border-bottom: 1px solid var(--vscode-panel-border);
                    padding-bottom: 10px;
                    margin-bottom: 20px;
                }
                .info {
                    padding: 8px;
                    margin: 8px 0;
                    background-color: var(--vscode-textCodeBlock-background);
                    border-radius: 4px;
                }
                code {
                    background-color: var(--vscode-textCodeBlock-background);
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-family: var(--vscode-editor-font-family);
                }
                .messages-list {
                    line-height: 1.6;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📜 Chat History: ${this.branch}</h1>
                <p>Total messages: ${messageCount}</p>
            </div>
            ${messagesHtml}
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid var(--vscode-panel-border);">
                <h3>Available Commands</h3>
                <ul>
                    <li><code>git-claude history ${this.branch}</code> - View full timeline</li>
                    <li><code>git-claude search "pattern"</code> - Search messages</li>
                    <li><code>git-claude stats</code> - Show statistics</li>
                </ul>
            </div>
        </body>
        </html>`;
    }
    dispose() {
        HistoryViewerPanel.currentPanel = undefined;
        this._panel.dispose();
        while (this._disposables.length) {
            const disposable = this._disposables.pop();
            if (disposable) {
                disposable.dispose();
            }
        }
    }
}
exports.HistoryViewerPanel = HistoryViewerPanel;
//# sourceMappingURL=historyViewer.js.map