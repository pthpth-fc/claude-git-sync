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
        // In a real implementation, fetch actual history from sessionManager
        const messageCount = await this.sessionManager.getMessageCount(this.branch);
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
                .message {
                    margin-bottom: 15px;
                    padding: 10px;
                    border-left: 3px solid var(--vscode-textLink-foreground);
                    background-color: var(--vscode-editor-inactiveSelectionBackground);
                }
                .message-role {
                    font-weight: bold;
                    margin-bottom: 5px;
                }
                .user { border-left-color: #4CAF50; }
                .assistant { border-left-color: #2196F3; }
                .system { border-left-color: #FF9800; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📜 Chat History: ${this.branch}</h1>
                <p>Total messages: ${messageCount}</p>
            </div>
            <div id="messages">
                <p>Use the Python CLI to view detailed history:</p>
                <code>python3 src/git_sync.py history ${this.branch}</code>
                <br><br>
                <p><em>Full interactive history viewer coming soon!</em></p>
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