import math
import os
import tkinter as tk


ICON_SIZES = (16, 24, 32, 48, 64, 128, 256)
# A personalização do template usa o ícone completo fornecido em ico.png.
ICON_SOURCE_CROP = (0.0, 0.0, 1.0, 1.0)


def _load_pillow_modules():
    try:
        from PIL import Image, ImageTk
    except ModuleNotFoundError:
        return None, None
    return Image, ImageTk


def _get_resample_filter(image_module):
    try:
        return image_module.Resampling.LANCZOS
    except AttributeError:
        return image_module.LANCZOS


def _calculate_crop_box(width, height):
    left = max(0, min(int(width * ICON_SOURCE_CROP[0]), width - 1))
    top = max(0, min(int(height * ICON_SOURCE_CROP[1]), height - 1))
    right = max(left + 1, min(int(width * ICON_SOURCE_CROP[2]), width))
    bottom = max(top + 1, min(int(height * ICON_SOURCE_CROP[3]), height))
    return left, top, right, bottom


def _crop_pillow_icon(image):
    return image.crop(_calculate_crop_box(*image.size))


def _crop_tk_icon(image, master):
    left, top, right, bottom = _calculate_crop_box(image.width(), image.height())
    cropped = tk.PhotoImage(master=master)
    cropped.tk.call(str(cropped), "copy", str(image), "-from", left, top, right, bottom, "-shrink")
    return cropped


def _get_tk_scale_factors(source_size, target_size):
    common = math.gcd(source_size, target_size)
    return max(1, target_size // common), max(1, source_size // common)


def _scale_tk_icon(image, target_size):
    source_size = image.width()
    if source_size == target_size:
        return image.zoom(1, 1)

    zoom_factor, subsample_factor = _get_tk_scale_factors(source_size, target_size)

    scaled = image
    if zoom_factor > 1:
        scaled = scaled.zoom(zoom_factor, zoom_factor)
    if subsample_factor > 1:
        scaled = scaled.subsample(subsample_factor, subsample_factor)
    return scaled


def _load_tk_icon_variants(window, icon_path):
    source_icon = tk.PhotoImage(file=icon_path, master=window)
    base_icon = _crop_tk_icon(source_icon, window)
    return [
        _scale_tk_icon(base_icon, size)
        for size in ICON_SIZES
    ]


def apply_window_icon(window, project_root, *, default=False, logger=None):
    """
    Apply the shared application icon from the project root to a Tk window.

    The source asset is `ico.png`, which is resized in memory to several common
    icon sizes so Tk and the OS can choose the most appropriate one.
    """
    icon_path = os.path.join(project_root, "ico.png")
    if not os.path.exists(icon_path):
        if logger:
            logger.debug("Ícone opcional não encontrado: %s", icon_path)
        return False

    try:
        Image, ImageTk = _load_pillow_modules()
        if Image is not None and ImageTk is not None:
            with Image.open(icon_path) as icon_source:
                base_icon = _crop_pillow_icon(icon_source.convert("RGBA"))
                resample = _get_resample_filter(Image)
                window._app_icon_images = [
                    ImageTk.PhotoImage(
                        base_icon.resize((size, size), resample),
                        master=window,
                    )
                    for size in ICON_SIZES
                ]
        else:
            window._app_icon_images = _load_tk_icon_variants(window, icon_path)

        window.iconphoto(default, *window._app_icon_images)
        return True
    except Exception as exc:
        if logger:
            logger.warning("Failed to apply window icon from %s: %s", icon_path, exc)
        return False
