"""Multimedia hooks — TTS and audio generation for StudyPack."""
from __future__ import annotations

import os
import logging
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)


def generate_tts_for_instructions(
    tasks: List[Dict],
    output_dir: str,
    language: str = "en",
    slow: bool = True
) -> List[Optional[str]]:
    """
    Generate audio files for task instructions.
    Returns list of audio file paths (None if generation failed).
    
    Requires: pip install gTTS
    Falls back to None if gTTS not available.
    """
    try:
        from gtts import gTTS
    except ImportError:
        logger.warning("gTTS not installed. Install with: pip install gTTS")
        return [None for _ in tasks]

    lang_code = "uk" if language in ("uk", "uk+en") else "ru" if language == "ru" else "en"
    
    os.makedirs(output_dir, exist_ok=True)
    audio_paths = []
    
    for i, task in enumerate(tasks):
        instruction = task.get("instruction") or task.get("question", "")
        if not instruction:
            audio_paths.append(None)
            continue
        
        audio_file = os.path.join(output_dir, f"task_{i+1}.mp3")
        try:
            tts = gTTS(text=instruction, lang=lang_code, slow=slow)
            tts.save(audio_file)
            audio_paths.append(audio_file)
            logger.info(f"Generated TTS: {audio_file}")
        except Exception as e:
            logger.error(f"TTS generation failed for task {i+1}: {e}")
            audio_paths.append(None)
    
    return audio_paths


def generate_page_audio(
    page_data: Dict,
    output_dir: str,
    page_index: int,
    language: str = "en"
) -> Optional[str]:
    """
    Generate a single audio file for entire page instructions.
    Returns path to audio file or None.
    """
    try:
        from gtts import gTTS
    except ImportError:
        logger.warning("gTTS not installed")
        return None

    lang_code = "uk" if language in ("uk", "uk+en") else "ru" if language == "ru" else "en"
    instruction = page_data.get("instruction", "")
    
    if not instruction:
        return None
    
    os.makedirs(output_dir, exist_ok=True)
    audio_file = os.path.join(output_dir, f"page_{page_index+1}.mp3")
    
    try:
        tts = gTTS(text=instruction, lang=lang_code, slow=True)
        tts.save(audio_file)
        return audio_file
    except Exception as e:
        logger.error(f"Page audio generation failed: {e}")
        return None


def create_qr_codes_for_audio(
    audio_paths: List[Optional[str]],
    output_dir: str,
    base_url: str = ""
) -> List[Optional[str]]:
    """
    Generate QR codes linking to audio files.
    Returns list of QR code image paths.
    
    Requires: pip install qrcode
    Falls back to None if qrcode not available.
    """
    try:
        import qrcode
    except ImportError:
        logger.warning("qrcode not installed. Install with: pip install qrcode")
        return [None for _ in audio_paths]

    os.makedirs(output_dir, exist_ok=True)
    qr_paths = []
    
    for i, audio_path in enumerate(audio_paths):
        if not audio_path:
            qr_paths.append(None)
            continue
        
        url = f"{base_url}/{os.path.basename(audio_path)}" if base_url else audio_path
        qr_file = os.path.join(output_dir, f"qr_task_{i+1}.png")
        
        try:
            img = qrcode.make(url)
            img.save(qr_file)
            qr_paths.append(qr_file)
        except Exception as e:
            logger.error(f"QR generation failed for task {i+1}: {e}")
            qr_paths.append(None)
    
    return qr_paths


def pack_has_multimedia_support() -> bool:
    """Check if optional multimedia dependencies are installed."""
    has_gtts = False
    has_qrcode = False
    
    try:
        import gtts
        has_gtts = True
    except ImportError:
        pass
    
    try:
        import qrcode
        has_qrcode = True
    except ImportError:
        pass
    
    return has_gtts or has_qrcode
