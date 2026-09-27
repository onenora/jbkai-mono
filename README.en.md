# JBKaiMono

English | [中文](README.md)

JetBrains Mono Nerd Font + LXGW WenKai Mono Screen = 2:1 CJK monospace coding font.

## Features

- **English**: JetBrains Mono NL Nerd Font (v3.5.1, single-width icons)
- **Chinese**: LXGW WenKai Mono GB Screen (v1.522, 31,332 glyphs)
- **Ratio**: Strict 2:1 width ratio (CJK 1200 FUnit, English 600 FUnit)
- **Styles**: Standard 4 styles (Regular, Bold, Italic, Bold Italic), natively matching IDE syntax highlighting

## Quick Build

### Dependencies

```bash
pip install fonttools pyyaml
```

### Build all 4 styles

```bash
python build.py
```

### Build single Regular style (Minimal mode)

```bash
python build.py --styles Regular
```

Generated fonts are saved in `output/fonts/`:
- `JBKaiMono-Regular.ttf`
- `JBKaiMono-Bold.ttf`
- `JBKaiMono-Italic.ttf`
- `JBKaiMono-BoldItalic.ttf`

## Installation & Configuration

### 1. Install fonts (macOS)

```bash
cp output/fonts/JBKaiMono-*.ttf ~/Library/Fonts/
```

### 2. Editor Settings (VS Code / Cursor)

```json
{
  "editor.fontFamily": "'JBKaiMono', monospace",
  "editor.fontLigatures": true,
  "editor.fontSize": 14,
  "editor.lineHeight": 1.5
}
```

## Configuration

Edit `config.yaml` to adjust build parameters:

```yaml
font:
  family_name: "JBKaiMono"
  version: "1.4"

styles:
  Regular:
    en_font: "JetBrainsMono-Regular.ttf"
    cn_font: "LXGWWenKaiMonoGBScreen.ttf"
    display_name: "Regular"
  Italic:
    en_font: "JetBrainsMono-Italic.ttf"
    cn_font: "LXGWWenKaiMonoGBScreen.ttf"
    display_name: "Italic"
  Bold:
    en_font: "JetBrainsMono-Bold.ttf"
    cn_font: "LXGWWenKaiMonoGBScreen.ttf"
    display_name: "Bold"
  BoldItalic:
    en_font: "JetBrainsMono-BoldItalic.ttf"
    cn_font: "LXGWWenKaiMonoGBScreen.ttf"
    display_name: "Bold Italic"

build:
  styles: "Regular,Bold,Italic,BoldItalic"
  output_dir: "output/fonts"
  parallel: 4

width:
  monospace: false
  visual_scale: 1.08
  en_width: 600
  cn_width: 1200
```

## Source Fonts

Located in `fonts/`:
- `JetBrainsMono-Regular.ttf` (JetBrains Mono v2.304)
- `JetBrainsMono-Bold.ttf` (JetBrains Mono v2.304)
- `JetBrainsMono-Italic.ttf` (JetBrains Mono v2.304)
- `JetBrainsMono-BoldItalic.ttf` (JetBrains Mono v2.304)
- `LXGWWenKaiMonoGBScreen.ttf` (LXGW WenKai Screen v1.522)
- `SymbolsNerdFont-Regular.ttf` (Nerd Fonts v3.5.1 Symbols Only)

## License

- JetBrains Mono: SIL Open Font License 1.1
- LXGW WenKai: SIL Open Font License 1.1
- Nerd Fonts: MIT License
