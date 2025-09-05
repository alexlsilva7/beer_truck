import os
import json
from typing import Any, Dict, Optional

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PATH = os.path.join(SCRIPT_DIR, "settings.json")

DEFAULT_SETTINGS: Dict[str, Any] = {
  "version": 1,
  "audio": {
    "master": 1.0,
    "music": 0.5,
    "sfx": 0.8
  },
  "toggles": {
    "beer": True,
    "invulnerability": True,
    "holes": True,
    "oil": False,
    "police": True
  },
  "joystick": {
    "selected_guid": None
  }
}

_settings: Dict[str, Any] = {}

def load_settings(path: Optional[str] = None) -> Dict[str, Any]:
    """Carrega settings de JSON; se ausente ou corrompido, usa defaults e regrava."""
    global _settings
    p = path or SETTINGS_PATH
    if not os.path.isfile(p):
        _settings = DEFAULT_SETTINGS.copy()
        save_settings(p)
        return _settings
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        _settings = _merge_with_defaults(data)
        return _settings
    except Exception:
        # Arquivo corrompido: restaura defaults e sobreescreve
        _settings = DEFAULT_SETTINGS.copy()
        save_settings(p)
        return _settings

def save_settings(path: Optional[str] = None) -> bool:
    """Salva settings atuais em JSON; retorna True se bem sucedido."""
    p = path or SETTINGS_PATH
    try:
        with open(p, "w", encoding="utf-8") as f:
            json.dump(_settings, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False

def _merge_with_defaults(data: Dict[str, Any]) -> Dict[str, Any]:
    """Merge simples recursivo de data sobre DEFAULTS, garantindo tipos esperados."""
    def merge(d, default):
        if not isinstance(d, dict):
            return default
        out = {}
        for k, v in default.items():
            if k in d:
                if isinstance(v, dict):
                    out[k] = merge(d.get(k, {}), v)
                else:
                    out[k] = d.get(k, v)
            else:
                out[k] = v
        # Preserve extra keys from d
        for k, v in d.items():
            if k not in out:
                out[k] = v
        return out
    return merge(data, DEFAULT_SETTINGS)

def get_settings() -> Dict[str, Any]:
    global _settings
    if not _settings:
        load_settings()
    return _settings

def get(path: str, default: Any = None) -> Any:
    """Pega valor por caminho usando pontos, ex: 'audio.sfx.horn'"""
    parts = path.split(".")
    cur = get_settings()
    for p in parts:
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return default
    return cur

def set(path: str, value: Any) -> None:
    """Define valor por caminho e salva automaticamente."""
    parts = path.split(".")
    cur = get_settings()
    for p in parts[:-1]:
        if p not in cur or not isinstance(cur[p], dict):
            cur[p] = {}
        cur = cur[p]
    cur[parts[-1]] = value
    save_settings()

def reset_defaults() -> None:
    global _settings
    _settings = DEFAULT_SETTINGS.copy()
    save_settings()

def get_master_volume() -> float:
    return float(get("audio.master", 1.0))

def get_music_volume() -> float:
    return float(get("audio.music", 0.8))

def get_sfx_volume(key: str) -> float:
    """Pega volume de SFX (unificado). O parâmetro key é ignorado, mantido para compatibilidade."""
    return float(get("audio.sfx", 0.8))

def get_effective_music_volume() -> float:
    return max(0.0, min(1.0, get_master_volume() * get_music_volume()))

def get_effective_sfx_volume(key: str) -> float:
    return max(0.0, min(1.0, get_master_volume() * get_sfx_volume(key)))

def get_toggle(name: str) -> bool:
    return bool(get(f"toggles.{name}", True))


def set_selected_joystick_guid(guid: Optional[str]) -> None:
    """Persiste seleção por GUID apenas."""
    set("joystick.selected_guid", guid)

def get_selected_joystick() -> Dict[str, Optional[Any]]:
    """Retorna um dict com field selected_guid."""
    return {
        "selected_guid": get("joystick.selected_guid", None)
    }

def apply_to_audio_manager(audio_manager_module) -> None:
    """Aplica volumes básicos ao audio_manager (se presente)."""
    try:
        # Ajusta volume da musica de fundo se estiver tocando
        bg_vol = get_effective_music_volume()
        if hasattr(audio_manager_module, "is_background_music_playing") and audio_manager_module.is_background_music_playing():
            try:
                # tenta setar sem reiniciar
                try:
                    import pygame
                    if pygame.mixer.get_init():
                        pygame.mixer.music.set_volume(bg_vol)
                except Exception:
                    pass
            except Exception:
                pass
    except Exception:
        pass

# Inicializa na importacao
load_settings()