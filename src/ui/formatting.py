from datetime import datetime
from colorama import Fore, Style

def format_chat_message(peer_id, message):
    """Formats chat messages"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    return f"\r{Fore.BLUE}[{timestamp}] {Fore.GREEN}{peer_id}{Fore.RESET}: {message}"

def format_system_message(message):
    """Formats system messages"""
    return f"{Fore.YELLOW}{message}{Style.RESET_ALL}"

def format_error_message(message):
    """Formats error messages"""
    return f"{Fore.RED}{message}{Style.RESET_ALL}"

def format_success_message(message):
    """Formats success messages"""
    return f"{Fore.GREEN}{message}{Style.RESET_ALL}"

def format_info_message(message):
    """Formats informational messages"""
    return f"{Fore.CYAN}{message}{Style.RESET_ALL}"

def format_connection_info(host, port, peer_id, secret):
    """Formats connection information"""
    header = f"\n{Fore.CYAN}{'=' * 20} Connection Information {'=' * 20}{Style.RESET_ALL}"
    info = [
        header,
        format_info_message(f"ID: {peer_id}"),
        format_info_message(f"Address: {host}:{port}"),
        format_info_message(f"Secret: {secret}"),
        f"\n{Fore.YELLOW}Connection string (copy this line):{Style.RESET_ALL}",
        f"{Fore.GREEN}{host}:{port}:{secret}{Style.RESET_ALL}",
        f"\n{Fore.CYAN}Type 'help' to see available commands{Style.RESET_ALL}",
        Fore.CYAN + "=" * 65 + Style.RESET_ALL + "\n"
    ]
    return '\n'.join(info)

def format_prompt(peer_id):
    """Formats the input prompt"""
    return f"{Fore.GREEN}{peer_id}{Fore.RESET}: "
