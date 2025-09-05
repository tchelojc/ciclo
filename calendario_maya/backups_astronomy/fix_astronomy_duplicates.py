import ast
import os
from pathlib import Path
import shutil
from typing import Dict, List

class AstronomyDuplicatesFixer:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.mayan_astro_path = self.root_dir / 'calendario_maya' / 'utils' / 'mayan_astronomy.py'
        self.backup_dir = self.root_dir / 'backups_astronomy'
        
    def create_backup(self):
        """Cria backup dos arquivos antes de modificar"""
        self.backup_dir.mkdir(exist_ok=True)
        for py_file in (self.root_dir / 'calendario_maya').rglob('*.py'):
            if 'mayan_astronomy.py' not in str(py_file):
                shutil.copy2(py_file, self.backup_dir / py_file.name)

    def find_duplicates(self) -> Dict[str, List[dict]]:
        """Identifica funções duplicadas em todo o projeto"""
        duplicates = {}
        for py_file in (self.root_dir / 'calendario_maya').rglob('*.py'):
            if 'test' in str(py_file) or 'mayan_astronomy.py' in str(py_file):
                continue
                
            with open(py_file, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
                
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_name = node.name
                    if func_name.startswith('_') or func_name.startswith('test'):
                        continue
                        
                    duplicates.setdefault(func_name, []).append({
                        'file': str(py_file),
                        'lineno': node.lineno,
                        'code': ast.get_source_segment(f.read(), node)
                    })
                    
        return {k: v for k, v in duplicates.items() if len(v) > 1}

    def consolidate_functions(self):
        """Consolida funções astronômicas no arquivo principal"""
        duplicates = self.find_duplicates()
        
        with open(self.mayan_astro_path, 'a', encoding='utf-8') as main_file:
            for func_name, locations in duplicates.items():
                # Adiciona apenas uma versão da função
                main_file.write(f"\n\n# Consolidated from: {locations[0]['file']}\n")
                main_file.write(locations[0]['code'] + "\n")
                
                # Comenta as duplicatas nos outros arquivos
                for loc in locations[1:]:
                    self._comment_out_duplicate(loc['file'], func_name)

    def _comment_out_duplicate(self, filepath: str, func_name: str):
        """Comenta a função duplicada no arquivo original"""
        with open(filepath, 'r+', encoding='utf-8') as f:
            lines = f.readlines()
            f.seek(0)
            
            for i, line in enumerate(lines):
                if f"def {func_name}(" in line:
                    lines[i] = f"# [DUPLICATE] Removed - Consolidated in mayan_astronomy.py\n# {line}"
                    
            f.writelines(lines)
            f.truncate()

if __name__ == "__main__":
    print("=== Iniciando correção de duplicatas astronômicas ===")
    fixer = AstronomyDuplicatesFixer()
    fixer.create_backup()
    fixer.consolidate_functions()
    print("✅ Duplicatas consolidadas com sucesso!")
    print(f"Backups disponíveis em: {fixer.backup_dir}")