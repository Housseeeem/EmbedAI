## Overview

**EmbedAI** is an academic project that facilitates the development and testing of STM32 code.

Our solution is a smart platform designed to assist developers in writing, analyzing, and improving STM32 code. It consists of two main components:

- A **web application** that supports intelligent code analysis and learning tools.
- A **Visual Studio Code (VS Code) extension** tailored to enhance different stages of the STM32 development workflow.
.

## Features

### 🌐 Web Application

The web application allows users to either **write STM32 code manually** or **upload existing STM32 code files**. Once submitted, the code is compiled using **Clang**, enabling:

- Detection of **syntax errors** and **bugs**.
- Clear feedback on the **exact line** and **type of error** to help users understand and resolve issues.

After analysis, users can:

-  **Download a detailed PDF report** containing results and suggestions.
-  **View statistical insights** about error types and frequency.
-  **Track their history** of code analysis sessions for review and learning.

This environment supports developers in continuously improving their code quality through informed feedback and insights.

---

### 🧩 VS Code Extension

The VS Code extension brings intelligent development features directly into the coding environment. Its key functionalities include:

-  **Prompt-based code generation**: Developers can enter a natural language prompt, and the system generates corresponding STM32 code.
-  **Automatic comment generation**: With a single click, the assistant generates descriptive comments, eliminating the need for manual documentation.
-  **AI-powered code autocompletion**: Real-time code suggestions are provided based on user input.
-  **Automatic unit test generation**: STM32-specific unit tests are created automatically to save development time.
-  **Bug detection with detailed feedback**: The system identifies bugs and highlights the error type and line for easier debugging.
-  **Integrated STM32 chatbot**: An embedded chatbot answers technical questions related to STM32, providing immediate developer support.
## 🛠 Tech Stack

**Frontend (Web App):**
- HTML
- CSS
- js
- jQuery
- AJAX 

**Backend:**
- FastAPI (Python)
- Clang (for STM32 code analysis)
- clang Tidy

**AI/ML Models:**
- T5 (for comment generation)
- Bidirectional LSTM (for bug detection and analysis)
- MLP (for classification tasks)

**VS Code Extension:**
- Visual Studio Code
- TypeScript

**Tools:**
- Git & GitHub
- Visual Studio Code


