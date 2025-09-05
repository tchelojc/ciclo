import sys
import importlib
from pathlib import Path
import os
from typing import Dict, List, Optional, Type, Any
import logging
import traceback

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class ImportOrganizer:
    """Organizador avançado de imports com diagnóstico e correção automática"""
    
    def __init__(self, base_dir: Optional[str] = None):
        self.logger = self._setup_logger()
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent
        self._add_to_path()
        self.import_cache: Dict[str, Any] = {}
        self.failed_imports: Dict[str, str] = {}
        
    def _setup_logger(self) -> logging.Logger:
        """Configura o logger para o organizador"""
        logger = logging.getLogger('ImportOrganizer')
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
        logger.addHandler(handler)
        return logger
        
    def _add_to_path(self) -> None:
        """Adiciona o diretório base ao path do Python"""
        if str(self.base_dir) not in sys.path:
            sys.path.insert(0, str(self.base_dir))
            self.logger.info(f"✅ Diretório base adicionado ao PATH: {self.base_dir}")
    
    def get_class(self, module_path: str, class_name: str) -> Optional[Type]:
        """
        Importa dinamicamente qualquer classe com tratamento robusto de erros
        e cache de imports bem-sucedidos.
        """
        cache_key = f"{module_path}.{class_name}"
        
        # Verifica o cache primeiro
        if cache_key in self.import_cache:
            self.logger.debug(f"Retornando {cache_key} do cache")
            return self.import_cache[cache_key]
            
        try:
            # Tenta importar o módulo
            module = importlib.import_module(module_path)
            
            # Obtém a classe do módulo
            klass = getattr(module, class_name)
            
            # Armazena no cache
            self.import_cache[cache_key] = klass
            self.logger.info(f"✅ Importado com sucesso: {module_path}.{class_name}")
            return klass
            
        except ImportError as e:
            self._handle_import_error(module_path, class_name, e)
            return None
            
    def _handle_import_error(self, module_path: str, class_name: str, error: Exception) -> None:
        """Trata erros de importação e sugere correções"""
        error_key = f"{module_path}.{class_name}"
        error_msg = str(error)
        self.failed_imports[error_key] = error_msg
        
        self.logger.error(f"❌ Falha ao importar {error_key}: {error_msg}")
        self.logger.debug(traceback.format_exc())
        
        # Sugestões baseadas no tipo de erro
        if "No module named" in error_msg:
            missing_module = error_msg.split("'")[1]
            self.logger.warning(f"👉 Você precisa instalar o módulo: pip install {missing_module}")
        elif "cannot import name" in error_msg:
            self.logger.warning("👉 Possível erro de dependência circular ou classe não existente")
            
    def verify_project_imports(self) -> bool:
        """Verifica todos os imports críticos do projeto"""
        critical_imports = [
            ("core.connector", "Connector"),
            ("interface.main_window", "MainWindow"),
            ("utils.mayan_astronomy", "MayanAstronomy"),
            ("core.data_manager", "DataManager")
        ]
        
        all_ok = True
        for module_path, class_name in critical_imports:
            if not self.get_class(module_path, class_name):
                all_ok = False
                
        return all_ok
        
    def diagnose_import_issues(self) -> Dict[str, List[str]]:
        """Diagnostica problemas comuns de importação e sugere soluções"""
        diagnosis = {"errors": [], "suggestions": []}
        
        # Verifica se o módulo está no path
        if str(self.base_dir) not in sys.path:
            diagnosis["errors"].append("Diretório base não está no PYTHONPATH")
            diagnosis["suggestions"].append(f"Adicione permanentemente: sys.path.append('{self.base_dir}')")
        
        # Verifica imports que falharam
        for imp, error in self.failed_imports.items():
            diagnosis["errors"].append(f"Falha ao importar {imp}: {error}")
            
            if "mayan_astronomy" in imp:
                diagnosis["suggestions"].append(
                    "Verifique se a classe MayanAstronomy está definida em utils/mayan_astronomy.py"
                )
        
        return diagnosis

# Teste avançado
if __name__ == "__main__":
    print("\n🔍 Iniciando diagnóstico completo de imports...")
    organizer = ImportOrganizer()
    
    # Teste de imports críticos
    if organizer.verify_project_imports():
        print("\n✅ Todos os imports críticos funcionando!")
    else:
        print("\n❌ Alguns imports críticos falharam")
        
    # Mostra diagnóstico detalhado
    diagnosis = organizer.diagnose_import_issues()
    if diagnosis["errors"]:
        print("\n=== PROBLEMAS ENCONTRADOS ===")
        for error in diagnosis["errors"]:
            print(f"- {error}")
            
        print("\n=== SUGESTÕES DE CORREÇÃO ===")
        for suggestion in diagnosis["suggestions"]:
            print(f"- {suggestion}")
    else:
        print("\n🌟 Nenhum problema grave encontrado!")
    
    # Teste de instanciação
    try:
        Connector = organizer.get_class("core.connector", "Connector")
        if Connector:
            connector = Connector()
            print(f"\n✅ Instância criada com sucesso: {connector}")
    except Exception as e:
        print(f"\n❌ Falha ao instanciar: {e}")