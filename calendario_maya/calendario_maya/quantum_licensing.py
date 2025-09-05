import os
import json
import hmac
import hashlib
import uuid
import platform
import subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta
import requests
import streamlit as st

class QuantumLicenseManager:
    """Sistema unificado de gerenciamento de licenças"""
    
    SERVER_URL = "http://localhost:5000"
    SECRET_KEY = "sua-chave-secreta-muito-longa-e-complexa-aqui"  # DEVE SER IGUAL NO SERVIDOR
    
    def __init__(self, app_name: str):
        self.app_name = app_name
        self.device_id = self._get_device_id()
        self.license_path = self._get_license_path()

    def _get_device_id(self):
        try:
            if platform.system() == "Windows":
                cmd = "wmic csproduct get uuid"
                result = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL)
                return result.decode().split('\n')[1].strip()
            return str(uuid.getnode())
        except Exception:
            return str(uuid.getnode())

    def _get_license_path(self):
        app_safe = ''.join(c if c.isalnum() else '_' for c in self.app_name)
        if platform.system() == "Windows":
            path = Path(os.getenv('LOCALAPPDATA')) / app_safe
        else:
            path = Path.home() / ".config" / app_safe.lower()
        path.mkdir(parents=True, exist_ok=True)
        return path / "quantum.license"

    def _generate_security_hash(self, license_key: str):
        """Gera hash de segurança - deve ser IDÊNTICO ao do servidor"""
        message = f"{license_key}{self.device_id}".encode()
        return hmac.new(
            self.SECRET_KEY.encode(),
            message,
            hashlib.sha256
        ).hexdigest()

    def activate_license(self, license_key: str):
        """Tenta ativar a licença no servidor"""
        payload = {
            'license_key': license_key,
            'device_id': self.device_id,
            'app_name': self.app_name,
            'hash': self._generate_security_hash(license_key)
        }
    
        try:
            response = requests.post(
                f"{self.SERVER_URL}/api/quantum/activate",
                json=payload,
                timeout=5
            )

            # 💥 ADICIONADO - DEBUG DA RESPOSTA DO SERVIDOR
            print(f"Status da resposta: {response.status_code}")
            print(f"Resposta bruta do servidor: {response.text}")

            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    self._save_license(result['license'])
                    return {'success': True, 'message': 'Licença ativada com sucesso!'}
                return result
        
            return {
                'success': False,
                'message': response.json().get('message', f'Erro {response.status_code}')
            }
        except requests.exceptions.RequestException as e:
            return {'success': False, 'message': f'Erro de conexão: {str(e)}'}

    def verify_license(self):
        """Verificação completa da licença"""
        license_data = self._load_license()
        if not license_data:
            return {'valid': False, 'message': 'Nenhuma licença encontrada'}
        
        # Verificação offline primeiro
        offline_result = self._verify_offline(license_data)
        if not offline_result['valid']:
            return offline_result
        
        # Tenta verificação online
        try:
            payload = {
                'license_key': license_data['key'],
                'device_id': self.device_id,
                'app_name': self.app_name,
                'hash': self._generate_security_hash(license_data['key'])
            }
            
            response = requests.post(
                f"{self.SERVER_URL}/api/quantum/validate",
                json=payload,
                timeout=3
            )
            
            if response.status_code == 200:
                return response.json()
            
        except requests.exceptions.RequestException:
            pass  # Fallback para verificação offline
        
        return offline_result

    def _verify_offline(self, license_data: dict):
        """Verificação local da licença"""
        # Verifica dispositivo
        if license_data.get('device_id') != self.device_id:
            return {'valid': False, 'message': 'Dispositivo não autorizado'}
        
        # Verifica hash
        expected_hash = self._generate_security_hash(license_data['key'])
        if not hmac.compare_digest(license_data.get('hash', ''), expected_hash):
            return {'valid': False, 'message': 'Assinatura inválida'}
        
        # Verifica expiração (com tratamento de fuso horário)
        try:
            expiration = datetime.fromisoformat(license_data['expiration_date'])
            now = datetime.now(timezone.utc)
            
            if expiration.tzinfo is None:
                expiration = expiration.replace(tzinfo=timezone.utc)
                
            if expiration < now:
                return {'valid': False, 'message': f'Licença expirada em {expiration.strftime("%d/%m/%Y")}'}
                
        except (ValueError, KeyError):
            return {'valid': False, 'message': 'Data de expiração inválida'}
        
        return {'valid': True, 'message': 'Licença válida (offline)'}

    def _save_license(self, license_data: dict):
        """Salva os dados da licença localmente"""
        try:
            with open(self.license_path, 'w', encoding='utf-8') as f:
                json.dump(license_data, f, indent=2)
            return True
        except (IOError, TypeError):
            return False

    def _load_license(self):
        """Carrega os dados da licença local"""
        try:
            if self.license_path.exists():
                with open(self.license_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (IOError, json.JSONDecodeError):
            pass
        return None

class StreamlitLicenseUI:
    """Interface de licença para Streamlit"""
    def __init__(self):
        self.manager = QuantumLicenseManager("OperadorConquistadorPro")
        
    def show_activation_screen(self):
        """Mostra a tela de ativação"""
        st.set_page_config(layout="centered")
        st.title("🔒 Ativação Necessária")
        st.error("Este software requer uma licença válida para operar.")
        
        with st.expander("Informações Técnicas"):
            st.code(f"App: OperadorConquistadorPro\nDevice ID: {self.manager.device_id}")
        
        with st.form("activation_form"):
            license_key = st.text_input("Chave de Licença", placeholder="PRO-XXXXXX")
            submitted = st.form_submit_button("Ativar Licença")
            
            if submitted:
                if not license_key:
                    st.warning("Por favor, insira uma chave de licença")
                else:
                    with st.spinner("Ativando licença..."):
                        result = self.manager.activate_license(license_key)
                    
                    if result.get('success'):
                        st.success("✅ Licença ativada com sucesso!")
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(f"❌ Falha na ativação: {result.get('message')}")