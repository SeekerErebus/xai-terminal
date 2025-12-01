# xAI Terminal

An interactive terminal application for interacting with xAI models (like Grok) via the command line. Features include streaming responses, conversation history, model selection, file input support, and configurable parameters.

## Features

- **Interactive Chat Sessions**: Continuous conversation loop with xAI models
- **Streaming Responses**: Real-time token streaming for immediate feedback
- **Conversation History**: Maintains context throughout the session
- **Model Selection**: Switch between different xAI models
- **File Input**: Read prompts from files
- **Configurable Parameters**: Adjust temperature, max tokens, and more
- **Rich Terminal UI**: Enhanced formatting with colors and panels
- **Command Interface**: Special commands for session management

## Installation

### Prerequisites

- Python 3.10 or higher
- An xAI API key

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd xai-terminal
```

2. Install dependencies using `uv` (recommended) or `pip`:
```bash
# Using uv
uv sync

# Or using pip
pip install -e .
```

3. Create a `.env` file in the project root and add your xAI API key:
```bash
echo "XAI_API_KEY=your_actual_api_key_here" > .env
```

Or manually create a `.env` file with:
```
XAI_API_KEY=your_actual_api_key_here
```

## Usage

### Basic Usage

Start an interactive chat session:
```bash
python main.py
```

### Command-Line Options

```bash
python main.py [OPTIONS]
```

**Options:**
- `--model MODEL`: Select xAI model (default: `grok-4-1-fast`)
- `--temperature FLOAT`: Set temperature parameter 0.0-2.0 (default: `0.7`)
- `--max-tokens INT`: Set maximum tokens in response (default: `2048`)
- `--file PATH`: Read initial prompt from a file
- `--no-stream`: Disable streaming responses (show complete response at once)
- `--system TEXT`: Set a system prompt for the conversation

### Examples

**Basic chat session:**
```bash
python main.py
```

**Use a specific model:**
```bash
python main.py --model grok-2
```

**Start with a file prompt:**
```bash
python main.py --file prompt.txt
```

**Custom temperature and max tokens:**
```bash
python main.py --temperature 0.9 --max-tokens 4096
```

**With a system prompt:**
```bash
python main.py --system "You are a helpful coding assistant."
```

**Non-streaming mode:**
```bash
python main.py --no-stream
```

## Interactive Commands

During a chat session, you can use the following commands:

- `/exit` or `/quit` - Exit the application
- `/clear` - Clear conversation history (keeps system prompt)
- `/model <name>` - Switch to a different model
- `/config` - Show current configuration
- `/help` - Show available commands
- `/temperature <value>` - Set temperature (0.0-2.0)
- `/max-tokens <value>` - Set maximum tokens
- `/stream on|off` - Enable/disable streaming

### Example Session

```
You: Hello! Can you help me with Python?

Assistant: Of course! I'd be happy to help you with Python. What would you like to know?

You: /config

Current Configuration:
  Model: grok-4-1-fast
  Temperature: 0.7
  Max Tokens: 2048
  Streaming: True

You: /temperature 0.5

Temperature set to: 0.5

You: /exit

Goodbye!
```

## Configuration

### Environment Variables

The application reads configuration from a `.env` file:

- `XAI_API_KEY`: Your xAI API key (required)

### Default Settings

- **Model**: `grok-4-1-fast`
- **Temperature**: `0.7`
- **Max Tokens**: `2048`
- **Streaming**: Enabled

These can be changed via command-line arguments or interactive commands during the session.

## Error Handling

The application includes comprehensive error handling for:
- Missing or invalid API keys
- Network errors
- API rate limits
- Invalid input
- File reading errors

All errors are displayed with clear, user-friendly messages.

## Development

### Project Structure

```
xai-terminal/
├── main.py              # Main application entry point
├── pyproject.toml       # Dependencies and project config
├── .gitignore           # Git ignore rules
├── README.md            # This file
└── uv.lock              # Dependency lock file
```

### Dependencies

- `xai-sdk>=1.4.1` - Official xAI Python SDK
- `python-dotenv>=1.0.0` - Environment variable management
- `rich>=13.0.0` - Enhanced terminal UI

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

