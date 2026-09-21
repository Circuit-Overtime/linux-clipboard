"""Small, offline collections for the text picker pages."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TextItem:
    value: str
    name: str
    category: str
    keywords: str = ""


KAOMOJI = (
    TextItem("(＾▽＾)", "Happy smile", "Happy", "joy cheerful"),
    TextItem("(ᵔ◡ᵔ)", "Gentle smile", "Happy", "content"),
    TextItem("(⌒‿⌒)", "Warm smile", "Happy", "cheerful"),
    TextItem("(✿◠‿◠)", "Flower smile", "Happy", "cute"),
    TextItem("(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧", "Sparkle celebration", "Happy", "excited yay"),
    TextItem("ヽ(・∀・)ﾉ", "Cheering", "Happy", "yay celebration"),
    TextItem("(ﾉ´ヮ`)ﾉ*: ･ﾟ", "Joyful wave", "Happy", "celebration"),
    TextItem("(≧▽≦)", "Big grin", "Happy", "laugh"),
    TextItem("(づ｡◕‿‿◕｡)づ", "Hug", "Love", "cuddle embrace"),
    TextItem("(っ´▽｀)っ", "Open arms", "Love", "hug embrace"),
    TextItem("(♡°▽°♡)", "In love", "Love", "heart adore"),
    TextItem("(｡♥‿♥｡)", "Heart eyes", "Love", "adoration"),
    TextItem("( ˘ ³˘)♥", "Kiss", "Love", "heart"),
    TextItem("(灬º‿º灬)♡", "Blushing heart", "Love", "shy"),
    TextItem("(╥﹏╥)", "Crying", "Sad", "tears upset"),
    TextItem("(ಥ_ಥ)", "Tearful", "Sad", "cry"),
    TextItem("(；ω；)", "Sad tears", "Sad", "cry"),
    TextItem("(｡•́︿•̀｡)", "Disappointed", "Sad", "upset"),
    TextItem("(つ﹏⊂)", "Hiding tears", "Sad", "cry"),
    TextItem("(╯°□°）╯︵ ┻━┻", "Table flip", "Angry", "rage frustrated"),
    TextItem("(ノಠ益ಠ)ノ彡┻━┻", "Angry table flip", "Angry", "rage"),
    TextItem("(ಠ_ಠ)", "Disapproval", "Angry", "annoyed glare"),
    TextItem("(¬_¬)", "Side eye", "Angry", "suspicious annoyed"),
    TextItem("(ง'̀-'́)ง", "Ready to fight", "Angry", "determined"),
    TextItem("(⊙_⊙)", "Wide eyes", "Surprised", "shocked wow"),
    TextItem("(☉_☉)", "Astonished", "Surprised", "shock"),
    TextItem("(°ロ°) !", "Gasp", "Surprised", "wow"),
    TextItem("(ﾉﾟ0ﾟ)ﾉ~", "Startled", "Surprised", "shock"),
    TextItem("¯\\_(ツ)_/¯", "Shrug", "Gestures", "dunno whatever"),
    TextItem("(☞ﾟヮﾟ)☞", "Finger guns", "Gestures", "point"),
    TextItem("(☝︎ ՞ਊ ՞)☝︎", "Hands up", "Gestures", "point"),
    TextItem("(￣ー￣)ゞ", "Salute", "Gestures", "respect"),
    TextItem("( •_•)>⌐■-■", "Putting on sunglasses", "Gestures", "cool"),
    TextItem("(⌐■_■)", "Cool sunglasses", "Gestures", "deal with it"),
    TextItem("(=^･ω･^=)", "Cat face", "Animals", "kitten"),
    TextItem("(=｀ω´=)", "Grumpy cat", "Animals", "kitten"),
    TextItem("ʕ•ᴥ•ʔ", "Bear", "Animals", "cute"),
    TextItem("ʕっ•ᴥ•ʔっ", "Bear hug", "Animals", "cuddle"),
    TextItem("(U・x・U)", "Dog face", "Animals", "puppy"),
    TextItem("(V●ᴥ●V)", "Puppy", "Animals", "dog"),
)


SYMBOL_GROUPS = (
    ("Arrows", "← ↑ → ↓ ↔ ↕ ↖ ↗ ↘ ↙ ↩ ↪ ↶ ↷ ⇐ ⇒ ⇑ ⇓ ⇔ ➜ ➤ ⟵ ⟶ ⟷"),
    ("Math", "± × ÷ ≠ ≈ ≤ ≥ ∞ √ ∑ ∏ ∫ ∂ ∆ ∇ ∝ ∈ ∉ ∩ ∪ ⊂ ⊃ ⊆ ⊇ ∀ ∃ ∅ ∴ ∵ ∠ ⊥ ∥ ⋅ ∘"),
    ("Currency", "$ € £ ¥ ₹ ₩ ₽ ₿ ¢ ₫ ₺ ₴ ₦ ₱ ₲ ₭"),
    ("Punctuation", "… • ‣ ‧ ‰ ′ ″ ‽ ¿ ¡ « » ‹ › ‘ ’ “ ” — – ‑ § ¶ ※ † ‡"),
    ("Shapes", "■ □ ▪ ▫ ▲ △ ▼ ▽ ◆ ◇ ● ○ ◉ ◎ ★ ☆ ♠ ♣ ♥ ♦ ✓ ✔ ✕ ✖ ☑ ☒"),
    ("Music", "♪ ♫ ♬ ♩ ♭ ♮ ♯ 𝄞"),
    ("Legal", "© ® ™ ℠ № ℗ ℮"),
    ("Units", "° ℃ ℉ µ Ω Å Å ² ³ ½ ¼ ¾"),
    ("Greek", "α β γ δ ε θ λ μ π σ φ ψ ω Α Β Γ Δ Θ Λ Π Σ Φ Ω"),
)

SYMBOL_ALIASES = {
    "©": "copyright copy",
    "®": "registered trademark",
    "™": "trademark brand",
    "→": "right arrow next forward",
    "←": "left arrow back previous",
    "↑": "up arrow",
    "↓": "down arrow",
    "∞": "infinity forever",
    "✓": "check tick done",
    "✔": "check tick done",
    "×": "multiply multiplication",
    "÷": "divide division",
    "π": "pi math",
    "€": "euro money",
    "₹": "rupee money india",
}

SYMBOLS = tuple(
    TextItem(
        value=symbol,
        name=unicodedata.name(symbol, symbol).replace("-", " ").title(),
        category=category,
        keywords=SYMBOL_ALIASES.get(symbol, ""),
    )
    for category, values in SYMBOL_GROUPS
    for symbol in values.split()
)
