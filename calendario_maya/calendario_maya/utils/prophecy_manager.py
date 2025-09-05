import json
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
import logging
from PyQt6.QtCore import QThread, pyqtSignal
from calendario_maya.utils.astronomy_utils import AstronomyUtils

class ProphecyManager:
    def __init__(self, connector=None):
        self.connector = connector
        self.events = []
        self.filtered_events = []
        self.timeline_events = []
        self.prophecy_patterns = []
        self.load_thread = None
        self.worker = None
        self._load_data()
        
        # Carregamento inicial seguro
        try:
            if connector:
                self._verify_connector()
                self._load_data()
            else:
                self._load_fallback_data()
        except Exception as e:
            print(f"⚠️ Erro na inicialização: {e}")
            self._load_fallback_data()
            
    def load_events(self):
        """Carrega eventos de profecia"""
        try:
            # Implemente a carga real dos eventos aqui
            self.events = [
                {'id': 1, 'title': 'Evento 1', 'date': '2012-01-01'},
                {'id': 2, 'title': 'Evento 2', 'date': '2012-06-01'}
            ]
        except Exception as e:
            print(f"Erro ao carregar eventos: {str(e)}")
            self.events = []

    def load_events_async(self):
        """Versão melhorada com tratamento de erro"""
        try:
            from PyQt6.QtCore import QThread, pyqtSignal
        
            class LoaderThread(QThread):
                finished = pyqtSignal(bool)
                error = pyqtSignal(str)

                def run(self):
                    try:
                        self.parent().load_events()
                        self.finished.emit(True)
                    except Exception as e:
                        self.error.emit(str(e))
        
            if not hasattr(self, 'load_thread'):
                self.load_thread = LoaderThread(self)
                self.load_thread.finished.connect(self.on_events_loaded)
                self.load_thread.error.connect(self.on_load_error)
                self.load_thread.start()
        except Exception as e:
            print(f"Erro ao configurar thread: {str(e)}")
            # Fallback síncrono
            self.load_events()
            self.on_events_loaded(True)
    
    def _verify_connector(self):
        """Verifica se o connector tem os métodos necessários"""
        if not hasattr(self.connector, 'get_data_path'):
            raise ValueError("Connector não possui método get_data_path")
            
    def _load_data(self):
        """Carrega dados com tratamento robusto de erros"""
        try:
            # Dados de teste padrão
            self.events = [
                {
                    "id": "2020-001",
                    "year": "2020",
                    "title": "Convergência Harmônica (Teste)",
                    "description": "Alinhamento planetário significativo",
                    "date": "2020-06-21",
                    "significance": "high",
                    "dados_ciclicos": {
                        "baktun": 13.2,
                        "venus_phase": 145.3,
                        "galactic_year": 2.8
                    }
                },
                {
                    "id": "2012-001",
                    "year": "2012",
                    "title": "Fim do 13º Baktun",
                    "description": "Transição para novo ciclo maia",
                    "date": "2012-12-21",
                    "significance": "critical",
                    "dados_ciclicos": {
                        "baktun": 13.0,
                        "venus_phase": 180.0,
                        "galactic_year": 0.0
                    }
                }
            ]
        
            # Tenta carregar do arquivo se existir
            if self.connector and hasattr(self.connector, 'get_data_path'):
                data_path = Path(self.connector.get_data_path()) / 'prophecy_events.json'
                if data_path.exists():
                    with open(data_path, 'r', encoding='utf-8') as f:
                        file_events = json.load(f)
                        if isinstance(file_events, list):
                            self.events.extend(file_events)
        except Exception as e:
            self.logger.error(f"Erro ao carregar profecias: {e}")
            self.events = self._get_fallback_prophecies()
    
    def on_events_loaded(self, events):
        self.timeline_events = [e for e in events if e.get('type') != 'prophecy']
        self.prophecy_patterns = [e for e in events if e.get('type') == 'prophecy']
        self.load_thread.quit()
        self.load_thread.wait()
        print("✅ Eventos carregados assincronamente")
    
    def on_load_error(self, error_msg):
        print(f"⚠️ Erro ao carregar eventos: {error_msg}")
        self.load_thread.quit()
        self.load_thread.wait()
        
    def _load_fallback_data(self):
        """Carrega dados mínimos de fallback"""
        self.events = [{
            'title': 'Fallback Event',
            'year': '2023',
            'description': 'Dados não carregados',
            'type': 'fallback'
        }]

    def _load_legacy_events(self):
        """Carrega dados no formato antigo"""
        try:
            all_events = self._load_all_events()
            self.timeline_events = [e for e in all_events if not e.get('is_prophecy', False)]
            self.prophecy_patterns = [e for e in all_events if e.get('is_prophecy', False)]
        except Exception as e:
            print(f"Erro ao carregar dados legados: {e}")
            self.timeline_events = self._get_fallback_timeline_data()
            self.prophecy_patterns = []

    def _load_json_data(self, filename):
        """Carrega dados de arquivo JSON com verificação usando Path"""
        try:
            if self.connector and hasattr(self.connector, 'get_data_path'):
                # Converter para Path e juntar caminhos corretamente
                path = Path(self.connector.get_data_path()) / filename
                if not path.exists():
                    print(f"Arquivo não encontrado: {path}")
                    return []
                
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('events', [])
        except Exception as e:
            print(f"Erro ao carregar {filename}: {e}")
            return []
        
    def _load_all_events(self):
        """Método legado para carregar todos os eventos com Path"""
        events = []
        files = ["historical_events.json", "timeline_events.json", "backup_events.json"]
    
        # Obter o caminho base como Path
        base_path = Path(self.connector.get_data_path())
    
        for file in files:
            try:
                file_path = base_path / file  # Juntando caminhos corretamente
                if not file_path.exists():
                    continue
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'events' in data:
                        events.extend(data['events'])
                    elif isinstance(data, list):
                        events.extend(data)
            except Exception as e:
                print(f"Erro ao carregar {file}: {e}")
            
        return sorted(self._process_events(events), key=lambda x: int(x.get('year', 0)))
    
    def _process_events(self, events):
        """Processa eventos convertendo anos para datas aproximadas"""
        processed = []
        for event in events:
            if 'year' in event:
                try:
                    year = int(event['year'])
                    event['approx_date'] = ApproximateDate(year).to_date()
                    event['cosmic_data'] = self._calculate_cosmic_data(year)
                except ValueError:
                    event['approx_date'] = None
                    event['cosmic_data'] = {}
            processed.append(event)
        return processed
    
    def _calculate_cosmic_data(self, year):
        """Versão robusta para cálculo de dados cósmicos por ano"""
        try:
            year_int = int(year)
            if not (-10000 < year_int < 10000):  # Range seguro
                return {}
            
            # Cálculos baseados apenas no ano
            years_since_2012 = year_int - 2012
            galactic_progress = (years_since_2012 / 5200) * 100  # Ciclo de 5200 anos
        
            return {
                'baktun': (year_int + 3114) / 394.26,
                'katun': (year_int + 3114) % 394.26 / 19.7,
                'venus_cycle': (years_since_2012 * 365) % 584 / 584 * 360,
                'galactic_progress': galactic_progress,
                'energy_level': min(100, max(10, 100 - (2023 - year_int)/50))
            }
        except:
            return {}
    
    def _calculate_energy(self, year):
        """Calcula energia cósmica baseada na idade do evento"""
        try:
            age = datetime.now().year - int(year)
            return min(100, max(10, 100 - (age / 50)))
        except:
            return 50
    
    def _get_fallback_timeline_data(self):
        """Dados mínimos de fallback"""
        return [
            {
                'year': 2024,
                'title': 'Fim do 13º Baktun',
                'description': 'Transição para novo ciclo maia',
                'cosmic_data': {
                    'baktun': 13.0,
                    'energy': 100
                }
            }
        ]
    
    def get_event_detail(self, event_id, is_prophecy=False):
        """Retorna detalhes formatados de um evento"""
        events = self.prophecy_patterns if is_prophecy else self.timeline_events
        if 0 <= event_id < len(events):
            event = events[event_id]
            cosmic = event.get('cosmic_data', {})
            
            return {
                'title': event.get('title', 'Evento Desconhecido'),
                'year': event.get('year', 'N/A'),
                'description': event.get('description', 'Descrição não disponível'),
                'civilization': event.get('civilization', 'Várias civilizações'),
                'cosmic_cycle': f"Baktun {cosmic.get('baktun', 0):.1f}, Katun {cosmic.get('katun', 0):.1f}",
                'venus_position': f"{cosmic.get('venus_cycle', 0):.1f}°",
                'energy_level': f"{cosmic.get('energy', 0):.1f}%",
                'frequency': self._calculate_frequency(event.get('year'))
            }
        return None
    
    def _calculate_frequency(self, year):
        """Estima frequência de eventos similares"""
        try:
            similar = [e for e in self.timeline_events 
                      if abs(int(e.get('year', 0)) - abs(int(year))) < 100]
            return f"A cada ~{5125//len(similar)} anos" if similar else "Evento único"
        except:
            return "Frequência desconhecida"
        
    def find_similar_alignments(self, reference_date, future_years=100):
        """
        Encontra alinhamentos similares ao de uma data de referência
        Args:
            reference_date (datetime): Data de referência (ex: 21/12/2012)
            future_years (int): Quantos anos no futuro procurar
        Returns:
            list: Datas de alinhamentos similares
        """
        try:
            if not hasattr(self.connector, 'astronomy_utils'):
                raise AttributeError("Connector não possui módulo astronômico")
                
            astronomy = self.connector.astronomy_utils
            ref_venus_pos = astronomy.get_planet_position(reference_date, 'venus')
            ref_earth_pos = astronomy.get_planet_position(reference_date, 'earth')
            ref_angle = astronomy.get_galactic_angle(reference_date)
            
            results = []
            for year in range(reference_date.year + 1, reference_date.year + future_years + 1):
                test_date = datetime(year, reference_date.month, reference_date.day)
                venus_pos = astronomy.get_planet_position(test_date, 'venus')
                earth_pos = astronomy.get_planet_position(test_date, 'earth')
                angle = astronomy.get_galactic_angle(test_date)
                
                # Verifica similaridade com tolerância de 5 graus
                if (abs(venus_pos - ref_venus_pos) < 5 and 
                    abs(earth_pos - ref_earth_pos) < 5 and
                    abs(angle - ref_angle) < 5):
                    results.append(test_date)
            
            return results
            
        except Exception as e:
            print(f"Erro ao buscar alinhamentos similares: {e}")
            return []
        
    def _load_prophecy_data(self):
        """Carrega e padroniza dados de profecia de diferentes formatos"""
        try:
            # Tenta carregar os dados do arquivo
            data = self._load_json_file()
        
            if not data:
                return self._get_fallback_prophecies()

            # Verifica qual formato está sendo usado
            if isinstance(data, list):
                # Formato simples já é uma lista de eventos
                return self._process_simple_format(data)
            elif isinstance(data, dict) and 'profecias' in data:
                # Formato completo com metadados
                return self._process_complete_format(data['profecias'])
            else:
                return self._get_fallback_prophecies()
            
        except Exception as e:
            print(f"Erro ao processar profecias: {e}")
            return self._get_fallback_prophecies()

    def _load_json_file(self):
        """Carrega o arquivo JSON com tratamento de erros"""
        try:
            data_path = self._get_data_path()
            if not data_path.exists():
                return None
            
            with open(data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao ler arquivo: {e}")
            return None

    def _get_data_path(self):
        """Retorna o Path para o arquivo de profecias"""
        if self.connector and hasattr(self.connector, 'get_data_path'):
            return Path(self.connector.get_data_path()) / 'prophecy_events.json'
        return Path('data/prophecy_events.json')

    def _process_simple_format(self, events):
        """Processa o formato simples de lista de eventos"""
        processed = []
        for event in events:
            processed.append({
                'id': event.get('id'),
                'year': event.get('year'),
                'title': event.get('title'),
                'description': event.get('description'),
                'date': event.get('date'),
                'significance': event.get('significance', 'medium'),
                'raw_data': event  # Mantém os dados originais
            })
        return processed

    def _process_complete_format(self, prophecies):
        """Processa o formato completo com metadados"""
        processed = []
        for prophecy in prophecies:
            # Extrai a data do evento (prioriza data_possivel_evento)
            event_date = prophecy.get('data_possivel_evento')
            if not event_date:
                event_date = prophecy.get('ligacao_com_calendarios', {}).get('gregoriano')
            
            # Extrai o ano da data
            year = event_date.split('-')[0] if event_date else '0000'
        
            processed.append({
                'id': prophecy.get('id'),
                'year': year,
                'title': prophecy.get('quadra_original', 'Profecia sem título'),
                'description': self._build_description(prophecy),
                'date': event_date,
                'significance': prophecy.get('status', 'unknown'),
                'astronomical_data': prophecy.get('evento_astronomico'),
                'frequency_data': prophecy.get('frequencia_vibracional'),
                'raw_data': prophecy  # Mantém todos os dados originais
            })
        return processed

    def _build_description(self, prophecy):
        """Constrói uma descrição unificada a partir dos dados da profecia"""
        parts = []
    
        if prophecy.get('quadra_original'):
            parts.append(f"Profecia: {prophecy['quadra_original']}")
        
        if prophecy.get('interpretacao', {}).get('metafora'):
            parts.append(f"Interpretação: {prophecy['interpretacao']['metafora']}")
        
        if prophecy.get('evento_astronomico', {}).get('tipo'):
            parts.append(f"Evento astronômico: {prophecy['evento_astronomico']['tipo']}")
        
        return "\n".join(parts) if parts else "Descrição não disponível"
        
    def find_next_cyclic_event(self, reference_event, years_ahead=100):
        """
        Encontra o próximo evento com padrão cíclico similar
        Args:
            reference_event: Dados do evento de referência
            years_ahead: Quantos anos no futuro procurar
        Returns:
            dict: Dados do próximo evento similar e informações dos ciclos
        """
        try:
            if not hasattr(self, 'astronomy_utils'):
                raise AttributeError("Astronomy utils não disponível")
                
            ref_date = self._parse_date(reference_event.get('date'))
            if not ref_date:
                return None
                
            # Obtém os ciclos da data de referência
            ref_cycles = {
                'baktun': self.astronomy_utils.calculate_baktun(ref_date),
                'venus_phase': self.astronomy_utils.venus_phase_angle(ref_date),
                'galactic_year': self.astronomy_utils.galactic_year_progress(ref_date)
            }
            
            # Procura eventos futuros com padrão similar
            current_date = datetime.now().date()
            end_date = current_date + timedelta(days=365*years_ahead)
            delta = timedelta(days=1)
            
            best_match = None
            best_score = 0
            
            while current_date <= end_date:
                try:
                    # Calcula os ciclos para a data atual
                    current_cycles = {
                        'baktun': self.astronomy_utils.calculate_baktun(current_date),
                        'venus_phase': self.astronomy_utils.venus_phase_angle(current_date),
                        'galactic_year': self.astronomy_utils.galactic_year_progress(current_date)
                    }
                    
                    # Calcula o score de similaridade
                    score = self._calculate_similarity_score(ref_cycles, current_cycles)
                    
                    # Atualiza o melhor match se necessário
                    if score > best_score:
                        best_score = score
                        best_match = {
                            'date': current_date,
                            'cycles': current_cycles,
                            'similarity_score': score
                        }
                        
                except Exception as e:
                    print(f"Erro ao processar data {current_date}: {e}")
                
                current_date += delta
                
            return best_match
            
        except Exception as e:
            print(f"Erro na análise profética: {e}")
            return None
    
    def _calculate_similarity_score(self, ref_cycles, current_cycles):
        """Calcula o score de similaridade entre ciclos"""
        # Pesos para cada ciclo (ajustáveis)
        weights = {
            'baktun': 0.4,
            'venus_phase': 0.4,
            'galactic_year': 0.2
        }
        
        # Calcula diferenças normalizadas
        baktun_diff = 1 - abs(ref_cycles['baktun'] - current_cycles['baktun']) / 20
        venus_diff = 1 - abs(ref_cycles['venus_phase'] - current_cycles['venus_phase']) / 360
        galactic_diff = 1 - abs(ref_cycles['galactic_year'] - current_cycles['galactic_year']) / 100
        
        # Score ponderado
        score = (weights['baktun'] * baktun_diff +
                weights['venus_phase'] * venus_diff +
                weights['galactic_year'] * galactic_diff)
                
        return score
    
    def generate_cyclic_prophecies(self, start_date, years=10):
        """Gera profecias baseadas em alinhamentos planetários"""
        prophecies = []
        current_date = start_date
    
        for _ in range(years):
            # Encontra próximo alinhamento significativo
            next_alignment = self.find_next_alignment(current_date)
        
            if next_alignment:
                prophecy = {
                    'date': next_alignment.isoformat(),
                    'title': f"Alinhamento {next_alignment.year}",
                    'description': self.get_alignment_description(next_alignment),
                    'category': 'Astronômico'
                }
                prophecies.append(prophecy)
                current_date = next_alignment + timedelta(days=180)  # Próxima busca em ~6 meses
        
        return prophecies

    def find_next_alignment(self, from_date):
        """Encontra próximo alinhamento Vênus-Terra significativo"""
        venus_cycle = 584  # Dias no ciclo sinódico de Vênus
        for days in range(0, 365*5, 5):  # Verifica a cada 5 dias por 5 anos
            check_date = from_date + timedelta(days=days)
            if self.is_significant_alignment(check_date):
                return check_date
        return None
    
class ApproximateDate:
    def __init__(self, year, month=None, day=None):
        self.year = year
        self.month = month or 6  # Mês padrão (meio do ano)
        self.day = day or 15     # Dia padrão (meio do mês)
        
    def to_date(self):
        """Retorna uma data aproximada para cálculos"""
        try:
            return date(self.year, self.month, self.day)
        except:
            return date(self.year, 6, 15)  # Fallback para data do meio do ano