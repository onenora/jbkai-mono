# JBKaiMono

[English](README.en.md) | 中文

JetBrains Mono Nerd Font + 霞鹜文楷屏幕阅读版等宽 = 2:1 中英文等宽编程字体。

## 特性

- **英文**: JetBrains Mono NL Nerd Font (v3.5.1，单宽图标)
- **中文**: 霞鹜文楷屏幕阅读版等宽 GB (v1.522，31,332 字完整字符集)
- **比例**: 严格 2:1 等宽（中文 1200 FUnit，英文 600 FUnit）
- **样式**: 标准 4 样式（Regular, Bold, Italic, Bold Italic），与主流 IDE 语法高亮无缝匹配

## 快速构建

### 依赖安装

```bash
pip install fonttools pyyaml
```

### 构建全部样式（4 样式）

```bash
python build.py
```

### 仅构建常规体（单文件极简模式）

```bash
python build.py --styles Regular
```

生成字体保存在 `output/fonts/`：
- `JBKaiMono-Regular.ttf`
- `JBKaiMono-Bold.ttf`
- `JBKaiMono-Italic.ttf`
- `JBKaiMono-BoldItalic.ttf`

## 安装与配置

### 1. 安装字体 (macOS)

```bash
cp output/fonts/JBKaiMono-*.ttf ~/Library/Fonts/
```

### 2. 编辑器设置 (VS Code / Cursor)

```json
{
  "editor.fontFamily": "'JBKaiMono', monospace",
  "editor.fontLigatures": true,
  "editor.fontSize": 14,
  "editor.lineHeight": 1.5
}
```

## 配置定制

修改 `config.yaml` 调整构建参数：

```yaml
font:
  family_name: "JBKaiMono"
  version: "1.4"

# 4 样式映射
styles:
  Regular:
    en_font: "JetBrainsMonoNLNerdFontMono-Regular.ttf"
    cn_font: "LXGWWenKaiMonoGBScreen.ttf"
    display_name: "Regular"
  Italic:
    en_font: "JetBrainsMonoNLNerdFontMono-Italic.ttf"
    cn_font: "LXGWWenKaiMonoGBScreen.ttf"
    display_name: "Italic"
  Bold:
    en_font: "JetBrainsMonoNLNerdFontMono-Bold.ttf"
    cn_font: "LXGWWenKaiMonoGBScreen.ttf"
    display_name: "Bold"
  BoldItalic:
    en_font: "JetBrainsMonoNLNerdFontMono-BoldItalic.ttf"
    cn_font: "LXGWWenKaiMonoGBScreen.ttf"
    display_name: "Bold Italic"

build:
  styles: "Regular,Bold,Italic,BoldItalic"
  output_dir: "output/fonts"
  parallel: 4

width:
  en_width: 600
  cn_width: 1200
  visual_scale: 1.08
```

## 源字体

放置于 `fonts/` 目录：
- `JetBrainsMonoNLNerdFontMono-Regular.ttf` (Nerd Fonts v3.5.1)
- `JetBrainsMonoNLNerdFontMono-Bold.ttf` (Nerd Fonts v3.5.1)
- `JetBrainsMonoNLNerdFontMono-Italic.ttf` (Nerd Fonts v3.5.1)
- `JetBrainsMonoNLNerdFontMono-BoldItalic.ttf` (Nerd Fonts v3.5.1)
- `LXGWWenKaiMonoGBScreen.ttf` (LXGW WenKai Screen v1.522)

## 许可证

- JetBrains Mono: SIL Open Font License 1.1
- 霞鹜文楷: SIL Open Font License 1.1
- Nerd Fonts: MIT License
