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
exports.ConflictHelperPanel = void 0;
const vscode = __importStar(require("vscode"));
class ConflictHelperPanel {
    constructor(panel, extensionUri, sessionManager) {
        this.sessionManager = sessionManager;
        this._disposables = [];
        this._panel = panel;
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
        this._update();
    }
    static createOrShow(extensionUri, sessionManager) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;
        if (ConflictHelperPanel.currentPanel) {
            ConflictHelperPanel.currentPanel._panel.reveal(column);
            ConflictHelperPanel.currentPanel._update();
            return;
        }
        const panel = vscode.window.createWebviewPanel('claudeConflictHelper', 'Merge Conflict Helper', column || vscode.ViewColumn.One, {
            enableScripts: true,
            localResourceRoots: [extensionUri]
        });
        ConflictHelperPanel.currentPanel = new ConflictHelperPanel(panel, extensionUri, sessionManager);
    }
    async _update() {
        this._panel.webview.html = await this._getHtmlForWebview();
    }
    async _getHtmlForWebview() {
        const conflictInfo = await this.sessionManager.getConflicts();
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Conflict Helper</title>
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
                .conflict {
                    margin-bottom: 20px;
                    padding: 15px;
                    background-color: var(--vscode-editor-inactiveSelectionBackground);
                    border-left: 4px solid #f44336;
                }
                .conflict-file {
                    font-weight: bold;
                    margin-bottom: 10px;
                    color: var(--vscode-errorForeground);
                }
                .context {
                    margin-top: 10px;
                    padding: 10px;
                    background-color: var(--vscode-textCodeBlock-background);
                    font-family: var(--vscode-editor-font-family);
                    font-size: 0.9em;
                }
                pre {
                    white-space: pre-wrap;
                    word-wrap: break-word;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔥 Merge Conflict Helper</h1>
                <p>Showing relevant chat context for conflicted files</p>
            </div>
            <div id="conflicts">
                <pre>${conflictInfo}</pre>
                <br>
                <p><em>For detailed conflict analysis, use:</em></p>
                <code>python3 src/git_sync.py conflicts</code>
            </div>
        </body>
        </html>`;
    }
    dispose() {
        ConflictHelperPanel.currentPanel = undefined;
        this._panel.dispose();
        while (this._disposables.length) {
            const disposable = this._disposables.pop();
            if (disposable) {
                disposable.dispose();
            }
        }
    }
}
exports.ConflictHelperPanel = ConflictHelperPanel;
//# sourceMappingURL=conflictHelper.js.map