"""
Componentes de interface do usuário
"""

from .formatting import (
    format_system_message,
    format_error_message,
    format_success_message,
    format_info_message,
    format_chat_message,
    format_connection_info,
    format_prompt,
    Fore,  # Adicionando Fore para uso em outros módulos
    Style  # Adicionando Style para uso em outros módulos
)

from .messages import MessageHandler

__all__ = [
    'MessageHandler',
    'format_system_message',
    'format_error_message',
    'format_success_message',
    'format_info_message',
    'format_chat_message',
    'format_connection_info',
    'format_prompt',
    'Fore',
    'Style'
]