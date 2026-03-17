from pathlib import Path

# Agent
ANTHROPIC_MODEL = "claude-sonnet-4-20250514"

# Images
MAX_IMAGE_HEIGHT = 200

# Settings
SETTINGS_FILE = Path.home() / ".ankiagent" / "settings.json"

# Languages
AVAILABLE_LANGUAGES: tuple[dict, ...] = (
    {
        "name": "Arabic",
        "iso_code": "ar",
        "native_name": "العربية",
        "audio_providers": ("google",),
    },
    {
        "name": "Chinese",
        "iso_code": "zh",
        "native_name": "中文",
        "audio_providers": ("google",),
    },
    {
        "name": "Dutch",
        "iso_code": "nl",
        "native_name": "Nederlands",
        "audio_providers": ("google",),
    },
    {
        "name": "English",
        "iso_code": "en",
        "native_name": "English",
        "audio_providers": ("google",),
    },
    {
        "name": "French",
        "iso_code": "fr",
        "native_name": "Français",
        "audio_providers": ("google",),
    },
    {
        "name": "German",
        "iso_code": "de",
        "native_name": "Deutsch",
        "audio_providers": ("google",),
    },
    {
        "name": "Irish",
        "iso_code": "ga",
        "native_name": "Gaeilge",
        "audio_providers": ("focloir",),
    },
    {
        "name": "Italian",
        "iso_code": "it",
        "native_name": "Italiano",
        "audio_providers": ("google",),
    },
    {
        "name": "Japanese",
        "iso_code": "ja",
        "native_name": "日本語",
        "audio_providers": ("google",),
    },
    {
        "name": "Korean",
        "iso_code": "ko",
        "native_name": "한국어",
        "audio_providers": ("google",),
    },
    {
        "name": "Polish",
        "iso_code": "pl",
        "native_name": "Polski",
        "audio_providers": ("google",),
    },
    {
        "name": "Portuguese",
        "iso_code": "pt",
        "native_name": "Português",
        "audio_providers": ("google",),
    },
    {
        "name": "Russian",
        "iso_code": "ru",
        "native_name": "Русский",
        "audio_providers": ("google",),
    },
    {
        "name": "Scottish Gaelic",
        "iso_code": "gd",
        "native_name": "Gàidhlig",
        "audio_providers": ("google",),
    },
    {
        "name": "Spanish",
        "iso_code": "es",
        "native_name": "Español",
        "audio_providers": ("google",),
    },
    {
        "name": "Welsh",
        "iso_code": "cy",
        "native_name": "Cymraeg",
        "audio_providers": ("google",),
    },
)
