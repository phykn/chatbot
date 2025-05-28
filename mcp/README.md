# MCP Server

A versatile MCP (Model Context Protocol) server built on the FastMCP framework. Currently implements web search functionality and is designed with a modular structure for easy extension of additional features.


## Overview

This server implements the MCP protocol, which provides standardized communication between AI models and external tools. FastMCP is a high-level Python framework that abstracts complex protocol details, allowing developers to focus on business logic.


## Currently Implemented Features

### Web Search

Provides real-time web search and content extraction functionality through DuckDuckGo. This feature is implemented using the `@mcp.tool()` decorator, enabling AI models to search for the latest information.


## Installation

### Required Packages

Install the following packages to run this server:

```
pip install fastmcp requests beautifulsoup4 duckduckgo-search transformers
```

Package roles:
- **fastmcp**: MCP server framework
- **requests**: HTTP request handling
- **beautifulsoup4**: HTML parsing and content extraction
- **duckduckgo-search**: DuckDuckGo search API client
- **transformers**: Tokenizer and language model processing


## Usage

### Running the Server

To start the server with default settings:

```
python main.py
```

This command runs the server on localhost:8002 with SSE (Server-Sent Events) transport by default.

### Command Line Options

You can configure various options when running the server:

```
python main.py --host localhost --port 8002 --transport sse
```

**Available Options:**
- `--host`: Host address for server binding (default: localhost)
- `--port`: Port number for the server (default: 8002)
- `--transport`: Communication transport method (default: sse)