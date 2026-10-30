"""Link the production shared glass policy into Java source-launcher harnesses."""
import re
from pathlib import Path
from test_personal_privacy import run_java as run_source


def run_java(source):
    if 'LiquidGlassStyle' in source:
        path = Path(__file__).resolve().parents[1] / 'TMessagesProj/src/main/java/app/freezgram/LiquidGlassStyle.java'
        shared = path.read_text()
        shared = shared[shared.index('public final class'):].replace('public final class', 'final class', 1)
        shared = shared.replace('BooleanSupplier', 'java.util.function.BooleanSupplier')
        if 'navigationGlassBlur()' not in source:
            source = re.sub(r'class AppearanceConfig\s*\{', 'class AppearanceConfig { static int navigationGlassBlur(){return 6;} static int navigationGlassIntensity(){return 55;} static int navigationGlassTransparency(){return -1;}', source)
        if 'key_windowBackgroundWhite' not in source:
            source = re.sub(r'class Theme\s*\{', 'class Theme { static int key_windowBackgroundWhite;', source)
        if 'glassEnhanceColors()' not in source:
            source = re.sub(r'class AppearanceConfig\s*\{', 'class AppearanceConfig { static boolean glassEnhanceColors(){return true;}', source)
        if 'glassWallpaperDim()' not in source:
            source = re.sub(r'class AppearanceConfig\s*\{', 'class AppearanceConfig { static boolean glassWallpaperDim(){return true;}', source)
        source += shared
    if 'isGlassPowerSaverApplied()' in source:
        source = source.replace('org.telegram.messenger.LiteMode', 'LiteMode')
        if 'class LiteMode' not in source:
            source += '\nclass LiteMode{static boolean isGlassPowerSaverApplied(){return false;}}'
        elif 'static boolean isGlassPowerSaverApplied()' not in source:
            body = 'return isPowerSaverApplied();' if 'static boolean isPowerSaverApplied()' in source else 'return false;'
            source = re.sub(r'class LiteMode\s*\{', 'class LiteMode { static boolean isGlassPowerSaverApplied(){'+body+'}', source)
    run_source(source)
