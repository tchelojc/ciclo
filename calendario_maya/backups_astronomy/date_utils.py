# utils/date_utils.py
from datetime import date as datetime_date
from astropy.time import Time
import math

MAYA_EPOCH = 584283  # JDN para 11 de agosto de -3113 (3114 AEC, gregoriano)
GALACTIC_EPOCH = datetime_date(2012, 12, 21)

__all__ = [
    "gregorian_to_jdn", "jdn_to_gregorian", "julian_day_to_gregorian",
    "gregorian_to_julian_day", "days_since_maya_epoch", "safe_date_convert",
    "MAYA_EPOCH", "GALACTIC_EPOCH"
]

def empty_mayan_data():
    """Retorna estrutura vazia para datas inválidas"""
    return {
        'baktun': 0,
        'galactic': 0,
        'venus': 0
    }

def mayan_date_system(py_date):
    """Calcula todos os componentes da data maia"""
    try:
        jd = safe_date_convert(date_obj=py_date)
        if jd < MAYA_EPOCH_JD:
            return empty_mayan_data()
            
        return {
            'baktun': calculate_baktun(py_date),
            'galactic': galactic_progress(py_date),
            'venus': venus_phase(py_date)
        }
    except:
        return empty_mayan_data()
    
def safe_date_convert(date_obj=None, year=None, month=None, day=None):
    """Conversão segura para data juliana"""
    try:
        if date_obj:
            if hasattr(date_obj, 'toPyDate'):
                date_obj = date_obj.toPyDate()
            return Time(f"{date_obj.year}-{date_obj.month}-{date_obj.day}").jd
        
        if year is not None and month is not None and day is not None:
            if year <= 0:  # Ano BCE
                astro_year = 1 - year
                return Time(f"{astro_year}-{month}-{day}", format='iso').jd
            return Time(f"{year}-{month}-{day}").jd
            
        return Time.now().jd
    except:
        # Fallback simples
        return 2451545.0 + (date_obj.toordinal() if date_obj else 0)

def galactic_progress(py_date):
    """Progresso no ciclo galáctico"""
    days_since = (py_date - GALACTIC_EPOCH).days
    return (days_since / 26000) * 100 if days_since >= 0 else 0

def venus_phase(py_date):
    """Fase de Vênus"""
    days_since = (py_date - GALACTIC_EPOCH).days
    return (days_since % 584) / 584 * 360

def handle_ancient_date(year, month, day):
    """Lida com datas antes de Cristo (BCE)"""
    try:
        if year <= 0:
            # Usa o ano astronômico (1 BCE = 0, 2 BCE = -1, etc.)
            astro_year = 1 - year
            return Time(f"{astro_year}-{month}-{day}", format='iso').jd
        return Time(f"{year}-{month}-{day}", format='iso').jd
    except:
        # Fallback para datas problemáticas
        return 1721423.5 + (abs(year) * 365.2425) + ((month - 1) * 30.44) + day

MAYA_EPOCH_JD = handle_ancient_date(-3113, 8, 11)  # 3114 BCE
GALACTIC_EPOCH = datetime_date(2012, 12, 21)