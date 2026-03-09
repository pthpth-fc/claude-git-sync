import * as vscode from 'vscode';
import { SessionManager } from '../sessionManager';

export class ConflictHelperPanel {
    public static currentPanel: ConflictHelperPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private _disposables: vscode.Disposable[] = [];

    private constructor(
        panel: vscode.WebviewPanel,
        extensionUri: vscode.Uri,
        private sessionManager: SessionManager
    ) {
        this._panel = panel;

        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
        this._update();
    }

    public static createOrShow(
        extensionUri: vscode.Uri,
        sessionManager: SessionManager
    ) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;

        if (ConflictHelperPanel.currentPanel) {
            ConflictHelperPanel.currentPanel._panel.reveal(column);
            ConflictHelperPanel.currentPanel._update();
            return;
        }

        const panel = vscode.window.createWebviewPanel(
            'claudeConflictHelper',
            'Merge Conflict Helper',
            column || vscode.ViewColumn.One,
            {
                enableScripts: true,
                localResourceRoots: [extensionUri]
            }
        );

        ConflictHelperPanel.currentPanel = new ConflictHelperPanel(
            panel,
            extensionUri,
            sessionManager
        );
    }

    private async _update() {
        this._panel.webview.html = await this._getHtmlForWebview();
    }

    private async _getHtmlForWebview(): Promise<string> {
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

    public dispose() {
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
