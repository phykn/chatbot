# Simple Chatbot
A concise chatbot interface developed using Gradio, offering seamless interaction with language models through a local API server. Features include real-time text generation, response streaming, and markdown rendering with adjustable parameters.

## Development Purpose
- Implement chatbot with minimal code
- Provide intuitive user interface
- Create interruptible response system
- Ensure easy extensibility

## Usage
```bash
# Install required libraries
pip install -r requirements.txt

# Run the application
python app.py

# Access at 
http://localhost:8081 (default)
```

## Key Features
- **User-Centered Interface**: Gradio-based UI with markdown rendering
- **Stop Functionality**: Response generation interruption via "STOP" button
- **Thinking Mode**: View model's reasoning process with toggle activation
- **Customizable Settings**: Adjust token limits and select different models

## Project Structure
```
simple-chatbot/
├── app.py              # Main Gradio application
├── src/                # Core functionality
└── assets/             # UI resources
```

## Example
![image]("example/figure.jpg")

## Planned Development
- MCP Server Integration