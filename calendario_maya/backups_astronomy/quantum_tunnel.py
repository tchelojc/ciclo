from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
import numpy as np
import logging
from typing import Optional

class QuantumTunnel(QObject):
    transition_started = pyqtSignal()
    transition_completed = pyqtSignal()
    culture_changed = pyqtSignal(str)
    quantum_state_updated = pyqtSignal(dict)  # Novo sinal para atualizações de estado
    
    def __init__(self, connector: Optional[QObject] = None):
        super().__init__()
        self.connector = connector
        self._entangled = False
        self._transition_matrix = np.array([
            [0.9, 0.1],  # Probabilidades de transição Maya → Maya/Aztec
            [0.1, 0.9]   # Probabilidades de transição Aztec → Aztec/Maya
        ])
        self._current_state = {
            'culture': 'maya',
            'quantum_phase': 0.0,
            'stability': 1.0
        }
        self.logger = logging.getLogger('QuantumTunnel')
        
    @pyqtSlot(str, str)
    def transition(self, from_culture: str, to_culture: str) -> bool:
        """Executa a transição quântica entre culturas com tratamento completo"""
        self.transition_started.emit()
        self.logger.info(f"Iniciando transição quântica: {from_culture} → {to_culture}")
        
        try:
            # 1. Pré-transição: colapso do estado anterior
            self._collapse_state(from_culture)
            
            # 2. Atualiza matriz de transição baseada no connector (se disponível)
            if self.connector and hasattr(self.connector, 'get_quantum_stability'):
                stability = self.connector.get_quantum_stability()
                self._update_transition_matrix(stability)
            
            # 3. Executa superposição quântica
            success = self._quantum_superposition(from_culture, to_culture)
            
            if not success:
                raise RuntimeError("Falha na superposição quântica")
            
            # 4. Observação do novo estado
            self._observe_state(to_culture)
            
            # 5. Emite sinais de conclusão
            self.culture_changed.emit(to_culture)
            self.transition_completed.emit()
            
            self.logger.info("Transição quântica completada com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Falha na transição quântica: {str(e)}", exc_info=True)
            self._emergency_rollback(from_culture)
            return False

    def _collapse_state(self, state: str) -> None:
        """Prepara o sistema para transição"""
        self._entangled = False
        self._current_state.update({
            'culture': state,
            'quantum_phase': 0.0,
            'stability': 0.5  # Estado instável durante transição
        })
        self.quantum_state_updated.emit(self._current_state)
        self.logger.debug(f"Estado colapsado: {state}")

    def _update_transition_matrix(self, stability: float) -> None:
        """Ajusta dinamicamente as probabilidades de transição"""
        self._transition_matrix = np.array([
            [stability, 1 - stability],
            [1 - stability, stability]
        ])
        self.logger.debug(f"Matriz de transição atualizada:\n{self._transition_matrix}")

    def _quantum_superposition(self, from_state: str, to_state: str) -> bool:
        """Executa a superposição quântica entre estados"""
        self._entangled = True
        self.logger.debug(f"Entrelaçamento quântico iniciado: {from_state} ↔ {to_state}")
        
        # Simula o processo de transição com pequenos passos
        steps = 10
        for step in range(1, steps + 1):
            if not self._entangled:  # Permite cancelamento
                return False
                
            phase = step / steps
            self._current_state.update({
                'quantum_phase': phase,
                'stability': 0.5 + (0.5 * phase)
            })
            self.quantum_state_updated.emit(self._current_state)
            
            QThread.msleep(50)  # Pequena pausa para efeito visual
            
        return True

    def _observe_state(self, state: str) -> None:
        """Finaliza a transição e estabiliza o novo estado"""
        self._entangled = False
        self._current_state.update({
            'culture': state,
            'quantum_phase': 1.0,
            'stability': 1.0
        })
        self.quantum_state_updated.emit(self._current_state)
        self.logger.info(f"Novo estado observado: {state}")

    def _emergency_rollback(self, original_state: str) -> None:
        """Retorna ao estado original em caso de falha"""
        self._entangled = False
        self._current_state.update({
            'culture': original_state,
            'quantum_phase': 0.0,
            'stability': 0.9  # Recuperação parcial
        })
        self.quantum_state_updated.emit(self._current_state)
        self.culture_changed.emit(original_state)
        self.logger.warning(f"Rollback para estado original: {original_state}")

    def get_current_state(self) -> dict:
        """Retorna o estado quântico atual"""
        return self._current_state.copy()

    def abort_transition(self) -> None:
        """Cancela uma transição em andamento"""
        if self._entangled:
            self.logger.warning("Transição quântica abortada")
            self._entangled = False