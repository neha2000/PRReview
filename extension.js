const vscode = require('vscode');

class PRReviewProvider {
    async reviewCode(pr_data) {
        try {
            const [model] = await vscode.lm.selectChatModels();
            
            // Create review prompt
            const prompt = `Review this pull request and provide detailed feedback:
                Title: ${pr_data.title}
                Author: ${pr_data.user}
                Changes: ${pr_data.total_changes} lines

                Files Changed:
                ${this._formatFiles(pr_data.files_changed)}

                Please analyze:
                1. Code quality and style
                2. Potential bugs
                3. Security concerns
                4. Performance
                5. Best practices
            `;

            // Get review from VS Code LM
            const response = await model.sendRequest(prompt);
            return response.text;
        } catch (err) {
            if (err instanceof vscode.LanguageModelError) {
                return `Review Error: ${err.message}`;
            }
            throw err;
        }
    }

    _formatFiles(files) {
        return files.map(file => 
            `File: ${file.filename}
             Status: ${file.status}
             Changes: +${file.additions} -${file.deletions}
             Patch:
             ${file.patch || 'No patch available'}`
        ).join('\n\n');
    }
}

module.exports = {
    PRReviewProvider
};
