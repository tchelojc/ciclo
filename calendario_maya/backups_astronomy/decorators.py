# core/decorators.py
def quantum_entangle(func):
    """Garante que todas as dependências estão entrelaçadas"""
    def wrapper(*args, **kwargs):
        from core.quantum_connector import qc
        required = ['DataManager', 'GlyphViewer']
        if all(qc.get(cls) for cls in required):
            return func(*args, **kwargs)
        raise ImportError("Sistema em estado de superposição")
    return wrapper