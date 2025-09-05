# tests/test_code_duplication.py
import ast
import os
import sys
from collections import defaultdict
from pathlib import Path

def analyze_ast_functions(filepath):
    """Analisa um arquivo Python e retorna suas funções/métodos"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(filepath, 'r', encoding='latin-1') as f:
                content = f.read()
        except Exception as e:
            print(f"Erro ao ler arquivo {filepath}: {e}")
            return []
    
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return []
    
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append({
                'name': node.name,
                'file': str(filepath),
                'lineno': node.lineno,
                'args': [a.arg for a in node.args.args]
            })
    return functions

def find_duplicate_functions(project_root):
    """Encontra funções duplicadas em todo o projeto"""
    project_path = Path(project_root)
    all_functions = []
    
    # Coleta todas as funções do projeto
    for py_file in project_path.rglob('*.py'):
        if 'tests' in str(py_file) or 'venv' in str(py_file):
            continue
        all_functions.extend(analyze_ast_functions(py_file))
    
    # Agrupa por nome de função
    func_dict = defaultdict(list)
    for func in all_functions:
        func_dict[func['name']].append(func)
    
    # Filtra apenas as duplicadas
    duplicates = {k: v for k, v in func_dict.items() if len(v) > 1}
    
    return duplicates

def test_code_duplication():
    """Teste que identifica e sugere correções para funções duplicadas"""
    project_root = os.path.dirname(os.path.dirname(__file__))
    duplicates = find_duplicate_functions(project_root)
    
    # Filtra apenas as funções astronômicas relevantes
    astronomy_duplicates = {
        k: v for k, v in duplicates.items()
        if any('astronom' in f['file'].lower() for f in v) 
        and not k.startswith('__')
    }
    
    # Gera relatório
    if astronomy_duplicates:
        print("\n🔍 Funções astronômicas duplicadas encontradas:")
        for func_name, locations in astronomy_duplicates.items():
            print(f"\nFunção: {func_name}")
            for loc in locations:
                print(f"  - {loc['file']}:{loc['lineno']}")
        
        # Sugere correção automática
        print("\n✅ Recomendação de correção:")
        print("1. Centralize todas as funções em utils/mayan_astronomy.py")
        print("2. Remova as duplicatas dos outros arquivos")
        print("3. Atualize os imports para usar a versão centralizada")
        
        # Cria arquivo de correção automática
        with open("fix_astronomy_duplicates.py", "w") as f:
            f.write("# Script de correção automática para funções duplicadas\n")
            f.write("from pathlib import Path\n\n")
            f.write("def fix_duplicates():\n")
            f.write("    \"\"\"Move funções para mayan_astronomy.py\"\"\"\n")
            f.write("    # Implementação da correção iria aqui\n")
            f.write("    print('Execute este script para aplicar as correções')\n")
        
        print("\n✏️ Script de correção gerado: fix_astronomy_duplicates.py")
    else:
        print("✅ Nenhuma função astronômica duplicada encontrada!")
    
    # O teste "falha" se encontrar duplicatas (para alertar)
    assert not astronomy_duplicates, "Funções duplicadas encontradas - ver relatório acima"

if __name__ == "__main__":
    test_code_duplication()