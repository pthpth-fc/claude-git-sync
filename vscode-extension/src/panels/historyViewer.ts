import * as vscode from 'vscode';
import { SessionManager } from '../sessionManager';

export class HistoryViewerPanel {
    public static currentPanel: HistoryViewerPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private _disposables: vscode.Disposable[] = [];

    private constructor(
        panel: vscode.WebviewPanel,
        extensionUri: vscode.Uri,
        private sessionManager: SessionManager,
        private branch: string
    ) {
        this._panel = panel;

        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
        this._update();
    }

    public static createOrShow(
        extensionUri: vscode.Uri,
        sessionManager: SessionManager,
        branch: string
    ) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;

        if (HistoryViewerPanel.currentPanel) {
            HistoryViewerPanel.currentPanel._panel.reveal(column);
            HistoryViewerPanel.currentPanel.branch = branch;
            HistoryViewerPanel.currentPanel._update();
            return;
        }

        const panel = vscode.window.createWebviewPanel(
            'claudeHistoryViewer',
            `Chat History: ${branch}`,
            column || vscode.ViewColumn.One,
            {
                enableScripts: true,
                localResourceRoots: [extensionUri]
            }
        );

        HistoryViewerPanel.currentPanel = new HistoryViewerPanel(
            panel,
            extensionUri,
            sessionManager,
            branch
        );
    }

    private async _update() {
        this._panel.title = `Chat History: ${this.branch}`;
        this._panel.webview.html = await this._getHtmlForWebview();
    }

    private async _getHtmlForWebview(): Promise<string> {
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

    public dispose() {
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
