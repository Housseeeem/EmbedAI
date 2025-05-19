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
