from __future__ import annotations

from copy import deepcopy

from fontTools.ttLib import TTFont

from .config import FontConfig
from .utils import is_cjk_codepoint, merge_os2_ranges

LEFT_PUNCTUATION: frozenset[int] = frozenset(
    {
        0x3010,  # 【
        0x300A,  # 《
        0x3008,  # 〈
        0x300C,  # 「
        0x300E,  # 『
        0x3014,  # 〔
        0x3016,  # 〖
        0x3018,  # 〘
        0x301A,  # 〚
        0xFF08,  # （
        0xFF3B,  # ［
        0xFF5B,  # ｛
        0x2018,  # '
        0x201C,  # "
    }
)

RIGHT_PUNCTUATION: frozenset[int] = frozenset(
    {
        0x3011,  # 】
        0x300B,  # 》
        0x3009,  # 〉
        0x300D,  # 」
        0x300F,  # 』
        0x3015,  # 〕
        0x3017,  # 〗
        0x3019,  # 〙
        0x301B,  # 〛
        0xFF09,  # ）
        0xFF3D,  # ］
        0xFF5D,  # ｝
        0x2019,  # '
        0x201D,  # "
    }
)

NERD_RANGES: tuple[tuple[int, int], ...] = (
    (0xE000, 0xF8FF),  # Private Use Area
    (0xF0000, 0xFFFFD),  # Supplementary Private Use Area-A
)

POWERLINE_RANGE: tuple[int, int] = (0xE0A0, 0xE0DF)

CJK_IDEOGRAPH_RANGES: tuple[tuple[int, int], ...] = (
    (0x4E00, 0x9FFF),  # CJK Unified Ideographs
    (0x3400, 0x4DBF),  # CJK Unified Ideographs Extension A
    (0x20000, 0x2A6DF),  # CJK Unified Ideographs Extension B
    (0x2A700, 0x2B73F),  # CJK Unified Ideographs Extension C
    (0x2B740, 0x2B81F),  # CJK Unified Ideographs Extension D
    (0x2B820, 0x2CEAF),  # CJK Unified Ideographs Extension E
    (0x2CEB0, 0x2EBEF),  # CJK Unified Ideographs Extension F
    (0x30000, 0x3134F),  # CJK Unified Ideographs Extension G
    (0x2E80, 0x2EFF),  # CJK Radicals Supplement
    (0x2F00, 0x2FDF),  # Kangxi Radicals
    (0x3100, 0x312F),  # Bopomofo
    (0x31A0, 0x31BF),  # Bopomofo Extended
    (0x31C0, 0x31EF),  # CJK Strokes
    (0xF900, 0xFAFF),  # CJK Compatibility Ideographs
    (0x2F800, 0x2FA1F),  # CJK Compatibility Ideographs Supplement
)


def get_cjk_cmap_entries(font: TTFont, config: FontConfig) -> dict[int, str]:
    """Get cmap entries for CJK codepoints."""
    cmap = font["cmap"].getBestCmap()
    if not cmap:
        return {}
    return {
        codepoint: glyph_name
        for codepoint, glyph_name in cmap.items()
        if is_cjk_codepoint(codepoint, config.cjk_ranges)
    }


def get_cjk_glyphs(font: TTFont, config: FontConfig) -> set[str]:
    """Get all CJK glyph names from a font."""
    return set(get_cjk_cmap_entries(font, config).values())


def merge_fonts(
    base_font_path: str,
    cn_font_path: str,
    config: FontConfig,
) -> TTFont:
    """Merge CJK glyphs from cn_font into base_font.

    The base font (JetBrains Mono NerdFont) provides:
    - English characters
    - NerdFont icons

    The CN font (LXGW WenKai Mono) provides:
    - CJK characters

    Args:
        base_font_path: Path to JetBrains Mono NerdFont
        cn_font_path: Path to LXGW WenKai Mono
        config: FontConfig object

    Returns:
        Merged TTFont object
    """
    print(f"  Loading base font: {base_font_path}")
    base_font = TTFont(base_font_path)
    print(f"  Loading CN font: {cn_font_path}")
    cn_font = TTFont(cn_font_path)

    # Get existing glyphs in base font (to avoid overwriting)
    base_glyph_names = set(base_font.getGlyphOrder())

    # Get CJK glyphs and cmap entries from CN font
    cjk_cmap = get_cjk_cmap_entries(cn_font, config)
    cjk_glyphs = set(cjk_cmap.values())

    print(f"  Found {len(cjk_glyphs)} CJK glyphs in CN font")

    # Get font tables
    base_glyf = base_font["glyf"]
    cn_glyf = cn_font["glyf"]
    base_hmtx = base_font["hmtx"]
    cn_hmtx = cn_font["hmtx"]

    # Calculate scaling factors
    base_upm = base_font["head"].unitsPerEm
    cn_upm = cn_font["head"].unitsPerEm

    # UPM normalization scale with visual adjustment
    # visual_scale adjusts the final glyph size (1.08 = 8% larger)
    upm_scale = base_upm / cn_upm  # e.g., 1000 / 2048 = 0.4883
    combined_scale = upm_scale * config.visual_scale
    print(
        f"  Scaling CN glyphs by {combined_scale:.4f} (UPM: {cn_upm} -> {base_upm}, visual: {config.visual_scale:.2f}x)"
    )

    glyphs_added = []

    for glyph_name in cjk_glyphs:
        # Skip if glyph already exists in base font
        if glyph_name in base_glyph_names:
            continue

        # Skip if glyph doesn't exist in cn font's glyf table
        if glyph_name not in cn_glyf.glyphs:
            continue

        # Copy glyph outline (deep copy to avoid modifying source font)
        # IMPORTANT: Use cn_glyf[name] instead of cn_glyf.glyphs[name]
        # The latter returns undecompiled glyph without coordinates attribute
        glyph = deepcopy(cn_glyf[glyph_name])
        base_glyf.glyphs[glyph_name] = glyph

        # Scale glyph to fit target width
        if hasattr(glyph, "coordinates") and glyph.numberOfContours > 0:
            # Ensure bounds are calculated before scaling
            if not hasattr(glyph, "xMin") or glyph.xMin is None:
                glyph.recalcBounds(base_glyf)

            # Apply combined scaling
            glyph.coordinates.scale((combined_scale, combined_scale))
            glyph.recalcBounds(base_glyf)

        # Set advance width to cn_width (1200) for 2:1 ratio
        # Preserve original LSB ratio for proper glyph positioning
        _, orig_lsb = cn_hmtx[glyph_name]
        scaled_lsb = int(orig_lsb * combined_scale)
        base_hmtx.metrics[glyph_name] = (config.cn_width, scaled_lsb)

        glyphs_added.append(glyph_name)

    print(f"  Added {len(glyphs_added)} new glyphs")

    if not glyphs_added:
        cn_font.close()
        return base_font

    # Update glyph order
    new_glyph_order = base_font.getGlyphOrder() + glyphs_added
    base_font.setGlyphOrder(new_glyph_order)
    base_font["maxp"].numGlyphs = len(new_glyph_order)

    # Update cmap with new glyphs
    # IMPORTANT: Must update all cmap subtables, not just getBestCmap()
    # Office applications may only read format=4 table for BMP characters
    glyphs_added_set = set(glyphs_added)
    for table in base_font["cmap"].tables:
        # Only update tables that map Unicode codepoints
        if table.platformID == 3 and table.platEncID in (1, 10):  # Windows Unicode BMP/Full
            for codepoint, glyph_name in cjk_cmap.items():
                if glyph_name in glyphs_added_set:
                    # format=4 only supports BMP (U+0000-U+FFFF)
                    if table.format == 4 and codepoint > 0xFFFF:
                        continue
                    if codepoint not in table.cmap:
                        table.cmap[codepoint] = glyph_name
        elif table.platformID == 0:  # Unicode platform
            for codepoint, glyph_name in cjk_cmap.items():
                if glyph_name in glyphs_added_set:
                    if table.format == 4 and codepoint > 0xFFFF:
                        continue
                    if codepoint not in table.cmap:
                        table.cmap[codepoint] = glyph_name

    # Update hhea table
    if "hhea" in base_font:
        base_font["hhea"].advanceWidthMax = max(base_font["hhea"].advanceWidthMax, config.cn_width)
        base_font["hhea"].numberOfHMetrics = len(base_hmtx.metrics)

    # Merge OS/2 ranges from CN font to base font
    merge_os2_ranges(base_font, cn_font)

    cn_font.close()
    return base_font


def scale_nerd_icons(font: TTFont, config: FontConfig) -> None:
    """Scale NerdFont icons to occupy 2x English character width (same as CJK).

    NerdFont icons are in Private Use Area:
    - U+E000-U+F8FF (BMP Private Use Area)
    - U+F0000-U+FFFFD (Supplementary Private Use Area-A)

    Powerline symbols (U+E0A0-U+E0DF) are handled specially:
    - They must maintain their original vertical bounds to align with text
    - Only horizontal width adjustment is applied, no scaling or vertical shift

    Args:
        font: TTFont object
        config: FontConfig object
    """
    glyf = font["glyf"]
    hmtx = font["hmtx"]
    cmap = font["cmap"].getBestCmap()
    if not cmap:
        return

    # Build mapping: codepoint -> glyph_name for nerd icons
    nerd_glyph_map: dict[str, int] = {}
    for codepoint, glyph_name in cmap.items():
        for start, end in NERD_RANGES:
            if start <= codepoint <= end:
                nerd_glyph_map[glyph_name] = codepoint
                break

    if not nerd_glyph_map:
        return

    print(f"  Processing {len(nerd_glyph_map)} NerdFont icons...")

    # Single-width icons: keep original size (~60-70% of 600 cell)
    # so content icons align with English characters instead of CJK width.
    # Powerline separators below remain 2-cells wide by design.
    scale_factor = 1.0

    powerline_count = 0
    scaled_count = 0

    for glyph_name, codepoint in nerd_glyph_map.items():
        if glyph_name not in glyf.glyphs:
            continue

        glyph = glyf[glyph_name]
        if glyph.numberOfContours <= 0:
            continue

        # Get current metrics
        width, _ = hmtx[glyph_name]
        if width != config.en_width:
            continue  # Skip if not standard English width

        # Check if this is a Powerline symbol
        is_powerline = POWERLINE_RANGE[0] <= codepoint <= POWERLINE_RANGE[1]

        if is_powerline:
            # Powerline symbols: only adjust width, no scaling or vertical shift
            # These symbols need to maintain their original vertical bounds
            if hasattr(glyph, "coordinates"):
                if not hasattr(glyph, "xMin") or glyph.xMin is None:
                    glyph.recalcBounds(glyf)

                # Only center horizontally, keep vertical position
                if hasattr(glyph, "xMin") and glyph.xMin is not None:
                    glyph_width = glyph.xMax - glyph.xMin
                    ideal_lsb = (config.cn_width - glyph_width) // 2
                    delta_x = ideal_lsb - glyph.xMin

                    if abs(delta_x) > 1:
                        glyph.coordinates.translate((delta_x, 0))
                        glyph.recalcBounds(glyf)

                    hmtx[glyph_name] = (config.cn_width, ideal_lsb)
                else:
                    hmtx[glyph_name] = (config.cn_width, 0)

            powerline_count += 1
        else:
            # Regular icons: scale and center both horizontally and vertically
            if hasattr(glyph, "coordinates"):
                # Ensure bounds are calculated
                if not hasattr(glyph, "xMin") or glyph.xMin is None:
                    glyph.recalcBounds(glyf)

                # Scale to 2x size
                glyph.coordinates.scale((scale_factor, scale_factor))
                glyph.recalcBounds(glyf)

            # Update advance width to English width (600) for single-width icons
            # Center the glyph horizontally and vertically
            if hasattr(glyph, "xMin") and glyph.xMin is not None:
                glyph_width = glyph.xMax - glyph.xMin
                ideal_lsb = (config.en_width - glyph_width) // 2
                delta_x = ideal_lsb - glyph.xMin

                # Vertical centering: align icon center with CJK center (~360)
                glyph_center_y = (glyph.yMin + glyph.yMax) / 2
                target_center_y = 360  # Similar to CJK vertical center
                delta_y = target_center_y - glyph_center_y

                if abs(delta_x) > 1 or abs(delta_y) > 1:
                    glyph.coordinates.translate((delta_x, delta_y))
                    glyph.recalcBounds(glyf)

                hmtx[glyph_name] = (config.en_width, ideal_lsb)
            else:
                hmtx[glyph_name] = (config.en_width, 0)

            scaled_count += 1

    print(f"    Powerline symbols (no scaling): {powerline_count}")
    print(f"    Regular icons (scaled {scale_factor}x, single-width): {scaled_count}")


def center_cjk_glyphs(font: TTFont, config: FontConfig) -> None:
    """Center CJK glyphs within their advance width.

    Only centers glyphs that occupy more than half the advance width.
    Narrow glyphs (like punctuation) keep their original position,
    except for paired punctuation (brackets, quotes) which are aligned
    to their respective sides.

    Args:
        font: TTFont object
        config: FontConfig object
    """
    glyf = font["glyf"]
    hmtx = font["hmtx"]
    cmap = font["cmap"].getBestCmap()
    if not cmap:
        return

    cjk_entries = {cp: gn for cp, gn in cmap.items() if is_cjk_codepoint(cp, config.cjk_ranges)}
    if not cjk_entries:
        return

    cjk_glyphs = set(cjk_entries.values())
    glyph_to_codepoint = {gn: cp for cp, gn in cjk_entries.items()}

    centered_count = 0
    skipped_count = 0
    paired_count = 0

    for glyph_name in cjk_glyphs:
        if glyph_name not in glyf.glyphs:
            continue

        glyph = glyf[glyph_name]
        if glyph.numberOfContours <= 0:
            continue

        width, _ = hmtx[glyph_name]
        if width != config.cn_width:
            continue

        # Calculate glyph bounds
        if not hasattr(glyph, "xMin") or glyph.xMin is None:
            glyph.recalcBounds(glyf)

        if glyph.xMin is None or glyph.xMax is None:
            continue

        glyph_width = glyph.xMax - glyph.xMin
        codepoint = glyph_to_codepoint.get(glyph_name, 0)

        # Handle paired punctuation specially
        if codepoint in LEFT_PUNCTUATION:
            # Left punctuation (opening): align to right side
            ideal_lsb = config.cn_width - glyph_width
            delta = ideal_lsb - glyph.xMin
            if abs(delta) > 1:
                glyph.coordinates.translate((delta, 0))
                glyph.recalcBounds(glyf)
                hmtx[glyph_name] = (config.cn_width, ideal_lsb)
            paired_count += 1
            continue

        if codepoint in RIGHT_PUNCTUATION:
            # Right punctuation (closing): align to left side
            ideal_lsb = 0
            delta = ideal_lsb - glyph.xMin
            if abs(delta) > 1:
                glyph.coordinates.translate((delta, 0))
                glyph.recalcBounds(glyf)
                hmtx[glyph_name] = (config.cn_width, ideal_lsb)
            paired_count += 1
            continue

        # Narrow glyphs (like punctuation) keep their original position,
        # but ideographs/radicals/bopomofo should always be centered.
        is_ideograph = any(start <= codepoint <= end for start, end in CJK_IDEOGRAPH_RANGES)
        if not is_ideograph and glyph_width <= config.cn_width // 2:
            skipped_count += 1
            continue

        # Calculate centering offset
        ideal_lsb = (config.cn_width - glyph_width) // 2
        delta = ideal_lsb - glyph.xMin

        if abs(delta) > 1:  # Only adjust if significant
            glyph.coordinates.translate((delta, 0))
            glyph.recalcBounds(glyf)
            hmtx[glyph_name] = (config.cn_width, ideal_lsb)
            centered_count += 1

    print(
        f"    Centered: {centered_count}, Paired punctuation: {paired_count}, Skipped (narrow): {skipped_count}"
    )
