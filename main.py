#!/usr/bin/env python3
"""
xAI Terminal - Interactive terminal application for interacting with xAI models.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Any

from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from xai_sdk import Client
from xai_sdk.chat import user, assistant

# Initialize Rich console for enhanced terminal output
console = Console()


class ChatSession:
    """Manages chat session state and conversation history."""
    
    def __init__(self, client: Client, model: str, system_prompt: Optional[str] = None):
        self.client = client
        self.model = model
        self.system_prompt = system_prompt
        self.chat = self._create_chat()
    
    def _create_chat(self):
        """Create a new chat session."""
        # Note: xAI SDK may not support system prompts directly in chat.create
        # We'll handle it by adding it as the first user message if needed
        return self.client.chat.create(model=self.model)
    
    def add_user_message(self, content: str):
        """Add a user message to the conversation history."""
        self.chat.append(user(content))
    
    def add_assistant_message(self, content: str):
        """Add an assistant message to the conversation history."""
        self.chat.append(assistant(content))
    
    def clear(self):
        """Clear conversation history and recreate chat session."""
        self.chat = self._create_chat()
        # Re-add system prompt if it exists
        if self.system_prompt:
            # System prompts might need to be handled differently
            # For now, we'll skip it as xAI SDK may not support it directly
            pass
    
    def switch_model(self, new_model: str):
        """Switch to a different model."""
        self.model = new_model
        self.chat = self._create_chat()


class Config:
    """Manages application configuration."""
    
    def __init__(
        self,
        model: str = "grok-4-1-fast",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = True,
        system_prompt: Optional[str] = None,
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.stream = stream
        self.system_prompt = system_prompt
    
    def update(self, **kwargs):
        """Update configuration parameters."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def display(self):
        """Display current configuration."""
        console.print("\n[bold cyan]Current Configuration:[/bold cyan]")
        console.print(f"  Model: {self.model}")
        console.print(f"  Temperature: {self.temperature}")
        console.print(f"  Max Tokens: {self.max_tokens}")
        console.print(f"  Streaming: {self.stream}")
        if self.system_prompt:
            console.print(f"  System Prompt: {self.system_prompt[:50]}...")
        console.print()


def load_config_from_env() -> Dict[str, Any]:
    """
    Load configuration from .env file.
    
    .env file format:
    # Required
    XAI_API_KEY=your_api_key_here
    
    # Optional configuration (with defaults)
    XAI_MODEL=grok-4-1-fast
    XAI_TEMPERATURE=0.7
    XAI_MAX_TOKENS=2048
    XAI_STREAM=true
    XAI_SYSTEM_PROMPT=You are a helpful assistant.
    """
    load_dotenv()
    
    config = {}
    
    # Required: API key
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        console.print("[bold red]Error:[/bold red] XAI_API_KEY not found in environment variables.")
        console.print("Please create a .env file with your API key:")
        console.print("  XAI_API_KEY=your_api_key_here")
        sys.exit(1)
    config["api_key"] = api_key
    
    # Optional: Model (default: grok-4-1-fast)
    config["model"] = os.getenv("XAI_MODEL", "grok-4-1-fast")
    
    # Optional: Temperature (default: 0.7)
    try:
        config["temperature"] = float(os.getenv("XAI_TEMPERATURE", "0.7"))
    except ValueError:
        config["temperature"] = 0.7
    
    # Optional: Max tokens (default: 2048)
    try:
        config["max_tokens"] = int(os.getenv("XAI_MAX_TOKENS", "2048"))
    except ValueError:
        config["max_tokens"] = 2048
    
    # Optional: Streaming (default: true)
    stream_val = os.getenv("XAI_STREAM", "true").lower()
    config["stream"] = stream_val in ["true", "1", "yes", "on"]
    
    # Optional: System prompt (default: None)
    config["system_prompt"] = os.getenv("XAI_SYSTEM_PROMPT", None)
    
    return config


def read_file_content(file_path: str) -> str:
    """Read content from a file."""
    try:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        return path.read_text(encoding="utf-8")
    except Exception as e:
        console.print(f"[bold red]Error reading file:[/bold red] {e}")
        sys.exit(1)


def display_help():
    """Display help information for available commands."""
    help_text = """
[bold cyan]Available Commands:[/bold cyan]

  [bold]/exit[/bold] or [bold]/quit[/bold]  - Exit the application
  [bold]/clear[/bold]                      - Clear conversation history
  [bold]/model <name>[/bold]               - Switch to a different model
  [bold]/config[/bold]                     - Show current configuration
  [bold]/help[/bold]                       - Show this help message

[bold cyan]Configuration Commands:[/bold cyan]

  [bold]/temperature <value>[/bold]        - Set temperature (0.0-2.0)
  [bold]/max-tokens <value>[/bold]         - Set maximum tokens
  [bold]/stream on|off[/bold]              - Enable/disable streaming
"""
    console.print(Panel(help_text, title="Help", border_style="blue"))


def handle_command(command: str, config: Config, session: ChatSession) -> bool:
    """
    Handle special commands. Returns True if command was handled, False otherwise.
    Returns None if the application should exit.
    """
    parts = command.strip().split()
    if not parts:
        return False
    
    cmd = parts[0].lower()
    
    if cmd in ["/exit", "/quit"]:
        console.print("\n[bold yellow]Goodbye![/bold yellow]")
        return None
    
    elif cmd == "/clear":
        session.clear()
        console.print("[bold green]Conversation history cleared.[/bold green]\n")
        return True
    
    elif cmd == "/model":
        if len(parts) < 2:
            console.print("[bold red]Error:[/bold red] Please specify a model name.")
            console.print("Example: /model grok-4-1-fast")
            return True
        new_model = parts[1]
        config.update(model=new_model)
        session.switch_model(new_model)
        console.print(f"[bold green]Model changed to:[/bold green] {new_model}\n")
        return True
    
    elif cmd == "/config":
        config.display()
        return True
    
    elif cmd == "/help":
        display_help()
        return True
    
    elif cmd == "/temperature":
        if len(parts) < 2:
            console.print("[bold red]Error:[/bold red] Please specify a temperature value (0.0-2.0).")
            return True
        try:
            temp = float(parts[1])
            if not 0.0 <= temp <= 2.0:
                raise ValueError("Temperature must be between 0.0 and 2.0")
            config.update(temperature=temp)
            console.print(f"[bold green]Temperature set to:[/bold green] {temp}\n")
        except ValueError as e:
            console.print(f"[bold red]Error:[/bold red] {e}\n")
        return True
    
    elif cmd == "/max-tokens":
        if len(parts) < 2:
            console.print("[bold red]Error:[/bold red] Please specify a max tokens value.")
            return True
        try:
            max_tokens = int(parts[1])
            if max_tokens < 1:
                raise ValueError("Max tokens must be at least 1")
            config.update(max_tokens=max_tokens)
            console.print(f"[bold green]Max tokens set to:[/bold green] {max_tokens}\n")
        except ValueError as e:
            console.print(f"[bold red]Error:[/bold red] {e}\n")
        return True
    
    elif cmd == "/stream":
        if len(parts) < 2:
            console.print("[bold red]Error:[/bold red] Please specify 'on' or 'off'.")
            return True
        stream_val = parts[1].lower()
        if stream_val in ["on", "true", "1"]:
            config.update(stream=True)
            console.print("[bold green]Streaming enabled.[/bold green]\n")
        elif stream_val in ["off", "false", "0"]:
            config.update(stream=False)
            console.print("[bold green]Streaming disabled.[/bold green]\n")
        else:
            console.print("[bold red]Error:[/bold red] Please specify 'on' or 'off'.\n")
        return True
    
    return False


def stream_response(session: ChatSession, config: Config) -> str:
    """Stream response from xAI API and display it in real-time."""
    full_response = ""
    
    try:
        console.print("[bold cyan]Assistant:[/bold cyan] ", end="")
        
        # xAI SDK streaming API
        for response, chunk in session.chat.stream():
            # Handle different chunk structures
            content = None
            if hasattr(chunk, "content"):
                content = chunk.content
            elif isinstance(chunk, str):
                content = chunk
            elif hasattr(chunk, "text"):
                content = chunk.text
            
            if content:
                full_response += content
                console.print(content, end="", style="white", flush=True)
        
        console.print("\n")
        return full_response
        
    except Exception as e:
        console.print(f"\n[bold red]Error during streaming:[/bold red] {e}")
        raise


def get_response(session: ChatSession, config: Config) -> str:
    """Get complete response from xAI API (non-streaming)."""
    try:
        response = session.chat.sample()
        
        # Handle different response structures
        if hasattr(response, "content"):
            return response.content
        elif hasattr(response, "text"):
            return response.text
        elif isinstance(response, str):
            return response
        else:
            raise ValueError("Invalid response format from API")
            
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise


def chat_loop(config: Config, session: ChatSession):
    """Main interactive chat loop."""
    console.print("\n[bold green]xAI Terminal[/bold green] - Interactive chat session started.")
    console.print("Type [bold]/help[/bold] for available commands, or [bold]/exit[/bold] to quit.\n")
    
    if config.system_prompt:
        console.print(f"[dim]System prompt: {config.system_prompt[:100]}...[/dim]\n")
    
    while True:
        try:
            # Get user input
            user_input = Prompt.ask("[bold yellow]You[/bold yellow]")
            
            if not user_input.strip():
                continue
            
            # Handle commands
            if user_input.startswith("/"):
                result = handle_command(user_input, config, session)
                if result is None:  # Exit command
                    break
                if result:  # Command was handled
                    continue
            
            # Add user message to session
            session.add_user_message(user_input)
            
            # Get response from API
            try:
                if config.stream:
                    response_text = stream_response(session, config)
                else:
                    console.print("[bold cyan]Assistant:[/bold cyan] ", end="")
                    response_text = get_response(session, config)
                    console.print(response_text)
                    console.print()
                
                # Add assistant response to session
                session.add_assistant_message(response_text)
                
            except KeyboardInterrupt:
                console.print("\n[bold yellow]Interrupted by user.[/bold yellow]\n")
                continue
            except Exception as e:
                console.print(f"\n[bold red]API Error:[/bold red] {e}\n")
                # Note: xAI SDK manages messages internally, so we don't need to manually remove
                continue
                
        except KeyboardInterrupt:
            console.print("\n\n[bold yellow]Exiting...[/bold yellow]")
            break
        except EOFError:
            console.print("\n\n[bold yellow]Exiting...[/bold yellow]")
            break


def parse_arguments():
    """Parse command-line arguments. CLI args override .env values."""
    parser = argparse.ArgumentParser(
        description="Interactive terminal application for xAI models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="xAI model to use (overrides XAI_MODEL from .env)",
    )
    
    parser.add_argument(
        "--temperature",
        type=float,
        default=None,
        help="Temperature parameter 0.0-2.0 (overrides XAI_TEMPERATURE from .env)",
    )
    
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=None,
        help="Maximum tokens in response (overrides XAI_MAX_TOKENS from .env)",
    )
    
    parser.add_argument(
        "--file",
        type=str,
        help="Read initial prompt from file",
    )
    
    parser.add_argument(
        "--no-stream",
        action="store_true",
        help="Disable streaming responses (overrides XAI_STREAM from .env)",
    )
    
    parser.add_argument(
        "--system",
        type=str,
        default=None,
        help="Set system prompt (overrides XAI_SYSTEM_PROMPT from .env)",
    )
    
    return parser.parse_args()


def main():
    """Main entry point."""
    # Load configuration from .env file
    # .env file format:
    # XAI_API_KEY=your_api_key_here          # Required
    # XAI_MODEL=grok-4-1-fast                     # Optional, default: grok-4-1-fast
    # XAI_TEMPERATURE=0.7                     # Optional, default: 0.7
    # XAI_MAX_TOKENS=2048                     # Optional, default: 2048
    # XAI_STREAM=true                          # Optional, default: true (use true/false, yes/no, on/off, 1/0)
    # XAI_SYSTEM_PROMPT=You are a helpful assistant.  # Optional, default: None
    env_config = load_config_from_env()
    
    # Parse command-line arguments (these override .env values)
    args = parse_arguments()
    
    # Initialize xAI client
    try:
        client = Client(api_key=env_config["api_key"])
    except Exception as e:
        console.print(f"[bold red]Error initializing xAI client:[/bold red] {e}")
        sys.exit(1)
    
    # Create configuration, using CLI args if provided, otherwise .env values
    # For streaming: if --no-stream is provided, disable it; otherwise use .env value
    stream_value = False if args.no_stream else env_config["stream"]
    
    config = Config(
        model=args.model if args.model is not None else env_config["model"],
        temperature=args.temperature if args.temperature is not None else env_config["temperature"],
        max_tokens=args.max_tokens if args.max_tokens is not None else env_config["max_tokens"],
        stream=stream_value,
        system_prompt=args.system if args.system is not None else env_config["system_prompt"],
    )
    
    # Create chat session
    session = ChatSession(client, config.model, system_prompt=config.system_prompt)
    
    # Handle file input if provided
    if args.file:
        file_content = read_file_content(args.file)
        console.print(f"[bold green]Loaded prompt from file:[/bold green] {args.file}\n")
        console.print(f"[dim]{file_content[:200]}...[/dim]\n")
        # Add file content as initial user message
        session.add_user_message(file_content)
        
        # Get response to file content
        try:
            if config.stream:
                response_text = stream_response(session, config)
            else:
                console.print("[bold cyan]Assistant:[/bold cyan] ", end="")
                response_text = get_response(session, config)
                console.print(response_text)
                console.print()
            
            session.add_assistant_message(response_text)
        except Exception as e:
            console.print(f"[bold red]Error processing file content:[/bold red] {e}")
            sys.exit(1)
    
    # Start interactive chat loop
    chat_loop(config, session)


if __name__ == "__main__":
    main()
