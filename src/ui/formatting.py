from datetime import datetime
from colorama import Fore, Style

def format_chat_message(peer_id, message):
    """Formata mensagens do chat"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    return f"\r{Fore.BLUE}[{timestamp}] {Fore.GREEN}{peer_id}{Fore.RESET}: {message}"

def format_system_message(message):
    """Formata mensagens do sistema"""
    return f"{Fore.YELLOW}{message}{Style.RESET_ALL}"

def format_error_message(message):
    """Formata mensagens de erro"""
    return f"{Fore.RED}{message}{Style.RESET_ALL}"

def format_success_message(message):
    """Formata mensagens de sucesso"""
    return f"{Fore.GREEN}{message}{Style.RESET_ALL}"

def format_info_message(message):
    """Formata mensagens informativas"""
    return f"{Fore.CYAN}{message}{Style.RESET_ALL}"

def format_connection_info(host, port, peer_id, secret):
    """Formata as informações de conexão"""
    header = f"\n{Fore.CYAN}{'=' * 20} Informações de Conexão {'=' * 20}{Style.RESET_ALL}"
    info = [
        header,
        format_info_message(f"ID: {peer_id}"),
        format_info_message(f"Endereço: {host}:{port}"),
        format_info_message(f"Secret: {secret}"),
        f"\n{Fore.YELLOW}String de conexão (copie esta linha):{Style.RESET_ALL}",
        f"{Fore.GREEN}{host}:{port}:{secret}{Style.RESET_ALL}",
        f"\n{Fore.CYAN}Digite 'help' para ver os comandos disponíveis{Style.RESET_ALL}",
        Fore.CYAN + "=" * 65 + Style.RESET_ALL + "\n"
    ]
    return '\n'.join(info)

def format_prompt(peer_id):
    """Formata o prompt de entrada"""
    return f"{Fore.GREEN}{peer_id}{Fore.RESET}: "