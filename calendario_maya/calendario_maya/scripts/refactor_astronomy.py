# scripts/refactor_astronomy.py
import os
import ast
from pathlib import Path
import shutil
import re

def backup_file(filepath):
    """Cria backup do arquivo"""
    backup_path = str(filepath) + '.bak'
    shutil.copyfile(filepath, backup_path)
    return backup_path

def comment_duplicate_functions(filepath, duplicates):
    """Comenta funções duplicadas no arquivo, mantendo a original"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    modified = False
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Verifica se é o início de uma função duplicada
        for func in duplicates:
            if f'def {func}(' in line and not line.strip().startswith('#'):
                # Encontra o bloco completo da função
                func_lines = [line]
                indent = len(re.match(r'^\s*', line).group())
                i += 1
                while i < len(lines):
                    current_line = lines[i]
                    if (current_line.strip() and 
                        len(re.match(r'^\s*', current_line).group()) > indent):
                        func_lines.append(current_line)
                        i += 1
                    else:
                        break
                
                # Comenta o bloco inteiro
                commented_block = []
                for l in func_lines:
                    if l.strip():  # Não comenta linhas vazias
                        commented_block.append(f"# [DUPLICADA - MOVIDA PARA mayan_astronomy.py]\n#{l}")
                    else:
                        commented_block.append(l)
                
                new_lines.extend(commented_block)
                modified = True
                continue
                
        new_lines.append(line)
        i += 1
    
    if modified:
        backup_file(filepath)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        return True
    return False

def replace_astronomy_calculations():
    """Substitui cálculos astronômicos pela classe centralizada"""
    project_root = Path(__file__).parent.parent
    mayan_astronomy_path = project_root / 'utils' / 'mayan_astronomy.py'
    
    # 1. Criar constants/astronomia.py se não existir
    constants_dir = project_root / 'constants'
    constants_dir.mkdir(exist_ok=True)
    
    astronomia_path = constants_dir / 'astronomia.py'
    if not astronomia_path.exists():
        with open(astronomia_path, 'w', encoding='utf-8') as f:
            f.write('''"""
Constantes astronômicas centralizadas
"""

from math import radians, degrees, sin, cos, acos

PERIODOS_ORBITAIS = {
    'terra': {
        'sideral': 365.256363004,
        'sinodico': 365.24219,
        'inclinacao': 23.4392811
    },
    'venus': {
        'sideral': 224.70079922,
        'sinodico': 583.92,
        'inclinacao': 3.39458
    }
}

EARTH_ORBITAL_PERIOD = PERIODOS_ORBITAIS['terra']['sideral']
VENUS_ORBITAL_PERIOD = PERIODOS_ORBITAIS['venus']['sideral']
GALACTIC_YEAR_DAYS = 225000000\n''')

    # 2. Lista de funções astronômicas duplicadas (do teste anterior)
    astronomy_duplicates = [
        '__init__', 'calculate_baktun', 'get_planetary_positions',
        'calculate_cosmic_data', '_harmonic_convergence', '_normalize_date',
        'calculate_galactic_venus_cycles', '_get_fallback_venus_data',
        'set_tikal_location', '_angular_distance', '_galactic_year_progress',
        '_next_venus_galactic_alignment', '_current_venus_cycle',
        'get_cosmic_calendar', 'get_venus_matrix', '_calculate_venus_energy',
        '_quantum_phase'
    ]
    
    # 3. Atualizar arquivos comentando as duplicatas
    target_files = [
        'interface/widgets/cosmos_view.py',
        'core/connector.py',
        'utils/astronomy.py',
        'utils/astronomy_utils.py',
        'utils/basic_astronomy.py',
        'utils/base_astronomy.py'
    ]
    
    files_modified = 0
    for file_path in target_files:
        full_path = project_root / file_path
        if full_path.exists():
            if comment_duplicate_functions(full_path, astronomy_duplicates):
                files_modified += 1
                print(f"✓ Comentou duplicatas em: {file_path}")
    
    # 4. Atualizar imports nos mesmos arquivos
    for file_path in target_files:
        full_path = project_root / file_path
        if full_path.exists():
            with open(full_path, 'r+', encoding='utf-8') as f:
                content = f.read()
                new_content = content.replace(
                    'from calendario_maya.utils.astronomy import',
                    'from calendario_maya.utils.mayan_astronomy import'
                )
                # Adiciona import se não existir
                if 'from calendario_maya.utils.mayan_astronomy import' not in new_content:
                    new_content = (
                        'from calendario_maya.utils.mayan_astronomy import MayanAstronomy\n' +
                        new_content
                    )
                f.seek(0)
                f.write(new_content)
                f.truncate()
    
    print(f"\n✅ Refatoração concluída com sucesso! {files_modified} arquivos modificados.")
    print("Backups dos arquivos originais foram criados com extensão .bak")
    print("\n⚠️ ATENÇÃO: As funções duplicadas foram comentadas, não removidas.")
    print("Você pode descomentar se necessário, mas recomendamos migrar para")
    print("a versão centralizada em utils/mayan_astronomy.py")

if __name__ == "__main__":
    replace_astronomy_calculations()