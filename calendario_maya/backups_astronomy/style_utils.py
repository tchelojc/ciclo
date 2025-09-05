import re
import warnings

# Silencia especificamente avisos de CSS
warnings.filterwarnings("ignore", category=UserWarning, message="Unknown property")

def sanitize_stylesheet(style):
    """
    Remove propriedades CSS não suportadas pelo Qt
    Args:
        style: string com código CSS
    Returns:
        string com CSS sanitizado
    """
    # Remove propriedades problemáticas
    properties_to_remove = [
        r'text-shadow\s*:.+?;',
        r'box-shadow\s*:.+?;',
        r'transform\s*:.+?;',
        r'filter\s*:.+?;'
    ]
    
    for prop in properties_to_remove:
        style = re.sub(prop, '', style)
    
    return style.strip()