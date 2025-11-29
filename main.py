#!/usr/bin/env python3
"""
xAI Terminal - Interactive terminal application for interacting with xAI models.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional

from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from xai_sdk import Client

# Initialize Rich console for enhanced terminal output
console = Console()


class ChatSession:
    """Manages chat session state and conversation history."""
    
    def __init__(self, system_prompt: Optional[str] = None):
        self.messages: List[Dict[str, str]] = []
        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})
    
    def add_user_message(self, content: str):
        """Add a user message to the conversation history."""
        self.messages.append({"role": "user", "content": content})
    
    def add_assistant_message(self, content: str):
        """Add an assistant message to the conversation history."""
        self.messages.append({"role": "assistant", "content": content})
    
    def clear(self):
        """Clear conversation history while preserving system prompt."""
        system_msg = None
        if self.messages and self.messages[0].get("role") == "system":
            system_msg = self.messages[0]
        self.messages = []
        if system_msg:
            self.messages.append(system_msg)
    
    def get_messages(self) -> List[Dict[str, str]]:
        """Get all messages in the conversation."""
        return self.messages.copy()


class Config:
    """Manages application configuration."""
    
    def __init__(
        self,
        model: str = "grok-beta",
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


def load_api_key() -> str:
    """Load API key from environment variables."""
    load_dotenv()
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        console.print("[bold red]Error:[/bold red] XAI_API_KEY not found in environment variables.")
        console.print("Please create a .env file with your API key:")
        console.print("  XAI_API_KEY=your_api_key_here")
        sys.exit(1)
    return api_key


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
            console.print("Example: /model grok-beta")
            return True
        new_model = parts[1]
        config.update(model=new_model)
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


def stream_response(client: Client, messages: List[Dict[str, str]], config: Config) -> str:
    """Stream response from xAI API and display it in real-time."""
    full_response = ""
    
    try:
        response = client.chat.completions.create(
            model=config.model,
            messages=messages,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            stream=True,
        )
        
        console.print("[bold cyan]Assistant:[/bold cyan] ", end="")
        
        for chunk in response:
            if hasattr(chunk, "choices") and chunk.choices:
                delta = chunk.choices[0].delta
                if hasattr(delta, "content") and delta.content:
                    content = delta.content
                    full_response += content
                    console.print(content, end="", style="white")
        
        console.print("\n")
        return full_response
        
    except Exception as e:
        console.print(f"\n[bold red]Error during streaming:[/bold red] {e}")
        raise


def get_response(client: Client, messages: List[Dict[str, str]], config: Config) -> str:
    """Get complete response from xAI API (non-streaming)."""
    try:
        response = client.chat.completions.create(
            model=config.model,
            messages=messages,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            stream=False,
        )
        
        if hasattr(response, "choices") and response.choices:
            content = response.choices[0].message.content
            return content
        else:
            raise ValueError("Invalid response format from API")
            
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise


def chat_loop(client: Client, config: Config, session: ChatSession):
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
                    response_text = stream_response(client, session.get_messages(), config)
                else:
                    console.print("[bold cyan]Assistant:[/bold cyan] ", end="")
                    response_text = get_response(client, session.get_messages(), config)
                    console.print(response_text)
                    console.print()
                
                # Add assistant response to session
                session.add_assistant_message(response_text)
                
            except KeyboardInterrupt:
                console.print("\n[bold yellow]Interrupted by user.[/bold yellow]\n")
                continue
            except Exception as e:
                console.print(f"\n[bold red]API Error:[/bold red] {e}\n")
                # Remove the user message if API call failed
                if session.messages and session.messages[-1].get("role") == "user":
                    session.messages.pop()
                continue
                
        except KeyboardInterrupt:
            console.print("\n\n[bold yellow]Exiting...[/bold yellow]")
            break
        except EOFError:
            console.print("\n\n[bold yellow]Exiting...[/bold yellow]")
            break


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Interactive terminal application for xAI models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default="grok-beta",
        help="xAI model to use (default: grok-beta)",
    )
    
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Temperature parameter (0.0-2.0, default: 0.7)",
    )
    
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=2048,
        help="Maximum tokens in response (default: 2048)",
    )
    
    parser.add_argument(
        "--file",
        type=str,
        help="Read initial prompt from file",
    )
    
    parser.add_argument(
        "--no-stream",
        action="store_true",
        help="Disable streaming responses",
    )
    
    parser.add_argument(
        "--system",
        type=str,
        help="Set system prompt",
    )
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Load API key
    api_key = load_api_key()
    
    # Initialize xAI client
    try:
        client = Client(api_key=api_key)
    except Exception as e:
        console.print(f"[bold red]Error initializing xAI client:[/bold red] {e}")
        sys.exit(1)
    
    # Create configuration
    config = Config(
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        stream=not args.no_stream,
        system_prompt=args.system,
    )
    
    # Create chat session
    session = ChatSession(system_prompt=config.system_prompt)
    
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
                response_text = stream_response(client, session.get_messages(), config)
            else:
                console.print("[bold cyan]Assistant:[/bold cyan] ", end="")
                response_text = get_response(client, session.get_messages(), config)
                console.print(response_text)
                console.print()
            
            session.add_assistant_message(response_text)
        except Exception as e:
            console.print(f"[bold red]Error processing file content:[/bold red] {e}")
            sys.exit(1)
    
    # Start interactive chat loop
    chat_loop(client, config, session)


if __name__ == "__main__":
    main()
