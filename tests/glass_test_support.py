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
        source += shared
    run_source(source)
