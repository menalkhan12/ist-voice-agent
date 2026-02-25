#!/usr/bin/env python3
"""
Diagnostic script to identify STT/TTS issues in the voice agent
"""
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("diagnose")

def check_environment():
    """Check required environment variables"""
    print("=== ENVIRONMENT CHECK ===")
    
    # Load environment
    root_dir = Path(__file__).resolve().parent
    env_file = root_dir / ".env.local"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✓ Loaded .env.local from {env_file}")
    else:
        print(f"✗ .env.local not found at {env_file}")
    
    # Check required API keys
    required_keys = {
        'GROQ_API_KEY': 'For CLI voice agent STT/LLM',
        'OPENAI_API_KEY': 'For LiveKit agent (if using OpenAI models)',
        'LIVEKIT_URL': 'For LiveKit connection',
        'LIVEKIT_API_KEY': 'For LiveKit connection', 
        'LIVEKIT_API_SECRET': 'For LiveKit connection'
    }
    
    missing_keys = []
    for key, desc in required_keys.items():
        value = os.getenv(key)
        if value:
            masked = value[:8] + "..." if len(value) > 8 else "***"
            print(f"✓ {key}: {masked} ({desc})")
        else:
            print(f"✗ {key}: MISSING ({desc})")
            missing_keys.append(key)
    
    return len(missing_keys) == 0

def check_dependencies():
    """Check if required packages are installed"""
    print("\n=== DEPENDENCY CHECK ===")
    
    required_packages = [
        ('livekit_agents', 'livekit_agents'),
        ('groq', 'groq'), 
        ('pyttsx3', 'pyttsx3'),
        ('sounddevice', 'sounddevice'),
        ('soundfile', 'soundfile'),
        ('numpy', 'numpy')
    ]
    
    missing_packages = []
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"✓ {package_name}")
        except ImportError:
            print(f"✗ {package_name}: NOT INSTALLED")
            missing_packages.append(package_name)
    
    return len(missing_packages) == 0

def check_audio_system():
    """Check audio recording/playback capabilities"""
    print("\n=== AUDIO SYSTEM CHECK ===")
    
    try:
        import sounddevice as sd
        import soundfile as sf
        
        # Check available devices
        devices = sd.query_devices()
        print(f"✓ Found {len(devices)} audio devices")
        
        # Show default input/output
        default_input = sd.default.device[0]
        default_output = sd.default.device[1]
        
        if default_input >= 0:
            print(f"✓ Default input device: {devices[default_input]['name']}")
        else:
            print("✗ No default input device found")
            
        if default_output >= 0:
            print(f"✓ Default output device: {devices[default_output]['name']}")
        else:
            print("✗ No default output device found")
            
        return True
        
    except Exception as e:
        print(f"✗ Audio system error: {e}")
        return False

def check_tts_voices():
    """Check available TTS voices"""
    print("\n=== TTS VOICES CHECK ===")
    
    try:
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        print(f"✓ Found {len(voices)} TTS voices:")
        for i, voice in enumerate(voices):
            lang = getattr(voice, 'languages', [getattr(voice, 'lang', 'unknown')])[0] if hasattr(voice, 'languages') or hasattr(voice, 'lang') else 'unknown'
            print(f"  {i+1}. {voice.name} ({lang})")
        
        # Check current voice
        current_voice = engine.getProperty('voice')
        if current_voice:
            voice_name = next((v.name for v in voices if v.id == current_voice), "Unknown")
            print(f"✓ Current voice: {voice_name}")
        
        engine.stop()
        return True
        
    except Exception as e:
        print(f"✗ TTS system error: {e}")
        return False

def test_groq_connection():
    """Test Groq API connection"""
    print("\n=== GROQ API TEST ===")
    
    try:
        from groq import Groq
        api_key = os.getenv('GROQ_API_KEY')
        
        if not api_key:
            print("✗ GROQ_API_KEY not set")
            return False
            
        client = Groq(api_key=api_key)
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "Say 'test'"}],
            max_tokens=10
        )
        
        print("✓ Groq API connection successful")
        print(f"✓ Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"✗ Groq API error: {e}")
        return False

def main():
    print("STT/TTS Diagnostic Tool")
    print("=" * 50)
    
    # Run all checks
    env_ok = check_environment()
    deps_ok = check_dependencies()
    audio_ok = check_audio_system()
    tts_ok = check_tts_voices()
    groq_ok = test_groq_connection()
    
    # Summary
    print("\n" + "=" * 50)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    all_checks = [
        ("Environment", env_ok),
        ("Dependencies", deps_ok), 
        ("Audio System", audio_ok),
        ("TTS Voices", tts_ok),
        ("Groq API", groq_ok)
    ]
    
    all_good = True
    for check_name, status in all_checks:
        status_symbol = "✓" if status else "✗"
        print(f"{status_symbol} {check_name}")
        if not status:
            all_good = False
    
    if all_good:
        print("\n🎉 All checks passed! Your STT/TTS should work correctly.")
    else:
        print("\n⚠️  Some checks failed. See issues above for fixes.")
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())
