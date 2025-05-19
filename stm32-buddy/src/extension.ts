import * as vscode from 'vscode';
import axios from 'axios';

interface PredictionResponse {
  prediction: "buggy" | "clean";
}

export function activate(context: vscode.ExtensionContext) {
    // Affiche un WebView avec ton chatbot
    // const panel = vscode.window.createWebviewPanel(
    //     'stm32BuddyChat',
    //     'STM32 Buddy Chatbot',
    //     vscode.ViewColumn.One,
    //     { enableScripts: true }
    // );

    // panel.webview.html = `
    // <html>
    //     <head>
    //         <title>STM32 Buddy Chatbot</title>
    //     </head>
    //     <body style="margin: 0; overflow: hidden;">
    //         <iframe 
    //             src="http://127.0.0.1:7860"
    //             allow="clipboard-read; clipboard-write; microphone"
    //             style="width: 100%; height: 100%; min-height: 700px; border: none;">
    //         </iframe>
    //     </body>
    // </html>`;

const openChatbotCommand = vscode.commands.registerCommand('stm32-buddy.openChatbot', () => {
  const panel = vscode.window.createWebviewPanel(
    'stm32BuddyChat',
    'STM32 Buddy Chatbot',
    vscode.ViewColumn.One,
    { enableScripts: true }
  );

  panel.webview.html = `
  <html>
      <head>
          <title>STM32 Buddy Chatbot</title>
      </head>
      <body style="margin: 0; overflow: hidden;">
          <iframe 
              src="http://127.0.0.1:7860"
              allow="clipboard-read; clipboard-write; microphone"
              style="width: 100%; height: 100%; min-height: 700px; border: none;">
          </iframe>
      </body>
  </html>`;
});

context.subscriptions.push(openChatbotCommand);


  const explainFunctionCommand = vscode.commands.registerCommand('commentgen.explainFunction', async () => {
    const editor = vscode.window.activeTextEditor;

    if (!editor) {
        vscode.window.showErrorMessage('Aucun éditeur actif.');
        return;
    }

    const selection = editor.selection;
    const selectedText = editor.document.getText(selection);

    if (!selectedText.trim()) {
        vscode.window.showErrorMessage('Aucune fonction sélectionnée.');
        return;
    }

    try {
        const response = await axios.post('http://127.0.0.1:8000/generate-comment', {
            code: selectedText
        });

        const comment = response.data.commented_code;

        const commentedLines = comment
            .split('\n')
            .map((line: string) => `// ${line}`)
            .join('\n');

        await editor.edit(editBuilder => {
        editBuilder.insert(selection.start, `${commentedLines}\n`);
});


        vscode.window.showInformationMessage('Commentaire ajouté avec succès.');
    } catch (error: any) {
        const message = error.response?.data?.detail || error.message || 'Erreur inconnue';
        vscode.window.showErrorMessage(`Erreur API : ${message}`);
    }
});

context.subscriptions.push(explainFunctionCommand);


let disposable = vscode.commands.registerCommand('bugDetector.detectBug', async () => {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      vscode.window.showErrorMessage("No active editor");
      return;
    }

    const selection = editor.selection;
    const selectedText = editor.document.getText(selection).trim();

    if (!selectedText) {
      vscode.window.showWarningMessage("Please select some code first.");
      return;
    }

    try {
      const res = await fetch("http://localhost:8000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: selectedText }),
      });

      if (!res.ok) {
        vscode.window.showErrorMessage(`API Error: ${res.statusText}`);
        return;
      }

      const data = (await res.json()) as PredictionResponse;

      if (data.prediction === "buggy") {
        vscode.window.showWarningMessage("🚨 The selected code is likely buggy.");
      } else {
        vscode.window.showInformationMessage("✅ The selected code looks clean.");
      }
    } catch (error) {
      vscode.window.showErrorMessage(`Request failed: ${error}`);
    }
  });

  context.subscriptions.push(disposable);

  // 🧠 Commande pour détecter le type d'erreur
const detectErrorType = vscode.commands.registerCommand('bugDetector.errorType', async () => {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage("No active editor.");
        return;
    }

    const selectedText = editor.document.getText(editor.selection).trim();
    if (!selectedText) {
        vscode.window.showWarningMessage("Please select some code first.");
        return;
    }

    try {
        const response = await axios.post("http://localhost:8000/predict-error-type", {
            code: selectedText
        });

        const errorType = response.data.error_type || "Unknown";
        vscode.window.showInformationMessage(`🧠 Type d'erreur détectée : ${errorType}`);
    } catch (error: any) {
        const message = error.response?.data?.detail || error.message || 'Erreur inconnue';
        vscode.window.showErrorMessage(`Erreur API : ${message}`);
    }
});
context.subscriptions.push(detectErrorType);

// 🔍 Commande pour analyse ligne par ligne
const analyzeLines = vscode.commands.registerCommand('bugDetector.lineByLine', async () => {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage("No active editor.");
        return;
    }

    const selectedText = editor.document.getText(editor.selection).trim();
    if (!selectedText) {
        vscode.window.showWarningMessage("Please select some code first.");
        return;
    }

    try {
        const response = await axios.post("http://localhost:8000/predict-lines-error-type", {
            code: selectedText
        });

        const result = response.data.result || [];
        if (result.length === 0) {
            vscode.window.showInformationMessage("✅ Aucun problème détecté ligne par ligne.");
            return;
        }

        // Afficher dans un OutputChannel pour plus de lisibilité
        const output = vscode.window.createOutputChannel("STM32 Line Analyzer");
        output.clear();
        output.appendLine("🔍 Résultat de l'analyse ligne par ligne :\n");
        result.forEach((item: { line: string; error_type: string }, index: number) => {
            output.appendLine(`Ligne ${index + 1}: ${item.line}`);
            output.appendLine(`   🛑 Erreur: ${item.error_type}\n`);
        });
        output.show();
    } catch (error: any) {
        const message = error.response?.data?.detail || error.message || 'Erreur inconnue';
        vscode.window.showErrorMessage(`Erreur API : ${message}`);
    }
});
context.subscriptions.push(analyzeLines);

// ✨ Inline Autocompletion Provider pour STM32
const inlineProvider: vscode.InlineCompletionItemProvider = {
    provideInlineCompletionItems: async (
        document: vscode.TextDocument,
        position: vscode.Position,
        context: vscode.InlineCompletionContext,
        token: vscode.CancellationToken
    ): Promise<vscode.InlineCompletionList> => {

        const linePrefix = document.lineAt(position).text.substring(0, position.character);

        try {
            const response = await axios.post('http://127.0.0.1:8000/stm32-autocomplete', {
                prefix: linePrefix
            });

            if (response.data && response.data.completion) {
                const completion = response.data.completion;
                const range = new vscode.Range(position, position);
                const item = new vscode.InlineCompletionItem(completion, range);
                return new vscode.InlineCompletionList([item]);
            }
        } catch (err) {
            console.error('API error:', err);
        }

        return new vscode.InlineCompletionList([]);
    }
};

// Enregistrement du fournisseur pour le langage C
context.subscriptions.push(
    vscode.languages.registerInlineCompletionItemProvider({ language: 'c' }, inlineProvider)
);

// Forcer l’activation du inlineSuggest
const config = vscode.workspace.getConfiguration('editor');
const previousSetting = config.get('inlineSuggest.enabled');
context.globalState.update('originalInlineSuggestEnabled', previousSetting);
config.update('inlineSuggest.enabled', true, vscode.ConfigurationTarget.Global);

console.log('Congratulations, your extension "t5-code-generator" is now active!');

  const helloWorldDisposable = vscode.commands.registerCommand('t5-code-generator.helloWorld', () => {
    vscode.window.showInformationMessage('Hello World from T5CodeGenerator!');
  });

  const generateCodeDisposable = vscode.commands.registerCommand('t5-code-generator.generateCode', async () => {
    const prompt = await vscode.window.showInputBox({
      placeHolder: 'Enter a function description (e.g., "Generate a function to initialize GPIO for STM32")',
      prompt: 'Describe the STM32 code you want to generate',
      validateInput: (value) => value.trim() ? null : 'Prompt cannot be empty'
    });

    if (prompt) {
      try {
        console.log('Sending request to server with prompt:', prompt);
        const response = await axios.post('http://127.0.0.1:5000/generate', { prompt });
        const generatedCode = (response.data as { code: string }).code;
        console.log('Received code from server:', generatedCode);

        if (!generatedCode || generatedCode.trim() === '') {
          vscode.window.showErrorMessage('No code generated by the server.');
          return;
        }

        const editor = vscode.window.activeTextEditor;
        if (editor) {
          editor.edit(editBuilder => {
            const position = editor.selection.active;
            editBuilder.insert(position, generatedCode + '\n');
          });
          vscode.window.showInformationMessage('Code inserted into editor!');
        } else {
          vscode.window.showInformationMessage(`Generated code:\n${generatedCode}`);
        }
      } catch (error) {
        const errorMessage = (error as any).message || 'Unknown error';
        console.log('Error from server:', errorMessage);
        vscode.window.showErrorMessage(`Error generating code: ${errorMessage}`);
      }
    } else {
      vscode.window.showInformationMessage('No prompt provided, code generation canceled.');
    }
  });

  context.subscriptions.push(helloWorldDisposable, generateCodeDisposable);

  const generateTestCodeDisposable = vscode.commands.registerCommand('t5-code-generator.generateTestCode', async () => {
  const functionCode = await vscode.window.showInputBox({
    placeHolder: 'Enter a function (e.g., "void init_GPIO() {...}")',
    prompt: 'Enter the STM32 function code you want to generate tests for',
    validateInput: (value) => value.trim() ? null : 'Function code cannot be empty'
  });

  if (functionCode) {
    try {
      console.log('Sending test generation request to server with function code:', functionCode);

      const response = await axios.post('http://127.0.0.1:7000/generate-test', {
        function_code: functionCode
      });

      const generatedTestCode = (response.data as { generated_test: string }).generated_test;
      console.log('Received generated test code from server:', generatedTestCode);

      if (!generatedTestCode || generatedTestCode.trim() === '') {
        vscode.window.showErrorMessage('No test code generated by the server.');
        return;
      }

      const editor = vscode.window.activeTextEditor;
      if (editor) {
        editor.edit(editBuilder => {
          const position = editor.selection.active;
          editBuilder.insert(position, generatedTestCode + '\n');
        });
        vscode.window.showInformationMessage('Test code inserted into editor!');
      } else {
        vscode.window.showInformationMessage(`Generated test code:\n${generatedTestCode}`);
      }
    } catch (error) {
      const errorMessage = (error as any).message || 'Unknown error';
      console.log('Error from test server:', errorMessage);
      vscode.window.showErrorMessage(`Error generating test code: ${errorMessage}`);
    }
  } else {
    vscode.window.showInformationMessage('No function code provided. Test generation canceled.');
  }
});

context.subscriptions.push(generateTestCodeDisposable);



}

export async function deactivate() {
    const config = vscode.workspace.getConfiguration('editor');
    const original = await vscode.workspace.getConfiguration().get('originalInlineSuggestEnabled');
    if (original !== undefined) {
        config.update('inlineSuggest.enabled', original, vscode.ConfigurationTarget.Global);
    }
}
