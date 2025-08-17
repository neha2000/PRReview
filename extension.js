const vscode = require('vscode');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

function activate(context) {
    console.log('PR Review extension activated');
    let disposable = vscode.commands.registerCommand('pr-review.start', async function () {
        console.log('pr-review.start command invoked');
        // Prompt for PR URL
        const prUrl = await vscode.window.showInputBox({
            prompt: 'Enter GitHub PR URL to review',
            placeHolder: 'https://github.com/owner/repo/pull/123'
        });
        console.log('PR URL entered:', prUrl);
        if (!prUrl) return;

        // Run Python backend to fetch PR details
        const pythonScript = path.join(context.extensionPath, 'pr_backend.py');
        // Ensure the Python backend writes to a path inside the extension folder
        const summaryPath = path.join(context.extensionPath, 'changes.txt');
        console.log('Running Python script:', pythonScript, 'with output:', summaryPath);
        exec(`python "${pythonScript}" "${prUrl}" "${summaryPath}"`, (err, stdout, stderr) => {
            console.log('Python backend exit. err=', err, 'stdout=', stdout, 'stderr=', stderr);
            if (err) {
                vscode.window.showErrorMessage('Error running Python backend: ' + stderr);
                return;
            }
            // Read PR details from pr_summary.md
            fs.readFile(summaryPath, 'utf8', (err, prDetails) => {
                if (err) {
                    vscode.window.showErrorMessage('Could not read PR summary: ' + err.message);
                    return;
                }
                // Read PR template
                const templatePath = path.join(context.extensionPath, 'prtemplate.md');
                fs.readFile(templatePath, 'utf8', (err, template) => {
                    if (err) {
                        vscode.window.showErrorMessage('Could not read PR template: ' + err.message);
                        return;
                    }
                    // Insert PR details into template
                    const finalContent = template.replace('<!-- The extension will insert PR details here automatically -->', prDetails);
                    // Write to a temp file and open in editor
                    const tempFile = path.join(context.extensionPath, 'pr_review.md');
                    fs.writeFile(tempFile, finalContent, err => {
                        if (err) {
                            vscode.window.showErrorMessage('Could not write review file: ' + err.message);
                            return;
                        }
                        vscode.workspace.openTextDocument(tempFile).then(doc => {
                            vscode.window.showTextDocument(doc);
                            vscode.window.showInformationMessage('PR review checklist and details opened.'
                               +'\n  Use Copilot Chat to review with following Prompt :'
                                + '\n\n' + 'Use PR Details section to certify sections in Pull Request Review checklist .'
                                +'\n Certify by yes/no update . For every yes/no give the reason'
                            );
                            // Auto-trigger Copilot Chat on the opened file
                            vscode.commands.executeCommand('github.copilot.chat.openPanel');
                        });
                    });
                });
            });
        });
    });
    context.subscriptions.push(disposable);
}

function deactivate() {
    console.log('PR Review extension deactivated');
}

module.exports = {
    activate,
    deactivate
};
