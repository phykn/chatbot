<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# MCP-Powered AI Chatbot with Web Search

This project is an AI chatbot system with web search capabilities utilizing **MCP (Model Context Protocol)**. When users ask questions, the AI searches for the latest information from the internet as needed and provides answers as an AI assistant. **The web interface is implemented with Gradio** to provide a user-friendly conversational interface without requiring complex web development knowledge.

**Designed with the simplest possible structure** to make it easy for beginners to understand and modify.

## System Requirements

### **WSL2 Environment**

This project utilizes **WSL2 (Windows Subsystem for Linux 2)** to run Linux-based AI model servers in a Windows environment:

- **Docker Support**: Running vLLM server in Linux container environment
- **GPU Passthrough**: Direct utilization of Windows NVIDIA GPU in WSL2


### **vLLM Server**

**vLLM** is a library for high-speed inference of large language models and **can be easily executed with a batch file (run_vllm.bat)**.

## What is MCP?

**MCP (Model Context Protocol)** is a standard protocol that allows AI models to access external tools or data sources. It acts like "USB-C for AI," helping AI perform tasks such as web searching, file reading, and database access.

## System Operation Principle

### **Step 1: User Input**

Users enter questions through the Gradio web interface.

### **Step 2: LLM Analysis**

The Qwen3 model running on the vLLM server in WSL2 analyzes the question to select appropriate thinking mode and determine web search necessity.

### **Step 3: Web Search (When Needed)**

- MCP server searches for relevant information through DuckDuckGo
- Extracts and summarizes content from searched web pages


### **Step 4: Answer Generation**

vLLM server generates answers based on search results according to the selected mode.

## Key Features

### **Real-time Web Search**

- Search for real-time information such as latest news, weather, stock prices
- Regional search support (configurable)
- Automatically summarize and provide search results


### **Conversation Management**

- Automatic saving and record keeping of conversation content
- Automatic cleanup of previous conversations according to token limits
- New conversation start functionality


### **Real-time Control**

- Response generation interruption functionality
- Real-time thinking mode switching
- Progressive result viewing through streaming responses


## Installation

### **Install Dependencies**

Install the required libraries using pip:

```bash
pip install -r requirements.txt
```


## Usage Instructions

### **1. vLLM Server Execution (Windows)**

```bash
# Execute in Windows Command Prompt
run_vllm.bat
```


### **2. MCP Server Execution**

```bash
python mcp_server.py
```


### **3. Chatbot Execution**

```bash
python chatbot.py
```


### **4. Web Interface Usage**

- **Think/No Think**: Select mode with radio buttons at the bottom
- **STOP**: Interrupt response generation
- **New Chat**: Initialize conversation history


## System Configuration

### **Configuration Files**

- `src/config/mcp.yaml` - MCP server settings
- `src/config/gradio.yaml` - Web interface settings
- `src/config/web.yaml` - Web search engine and summarization settings


### **Prompt Files**

- `src/prompt/core.yaml` - AI system prompts


### **Execution Scripts**

- `run_vllm.bat` - Windows vLLM server execution script


## Qwen3 Features

This system is **written for the Qwen3 model**:

### **Hybrid Thinking Mode**

- **Think Mode**: Functionality that shows step-by-step reasoning processes for complex math, logic, and coding problems
- **No Think Mode**: Functionality that provides quick responses to simple questions
- **Direct Control from Web Interface**: Real-time mode switching with Think/No Think radio buttons on the chatbot screen
- Mode switching also possible through `/think` and `/no_think` tags in prompts