# -*- coding: utf-8 -*-
"""Module with constants defining the language support of underlying NLP libraries: spaCy and SymSpell"""

SUPPORTED_LANGUAGES_SYMSPELL = {
    "ar": "Arabic",
    "bg": "Bulgarian",
    "ca": "Catalan",
    "cs": "Czech",
    "da": "Danish",
    "de": "German",
    "el": "Greek",
    "en": "English",
    "es": "Spanish",
    "et": "Estonian",
    "fa": "Persian",
    "fi": "Finnish",
    "fr": "French",
    "he": "Hebrew",
    "hr": "Croatian",
    "hu": "Hungarian",
    "id": "Indonesian",
    "is": "Icelandic",
    "it": "Italian",
    "ja": "Japanese",
    "lt": "Lithuanian",
    "lv": "Latvian",
    "nl": "Dutch",
    "pl": "Polish",
    "pt": "Portuguese",
    "ro": "Romanian",
    "ru": "Russian",
    "sk": "Slovak",
    "sl": "Slovenian",
    "sq": "Albanian",
    "sr": "Serbian",
    "sv": "Swedish",
    "th": "Thai",
    "tr": "Turkish",
    "vi": "Vietnamese",
    "zh": "Chinese (simplified)",
}
"""dict: SymSpell dictionaries included in this plugin
Dictionary with ISO 639-1 language code (key) and language name (value)
"""

SUPPORTED_LANGUAGES_SPACY = {
    "af": "Afrikaans",
    "ar": "Arabic",
    "bg": "Bulgarian",
    "bn": "Bengali",
    "ca": "Catalan",
    "cs": "Czech",
    "da": "Danish",
    "de": "German",
    "el": "Greek",
    "en": "English",
    "es": "Spanish",
    "et": "Estonian",
    "eu": "Basque",
    "fa": "Persian",
    "fi": "Finnish",
    "fr": "French",
    "ga": "Irish",
    "gu": "Gujarati",
    "he": "Hebrew",
    "hi": "Hindi",
    "hr": "Croatian",
    "hu": "Hungarian",
    "hy": "Armenian",
    "id": "Indonesian",
    "is": "Icelandic",
    "it": "Italian",
    "ja": "Japanese",
    "kn": "Kannada",
    "lb": "Luxembourgish",
    "lt": "Lithuanian",
    "lv": "Latvian",
    "ml": "Malayalam",
    "mr": "Marathi",
    "nb": "Norwegian Bokmål",
    "nl": "Dutch",
    "pl": "Polish",
    "pt": "Portuguese",
    "ro": "Romanian",
    "ru": "Russian",
    "si": "Sinhala",
    "sk": "Slovak",
    "sl": "Slovenian",
    "sq": "Albanian",
    "sr": "Serbian",
    "sv": "Swedish",
    "ta": "Tamil",
    "te": "Telugu",
    "th": "Thai",
    "tl": "Tagalog",
    "tr": "Turkish",
    "tt": "Tatar",
    "ur": "Urdu",
    "vi": "Vietnamese",
    "yo": "Yoruba",
    "zh": "Chinese (simplified)",
}
"""dict: Languages supported by spaCy: https://spacy.io/usage/models#languages
Dictionary with ISO 639-1 language code (key) and language name (value).
Korean and Ukrainian not included because they require system-level package installations
"""

SPACY_LANGUAGE_MODELS = {
    "en": "en_core_web_sm",  # OntoNotes
    "es": "es_core_news_sm",  # Wikipedia
    "zh": "zh_core_web_sm",  # OntoNotes
    "xx": "xx_ent_wiki_sm",  # Wikipedia
    "pl": "nb_core_news_sm",  # NorNE
    "fr": "fr_core_news_sm",  # Wikipedia
    "de": "de_core_news_sm",  # OntoNotes
}
"""dict: Mapping between ISO 639-1 language code and spaCy model identifiers
Models with Creative Commons licenses are not included because this plugin is licensed under Apache-2
"""
