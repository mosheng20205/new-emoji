"""
Public Python ctypes helpers for new_emoji.dll.

This module is shared by the gallery demo and small Python examples. It keeps
the native EU_* signatures and convenience helpers out of the test folder so
open source users can start from a clean example surface.
"""
import ctypes
from ctypes import wintypes
import sys
import os
import time
import json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

def resource_path(relative_path):
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", relative_path))


DLL_PATH = resource_path(os.path.join("bin", "x64", "Release", "new_emoji.dll"))

# Load DLL
dll = ctypes.WinDLL(DLL_PATH)

# 鈹€鈹€ Callback types 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
ClickCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int)
ResizeCallback = ctypes.WINFUNCTYPE(None, wintypes.HWND, ctypes.c_int, ctypes.c_int)
CloseCallback  = ctypes.WINFUNCTYPE(None, wintypes.HWND)
MessageBoxCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int, ctypes.c_int)
MessageBoxExCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int, ctypes.c_int,
                                          ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int)
TextCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int)
ValueCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int)
ReorderCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int)
BeforeCloseCallback = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int)
TableCellCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int)
TableCellEditCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                           ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int)
TableVirtualRowCallback = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                             ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int)
DropdownCommandCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int, ctypes.c_int,
                                             ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int)
MenuSelectCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int, ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int)
TreeNodeEventCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                           ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int)
TreeNodeAllowDragCallback = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int,
                                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int)
TreeNodeAllowDropCallback = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int,
                                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                               ctypes.c_int)
DateDisabledCallback = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int)

EXTENDED_PLACEMENTS = {
    "top-start": 0, "top": 1, "top-end": 2,
    "bottom-start": 3, "bottom": 4, "bottom-end": 5,
    "left-start": 6, "left": 7, "left-end": 8,
    "right-start": 9, "right": 10, "right-end": 11,
}

TRIGGER_MODES = {
    "click": 0,
    "hover": 1,
    "focus": 2,
    "manual": 3,
}

CAROUSEL_TRIGGER_MODES = {"hover": 0, "click": 1}
CAROUSEL_ARROW_MODES = {"hover": 0, "always": 1, "never": 2}
CAROUSEL_DIRECTIONS = {"horizontal": 0, "vertical": 1}
CAROUSEL_TYPES = {"normal": 0, "card": 1}

EU_WINDOW_FRAME_DEFAULT = 0x0000
EU_WINDOW_FRAME_BORDERLESS = 0x0001
EU_WINDOW_FRAME_CUSTOM_CAPTION = 0x0002
EU_WINDOW_FRAME_CUSTOM_BUTTONS = 0x0004
EU_WINDOW_FRAME_RESIZABLE = 0x0008
EU_WINDOW_FRAME_ROUNDED = 0x0010
EU_WINDOW_FRAME_HIDE_TITLEBAR = 0x0020
EU_WINDOW_FRAME_BROWSER_SHELL = (
    EU_WINDOW_FRAME_BORDERLESS |
    EU_WINDOW_FRAME_CUSTOM_CAPTION |
    EU_WINDOW_FRAME_CUSTOM_BUTTONS |
    EU_WINDOW_FRAME_RESIZABLE |
    EU_WINDOW_FRAME_ROUNDED |
    EU_WINDOW_FRAME_HIDE_TITLEBAR
)

EU_WINDOW_COMMAND_NONE = 0
EU_WINDOW_COMMAND_MINIMIZE = 1
EU_WINDOW_COMMAND_TOGGLE_MAXIMIZE = 2
EU_WINDOW_COMMAND_CLOSE = 3

# 鈹€鈹€ Export signatures 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

def ptr(s): return ctypes.c_char_p(s) if isinstance(s, bytes) else ctypes.c_char_p(s.encode('utf-8'))

dll.EU_CreateWindow.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                 ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                 ctypes.c_uint32]
dll.EU_CreateWindow.restype = wintypes.HWND
dll.EU_CreateWindowEx.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                  ctypes.c_uint32, ctypes.c_int]
dll.EU_CreateWindowEx.restype = wintypes.HWND
dll.EU_SetWindowIcon.argtypes = [wintypes.HWND, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetWindowIcon.restype = ctypes.c_int
dll.EU_SetWindowIconFromBytes.argtypes = [wintypes.HWND, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetWindowIconFromBytes.restype = ctypes.c_int

dll.EU_DestroyWindow.argtypes = [wintypes.HWND]
dll.EU_ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]

dll.EU_CreatePanel.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                ctypes.c_int, ctypes.c_int]
dll.EU_CreatePanel.restype = ctypes.c_int

dll.EU_CreateButton.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                 ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateButton.restype = ctypes.c_int

dll.EU_CreateEditBox.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateEditBox.restype = ctypes.c_int

dll.EU_CreateInfoBox.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateInfoBox.restype = ctypes.c_int

dll.EU_CreateText.argtypes = [wintypes.HWND, ctypes.c_int,
                              ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                              ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateText.restype = ctypes.c_int

dll.EU_CreateLink.argtypes = [wintypes.HWND, ctypes.c_int,
                              ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                              ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateLink.restype = ctypes.c_int

dll.EU_CreateIcon.argtypes = [wintypes.HWND, ctypes.c_int,
                              ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                              ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateIcon.restype = ctypes.c_int

dll.EU_CreateIconButton.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateIconButton.restype = ctypes.c_int

dll.EU_CreateOmnibox.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                 ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateOmnibox.restype = ctypes.c_int

dll.EU_CreateBrowserViewport.argtypes = [wintypes.HWND, ctypes.c_int,
                                         ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateBrowserViewport.restype = ctypes.c_int

dll.EU_CreateSpace.argtypes = [wintypes.HWND, ctypes.c_int,
                               ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateSpace.restype = ctypes.c_int

dll.EU_CreateContainer.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateContainer.restype = ctypes.c_int

_container_region_args = [wintypes.HWND, ctypes.c_int,
                          ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                          ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateHeader.argtypes = _container_region_args
dll.EU_CreateHeader.restype = ctypes.c_int
dll.EU_CreateAside.argtypes = _container_region_args
dll.EU_CreateAside.restype = ctypes.c_int
dll.EU_CreateMain.argtypes = _container_region_args
dll.EU_CreateMain.restype = ctypes.c_int
dll.EU_CreateFooter.argtypes = _container_region_args
dll.EU_CreateFooter.restype = ctypes.c_int

dll.EU_CreateLayout.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateLayout.restype = ctypes.c_int

dll.EU_CreateBorder.argtypes = [wintypes.HWND, ctypes.c_int,
                                ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateBorder.restype = ctypes.c_int

dll.EU_CreateCheckbox.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateCheckbox.restype = ctypes.c_int

dll.EU_CreateCheckboxGroup.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                       ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                       ctypes.c_int, ctypes.c_int,
                                       ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateCheckboxGroup.restype = ctypes.c_int

dll.EU_CreateRadio.argtypes = [wintypes.HWND, ctypes.c_int,
                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                               ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateRadio.restype = ctypes.c_int

dll.EU_CreateRadioGroup.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateRadioGroup.restype = ctypes.c_int

dll.EU_CreateSwitch.argtypes = [wintypes.HWND, ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateSwitch.restype = ctypes.c_int

dll.EU_CreateSlider.argtypes = [wintypes.HWND, ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateSlider.restype = ctypes.c_int

dll.EU_CreateInputNumber.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                      ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                      ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateInputNumber.restype = ctypes.c_int

dll.EU_CreateInput.argtypes = [wintypes.HWND, ctypes.c_int,
                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                               ctypes.c_int,
                               ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateInput.restype = ctypes.c_int

dll.EU_CreateInputGroup.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateInputGroup.restype = ctypes.c_int

dll.EU_SetInputIcons.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetInputIcons.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetInputIcons.restype = ctypes.c_int
dll.EU_SetInputVisualOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                         ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                         ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetInputVisualOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                         ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                         ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                         ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetInputVisualOptions.restype = ctypes.c_int
dll.EU_SetInputSelection.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetInputSelection.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetInputSelection.restype = ctypes.c_int
dll.EU_SetInputContextMenuEnabled.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetInputContextMenuEnabled.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetInputContextMenuEnabled.restype = ctypes.c_int
dll.EU_SetInputGroupValue.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetInputGroupValue.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetInputGroupValue.restype = ctypes.c_int
dll.EU_SetInputGroupOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                        ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetInputGroupOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                        ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                        ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                        ctypes.POINTER(ctypes.c_int)]
dll.EU_GetInputGroupOptions.restype = ctypes.c_int
dll.EU_SetInputGroupTextAddon.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                          ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetInputGroupButtonAddon.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                            ctypes.c_int]
dll.EU_SetInputGroupSelectAddon.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                            ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_ClearInputGroupAddon.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetInputGroupInputElementId.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetInputGroupInputElementId.restype = ctypes.c_int
dll.EU_GetInputGroupAddonElementId.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetInputGroupAddonElementId.restype = ctypes.c_int

dll.EU_CreateInputTag.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateInputTag.restype = ctypes.c_int

dll.EU_CreateSelect.argtypes = [wintypes.HWND, ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                ctypes.c_int,
                                ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateSelect.restype = ctypes.c_int

dll.EU_CreateSelectV2.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateSelectV2.restype = ctypes.c_int

dll.EU_CreateRate.argtypes = [wintypes.HWND, ctypes.c_int,
                              ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                              ctypes.c_int, ctypes.c_int,
                              ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateRate.restype = ctypes.c_int

dll.EU_CreateColorPicker.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                     ctypes.c_uint32,
                                     ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateColorPicker.restype = ctypes.c_int

dll.EU_CreateTag.argtypes = [wintypes.HWND, ctypes.c_int,
                             ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                             ctypes.c_int, ctypes.c_int, ctypes.c_int,
                             ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateTag.restype = ctypes.c_int

dll.EU_CreateBadge.argtypes = [wintypes.HWND, ctypes.c_int,
                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                               ctypes.c_int, ctypes.c_int,
                               ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateBadge.restype = ctypes.c_int

dll.EU_CreateProgress.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateProgress.restype = ctypes.c_int

dll.EU_CreateAvatar.argtypes = [wintypes.HWND, ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                ctypes.c_int,
                                ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateAvatar.restype = ctypes.c_int

dll.EU_CreateEmpty.argtypes = [wintypes.HWND, ctypes.c_int,
                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                               ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateEmpty.restype = ctypes.c_int

dll.EU_CreateSkeleton.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateSkeleton.restype = ctypes.c_int

dll.EU_CreateDescriptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                      ctypes.c_int, ctypes.c_int,
                                      ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateDescriptions.restype = ctypes.c_int

dll.EU_CreateTable.argtypes = [wintypes.HWND, ctypes.c_int,
                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                               ctypes.c_int, ctypes.c_int,
                               ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateTable.restype = ctypes.c_int

dll.EU_CreateCard.argtypes = [wintypes.HWND, ctypes.c_int,
                              ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                              ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                              ctypes.c_int,
                              ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateCard.restype = ctypes.c_int

dll.EU_CreateCollapse.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateCollapse.restype = ctypes.c_int

dll.EU_CreateTimeline.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateTimeline.restype = ctypes.c_int

dll.EU_CreateStatistic.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                   ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateStatistic.restype = ctypes.c_int

dll.EU_CreateKpiCard.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                 ctypes.c_int,
                                 ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateKpiCard.restype = ctypes.c_int

dll.EU_CreateTrend.argtypes = [wintypes.HWND, ctypes.c_int,
                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                               ctypes.c_int,
                               ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateTrend.restype = ctypes.c_int

dll.EU_CreateStatusDot.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                   ctypes.c_int,
                                   ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateStatusDot.restype = ctypes.c_int

dll.EU_CreateGauge.argtypes = [wintypes.HWND, ctypes.c_int,
                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                               ctypes.c_int,
                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                               ctypes.c_int,
                               ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateGauge.restype = ctypes.c_int

dll.EU_CreateRingProgress.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                      ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                      ctypes.c_int,
                                      ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateRingProgress.restype = ctypes.c_int

dll.EU_CreateBulletProgress.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                        ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                        ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateBulletProgress.restype = ctypes.c_int

dll.EU_CreateLineChart.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                   ctypes.c_int,
                                   ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateLineChart.restype = ctypes.c_int

dll.EU_CreateBarChart.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateBarChart.restype = ctypes.c_int

dll.EU_CreateDonutChart.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                    ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateDonutChart.restype = ctypes.c_int

dll.EU_CreateDivider.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                 ctypes.c_int, ctypes.c_int,
                                 ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateDivider.restype = ctypes.c_int

dll.EU_CreateCalendar.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateCalendar.restype = ctypes.c_int

dll.EU_CreateTree.argtypes = [wintypes.HWND, ctypes.c_int,
                              ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                              ctypes.c_int,
                              ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateTree.restype = ctypes.c_int

dll.EU_CreateTreeSelect.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                    ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateTreeSelect.restype = ctypes.c_int

dll.EU_CreateTransfer.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateTransfer.restype = ctypes.c_int

dll.EU_CreateAutocomplete.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                      ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateAutocomplete.restype = ctypes.c_int

dll.EU_SetAutocompletePlaceholder.argtypes = [wintypes.HWND, ctypes.c_int,
                                              ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetAutocompletePlaceholder.argtypes = [wintypes.HWND, ctypes.c_int,
                                              ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetAutocompletePlaceholder.restype = ctypes.c_int
dll.EU_SetAutocompleteIcons.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetAutocompleteIcons.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetAutocompleteIcons.restype = ctypes.c_int
dll.EU_SetAutocompleteBehaviorOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetAutocompleteBehaviorOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                                  ctypes.POINTER(ctypes.c_int)]
dll.EU_GetAutocompleteBehaviorOptions.restype = ctypes.c_int

dll.EU_CreateMentions.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateMentions.restype = ctypes.c_int

dll.EU_CreateCascader.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateCascader.restype = ctypes.c_int

dll.EU_CreateDatePicker.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateDatePicker.restype = ctypes.c_int

dll.EU_CreateTimePicker.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateTimePicker.restype = ctypes.c_int

dll.EU_CreateDateTimePicker.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                        ctypes.c_int, ctypes.c_int,
                                        ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateDateTimePicker.restype = ctypes.c_int

dll.EU_CreateTimeSelect.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateTimeSelect.restype = ctypes.c_int

dll.EU_CreateDropdown.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateDropdown.restype = ctypes.c_int

dll.EU_CreateMenu.argtypes = [wintypes.HWND, ctypes.c_int,
                              ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                              ctypes.c_int, ctypes.c_int,
                              ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateMenu.restype = ctypes.c_int

dll.EU_CreateAnchor.argtypes = [wintypes.HWND, ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                ctypes.c_int,
                                ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateAnchor.restype = ctypes.c_int

dll.EU_CreateBacktop.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                 ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateBacktop.restype = ctypes.c_int

dll.EU_CreateSegmented.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                   ctypes.c_int,
                                   ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateSegmented.restype = ctypes.c_int

dll.EU_CreatePageHeader.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreatePageHeader.restype = ctypes.c_int

dll.EU_CreateAffix.argtypes = [wintypes.HWND, ctypes.c_int,
                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                               ctypes.c_int,
                               ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateAffix.restype = ctypes.c_int

dll.EU_CreateWatermark.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                   ctypes.c_int, ctypes.c_int,
                                   ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateWatermark.restype = ctypes.c_int

dll.EU_CreateTour.argtypes = [wintypes.HWND, ctypes.c_int,
                              ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                              ctypes.c_int, ctypes.c_int,
                              ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateTour.restype = ctypes.c_int

dll.EU_CreateImage.argtypes = [wintypes.HWND, ctypes.c_int,
                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                               ctypes.c_int,
                               ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateImage.restype = ctypes.c_int

dll.EU_CreateCarousel.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateCarousel.restype = ctypes.c_int

dll.EU_CreateUpload.argtypes = [wintypes.HWND, ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateUpload.restype = ctypes.c_int

dll.EU_CreateInfiniteScroll.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                        ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateInfiniteScroll.restype = ctypes.c_int

dll.EU_CreateBreadcrumb.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                    ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateBreadcrumb.restype = ctypes.c_int

dll.EU_CreateTabs.argtypes = [wintypes.HWND, ctypes.c_int,
                              ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                              ctypes.c_int, ctypes.c_int,
                              ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateTabs.restype = ctypes.c_int

dll.EU_CreatePagination.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreatePagination.restype = ctypes.c_int

dll.EU_CreateSteps.argtypes = [wintypes.HWND, ctypes.c_int,
                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                               ctypes.c_int,
                               ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateSteps.restype = ctypes.c_int

dll.EU_CreateAlert.argtypes = [wintypes.HWND, ctypes.c_int,
                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                               ctypes.c_int, ctypes.c_int, ctypes.c_int,
                               ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateAlert.restype = ctypes.c_int
dll.EU_CreateAlertEx.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                 ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                 ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                 ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateAlertEx.restype = ctypes.c_int

dll.EU_CreateResult.argtypes = [wintypes.HWND, ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                ctypes.c_int,
                                ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateResult.restype = ctypes.c_int

dll.EU_CreateNotification.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                      ctypes.c_int, ctypes.c_int,
                                      ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateNotification.restype = ctypes.c_int

dll.EU_ShowMessage.argtypes = [wintypes.HWND,
                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                               ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                               ctypes.c_int, ctypes.c_int]
dll.EU_ShowMessage.restype = ctypes.c_int

dll.EU_ShowNotification.argtypes = [wintypes.HWND,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int]
dll.EU_ShowNotification.restype = ctypes.c_int

dll.EU_CreateLoading.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                 ctypes.c_int,
                                 ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateLoading.restype = ctypes.c_int

dll.EU_CreateDialog.argtypes = [wintypes.HWND,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                ctypes.c_int, ctypes.c_int,
                                ctypes.c_int, ctypes.c_int]
dll.EU_CreateDialog.restype = ctypes.c_int

dll.EU_CreateDrawer.argtypes = [wintypes.HWND,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                ctypes.c_int]
dll.EU_CreateDrawer.restype = ctypes.c_int

dll.EU_CreateTooltip.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                 ctypes.c_int,
                                 ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateTooltip.restype = ctypes.c_int

dll.EU_CreatePopover.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                 ctypes.c_int,
                                 ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreatePopover.restype = ctypes.c_int

dll.EU_CreatePopconfirm.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                    ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreatePopconfirm.restype = ctypes.c_int

dll.EU_ShowMessageBox.argtypes = [wintypes.HWND,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                   MessageBoxCallback]
dll.EU_ShowMessageBox.restype = ctypes.c_int

dll.EU_ShowConfirmBox.argtypes = [wintypes.HWND,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  MessageBoxCallback]
dll.EU_ShowConfirmBox.restype = ctypes.c_int

dll.EU_ShowMessageBoxEx.argtypes = [wintypes.HWND,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                    ctypes.c_int, MessageBoxExCallback]
dll.EU_ShowMessageBoxEx.restype = ctypes.c_int

dll.EU_ShowPromptBox.argtypes = [wintypes.HWND,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                 ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                 MessageBoxExCallback]
dll.EU_ShowPromptBox.restype = ctypes.c_int

dll.EU_SetElementColor.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_uint32, ctypes.c_uint32]
dll.EU_SetElementText.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetElementText.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetElementText.restype = ctypes.c_int
dll.EU_SetElementBounds.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetElementBounds.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetElementBounds.restype = ctypes.c_int
dll.EU_SetElementVisible.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetElementVisible.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetElementVisible.restype = ctypes.c_int
dll.EU_SetElementEnabled.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetElementEnabled.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetElementEnabled.restype = ctypes.c_int
dll.EU_SetTextOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetTextOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                  ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTextOptions.restype = ctypes.c_int
dll.EU_SetLinkOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetLinkOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                  ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetLinkOptions.restype = ctypes.c_int
dll.EU_SetLinkContent.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetLinkContent.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetLinkContent.restype = ctypes.c_int
dll.EU_SetLinkVisited.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetLinkVisited.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetLinkVisited.restype = ctypes.c_int
dll.EU_SetIconOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_float, ctypes.c_float]
dll.EU_GetIconOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]
dll.EU_GetIconOptions.restype = ctypes.c_int
dll.EU_SetPanelStyle.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_uint32, ctypes.c_uint32,
                                 ctypes.c_float, ctypes.c_float, ctypes.c_int]
dll.EU_GetPanelStyle.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
                                 ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float),
                                 ctypes.POINTER(ctypes.c_int)]
dll.EU_GetPanelStyle.restype = ctypes.c_int
dll.EU_SetPanelLayout.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetPanelLayout.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetPanelLayout.restype = ctypes.c_int
dll.EU_SetContainerLayout.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetContainerLayout.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetContainerLayout.restype = ctypes.c_int
dll.EU_SetContainerRegionTextOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                                 ctypes.c_int, ctypes.c_int]
dll.EU_GetContainerRegionTextOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                                 ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                                 ctypes.POINTER(ctypes.c_int)]
dll.EU_GetContainerRegionTextOptions.restype = ctypes.c_int
dll.EU_SetLayoutOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetLayoutOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                    ctypes.POINTER(ctypes.c_int)]
dll.EU_GetLayoutOptions.restype = ctypes.c_int
dll.EU_SetLayoutChildWeight.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetLayoutChildWeight.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetLayoutChildWeight.restype = ctypes.c_int
dll.EU_SetBorderOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_uint32,
                                    ctypes.c_float, ctypes.c_float,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetBorderOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_uint32),
                                    ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]
dll.EU_GetBorderOptions.restype = ctypes.c_int
dll.EU_SetBorderDashed.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetBorderDashed.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetBorderDashed.restype = ctypes.c_int
dll.EU_SetInfoBoxText.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetInfoBoxOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                     ctypes.c_uint32, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetInfoBoxClosed.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetInfoBoxClosed.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetInfoBoxClosed.restype = ctypes.c_int
dll.EU_GetInfoBoxPreferredHeight.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetInfoBoxPreferredHeight.restype = ctypes.c_int
dll.EU_SetSpaceSize.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetSpaceSize.argtypes = [wintypes.HWND, ctypes.c_int,
                                ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetSpaceSize.restype = ctypes.c_int
dll.EU_SetDividerOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.c_int, ctypes.c_int, ctypes.c_uint32,
                                     ctypes.c_float, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetDividerOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                     ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_float),
                                     ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDividerOptions.restype = ctypes.c_int
dll.EU_SetDividerSpacing.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetDividerSpacing.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDividerSpacing.restype = ctypes.c_int
dll.EU_SetDividerLineStyle.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetDividerLineStyle.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDividerLineStyle.restype = ctypes.c_int
dll.EU_SetDividerContent.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetDividerContent.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetDividerContent.restype = ctypes.c_int
dll.EU_SetButtonEmoji.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetButtonVariant.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetButtonState.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                  ctypes.POINTER(ctypes.c_int)]
dll.EU_GetButtonState.restype = ctypes.c_int
dll.EU_SetButtonOptions.argtypes = [
    wintypes.HWND, ctypes.c_int,
    ctypes.c_int, ctypes.c_int, ctypes.c_int,
    ctypes.c_int, ctypes.c_int, ctypes.c_int,
]
dll.EU_GetButtonOptions.argtypes = [
    wintypes.HWND, ctypes.c_int,
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
]
dll.EU_GetButtonOptions.restype = ctypes.c_int
dll.EU_SetEditBoxText.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetEditBoxOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint32,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetEditBoxOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                     ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_uint32)]
dll.EU_GetEditBoxOptions.restype = ctypes.c_int
dll.EU_GetEditBoxState.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                   ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetEditBoxState.restype = ctypes.c_int

dll.EU_SetWindowResizeCallback.argtypes = [wintypes.HWND, ResizeCallback]
dll.EU_SetWindowCloseCallback.argtypes = [wintypes.HWND, CloseCallback]
dll.EU_SetElementClickCallback.argtypes = [wintypes.HWND, ctypes.c_int, ClickCallback]
dll.EU_SetThemeMode.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_SetThemeMode.restype = None
dll.EU_GetThemeMode.argtypes = [wintypes.HWND]
dll.EU_GetThemeMode.restype = ctypes.c_int
dll.EU_ResetTheme.argtypes = [wintypes.HWND]
dll.EU_ResetTheme.restype = None
dll.EU_SetChromeThemePreset.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_SetThemeToken.argtypes = [wintypes.HWND, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_uint32]
dll.EU_GetThemeToken.argtypes = [wintypes.HWND, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_uint32)]
dll.EU_GetThemeToken.restype = ctypes.c_int
dll.EU_SetHighContrastMode.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_SetIncognitoMode.argtypes = [wintypes.HWND, ctypes.c_int]

dll.EU_GetEditBoxText.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetEditBoxText.restype = ctypes.c_int
dll.EU_SetEditBoxScroll.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetEditBoxScroll.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetEditBoxScroll.restype = ctypes.c_int
dll.EU_SetEditBoxTextCallback.argtypes = [wintypes.HWND, ctypes.c_int, TextCallback]
dll.EU_SetElementFocus.argtypes = [wintypes.HWND, ctypes.c_int]

dll.EU_SetCheckboxChecked.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetCheckboxChecked.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetCheckboxChecked.restype = ctypes.c_int
dll.EU_SetCheckboxIndeterminate.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetCheckboxIndeterminate.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetCheckboxIndeterminate.restype = ctypes.c_int
dll.EU_SetCheckboxOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetCheckboxOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetCheckboxOptions.restype = ctypes.c_int
dll.EU_SetCheckboxGroupItems.argtypes = [wintypes.HWND, ctypes.c_int,
                                         ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetCheckboxGroupValue.argtypes = [wintypes.HWND, ctypes.c_int,
                                         ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetCheckboxGroupValue.argtypes = [wintypes.HWND, ctypes.c_int,
                                         ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetCheckboxGroupValue.restype = ctypes.c_int
dll.EU_SetCheckboxGroupOptions.argtypes = [
    wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
    ctypes.c_int, ctypes.c_int
]
dll.EU_GetCheckboxGroupOptions.argtypes = [
    wintypes.HWND, ctypes.c_int,
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int)
]
dll.EU_GetCheckboxGroupOptions.restype = ctypes.c_int
dll.EU_GetCheckboxGroupState.argtypes = [
    wintypes.HWND, ctypes.c_int,
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)
]
dll.EU_GetCheckboxGroupState.restype = ctypes.c_int
dll.EU_SetCheckboxGroupChangeCallback.argtypes = [wintypes.HWND, ctypes.c_int, ValueCallback]
dll.EU_SetRadioChecked.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetRadioChecked.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetRadioChecked.restype = ctypes.c_int
dll.EU_SetRadioGroup.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetRadioGroup.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetRadioGroup.restype = ctypes.c_int
dll.EU_SetRadioValue.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetRadioValue.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetRadioValue.restype = ctypes.c_int
dll.EU_SetRadioOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetRadioOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetRadioOptions.restype = ctypes.c_int
dll.EU_SetRadioGroupItems.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetRadioGroupValue.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetRadioGroupValue.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetRadioGroupValue.restype = ctypes.c_int
dll.EU_GetRadioGroupSelectedIndex.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetRadioGroupSelectedIndex.restype = ctypes.c_int
dll.EU_SetRadioGroupOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetRadioGroupOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                        ctypes.POINTER(ctypes.c_int)]
dll.EU_GetRadioGroupOptions.restype = ctypes.c_int
dll.EU_GetRadioGroupState.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int)]
dll.EU_GetRadioGroupState.restype = ctypes.c_int
dll.EU_SetRadioGroupChangeCallback.argtypes = [wintypes.HWND, ctypes.c_int, ValueCallback]
dll.EU_SetSwitchChecked.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetSwitchChecked.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSwitchChecked.restype = ctypes.c_int
dll.EU_SetSwitchLoading.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetSwitchLoading.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSwitchLoading.restype = ctypes.c_int
dll.EU_SetSwitchTexts.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetSwitchOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetSwitchOptions.restype = ctypes.c_int
dll.EU_SetSwitchActiveColor.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_uint32]
dll.EU_GetSwitchActiveColor.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSwitchActiveColor.restype = ctypes.c_uint32
dll.EU_SetSwitchInactiveColor.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_uint32]
dll.EU_GetSwitchInactiveColor.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSwitchInactiveColor.restype = ctypes.c_uint32
dll.EU_SetSwitchValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetSwitchValue.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSwitchValue.restype = ctypes.c_int
dll.EU_SetSwitchSize.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetSwitchSize.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSwitchSize.restype = ctypes.c_int
dll.EU_SetSliderRange.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetSliderValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetSliderValue.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSliderValue.restype = ctypes.c_int
dll.EU_SetSliderOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetSliderStep.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSliderStep.restype = ctypes.c_int
dll.EU_GetSliderOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetSliderOptions.restype = ctypes.c_int
dll.EU_SetSliderRangeValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetSliderRangeValue.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetSliderRangeValue.restype = ctypes.c_int
dll.EU_SetSliderRangeMode.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetSliderRangeMode.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int)]
dll.EU_GetSliderRangeMode.restype = ctypes.c_int
dll.EU_SetSliderValueCallback.argtypes = [wintypes.HWND, ctypes.c_int, ValueCallback]
dll.EU_SetInputNumberRange.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetInputNumberStep.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetInputNumberValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetInputNumberValue.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetInputNumberValue.restype = ctypes.c_int
dll.EU_GetInputNumberCanStep.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetInputNumberCanStep.restype = ctypes.c_int
dll.EU_GetInputNumberOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                         ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                         ctypes.POINTER(ctypes.c_int)]
dll.EU_GetInputNumberOptions.restype = ctypes.c_int
dll.EU_SetInputNumberPrecision.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetInputNumberPrecision.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetInputNumberPrecision.restype = ctypes.c_int
dll.EU_SetInputNumberText.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetInputNumberText.restype = ctypes.c_int
dll.EU_GetInputNumberText.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetInputNumberText.restype = ctypes.c_int
dll.EU_GetInputNumberState.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int)]
dll.EU_GetInputNumberState.restype = ctypes.c_int
dll.EU_SetInputNumberValueCallback.argtypes = [wintypes.HWND, ctypes.c_int, ValueCallback]
dll.EU_SetInputNumberStepStrictly.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetInputNumberStepStrictly.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetInputNumberStepStrictly.restype = ctypes.c_int
dll.EU_SetInputValue.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetInputValue.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetInputValue.restype = ctypes.c_int
dll.EU_SetInputPlaceholder.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetInputAffixes.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetInputClearable.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetInputOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetInputState.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                 ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                 ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                 ctypes.POINTER(ctypes.c_int)]
dll.EU_GetInputState.restype = ctypes.c_int
dll.EU_SetInputScroll.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetInputScroll.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                  ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetInputScroll.restype = ctypes.c_int
dll.EU_SetInputMaxLength.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetInputMaxLength.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetInputMaxLength.restype = ctypes.c_int
dll.EU_SetInputTextCallback.argtypes = [wintypes.HWND, ctypes.c_int, TextCallback]
dll.EU_SetInputTagTags.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetInputTagPlaceholder.argtypes = [wintypes.HWND, ctypes.c_int,
                                          ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetInputTagOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetInputTagCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetInputTagCount.restype = ctypes.c_int
dll.EU_GetInputTagOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetInputTagOptions.restype = ctypes.c_int
dll.EU_AddInputTagItem.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_AddInputTagItem.restype = ctypes.c_int
dll.EU_RemoveInputTagItem.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_RemoveInputTagItem.restype = ctypes.c_int
dll.EU_SetInputTagInputValue.argtypes = [wintypes.HWND, ctypes.c_int,
                                         ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetInputTagInputValue.argtypes = [wintypes.HWND, ctypes.c_int,
                                         ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetInputTagInputValue.restype = ctypes.c_int
dll.EU_GetInputTagItem.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetInputTagItem.restype = ctypes.c_int
dll.EU_SetInputTagChangeCallback.argtypes = [wintypes.HWND, ctypes.c_int, TextCallback]
dll.EU_SetSelectOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetSelectIndex.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetSelectIndex.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSelectIndex.restype = ctypes.c_int
dll.EU_SetSelectOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetSelectOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSelectOpen.restype = ctypes.c_int
dll.EU_SetSelectSearch.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetSelectOptionDisabled.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetSelectOptionAlignment.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetSelectOptionAlignment.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSelectOptionAlignment.restype = ctypes.c_int
dll.EU_SetSelectValueAlignment.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetSelectValueAlignment.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSelectValueAlignment.restype = ctypes.c_int
dll.EU_GetSelectOptionCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSelectOptionCount.restype = ctypes.c_int
dll.EU_GetSelectMatchedCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSelectMatchedCount.restype = ctypes.c_int
dll.EU_GetSelectOptionDisabled.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetSelectOptionDisabled.restype = ctypes.c_int
dll.EU_SetSelectMultiple.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetSelectMultiple.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSelectMultiple.restype = ctypes.c_int
dll.EU_SetSelectSelectedIndices.argtypes = [wintypes.HWND, ctypes.c_int,
                                           ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetSelectSelectedCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSelectSelectedCount.restype = ctypes.c_int
dll.EU_GetSelectSelectedAt.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetSelectSelectedAt.restype = ctypes.c_int
dll.EU_SetSelectChangeCallback.argtypes = [wintypes.HWND, ctypes.c_int, ValueCallback]
dll.EU_SetSelectV2Options.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetSelectV2Index.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetSelectV2VisibleCount.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetSelectV2Index.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSelectV2Index.restype = ctypes.c_int
dll.EU_GetSelectV2VisibleCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSelectV2VisibleCount.restype = ctypes.c_int
dll.EU_SetSelectV2Open.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetSelectV2Open.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSelectV2Open.restype = ctypes.c_int
dll.EU_SetSelectV2Search.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetSelectV2OptionDisabled.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetSelectV2OptionAlignment.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetSelectV2OptionAlignment.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSelectV2OptionAlignment.restype = ctypes.c_int
dll.EU_SetSelectV2ValueAlignment.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetSelectV2ValueAlignment.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSelectV2ValueAlignment.restype = ctypes.c_int
dll.EU_GetSelectV2OptionCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSelectV2OptionCount.restype = ctypes.c_int
dll.EU_GetSelectV2MatchedCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSelectV2MatchedCount.restype = ctypes.c_int
dll.EU_GetSelectV2OptionDisabled.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetSelectV2OptionDisabled.restype = ctypes.c_int
dll.EU_SetSelectV2ScrollIndex.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetSelectV2ScrollIndex.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSelectV2ScrollIndex.restype = ctypes.c_int
dll.EU_SetSelectV2ChangeCallback.argtypes = [wintypes.HWND, ctypes.c_int, ValueCallback]
dll.EU_SetRateValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetRateValue.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetRateValue.restype = ctypes.c_int
dll.EU_SetRateMax.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetRateMax.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetRateMax.restype = ctypes.c_int
dll.EU_SetRateValueX2.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetRateValueX2.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetRateValueX2.restype = ctypes.c_int
dll.EU_SetRateOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetRateOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                  ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetRateOptions.restype = ctypes.c_int
dll.EU_SetRateTexts.argtypes = [wintypes.HWND, ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                ctypes.c_int]
dll.EU_SetRateColors.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
dll.EU_GetRateColors.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
                                 ctypes.POINTER(ctypes.c_uint32)]
dll.EU_GetRateColors.restype = ctypes.c_int
dll.EU_SetRateIcons.argtypes = [wintypes.HWND, ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetRateIcons.argtypes = [wintypes.HWND, ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetRateIcons.restype = ctypes.c_int
dll.EU_SetRateTextItems.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetRateDisplayOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                         ctypes.c_int, ctypes.c_int, ctypes.c_uint32,
                                         ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetRateDisplayOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                         ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                         ctypes.POINTER(ctypes.c_uint32),
                                         ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetRateDisplayOptions.restype = ctypes.c_int
dll.EU_SetRateChangeCallback.argtypes = [wintypes.HWND, ctypes.c_int, ValueCallback]
dll.EU_SetColorPickerColor.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_uint32]
dll.EU_GetColorPickerColor.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetColorPickerColor.restype = ctypes.c_uint32
dll.EU_SetColorPickerAlpha.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetColorPickerAlpha.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetColorPickerAlpha.restype = ctypes.c_int
dll.EU_SetColorPickerHex.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetColorPickerHex.restype = ctypes.c_int
dll.EU_GetColorPickerHex.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetColorPickerHex.restype = ctypes.c_int
dll.EU_SetColorPickerOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetColorPickerOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetColorPickerOpen.restype = ctypes.c_int
dll.EU_SetColorPickerPalette.argtypes = [wintypes.HWND, ctypes.c_int,
                                         ctypes.POINTER(ctypes.c_uint32), ctypes.c_int]
dll.EU_GetColorPickerPaletteCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetColorPickerPaletteCount.restype = ctypes.c_int
dll.EU_SetColorPickerOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                         ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetColorPickerOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                         ctypes.POINTER(ctypes.c_int),
                                         ctypes.POINTER(ctypes.c_int),
                                         ctypes.POINTER(ctypes.c_int)]
dll.EU_GetColorPickerOptions.restype = ctypes.c_int
dll.EU_ClearColorPicker.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetColorPickerHasValue.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetColorPickerHasValue.restype = ctypes.c_int
dll.EU_SetColorPickerChangeCallback.argtypes = [wintypes.HWND, ctypes.c_int, ValueCallback]
dll.EU_SetTagType.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTagEffect.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTagClosable.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTagClosed.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetTagClosed.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTagClosed.restype = ctypes.c_int
dll.EU_GetTagOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                 ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTagOptions.restype = ctypes.c_int
dll.EU_SetTagSize.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTagThemeColor.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_uint32]
dll.EU_GetTagVisualOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_uint32)]
dll.EU_GetTagVisualOptions.restype = ctypes.c_int
dll.EU_SetTagCloseCallback.argtypes = [wintypes.HWND, ctypes.c_int, ClickCallback]
dll.EU_SetBadgeValue.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetBadgeMax.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetBadgeType.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetBadgeDot.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetBadgeOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetBadgeHidden.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetBadgeHidden.restype = ctypes.c_int
dll.EU_GetBadgeOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                   ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                   ctypes.POINTER(ctypes.c_int)]
dll.EU_GetBadgeOptions.restype = ctypes.c_int
dll.EU_GetBadgeType.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetBadgeType.restype = ctypes.c_int
dll.EU_SetBadgeLayoutOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetBadgeLayoutOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                         ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetBadgeLayoutOptions.restype = ctypes.c_int
dll.EU_SetProgressPercentage.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetProgressPercentage.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetProgressPercentage.restype = ctypes.c_int
dll.EU_SetProgressStatus.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetProgressStatus.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetProgressStatus.restype = ctypes.c_int
dll.EU_SetProgressShowText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetProgressOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetProgressOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int)]
dll.EU_GetProgressOptions.restype = ctypes.c_int
dll.EU_SetProgressFormatOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetProgressFormatOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetProgressFormatOptions.restype = ctypes.c_int
dll.EU_SetProgressTextInside.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetProgressTextInside.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetProgressTextInside.restype = ctypes.c_int
dll.EU_SetProgressColors.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
dll.EU_GetProgressColors.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
                                     ctypes.POINTER(ctypes.c_uint32)]
dll.EU_GetProgressColors.restype = ctypes.c_int
dll.EU_SetProgressColorStops.argtypes = [wintypes.HWND, ctypes.c_int,
                                         ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetProgressColorStopCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetProgressColorStopCount.restype = ctypes.c_int
dll.EU_GetProgressColorStop.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetProgressColorStop.restype = ctypes.c_int
dll.EU_SetProgressCompleteText.argtypes = [wintypes.HWND, ctypes.c_int,
                                           ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetProgressCompleteText.argtypes = [wintypes.HWND, ctypes.c_int,
                                           ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetProgressCompleteText.restype = ctypes.c_int
dll.EU_SetProgressTextTemplate.argtypes = [wintypes.HWND, ctypes.c_int,
                                           ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetProgressTextTemplate.argtypes = [wintypes.HWND, ctypes.c_int,
                                           ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetProgressTextTemplate.restype = ctypes.c_int
dll.EU_SetAvatarShape.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetAvatarSource.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetAvatarFallbackSource.argtypes = [wintypes.HWND, ctypes.c_int,
                                           ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetAvatarIcon.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetAvatarErrorText.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetAvatarFit.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetAvatarImageStatus.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetAvatarImageStatus.restype = ctypes.c_int
dll.EU_GetAvatarOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetAvatarOptions.restype = ctypes.c_int
dll.EU_SetEmptyDescription.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetEmptyOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetEmptyActionClicked.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetEmptyActionClicked.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetEmptyActionClicked.restype = ctypes.c_int
dll.EU_SetEmptyActionCallback.argtypes = [wintypes.HWND, ctypes.c_int, ClickCallback]
dll.EU_SetEmptyImage.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetEmptyImageSize.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetEmptyImageStatus.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetEmptyImageStatus.restype = ctypes.c_int
dll.EU_GetEmptyImageSize.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetEmptyImageSize.restype = ctypes.c_int
dll.EU_SetSkeletonRows.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetSkeletonAnimated.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetSkeletonLoading.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetSkeletonOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetSkeletonLoading.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSkeletonLoading.restype = ctypes.c_int
dll.EU_GetSkeletonOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetSkeletonOptions.restype = ctypes.c_int
dll.EU_SetDescriptionsItems.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDescriptionsColumns.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetDescriptionsBordered.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetDescriptionsLayout.argtypes = [wintypes.HWND, ctypes.c_int,
                                         ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetDescriptionsItemsEx.argtypes = [wintypes.HWND, ctypes.c_int,
                                          ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDescriptionsOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                          ctypes.c_int, ctypes.c_int,
                                          ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetDescriptionsItemCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDescriptionsItemCount.restype = ctypes.c_int
dll.EU_SetDescriptionsAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetDescriptionsColors.argtypes = [wintypes.HWND, ctypes.c_int,
                                         ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                                         ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
dll.EU_SetDescriptionsExtra.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                        ctypes.c_int, ctypes.c_int]
dll.EU_GetDescriptionsOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                          ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                          ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                          ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                          ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDescriptionsOptions.restype = ctypes.c_int
dll.EU_GetDescriptionsFullState.argtypes = [wintypes.HWND, ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDescriptionsFullState.restype = ctypes.c_int
dll.EU_SetTableData.argtypes = [wintypes.HWND, ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTableStriped.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTableBordered.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTableEmptyText.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTableSelectedRow.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetTableSelectedRow.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTableSelectedRow.restype = ctypes.c_int
dll.EU_GetTableRowCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTableRowCount.restype = ctypes.c_int
dll.EU_GetTableColumnCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTableColumnCount.restype = ctypes.c_int
dll.EU_SetTableOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.c_int, ctypes.c_int,
                                   ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTableSort.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTableScrollRow.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTableColumnWidth.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetTableOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                   ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                   ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                   ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                   ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTableOptions.restype = ctypes.c_int
dll.EU_SetTableColumnsEx.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTableRowsEx.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_AddTableRow.argtypes = [wintypes.HWND, ctypes.c_int,
                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_AddTableRow.restype = ctypes.c_int
dll.EU_InsertTableRow.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_InsertTableRow.restype = ctypes.c_int
dll.EU_DeleteTableRow.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_DeleteTableRow.restype = ctypes.c_int
dll.EU_ClearTableRows.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_ClearTableRows.restype = ctypes.c_int
dll.EU_SetTableCellEx.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTableRowStyle.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                     ctypes.c_uint32, ctypes.c_uint32,
                                     ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTableCellStyle.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                      ctypes.c_uint32, ctypes.c_uint32,
                                      ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTableSelectionMode.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTableSelectedRows.argtypes = [wintypes.HWND, ctypes.c_int,
                                         ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTableFilter.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_ClearTableFilter.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTableSearch.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTableSpan.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                 ctypes.c_int, ctypes.c_int]
dll.EU_ClearTableSpans.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_SetTableSummary.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTableRowExpanded.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTableTreeOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTableViewportOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTableScroll.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTableHeaderDragOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                              ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTableDoubleClickEdit.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTableColumnDoubleClickEdit.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTableCellDoubleClickEdit.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetTableCellDoubleClickEditable.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetTableCellDoubleClickEditable.restype = ctypes.c_int
dll.EU_GetTableDoubleClickEditState.argtypes = [wintypes.HWND, ctypes.c_int,
                                                ctypes.POINTER(ctypes.c_int),
                                                ctypes.POINTER(ctypes.c_int),
                                                ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTableDoubleClickEditState.restype = ctypes.c_int
dll.EU_ExportTableExcel.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int]
dll.EU_ExportTableExcel.restype = ctypes.c_int
dll.EU_ImportTableExcel.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int]
dll.EU_ImportTableExcel.restype = ctypes.c_int
dll.EU_SetTableCellClickCallback.argtypes = [wintypes.HWND, ctypes.c_int, TableCellCallback]
dll.EU_SetTableCellActionCallback.argtypes = [wintypes.HWND, ctypes.c_int, TableCellCallback]
dll.EU_SetTableCellEditCallback.argtypes = [wintypes.HWND, ctypes.c_int, TableCellEditCallback]
dll.EU_SetTableVirtualOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTableVirtualRowProvider.argtypes = [wintypes.HWND, ctypes.c_int, TableVirtualRowCallback]
dll.EU_ClearTableVirtualCache.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTableCellValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTableCellValue.restype = ctypes.c_int
dll.EU_GetTableFullState.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTableFullState.restype = ctypes.c_int
dll.EU_SetCardTitle.argtypes = [wintypes.HWND, ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetCardBody.argtypes = [wintypes.HWND, ctypes.c_int,
                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetCardFooter.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetCardItems.argtypes = [wintypes.HWND, ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetCardActions.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetCardItemCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetCardItemCount.restype = ctypes.c_int
dll.EU_GetCardAction.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetCardAction.restype = ctypes.c_int
dll.EU_ResetCardAction.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_SetCardShadow.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetCardOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetCardStyle.argtypes = [wintypes.HWND, ctypes.c_int,
                                ctypes.c_uint32, ctypes.c_uint32, ctypes.c_float,
                                ctypes.c_float, ctypes.c_int]
dll.EU_GetCardStyle.argtypes = [wintypes.HWND, ctypes.c_int,
                                ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
                                ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float),
                                ctypes.POINTER(ctypes.c_int)]
dll.EU_GetCardStyle.restype = ctypes.c_int
dll.EU_SetCardBodyStyle.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                    ctypes.c_float, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetCardBodyStyle.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                    ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_int),
                                    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetCardBodyStyle.restype = ctypes.c_int
dll.EU_GetCardOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                  ctypes.POINTER(ctypes.c_int)]
dll.EU_GetCardOptions.restype = ctypes.c_int
dll.EU_SetCollapseItems.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetCollapseItemsEx.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetCollapseActive.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetCollapseActive.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetCollapseActive.restype = ctypes.c_int
dll.EU_SetCollapseActiveItems.argtypes = [wintypes.HWND, ctypes.c_int,
                                          ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetCollapseActiveItems.argtypes = [wintypes.HWND, ctypes.c_int,
                                          ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetCollapseActiveItems.restype = ctypes.c_int
dll.EU_GetCollapseItemCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetCollapseItemCount.restype = ctypes.c_int
dll.EU_SetCollapseOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.c_int, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetCollapseAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                              ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                              ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetCollapseOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetCollapseOptions.restype = ctypes.c_int
dll.EU_GetCollapseStateJson.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetCollapseStateJson.restype = ctypes.c_int
dll.EU_SetTimelineItems.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTimelineOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetTimelineItemCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTimelineItemCount.restype = ctypes.c_int
dll.EU_GetTimelineOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTimelineOptions.restype = ctypes.c_int
dll.EU_SetTimelineAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                              ctypes.c_int, ctypes.c_int,
                                              ctypes.c_int, ctypes.c_int]
dll.EU_GetTimelineAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                              ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                              ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTimelineAdvancedOptions.restype = ctypes.c_int
dll.EU_SetStatisticValue.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetStatisticFormat.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetStatisticOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetStatisticOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetStatisticOptions.restype = ctypes.c_int
dll.EU_SetStatisticNumberOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                             ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                             ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                             ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetStatisticAffixOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                                            ctypes.c_int]
dll.EU_SetStatisticDisplayText.argtypes = [wintypes.HWND, ctypes.c_int,
                                           ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetStatisticCountdown.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_longlong,
                                         ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetStatisticCountdownState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_AddStatisticCountdownTime.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_longlong]
dll.EU_SetStatisticFinishCallback.argtypes = [wintypes.HWND, ctypes.c_int, ClickCallback]
dll.EU_SetStatisticSuffixClickCallback.argtypes = [wintypes.HWND, ctypes.c_int, ClickCallback]
dll.EU_GetStatisticFullState.argtypes = [wintypes.HWND, ctypes.c_int,
                                         ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                         ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                         ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                         ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_longlong)]
dll.EU_GetStatisticFullState.restype = ctypes.c_int
dll.EU_SetKpiCardData.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.c_int]
dll.EU_SetKpiCardOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetKpiCardOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetKpiCardOptions.restype = ctypes.c_int
dll.EU_SetTrendData.argtypes = [wintypes.HWND, ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                ctypes.c_int]
dll.EU_SetTrendOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetTrendDirection.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTrendDirection.restype = ctypes.c_int
dll.EU_GetTrendOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTrendOptions.restype = ctypes.c_int
dll.EU_SetStatusDot.argtypes = [wintypes.HWND, ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                ctypes.c_int]
dll.EU_SetStatusDotOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetStatusDotStatus.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetStatusDotStatus.restype = ctypes.c_int
dll.EU_GetStatusDotOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetStatusDotOptions.restype = ctypes.c_int
dll.EU_SetGaugeValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                 ctypes.c_int]
dll.EU_SetGaugeOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                   ctypes.c_int, ctypes.c_int]
dll.EU_GetGaugeValue.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetGaugeValue.restype = ctypes.c_int
dll.EU_GetGaugeStatus.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetGaugeStatus.restype = ctypes.c_int
dll.EU_GetGaugeOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                   ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                   ctypes.POINTER(ctypes.c_int)]
dll.EU_GetGaugeOptions.restype = ctypes.c_int
dll.EU_SetRingProgressValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                        ctypes.c_int]
dll.EU_SetRingProgressOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                          ctypes.c_int, ctypes.c_int]
dll.EU_GetRingProgressValue.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetRingProgressValue.restype = ctypes.c_int
dll.EU_GetRingProgressStatus.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetRingProgressStatus.restype = ctypes.c_int
dll.EU_GetRingProgressOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                          ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetRingProgressOptions.restype = ctypes.c_int
dll.EU_SetBulletProgressValue.argtypes = [wintypes.HWND, ctypes.c_int,
                                          ctypes.c_int, ctypes.c_int,
                                          ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                          ctypes.c_int]
dll.EU_SetBulletProgressOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                            ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetBulletProgressValue.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetBulletProgressValue.restype = ctypes.c_int
dll.EU_GetBulletProgressTarget.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetBulletProgressTarget.restype = ctypes.c_int
dll.EU_GetBulletProgressStatus.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetBulletProgressStatus.restype = ctypes.c_int
dll.EU_GetBulletProgressOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_int),
                                            ctypes.POINTER(ctypes.c_int),
                                            ctypes.POINTER(ctypes.c_int)]
dll.EU_GetBulletProgressOptions.restype = ctypes.c_int
dll.EU_SetLineChartData.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetLineChartSeries.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetLineChartOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetLineChartSelected.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetLineChartPointCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetLineChartPointCount.restype = ctypes.c_int
dll.EU_GetLineChartSeriesCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetLineChartSeriesCount.restype = ctypes.c_int
dll.EU_GetLineChartSelected.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetLineChartSelected.restype = ctypes.c_int
dll.EU_GetLineChartOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetLineChartOptions.restype = ctypes.c_int
dll.EU_SetBarChartData.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetBarChartSeries.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetBarChartOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetBarChartSelected.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetBarChartBarCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetBarChartBarCount.restype = ctypes.c_int
dll.EU_GetBarChartSeriesCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetBarChartSeriesCount.restype = ctypes.c_int
dll.EU_GetBarChartSelected.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetBarChartSelected.restype = ctypes.c_int
dll.EU_GetBarChartOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int)]
dll.EU_GetBarChartOptions.restype = ctypes.c_int
dll.EU_SetDonutChartData.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                     ctypes.c_int]
dll.EU_SetDonutChartOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.c_int, ctypes.c_int]
dll.EU_SetDonutChartAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                                ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetDonutChartActive.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetDonutChartSliceCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDonutChartSliceCount.restype = ctypes.c_int
dll.EU_GetDonutChartActive.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDonutChartActive.restype = ctypes.c_int
dll.EU_GetDonutChartOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDonutChartOptions.restype = ctypes.c_int
dll.EU_GetDonutChartAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                                ctypes.POINTER(ctypes.c_int),
                                                ctypes.POINTER(ctypes.c_int),
                                                ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDonutChartAdvancedOptions.restype = ctypes.c_int
dll.EU_SetCalendarDate.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetCalendarRange.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int]
dll.EU_SetCalendarOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.c_int, ctypes.c_int]
dll.EU_CalendarMoveMonth.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetCalendarValue.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetCalendarValue.restype = ctypes.c_int
dll.EU_GetCalendarRange.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetCalendarRange.restype = ctypes.c_int
dll.EU_GetCalendarOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetCalendarOptions.restype = ctypes.c_int
dll.EU_SetCalendarSelectionRange.argtypes = [wintypes.HWND, ctypes.c_int,
                                             ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetCalendarSelectionRange.argtypes = [wintypes.HWND, ctypes.c_int,
                                             ctypes.POINTER(ctypes.c_int),
                                             ctypes.POINTER(ctypes.c_int),
                                             ctypes.POINTER(ctypes.c_int)]
dll.EU_GetCalendarSelectionRange.restype = ctypes.c_int
dll.EU_SetCalendarDisplayRange.argtypes = [wintypes.HWND, ctypes.c_int,
                                           ctypes.c_int, ctypes.c_int]
dll.EU_GetCalendarDisplayRange.argtypes = [wintypes.HWND, ctypes.c_int,
                                           ctypes.POINTER(ctypes.c_int),
                                           ctypes.POINTER(ctypes.c_int)]
dll.EU_GetCalendarDisplayRange.restype = ctypes.c_int
dll.EU_SetCalendarCellItems.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetCalendarCellItems.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetCalendarCellItems.restype = ctypes.c_int
dll.EU_ClearCalendarCellItems.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_SetCalendarVisualOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                            ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                            ctypes.c_int, ctypes.c_float]
dll.EU_GetCalendarVisualOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_int),
                                            ctypes.POINTER(ctypes.c_int),
                                            ctypes.POINTER(ctypes.c_int),
                                            ctypes.POINTER(ctypes.c_int),
                                            ctypes.POINTER(ctypes.c_float)]
dll.EU_GetCalendarVisualOptions.restype = ctypes.c_int
dll.EU_SetCalendarStateColors.argtypes = [wintypes.HWND, ctypes.c_int,
                                          ctypes.c_uint32, ctypes.c_uint32,
                                          ctypes.c_uint32, ctypes.c_uint32,
                                          ctypes.c_uint32, ctypes.c_uint32,
                                          ctypes.c_uint32]
dll.EU_GetCalendarStateColors.argtypes = [wintypes.HWND, ctypes.c_int,
                                          ctypes.POINTER(ctypes.c_uint32),
                                          ctypes.POINTER(ctypes.c_uint32),
                                          ctypes.POINTER(ctypes.c_uint32),
                                          ctypes.POINTER(ctypes.c_uint32),
                                          ctypes.POINTER(ctypes.c_uint32),
                                          ctypes.POINTER(ctypes.c_uint32),
                                          ctypes.POINTER(ctypes.c_uint32)]
dll.EU_GetCalendarStateColors.restype = ctypes.c_int
dll.EU_SetCalendarSelectedMarker.argtypes = [wintypes.HWND, ctypes.c_int,
                                             ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetCalendarChangeCallback.argtypes = [wintypes.HWND, ctypes.c_int, ValueCallback]
dll.EU_SetTreeItems.argtypes = [wintypes.HWND, ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTreeSelected.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetTreeSelected.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTreeSelected.restype = ctypes.c_int
dll.EU_SetTreeOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetTreeOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                  ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                  ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTreeOptions.restype = ctypes.c_int
dll.EU_SetTreeItemExpanded.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.c_int, ctypes.c_int]
dll.EU_ToggleTreeItemExpanded.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetTreeItemExpanded.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetTreeItemExpanded.restype = ctypes.c_int
dll.EU_SetTreeItemChecked.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.c_int, ctypes.c_int]
dll.EU_GetTreeItemChecked.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetTreeItemChecked.restype = ctypes.c_int
dll.EU_SetTreeItemLazy.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.c_int, ctypes.c_int]
dll.EU_GetTreeItemLazy.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetTreeItemLazy.restype = ctypes.c_int
dll.EU_GetTreeVisibleCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTreeVisibleCount.restype = ctypes.c_int
dll.EU_SetTreeSelectItems.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTreeSelectSelected.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetTreeSelectSelected.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTreeSelectSelected.restype = ctypes.c_int
dll.EU_SetTreeSelectOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetTreeSelectOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTreeSelectOpen.restype = ctypes.c_int
dll.EU_SetTreeSelectOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetTreeSelectOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                        ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                        ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTreeSelectOptions.restype = ctypes.c_int
dll.EU_SetTreeSelectSearch.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTreeSelectSearch.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTreeSelectSearch.restype = ctypes.c_int
dll.EU_ClearTreeSelect.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_SetTreeSelectSelectedItems.argtypes = [wintypes.HWND, ctypes.c_int,
                                              ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTreeSelectSelectedCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTreeSelectSelectedCount.restype = ctypes.c_int
dll.EU_GetTreeSelectSelectedItem.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetTreeSelectSelectedItem.restype = ctypes.c_int
dll.EU_SetTreeSelectItemExpanded.argtypes = [wintypes.HWND, ctypes.c_int,
                                             ctypes.c_int, ctypes.c_int]
dll.EU_ToggleTreeSelectItemExpanded.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetTreeSelectItemExpanded.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetTreeSelectItemExpanded.restype = ctypes.c_int
dll.EU_SetTreeDataJson.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTreeDataJson.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTreeDataJson.restype = ctypes.c_int
dll.EU_SetTreeOptionsJson.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTreeStateJson.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTreeStateJson.restype = ctypes.c_int
dll.EU_SetTreeCheckedKeysJson.argtypes = [wintypes.HWND, ctypes.c_int,
                                          ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTreeCheckedKeysJson.argtypes = [wintypes.HWND, ctypes.c_int,
                                          ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTreeCheckedKeysJson.restype = ctypes.c_int
dll.EU_SetTreeExpandedKeysJson.argtypes = [wintypes.HWND, ctypes.c_int,
                                           ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTreeExpandedKeysJson.argtypes = [wintypes.HWND, ctypes.c_int,
                                           ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTreeExpandedKeysJson.restype = ctypes.c_int
dll.EU_AppendTreeNodeJson.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_UpdateTreeNodeJson.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_RemoveTreeNodeByKey.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTreeNodeEventCallback.argtypes = [wintypes.HWND, ctypes.c_int, TreeNodeEventCallback]
dll.EU_SetTreeLazyLoadCallback.argtypes = [wintypes.HWND, ctypes.c_int, TreeNodeEventCallback]
dll.EU_SetTreeDragCallback.argtypes = [wintypes.HWND, ctypes.c_int, TreeNodeEventCallback]
dll.EU_SetTreeAllowDragCallback.argtypes = [wintypes.HWND, ctypes.c_int, TreeNodeAllowDragCallback]
dll.EU_SetTreeAllowDropCallback.argtypes = [wintypes.HWND, ctypes.c_int, TreeNodeAllowDropCallback]
dll.EU_SetTreeSelectDataJson.argtypes = [wintypes.HWND, ctypes.c_int,
                                         ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTreeSelectDataJson.argtypes = [wintypes.HWND, ctypes.c_int,
                                         ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTreeSelectDataJson.restype = ctypes.c_int
dll.EU_SetTreeSelectOptionsJson.argtypes = [wintypes.HWND, ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTreeSelectStateJson.argtypes = [wintypes.HWND, ctypes.c_int,
                                          ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTreeSelectStateJson.restype = ctypes.c_int
dll.EU_SetTreeSelectSelectedKeysJson.argtypes = [wintypes.HWND, ctypes.c_int,
                                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTreeSelectSelectedKeysJson.argtypes = [wintypes.HWND, ctypes.c_int,
                                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTreeSelectSelectedKeysJson.restype = ctypes.c_int
dll.EU_SetTreeSelectExpandedKeysJson.argtypes = [wintypes.HWND, ctypes.c_int,
                                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTreeSelectExpandedKeysJson.argtypes = [wintypes.HWND, ctypes.c_int,
                                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTreeSelectExpandedKeysJson.restype = ctypes.c_int
dll.EU_AppendTreeSelectNodeJson.argtypes = [wintypes.HWND, ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_UpdateTreeSelectNodeJson.argtypes = [wintypes.HWND, ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_RemoveTreeSelectNodeByKey.argtypes = [wintypes.HWND, ctypes.c_int,
                                             ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTreeSelectNodeEventCallback.argtypes = [wintypes.HWND, ctypes.c_int, TreeNodeEventCallback]
dll.EU_SetTreeSelectLazyLoadCallback.argtypes = [wintypes.HWND, ctypes.c_int, TreeNodeEventCallback]
dll.EU_SetTreeSelectDragCallback.argtypes = [wintypes.HWND, ctypes.c_int, TreeNodeEventCallback]
dll.EU_SetTreeSelectAllowDragCallback.argtypes = [wintypes.HWND, ctypes.c_int, TreeNodeAllowDragCallback]
dll.EU_SetTreeSelectAllowDropCallback.argtypes = [wintypes.HWND, ctypes.c_int, TreeNodeAllowDropCallback]
dll.EU_SetTransferItems.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_TransferMoveRight.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_TransferMoveLeft.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_TransferMoveAllRight.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_TransferMoveAllLeft.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_SetTransferSelected.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.c_int, ctypes.c_int]
dll.EU_GetTransferSelected.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetTransferSelected.restype = ctypes.c_int
dll.EU_GetTransferCount.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetTransferCount.restype = ctypes.c_int
dll.EU_SetTransferFilters.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTransferMatchedCount.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetTransferMatchedCount.restype = ctypes.c_int
dll.EU_SetTransferItemDisabled.argtypes = [wintypes.HWND, ctypes.c_int,
                                           ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetTransferItemDisabled.argtypes = [wintypes.HWND, ctypes.c_int,
                                           ctypes.c_int, ctypes.c_int]
dll.EU_GetTransferItemDisabled.restype = ctypes.c_int
dll.EU_GetTransferDisabledCount.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetTransferDisabledCount.restype = ctypes.c_int
dll.EU_SetTransferDataEx.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTransferOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                      ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetTransferOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTransferOptions.restype = ctypes.c_int
dll.EU_SetTransferTitles.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTransferButtonTexts.argtypes = [wintypes.HWND, ctypes.c_int,
                                          ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                          ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTransferFormat.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTransferItemTemplate.argtypes = [wintypes.HWND, ctypes.c_int,
                                           ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTransferFooterTexts.argtypes = [wintypes.HWND, ctypes.c_int,
                                          ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                          ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTransferFilterPlaceholder.argtypes = [wintypes.HWND, ctypes.c_int,
                                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTransferCheckedKeys.argtypes = [wintypes.HWND, ctypes.c_int,
                                          ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                          ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTransferCheckedCount.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetTransferCheckedCount.restype = ctypes.c_int
dll.EU_GetTransferValueKeys.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTransferValueKeys.restype = ctypes.c_int
dll.EU_GetTransferText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTransferText.restype = ctypes.c_int
dll.EU_SetAutocompleteSuggestions.argtypes = [wintypes.HWND, ctypes.c_int,
                                              ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetAutocompleteValue.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetAutocompletePlaceholder.argtypes = [wintypes.HWND, ctypes.c_int,
                                              ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetAutocompletePlaceholder.argtypes = [wintypes.HWND, ctypes.c_int,
                                              ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetAutocompletePlaceholder.restype = ctypes.c_int
dll.EU_SetAutocompleteIcons.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetAutocompleteIcons.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetAutocompleteIcons.restype = ctypes.c_int
dll.EU_SetAutocompleteBehaviorOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetAutocompleteBehaviorOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                                  ctypes.POINTER(ctypes.c_int)]
dll.EU_GetAutocompleteBehaviorOptions.restype = ctypes.c_int
dll.EU_SetAutocompleteOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetAutocompleteSelected.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetAutocompleteAsyncState.argtypes = [wintypes.HWND, ctypes.c_int,
                                             ctypes.c_int, ctypes.c_int]
dll.EU_SetAutocompleteEmptyText.argtypes = [wintypes.HWND, ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetAutocompleteValue.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetAutocompleteValue.restype = ctypes.c_int
dll.EU_GetAutocompleteOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetAutocompleteOpen.restype = ctypes.c_int
dll.EU_GetAutocompleteSelected.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetAutocompleteSelected.restype = ctypes.c_int
dll.EU_GetAutocompleteSuggestionCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetAutocompleteSuggestionCount.restype = ctypes.c_int
dll.EU_GetAutocompleteOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                          ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                          ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                          ctypes.POINTER(ctypes.c_int)]
dll.EU_GetAutocompleteOptions.restype = ctypes.c_int
dll.EU_SetMentionsValue.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetMentionsSuggestions.argtypes = [wintypes.HWND, ctypes.c_int,
                                          ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetMentionsOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetMentionsSelected.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetMentionsOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                      ctypes.c_int, ctypes.c_int]
dll.EU_SetMentionsFilter.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_InsertMentionsSelected.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetMentionsValue.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetMentionsValue.restype = ctypes.c_int
dll.EU_GetMentionsOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetMentionsOpen.restype = ctypes.c_int
dll.EU_GetMentionsSelected.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetMentionsSelected.restype = ctypes.c_int
dll.EU_GetMentionsSuggestionCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetMentionsSuggestionCount.restype = ctypes.c_int
dll.EU_GetMentionsOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int)]
dll.EU_GetMentionsOptions.restype = ctypes.c_int
dll.EU_SetCascaderOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetCascaderValue.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetCascaderOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetCascaderAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                              ctypes.c_int, ctypes.c_int]
dll.EU_SetCascaderSearch.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetCascaderOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetCascaderOpen.restype = ctypes.c_int
dll.EU_GetCascaderOptionCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetCascaderOptionCount.restype = ctypes.c_int
dll.EU_GetCascaderSelectedDepth.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetCascaderSelectedDepth.restype = ctypes.c_int
dll.EU_GetCascaderLevelCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetCascaderLevelCount.restype = ctypes.c_int
dll.EU_GetCascaderAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                              ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                              ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetCascaderAdvancedOptions.restype = ctypes.c_int
dll.EU_SetDatePickerDate.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetDatePickerRange.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.c_int, ctypes.c_int]
dll.EU_SetDatePickerOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetDatePickerOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_ClearDatePicker.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_DatePickerSelectToday.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDatePickerOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDatePickerOpen.restype = ctypes.c_int
dll.EU_GetDatePickerValue.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDatePickerValue.restype = ctypes.c_int
dll.EU_DatePickerMoveMonth.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetDatePickerRange.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDatePickerRange.restype = ctypes.c_int
dll.EU_GetDatePickerOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                        ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDatePickerOptions.restype = ctypes.c_int
dll.EU_SetDatePickerSelectionRange.argtypes = [wintypes.HWND, ctypes.c_int,
                                               ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetDatePickerSelectionRange.argtypes = [wintypes.HWND, ctypes.c_int,
                                               ctypes.POINTER(ctypes.c_int),
                                               ctypes.POINTER(ctypes.c_int),
                                               ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDatePickerSelectionRange.restype = ctypes.c_int
dll.EU_SetDatePickerPlaceholder.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDatePickerRangeSeparator.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDatePickerFormat.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDatePickerAlign.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetDatePickerMode.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetDatePickerMode.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDatePickerMode.restype = ctypes.c_int
dll.EU_SetDatePickerMultiSelect.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetDatePickerSelectedDates.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetDatePickerSelectedDates.restype = ctypes.c_int
dll.EU_SetDatePickerShortcuts.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDatePickerDisabledDateCallback.argtypes = [wintypes.HWND, ctypes.c_int, DateDisabledCallback]
dll.EU_CreateDateRangePicker.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateDateRangePicker.restype = ctypes.c_int
dll.EU_SetDateRangePickerValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetDateRangePickerValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDateRangePickerValue.restype = ctypes.c_int
dll.EU_SetDateRangePickerRange.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetDateRangePickerPlaceholders.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDateRangePickerSeparator.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDateRangePickerFormat.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetDateRangePickerAlign.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetDateRangePickerShortcuts.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDateRangePickerDisabledDateCallback.argtypes = [wintypes.HWND, ctypes.c_int, DateDisabledCallback]
dll.EU_SetDateRangePickerOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetDateRangePickerOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDateRangePickerOpen.restype = ctypes.c_int
dll.EU_DateRangePickerClear.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_SetTimePickerTime.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.c_int, ctypes.c_int]
dll.EU_SetTimePickerRange.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.c_int, ctypes.c_int]
dll.EU_SetTimePickerOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.c_int, ctypes.c_int]
dll.EU_SetTimePickerOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTimePickerScroll.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetTimePickerOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTimePickerOpen.restype = ctypes.c_int
dll.EU_GetTimePickerValue.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTimePickerValue.restype = ctypes.c_int
dll.EU_GetTimePickerRange.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTimePickerRange.restype = ctypes.c_int
dll.EU_GetTimePickerOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTimePickerOptions.restype = ctypes.c_int
dll.EU_GetTimePickerScroll.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTimePickerScroll.restype = ctypes.c_int
dll.EU_SetTimePickerArrowControl.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetTimePickerArrowControl.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTimePickerArrowControl.restype = ctypes.c_int
dll.EU_SetTimePickerRangeSelect.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTimePickerStartPlaceholder.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTimePickerEndPlaceholder.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTimePickerRangeSeparator.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTimePickerRangeValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTimePickerRangeValue.restype = ctypes.c_int
dll.EU_SetDateTimePickerDateTime.argtypes = [wintypes.HWND, ctypes.c_int,
                                             ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                             ctypes.c_int, ctypes.c_int]
dll.EU_SetDateTimePickerRange.argtypes = [wintypes.HWND, ctypes.c_int,
                                          ctypes.c_int, ctypes.c_int,
                                          ctypes.c_int, ctypes.c_int]
dll.EU_SetDateTimePickerOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                            ctypes.c_int, ctypes.c_int,
                                            ctypes.c_int, ctypes.c_int]
dll.EU_SetDateTimePickerOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_ClearDateTimePicker.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_DateTimePickerSelectToday.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_DateTimePickerSelectNow.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_SetDateTimePickerScroll.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetDateTimePickerOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDateTimePickerOpen.restype = ctypes.c_int
dll.EU_GetDateTimePickerDateValue.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDateTimePickerDateValue.restype = ctypes.c_int
dll.EU_GetDateTimePickerTimeValue.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDateTimePickerTimeValue.restype = ctypes.c_int
dll.EU_DateTimePickerMoveMonth.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetDateTimePickerRange.argtypes = [wintypes.HWND, ctypes.c_int,
                                          ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                          ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDateTimePickerRange.restype = ctypes.c_int
dll.EU_GetDateTimePickerOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDateTimePickerOptions.restype = ctypes.c_int
dll.EU_GetDateTimePickerScroll.argtypes = [wintypes.HWND, ctypes.c_int,
                                           ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDateTimePickerScroll.restype = ctypes.c_int
dll.EU_SetDateTimePickerShortcuts.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDateTimePickerStartPlaceholder.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDateTimePickerEndPlaceholder.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDateTimePickerDefaultTime.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetDateTimePickerRangeDefaultTime.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetDateTimePickerRangeSeparator.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDateTimePickerRangeSelect.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetDateTimePickerRangeValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDateTimePickerRangeValue.restype = ctypes.c_int
dll.EU_SetTimeSelectTime.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.c_int, ctypes.c_int]
dll.EU_SetTimeSelectRange.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.c_int, ctypes.c_int]
dll.EU_SetTimeSelectOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.c_int, ctypes.c_int]
dll.EU_SetTimeSelectOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTimeSelectScroll.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetTimeSelectOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTimeSelectOpen.restype = ctypes.c_int
dll.EU_GetTimeSelectValue.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTimeSelectValue.restype = ctypes.c_int
dll.EU_GetTimeSelectRange.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTimeSelectRange.restype = ctypes.c_int
dll.EU_GetTimeSelectOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTimeSelectOptions.restype = ctypes.c_int
dll.EU_GetTimeSelectState.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTimeSelectState.restype = ctypes.c_int
dll.EU_SetTimeSelectPlaceholder.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDropdownItems.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDropdownSelected.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetDropdownSelected.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDropdownSelected.restype = ctypes.c_int
dll.EU_SetDropdownOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetDropdownOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDropdownOpen.restype = ctypes.c_int
dll.EU_GetDropdownItemCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDropdownItemCount.restype = ctypes.c_int
dll.EU_SetDropdownDisabled.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_int), ctypes.c_int]
dll.EU_GetDropdownState.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                    ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDropdownState.restype = ctypes.c_int
dll.EU_SetDropdownOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                      ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetDropdownOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDropdownOptions.restype = ctypes.c_int
dll.EU_SetDropdownItemMeta.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_int), ctypes.c_int]
dll.EU_GetDropdownItemMeta.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDropdownItemMeta.restype = ctypes.c_int
dll.EU_SetDropdownCommandCallback.argtypes = [wintypes.HWND, ctypes.c_int, DropdownCommandCallback]
dll.EU_SetDropdownMainClickCallback.argtypes = [wintypes.HWND, ctypes.c_int, ClickCallback]
dll.EU_SetMenuItems.argtypes = [wintypes.HWND, ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetMenuActive.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetMenuActive.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetMenuActive.restype = ctypes.c_int
dll.EU_SetMenuOrientation.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetMenuOrientation.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetMenuOrientation.restype = ctypes.c_int
dll.EU_GetMenuItemCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetMenuItemCount.restype = ctypes.c_int
dll.EU_SetMenuExpanded.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_int), ctypes.c_int]
dll.EU_GetMenuState.argtypes = [wintypes.HWND, ctypes.c_int,
                                ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                ctypes.POINTER(ctypes.c_int)]
dll.EU_GetMenuState.restype = ctypes.c_int
dll.EU_GetMenuActivePath.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetMenuActivePath.restype = ctypes.c_int
dll.EU_SetMenuColors.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                                 ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
dll.EU_GetMenuColors.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
                                 ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
                                 ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)]
dll.EU_GetMenuColors.restype = ctypes.c_int
dll.EU_SetMenuCollapsed.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetMenuCollapsed.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetMenuCollapsed.restype = ctypes.c_int
dll.EU_SetMenuItemMeta.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_int), ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetMenuItemMeta.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                   ctypes.POINTER(ctypes.c_int)]
dll.EU_GetMenuItemMeta.restype = ctypes.c_int
dll.EU_SetMenuSelectCallback.argtypes = [wintypes.HWND, ctypes.c_int, MenuSelectCallback]
dll.EU_SetMenuItemIcon.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetMenuItemShortcut.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetMenuItemChecked.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetMenuItemSeparator.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetMenuItemSubmenu.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetMenuPopupPosition.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetContextMenuCallback.argtypes = [wintypes.HWND, ctypes.c_int, ValueCallback]
dll.EU_SetAnchorItems.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetAnchorActive.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetAnchorActive.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetAnchorActive.restype = ctypes.c_int
dll.EU_GetAnchorItemCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetAnchorItemCount.restype = ctypes.c_int
dll.EU_SetAnchorTargets.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_int), ctypes.c_int]
dll.EU_SetAnchorOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetAnchorScroll.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetAnchorState.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                  ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                  ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                  ctypes.POINTER(ctypes.c_int)]
dll.EU_GetAnchorState.restype = ctypes.c_int
dll.EU_SetBacktopState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetBacktopVisible.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetBacktopVisible.restype = ctypes.c_int
dll.EU_GetBacktopState.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                   ctypes.POINTER(ctypes.c_int)]
dll.EU_GetBacktopState.restype = ctypes.c_int
dll.EU_SetBacktopOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                     ctypes.c_int, ctypes.c_int]
dll.EU_SetBacktopScroll.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_TriggerBacktop.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetBacktopFullState.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetBacktopFullState.restype = ctypes.c_int
dll.EU_SetSegmentedItems.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetSegmentedActive.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetSegmentedActive.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSegmentedActive.restype = ctypes.c_int
dll.EU_GetSegmentedItemCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSegmentedItemCount.restype = ctypes.c_int
dll.EU_SetSegmentedDisabled.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_int), ctypes.c_int]
dll.EU_GetSegmentedState.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                     ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetSegmentedState.restype = ctypes.c_int
dll.EU_SetPageHeaderText.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetPageHeaderBreadcrumbs.argtypes = [wintypes.HWND, ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetPageHeaderActions.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetPageHeaderAction.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetPageHeaderAction.restype = ctypes.c_int
dll.EU_SetPageHeaderBackText.argtypes = [wintypes.HWND, ctypes.c_int,
                                         ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetPageHeaderActiveAction.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetPageHeaderBreadcrumbActive.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_TriggerPageHeaderBack.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_ResetPageHeaderResult.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetPageHeaderState.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetPageHeaderState.restype = ctypes.c_int
dll.EU_SetAffixText.argtypes = [wintypes.HWND, ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetAffixState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetAffixFixed.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetAffixFixed.restype = ctypes.c_int
dll.EU_GetAffixState.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                 ctypes.POINTER(ctypes.c_int)]
dll.EU_GetAffixState.restype = ctypes.c_int
dll.EU_SetAffixOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                   ctypes.c_int, ctypes.c_int]
dll.EU_GetAffixOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                   ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                   ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                   ctypes.POINTER(ctypes.c_int)]
dll.EU_GetAffixOptions.restype = ctypes.c_int
dll.EU_SetWatermarkContent.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetWatermarkOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetWatermarkOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetWatermarkOptions.restype = ctypes.c_int
dll.EU_SetWatermarkLayer.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetWatermarkFullOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                           ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                           ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                           ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                           ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                           ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetWatermarkFullOptions.restype = ctypes.c_int
dll.EU_SetTourSteps.argtypes = [wintypes.HWND, ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTourActive.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTourOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTourOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTourTargetElement.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTourMaskBehavior.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetTourActive.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTourActive.restype = ctypes.c_int
dll.EU_GetTourOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTourOpen.restype = ctypes.c_int
dll.EU_GetTourStepCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTourStepCount.restype = ctypes.c_int
dll.EU_GetTourOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                  ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                  ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTourOptions.restype = ctypes.c_int
dll.EU_GetTourFullState.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                    ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTourFullState.restype = ctypes.c_int
dll.EU_SetImageSource.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetImageFit.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetImagePreview.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetImagePreviewEnabled.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetImagePreviewTransform.argtypes = [wintypes.HWND, ctypes.c_int,
                                            ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetImageCacheEnabled.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetImageLazy.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetImagePlaceholder.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                       ctypes.c_uint32, ctypes.c_uint32]
dll.EU_SetImageErrorContent.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                        ctypes.c_uint32, ctypes.c_uint32]
dll.EU_SetImagePreviewList.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                       ctypes.c_int]
dll.EU_SetImagePreviewIndex.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetImageStatus.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetImageStatus.restype = ctypes.c_int
dll.EU_GetImagePreviewOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetImagePreviewOpen.restype = ctypes.c_int
dll.EU_GetImageOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                   ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetImageOptions.restype = ctypes.c_int
dll.EU_GetImageFullOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int)]
dll.EU_GetImageFullOptions.restype = ctypes.c_int
dll.EU_GetImageAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                           ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                           ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                           ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                           ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                           ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetImageAdvancedOptions.restype = ctypes.c_int
dll.EU_SetCarouselItems.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetCarouselActive.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetCarouselOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetCarouselBehavior.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                       ctypes.c_int, ctypes.c_int]
dll.EU_GetCarouselBehavior.argtypes = [
    wintypes.HWND, ctypes.c_int,
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
]
dll.EU_GetCarouselBehavior.restype = ctypes.c_int
dll.EU_SetCarouselVisual.argtypes = [
    wintypes.HWND, ctypes.c_int,
    ctypes.c_uint32, ctypes.c_int, ctypes.c_int,
    ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
    ctypes.c_uint32, ctypes.c_uint32, ctypes.c_int,
]
dll.EU_GetCarouselVisual.argtypes = [
    wintypes.HWND, ctypes.c_int,
    ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
    ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_int),
]
dll.EU_GetCarouselVisual.restype = ctypes.c_int
dll.EU_SetCarouselAutoplay.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.c_int, ctypes.c_int]
dll.EU_SetCarouselAnimation.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_CarouselAdvance.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_CarouselTick.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetCarouselActive.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetCarouselActive.restype = ctypes.c_int
dll.EU_GetCarouselItemCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetCarouselItemCount.restype = ctypes.c_int
dll.EU_GetCarouselOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetCarouselOptions.restype = ctypes.c_int
dll.EU_GetCarouselFullState.argtypes = [
    wintypes.HWND, ctypes.c_int,
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
]
dll.EU_GetCarouselFullState.restype = ctypes.c_int
dll.EU_SetUploadFiles.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetUploadFileItems.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetUploadOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetUploadStyle.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int]
dll.EU_GetUploadStyle.argtypes = [
    wintypes.HWND, ctypes.c_int,
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
]
dll.EU_GetUploadStyle.restype = ctypes.c_int
dll.EU_SetUploadTexts.argtypes = [
    wintypes.HWND, ctypes.c_int,
    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
]
dll.EU_SetUploadConstraints.argtypes = [
    wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int,
    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
]
dll.EU_GetUploadConstraints.argtypes = [
    wintypes.HWND, ctypes.c_int,
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
]
dll.EU_GetUploadConstraints.restype = ctypes.c_int
dll.EU_SetUploadPreviewOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetUploadPreviewState.argtypes = [
    wintypes.HWND, ctypes.c_int,
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
]
dll.EU_GetUploadPreviewState.restype = ctypes.c_int
dll.EU_SetUploadSelectedFiles.argtypes = [wintypes.HWND, ctypes.c_int,
                                          ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetUploadFileStatus.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_RemoveUploadFile.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_RetryUploadFile.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_ClearUploadFiles.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_OpenUploadFileDialog.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_OpenUploadFileDialog.restype = ctypes.c_int
dll.EU_StartUpload.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_StartUpload.restype = ctypes.c_int
dll.EU_GetUploadFileCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetUploadFileCount.restype = ctypes.c_int
dll.EU_GetUploadFileStatus.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetUploadFileStatus.restype = ctypes.c_int
dll.EU_GetUploadSelectedFiles.argtypes = [wintypes.HWND, ctypes.c_int,
                                          ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetUploadSelectedFiles.restype = ctypes.c_int
dll.EU_GetUploadFileName.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetUploadFileName.restype = ctypes.c_int
dll.EU_GetUploadFullState.argtypes = [
    wintypes.HWND, ctypes.c_int,
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
]
dll.EU_GetUploadFullState.restype = ctypes.c_int
dll.EU_SetUploadSelectCallback.argtypes = [wintypes.HWND, ctypes.c_int, TextCallback]
dll.EU_SetUploadActionCallback.argtypes = [wintypes.HWND, ctypes.c_int, ValueCallback]
dll.EU_SetInfiniteScrollItems.argtypes = [wintypes.HWND, ctypes.c_int,
                                          ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_AppendInfiniteScrollItems.argtypes = [wintypes.HWND, ctypes.c_int,
                                             ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_ClearInfiniteScrollItems.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_SetInfiniteScrollState.argtypes = [wintypes.HWND, ctypes.c_int,
                                          ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetInfiniteScrollOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                            ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                            ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetInfiniteScrollTexts.argtypes = [
    wintypes.HWND, ctypes.c_int,
    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
]
dll.EU_SetInfiniteScrollScroll.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetInfiniteScrollFullState.argtypes = [
    wintypes.HWND, ctypes.c_int,
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
]
dll.EU_GetInfiniteScrollFullState.restype = ctypes.c_int
dll.EU_SetInfiniteScrollLoadCallback.argtypes = [wintypes.HWND, ctypes.c_int, ValueCallback]
dll.EU_SetBreadcrumbItems.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetBreadcrumbSeparator.argtypes = [wintypes.HWND, ctypes.c_int,
                                          ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetBreadcrumbCurrent.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_TriggerBreadcrumbClick.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetBreadcrumbCurrent.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetBreadcrumbCurrent.restype = ctypes.c_int
dll.EU_GetBreadcrumbItemCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetBreadcrumbItemCount.restype = ctypes.c_int
dll.EU_GetBreadcrumbState.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetBreadcrumbState.restype = ctypes.c_int
dll.EU_GetBreadcrumbItem.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetBreadcrumbItem.restype = ctypes.c_int
dll.EU_GetBreadcrumbFullState.argtypes = [
    wintypes.HWND, ctypes.c_int,
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
]
dll.EU_GetBreadcrumbFullState.restype = ctypes.c_int
dll.EU_SetBreadcrumbSelectCallback.argtypes = [wintypes.HWND, ctypes.c_int, ValueCallback]
dll.EU_SetTabsItems.argtypes = [wintypes.HWND, ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTabsItemsEx.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTabsActive.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTabsActiveName.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTabsType.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTabsPosition.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTabsHeaderAlign.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTabsOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTabsEditable.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTabsContentVisible.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_AddTabsItem.argtypes = [wintypes.HWND, ctypes.c_int,
                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_CloseTabsItem.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTabsScroll.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_TabsScroll.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetTabsActive.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTabsActive.restype = ctypes.c_int
dll.EU_GetTabsHeaderAlign.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTabsHeaderAlign.restype = ctypes.c_int
dll.EU_GetTabsItemCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTabsItemCount.restype = ctypes.c_int
dll.EU_GetTabsState.argtypes = [wintypes.HWND, ctypes.c_int,
                                ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTabsState.restype = ctypes.c_int
dll.EU_GetTabsItem.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTabsItem.restype = ctypes.c_int
dll.EU_GetTabsActiveName.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTabsActiveName.restype = ctypes.c_int
dll.EU_GetTabsItemContent.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTabsItemContent.restype = ctypes.c_int
dll.EU_GetTabsFullState.argtypes = [
    wintypes.HWND, ctypes.c_int,
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
]
dll.EU_GetTabsFullState.restype = ctypes.c_int
dll.EU_GetTabsFullStateEx.argtypes = dll.EU_GetTabsFullState.argtypes + [
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
]
dll.EU_GetTabsFullStateEx.restype = ctypes.c_int
dll.EU_SetTabsChangeCallback.argtypes = [wintypes.HWND, ctypes.c_int, ValueCallback]
dll.EU_SetTabsCloseCallback.argtypes = [wintypes.HWND, ctypes.c_int, ValueCallback]
dll.EU_SetTabsAddCallback.argtypes = [wintypes.HWND, ctypes.c_int, ValueCallback]
dll.EU_SetPagination.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetPaginationCurrent.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetPaginationPageSize.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetPaginationOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetPaginationAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                                ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetPaginationPageSizeOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                                ctypes.POINTER(ctypes.c_int), ctypes.c_int]
dll.EU_SetPaginationJumpPage.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_TriggerPaginationJump.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_NextPaginationPageSize.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetPaginationCurrent.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetPaginationCurrent.restype = ctypes.c_int
dll.EU_GetPaginationPageCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetPaginationPageCount.restype = ctypes.c_int
dll.EU_GetPaginationState.argtypes = [wintypes.HWND, ctypes.c_int,
                                ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetPaginationState.restype = ctypes.c_int
dll.EU_GetPaginationFullState.argtypes = [
    wintypes.HWND, ctypes.c_int,
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
]
dll.EU_GetPaginationFullState.restype = ctypes.c_int
dll.EU_GetPaginationAdvancedOptions.argtypes = [
    wintypes.HWND, ctypes.c_int,
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
]
dll.EU_GetPaginationAdvancedOptions.restype = ctypes.c_int
dll.EU_SetPaginationChangeCallback.argtypes = [wintypes.HWND, ctypes.c_int, ValueCallback]
dll.EU_SetStepsItems.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetStepsDetailItems.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetStepsIconItems.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetStepsActive.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetStepsDirection.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetStepsOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int]
dll.EU_GetStepsOptions.argtypes = [
    wintypes.HWND, ctypes.c_int,
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
]
dll.EU_GetStepsOptions.restype = ctypes.c_int
dll.EU_SetStepsStatuses.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_int), ctypes.c_int]
dll.EU_TriggerStepsClick.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetStepsActive.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetStepsActive.restype = ctypes.c_int
dll.EU_GetStepsItemCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetStepsItemCount.restype = ctypes.c_int
dll.EU_GetStepsState.argtypes = [wintypes.HWND, ctypes.c_int,
                                ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                ctypes.POINTER(ctypes.c_int)]
dll.EU_GetStepsState.restype = ctypes.c_int
dll.EU_GetStepsItem.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetStepsItem.restype = ctypes.c_int
dll.EU_GetStepsFullState.argtypes = [
    wintypes.HWND, ctypes.c_int,
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
]
dll.EU_GetStepsFullState.restype = ctypes.c_int
dll.EU_GetStepsVisualState.argtypes = [
    wintypes.HWND, ctypes.c_int,
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
]
dll.EU_GetStepsVisualState.restype = ctypes.c_int
dll.EU_SetStepsChangeCallback.argtypes = [wintypes.HWND, ctypes.c_int, ValueCallback]
dll.EU_SetAlertDescription.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetAlertType.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetAlertEffect.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetAlertClosable.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetAlertAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                           ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetAlertAdvancedOptions.argtypes = [
    wintypes.HWND, ctypes.c_int,
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
]
dll.EU_GetAlertAdvancedOptions.restype = ctypes.c_int
dll.EU_SetAlertCloseText.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetAlertText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetAlertText.restype = ctypes.c_int
dll.EU_SetAlertClosed.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_TriggerAlertClose.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetAlertClosed.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetAlertClosed.restype = ctypes.c_int
dll.EU_GetAlertOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                   ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetAlertOptions.restype = ctypes.c_int
dll.EU_GetAlertFullState.argtypes = [
    wintypes.HWND, ctypes.c_int,
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
]
dll.EU_GetAlertFullState.restype = ctypes.c_int
dll.EU_SetAlertCloseCallback.argtypes = [wintypes.HWND, ctypes.c_int, ValueCallback]
dll.EU_SetResultSubtitle.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetResultType.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetResultActions.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetResultAction.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetResultAction.restype = ctypes.c_int
dll.EU_GetResultOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                    ctypes.POINTER(ctypes.c_int)]
dll.EU_GetResultOptions.restype = ctypes.c_int
dll.EU_SetResultExtraContent.argtypes = [wintypes.HWND, ctypes.c_int,
                                         ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_TriggerResultAction.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetResultText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetResultText.restype = ctypes.c_int
dll.EU_GetResultActionText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetResultActionText.restype = ctypes.c_int
dll.EU_GetResultFullState.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetResultFullState.restype = ctypes.c_int
dll.EU_SetResultActionCallback.argtypes = [wintypes.HWND, ctypes.c_int, ValueCallback]
dll.EU_SetMessageBoxBeforeClose.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetMessageBoxInput.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetMessageBoxInput.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetMessageBoxInput.restype = ctypes.c_int
dll.EU_GetMessageBoxFullState.argtypes = [wintypes.HWND, ctypes.c_int,
                                          ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                          ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                          ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                          ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                          ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetMessageBoxFullState.restype = ctypes.c_int
dll.EU_SetMessageText.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetMessageOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                     ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetMessageClosed.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetMessageOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                     ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                     ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                     ctypes.POINTER(ctypes.c_int)]
dll.EU_GetMessageOptions.restype = ctypes.c_int
dll.EU_GetMessageFullState.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int)]
dll.EU_GetMessageFullState.restype = ctypes.c_int
dll.EU_TriggerMessageClose.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_SetMessageCloseCallback.argtypes = [wintypes.HWND, ctypes.c_int, ValueCallback]
dll.EU_SetNotificationBody.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetNotificationType.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetNotificationClosable.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetNotificationPlacement.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetNotificationRichMode.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetNotificationOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                          ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetNotificationClosed.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetNotificationClosed.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetNotificationClosed.restype = ctypes.c_int
dll.EU_GetNotificationOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                          ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                          ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetNotificationOptions.restype = ctypes.c_int
dll.EU_SetNotificationStack.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_TriggerNotificationClose.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetNotificationText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetNotificationText.restype = ctypes.c_int
dll.EU_GetNotificationFullState.argtypes = [wintypes.HWND, ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetNotificationFullState.restype = ctypes.c_int
dll.EU_GetNotificationFullStateEx.argtypes = [wintypes.HWND, ctypes.c_int,
                                              ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                              ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                              ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                              ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                              ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                              ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                              ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                              ctypes.POINTER(ctypes.c_int)]
dll.EU_GetNotificationFullStateEx.restype = ctypes.c_int
dll.EU_SetNotificationCloseCallback.argtypes = [wintypes.HWND, ctypes.c_int, ValueCallback]
dll.EU_SetLoadingActive.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetLoadingText.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetLoadingOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetLoadingStyle.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                                   ctypes.c_int, ctypes.c_int]
dll.EU_GetLoadingActive.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetLoadingActive.restype = ctypes.c_int
dll.EU_GetLoadingOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                     ctypes.POINTER(ctypes.c_int)]
dll.EU_GetLoadingOptions.restype = ctypes.c_int
dll.EU_SetLoadingTarget.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetLoadingText.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetLoadingText.restype = ctypes.c_int
dll.EU_GetLoadingStyle.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
                                   ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_int),
                                   ctypes.POINTER(ctypes.c_int)]
dll.EU_GetLoadingStyle.restype = ctypes.c_int
dll.EU_ShowLoading.argtypes = [wintypes.HWND, ctypes.c_int,
                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                               ctypes.c_int, ctypes.c_int,
                               ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                               ctypes.c_int]
dll.EU_ShowLoading.restype = ctypes.c_int
dll.EU_CloseLoading.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_CloseLoading.restype = ctypes.c_int
dll.EU_GetLoadingFullState.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int)]
dll.EU_GetLoadingFullState.restype = ctypes.c_int
dll.EU_SetDialogOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetDialogTitle.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDialogBody.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDialogOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int]
dll.EU_SetDialogAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                            ctypes.c_int, ctypes.c_int,
                                            ctypes.c_int, ctypes.c_int,
                                            ctypes.c_int, ctypes.c_int]
dll.EU_GetDialogAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                            ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDialogAdvancedOptions.restype = ctypes.c_int
dll.EU_GetDialogContentParent.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDialogContentParent.restype = ctypes.c_int
dll.EU_GetDialogFooterParent.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDialogFooterParent.restype = ctypes.c_int
dll.EU_SetDialogBeforeCloseCallback.argtypes = [wintypes.HWND, ctypes.c_int, BeforeCloseCallback]
dll.EU_ConfirmDialogClose.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetDialogOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDialogOpen.restype = ctypes.c_int
dll.EU_GetDialogOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                    ctypes.POINTER(ctypes.c_int),
                                    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDialogOptions.restype = ctypes.c_int
dll.EU_SetDialogButtons.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_TriggerDialogButton.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetDialogText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetDialogText.restype = ctypes.c_int
dll.EU_GetDialogButtonText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetDialogButtonText.restype = ctypes.c_int
dll.EU_GetDialogFullState.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDialogFullState.restype = ctypes.c_int
dll.EU_SetDialogButtonCallback.argtypes = [wintypes.HWND, ctypes.c_int, ValueCallback]
dll.EU_SetDrawerOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetDrawerTitle.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDrawerBody.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDrawerPlacement.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetDrawerOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int]
dll.EU_SetDrawerAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                            ctypes.c_int, ctypes.c_int,
                                            ctypes.c_int, ctypes.c_int,
                                            ctypes.c_int, ctypes.c_int,
                                            ctypes.c_int]
dll.EU_GetDrawerAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDrawerAdvancedOptions.restype = ctypes.c_int
dll.EU_GetDrawerContentParent.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDrawerContentParent.restype = ctypes.c_int
dll.EU_GetDrawerFooterParent.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDrawerFooterParent.restype = ctypes.c_int
dll.EU_SetDrawerBeforeCloseCallback.argtypes = [wintypes.HWND, ctypes.c_int, BeforeCloseCallback]
dll.EU_ConfirmDrawerClose.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetDrawerOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDrawerOpen.restype = ctypes.c_int
dll.EU_GetDrawerOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDrawerOptions.restype = ctypes.c_int
dll.EU_SetDrawerAnimation.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_TriggerDrawerClose.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDrawerText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetDrawerText.restype = ctypes.c_int
dll.EU_GetDrawerFullState.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDrawerFullState.restype = ctypes.c_int
dll.EU_SetDrawerCloseCallback.argtypes = [wintypes.HWND, ctypes.c_int, ValueCallback]
dll.EU_SetTooltipContent.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTooltipOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTooltipOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetTooltipOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTooltipOpen.restype = ctypes.c_int
dll.EU_GetTooltipOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                     ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTooltipOptions.restype = ctypes.c_int
dll.EU_SetTooltipBehavior.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.c_int, ctypes.c_int,
                                      ctypes.c_int, ctypes.c_int]
dll.EU_SetTooltipAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                             ctypes.c_int, ctypes.c_int,
                                             ctypes.c_int, ctypes.c_int,
                                             ctypes.c_int, ctypes.c_int]
dll.EU_GetTooltipAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                             ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                             ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                             ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTooltipAdvancedOptions.restype = ctypes.c_int
dll.EU_TriggerTooltip.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetTooltipText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTooltipText.restype = ctypes.c_int
dll.EU_GetTooltipFullState.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTooltipFullState.restype = ctypes.c_int
dll.EU_SetPopoverOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetPopoverContent.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetPopoverTitle.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetPopoverOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.c_int, ctypes.c_int,
                                     ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetPopoverAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                             ctypes.c_int, ctypes.c_int,
                                             ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetPopoverBehavior.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.c_int, ctypes.c_int,
                                      ctypes.c_int, ctypes.c_int]
dll.EU_GetPopoverBehavior.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetPopoverBehavior.restype = ctypes.c_int
dll.EU_GetPopoverContentParent.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetPopoverContentParent.restype = ctypes.c_int
dll.EU_GetPopoverOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetPopoverOpen.restype = ctypes.c_int
dll.EU_GetPopoverOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                     ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                     ctypes.POINTER(ctypes.c_int)]
dll.EU_GetPopoverOptions.restype = ctypes.c_int
dll.EU_TriggerPopover.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetPopoverText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetPopoverText.restype = ctypes.c_int
dll.EU_GetPopoverFullState.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetPopoverFullState.restype = ctypes.c_int
dll.EU_SetPopoverActionCallback.argtypes = [wintypes.HWND, ctypes.c_int, ValueCallback]
dll.EU_SetPopoverAnchorElement.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetPopoverArrow.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetPopoverElevation.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetPopoverAutoPlacement.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetPopoverDismissBehavior.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetPopupAnchorElement.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetPopupPlacement.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetPopupOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetPopupOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetPopupOpen.restype = ctypes.c_int
dll.EU_SetPopupDismissBehavior.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetElementPopup.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_ClearElementPopup.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetElementPopup.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetElementPopup.restype = ctypes.c_int
dll.EU_SetPopconfirmOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]

# Chrome shell extensions
dll.EU_SetIconButtonIcon.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetIconButtonTooltip.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetIconButtonBadge.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int]
dll.EU_SetIconButtonChecked.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetIconButtonChecked.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetIconButtonChecked.restype = ctypes.c_int
dll.EU_SetIconButtonDropdown.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetIconButtonColors.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                                       ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
dll.EU_SetIconButtonShape.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetIconButtonPadding.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                        ctypes.c_int, ctypes.c_int]
dll.EU_SetIconButtonIconSize.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetIconButtonState.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetIconButtonState.restype = ctypes.c_int

dll.EU_SetTabsChromeMode.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetTabsChromeMode.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTabsChromeMode.restype = ctypes.c_int
dll.EU_SetTabsItemIcon.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTabsItemLoading.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTabsItemPinned.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTabsItemMuted.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTabsItemClosable.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTabsItemChromeState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                          ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetTabsItemChromeState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                          ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                          ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTabsItemChromeState.restype = ctypes.c_int
dll.EU_SetTabsChromeMetrics.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                        ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTabsNewButtonVisible.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTabsDragOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTabsReorderCallback.argtypes = [wintypes.HWND, ctypes.c_int, ReorderCallback]

dll.EU_SetOmniboxValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetOmniboxValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetOmniboxValue.restype = ctypes.c_int
dll.EU_SetOmniboxPlaceholder.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetOmniboxSecurityState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                           ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetOmniboxPrefixChip.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                        ctypes.c_uint32, ctypes.c_uint32]
dll.EU_SetOmniboxActionIcons.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetOmniboxSuggestionItems.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetOmniboxSuggestionOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetOmniboxSuggestionSelected.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetOmniboxSuggestionState.argtypes = [wintypes.HWND, ctypes.c_int,
                                             ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                             ctypes.POINTER(ctypes.c_int)]
dll.EU_GetOmniboxSuggestionState.restype = ctypes.c_int
dll.EU_SetOmniboxCommitCallback.argtypes = [wintypes.HWND, ctypes.c_int, TextCallback]
dll.EU_SetOmniboxIconButtonCallback.argtypes = [wintypes.HWND, ctypes.c_int, ValueCallback]

dll.EU_SetTitleBarVisible.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_SetTitleBarHeight.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_SetTitleBarButtonStyle.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                          ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
dll.EU_GetWindowFrameFlags.argtypes = [wintypes.HWND]
dll.EU_GetWindowFrameFlags.restype = ctypes.c_int
dll.EU_SetWindowFrameFlags.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_SetWindowResizeBorder.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                         ctypes.c_int, ctypes.c_int]
dll.EU_GetWindowResizeBorder.argtypes = [wintypes.HWND, ctypes.POINTER(ctypes.c_int),
                                         ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                         ctypes.POINTER(ctypes.c_int)]
dll.EU_GetWindowResizeBorder.restype = ctypes.c_int
dll.EU_SetWindowDragRegion.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                       ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_ClearWindowDragRegions.argtypes = [wintypes.HWND]
dll.EU_SetWindowNoDragRegion.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                         ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_ClearWindowNoDragRegions.argtypes = [wintypes.HWND]
dll.EU_SetElementWindowCommand.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetElementWindowCommand.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetElementWindowCommand.restype = ctypes.c_int
dll.EU_SetWindowCaptionButtonBounds.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                               ctypes.c_int, ctypes.c_int]
dll.EU_SetWindowRoundedCorners.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetContainerFlexLayout.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                          ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetElementFlexGrow.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetElementMinMaxSize.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                        ctypes.c_int, ctypes.c_int]
dll.EU_SetElementMargin.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int]
dll.EU_SetElementAlignSelf.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]

dll.EU_SetBrowserViewportState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetBrowserViewportPlaceholder.argtypes = [wintypes.HWND, ctypes.c_int,
                                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetBrowserViewportLoading.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetBrowserViewportScreenshot.argtypes = [wintypes.HWND, ctypes.c_int,
                                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetBrowserViewportState.argtypes = [wintypes.HWND, ctypes.c_int,
                                           ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                           ctypes.POINTER(ctypes.c_int)]
dll.EU_GetBrowserViewportState.restype = ctypes.c_int
dll.EU_SetPopconfirmOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.c_int, ctypes.c_int,
                                        ctypes.c_int, ctypes.c_int]
dll.EU_SetPopconfirmAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                                ctypes.c_int, ctypes.c_int,
                                                ctypes.c_int, ctypes.c_int,
                                                ctypes.c_int, ctypes.c_int,
                                                ctypes.c_int, ctypes.c_int]
dll.EU_SetPopconfirmContent.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetPopconfirmButtons.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetPopconfirmIcon.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                     ctypes.c_uint32, ctypes.c_int]
dll.EU_GetPopconfirmIcon.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetPopconfirmIcon.restype = ctypes.c_int
dll.EU_ResetPopconfirmResult.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetPopconfirmOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetPopconfirmOpen.restype = ctypes.c_int
dll.EU_GetPopconfirmResult.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetPopconfirmResult.restype = ctypes.c_int
dll.EU_GetPopconfirmOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                        ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                        ctypes.POINTER(ctypes.c_int)]
dll.EU_GetPopconfirmOptions.restype = ctypes.c_int
dll.EU_TriggerPopconfirmResult.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetPopconfirmText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetPopconfirmText.restype = ctypes.c_int
dll.EU_GetPopconfirmFullState.argtypes = [wintypes.HWND, ctypes.c_int,
                                          ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                          ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                          ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                          ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                          ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                          ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                          ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                          ctypes.POINTER(ctypes.c_int)]
dll.EU_GetPopconfirmFullState.restype = ctypes.c_int
dll.EU_SetPopconfirmResultCallback.argtypes = [wintypes.HWND, ctypes.c_int, ValueCallback]

# 鈹€鈹€ Helpers 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

def make_utf8(text: str) -> bytes:
    return text.encode('utf-8')

def bytes_arg(data: bytes):
    if not data:
        return None
    return (ctypes.c_ubyte * len(data))(*data)

def json_bytes(value) -> bytes:
    if value is None:
        value = {}
    if isinstance(value, bytes):
        return value
    if isinstance(value, bytearray):
        return bytes(value)
    if isinstance(value, str):
        return make_utf8(value)
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

def read_json_result(fn, hwnd, element_id):
    needed = fn(hwnd, element_id, None, 0)
    if needed <= 0:
        return {}
    buf = (ctypes.c_ubyte * (needed + 1))()
    copied = fn(hwnd, element_id, buf, needed + 1)
    text = bytes(buf[:min(copied, needed)]).decode("utf-8", errors="replace")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text

def tree_callback_payload(payload_ptr, payload_len):
    if not payload_ptr or payload_len <= 0:
        return {}
    text = bytes(payload_ptr[:payload_len]).decode("utf-8", errors="replace")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text

_tree_callback_refs = {}

def _callback_key(hwnd, element_id, name):
    return (int(hwnd) if hwnd else 0, int(element_id), name)

def _wrap_callback(factory, callback):
    if callback is None:
        return None
    if isinstance(callback, ctypes._CFuncPtr):
        return callback
    return factory(callback)

def _extended_placement_value(placement, default="bottom"):
    if isinstance(placement, str):
        return EXTENDED_PLACEMENTS.get(placement, EXTENDED_PLACEMENTS[default])
    try:
        value = int(placement)
    except (TypeError, ValueError):
        value = EXTENDED_PLACEMENTS[default]
    return max(0, min(11, value))

def _trigger_mode_value(trigger_mode, default="click"):
    if isinstance(trigger_mode, str):
        return TRIGGER_MODES.get(trigger_mode, TRIGGER_MODES[default])
    try:
        value = int(trigger_mode)
    except (TypeError, ValueError):
        value = TRIGGER_MODES[default]
    return max(0, min(3, value))

def _carousel_enum_value(value, mapping, default):
    if isinstance(value, str):
        return mapping.get(value, mapping[default])
    try:
        raw = int(value)
    except (TypeError, ValueError):
        raw = mapping[default]
    return max(0, min(max(mapping.values()), raw))

def _carousel_trigger_value(value):
    return _carousel_enum_value(value, CAROUSEL_TRIGGER_MODES, "click")

def _carousel_arrow_value(value):
    return _carousel_enum_value(value, CAROUSEL_ARROW_MODES, "always")

def _carousel_direction_value(value):
    return _carousel_enum_value(value, CAROUSEL_DIRECTIONS, "horizontal")

def _carousel_type_value(value):
    return _carousel_enum_value(value, CAROUSEL_TYPES, "normal")

def _autocomplete_suggestions_data(suggestions):
    if suggestions is None:
        suggestions = ["北京", "上海", "广州", "深圳"]
    rows = []
    for item in suggestions:
        if isinstance(item, (list, tuple)):
            if not item:
                continue
            title = str(item[0])
            subtitle = str(item[1]) if len(item) >= 2 else ""
            write_value = str(item[2]) if len(item) >= 3 else title
            rows.append("\t".join([title, subtitle, write_value]))
        else:
            rows.append(str(item))
    return make_utf8("\n".join(rows))

def _input_group_select_items_data(items):
    rows = []
    for item in items or []:
        if isinstance(item, (list, tuple)):
            label = str(item[0]) if len(item) >= 1 else ""
            value = str(item[1]) if len(item) >= 2 else label
        else:
            label = str(item)
            value = label
        if label:
            rows.append(f"{label}\t{value}")
    return make_utf8("\n".join(rows))

def create_window(title="New Emoji Test", x=300, y=200, w=800, h=600):
    data = make_utf8(title)
    hwnd = dll.EU_CreateWindow(
        (ctypes.c_ubyte * len(data))(*data), len(data),
        x, y, w, h,
        0xFF181825  # titlebar color
    )
    return hwnd

def create_window_ex(title="New Emoji Test", x=300, y=200, w=800, h=600,
                     titlebar_color=0xFF181825, frame_flags=EU_WINDOW_FRAME_DEFAULT):
    data = make_utf8(title)
    return dll.EU_CreateWindowEx(
        (ctypes.c_ubyte * len(data))(*data), len(data),
        x, y, w, h,
        titlebar_color,
        frame_flags,
    )

def set_window_icon(hwnd, icon_path):
    data = make_utf8(os.fspath(icon_path))
    return bool(dll.EU_SetWindowIcon(hwnd, bytes_arg(data), len(data)))

def set_window_icon_from_bytes(hwnd, icon_bytes):
    data = bytes(icon_bytes or b"")
    return bool(dll.EU_SetWindowIconFromBytes(hwnd, bytes_arg(data), len(data)))

def create_borderless_window(title="无标题栏窗口", x=300, y=200, w=800, h=600):
    flags = (
        EU_WINDOW_FRAME_BORDERLESS |
        EU_WINDOW_FRAME_CUSTOM_CAPTION |
        EU_WINDOW_FRAME_CUSTOM_BUTTONS |
        EU_WINDOW_FRAME_RESIZABLE |
        EU_WINDOW_FRAME_ROUNDED |
        EU_WINDOW_FRAME_HIDE_TITLEBAR
    )
    return create_window_ex(title, x, y, w, h, 0xFF181825, flags)

def create_browser_shell_window(title="浏览器式窗口", x=300, y=200, w=1000, h=700):
    return create_window_ex(title, x, y, w, h, 0xFF181825, EU_WINDOW_FRAME_BROWSER_SHELL)

def set_titlebar_visible(hwnd, visible=True):
    dll.EU_SetTitleBarVisible(hwnd, 1 if visible else 0)

def set_titlebar_height(hwnd, height=32):
    dll.EU_SetTitleBarHeight(hwnd, height)

def set_titlebar_button_style(hwnd, button_width=46, button_height=32,
                              icon_color=0xFF5F6368, hover_bg=0x14000000,
                              close_hover_bg=0xFFE81123):
    dll.EU_SetTitleBarButtonStyle(hwnd, button_width, button_height, icon_color, hover_bg, close_hover_bg)

def set_window_drag_region(hwnd, x, y, w, h, enabled=True):
    dll.EU_SetWindowDragRegion(hwnd, x, y, w, h, 1 if enabled else 0)

def clear_window_drag_regions(hwnd):
    dll.EU_ClearWindowDragRegions(hwnd)

def set_window_caption_button_bounds(hwnd, x, y, w, h):
    dll.EU_SetWindowCaptionButtonBounds(hwnd, x, y, w, h)

def set_window_rounded_corners(hwnd, enabled=True, radius=8):
    dll.EU_SetWindowRoundedCorners(hwnd, 1 if enabled else 0, radius)

def get_window_frame_flags(hwnd):
    return dll.EU_GetWindowFrameFlags(hwnd)

def set_window_frame_flags(hwnd, frame_flags):
    dll.EU_SetWindowFrameFlags(hwnd, frame_flags)

def set_window_resize_border(hwnd, left=6, top=6, right=6, bottom=6):
    dll.EU_SetWindowResizeBorder(hwnd, left, top, right, bottom)

def get_window_resize_border(hwnd):
    left = ctypes.c_int()
    top = ctypes.c_int()
    right = ctypes.c_int()
    bottom = ctypes.c_int()
    ok = dll.EU_GetWindowResizeBorder(hwnd, ctypes.byref(left), ctypes.byref(top),
                                      ctypes.byref(right), ctypes.byref(bottom))
    if not ok:
        return None
    return left.value, top.value, right.value, bottom.value

def set_window_no_drag_region(hwnd, x, y, w, h, enabled=True):
    dll.EU_SetWindowNoDragRegion(hwnd, x, y, w, h, 1 if enabled else 0)

def clear_window_no_drag_regions(hwnd):
    dll.EU_ClearWindowNoDragRegions(hwnd)

def set_element_window_command(hwnd, element_id, command):
    dll.EU_SetElementWindowCommand(hwnd, element_id, command)

def get_element_window_command(hwnd, element_id):
    return dll.EU_GetElementWindowCommand(hwnd, element_id)

def set_chrome_theme_preset(hwnd, preset=0):
    dll.EU_SetChromeThemePreset(hwnd, preset)

def set_theme_token(hwnd, token, color):
    data = make_utf8(token)
    dll.EU_SetThemeToken(hwnd, bytes_arg(data), len(data), color)

def get_theme_token(hwnd, token):
    data = make_utf8(token)
    color = ctypes.c_uint32()
    ok = dll.EU_GetThemeToken(hwnd, bytes_arg(data), len(data), ctypes.byref(color))
    return color.value if ok else None

def set_high_contrast_mode(hwnd, enabled=True):
    dll.EU_SetHighContrastMode(hwnd, 1 if enabled else 0)

def set_incognito_mode(hwnd, enabled=True):
    dll.EU_SetIncognitoMode(hwnd, 1 if enabled else 0)

def create_panel(hwnd, parent_id=0, x=0, y=0, w=800, h=600, color=0):
    pid = dll.EU_CreatePanel(hwnd, parent_id, x, y, w, h)
    if color:
        dll.EU_SetElementColor(hwnd, pid, color, 0xFFFFFFFF)
    return pid

def create_button(hwnd, parent_id, emoji="", text="Button", x=0, y=0, w=200, h=40,
                  variant=0, plain=False, round=False, circle=False, loading=False, size=0):
    e_data = make_utf8(emoji)
    t_data = make_utf8(text)
    element_id = dll.EU_CreateButton(
        hwnd, parent_id,
        (ctypes.c_ubyte * len(e_data))(*e_data), len(e_data),
        (ctypes.c_ubyte * len(t_data))(*t_data), len(t_data),
        x, y, w, h
    )
    if element_id and (variant or plain or round or circle or loading or size):
        set_button_options(hwnd, element_id, variant, plain, round, circle, loading, size)
    return element_id

def create_editbox(hwnd, parent_id, x=0, y=0, w=300, h=32):
    return dll.EU_CreateEditBox(hwnd, parent_id, x, y, w, h)

def set_editbox_text(hwnd, element_id, text=""):
    data = make_utf8(text)
    dll.EU_SetEditBoxText(hwnd, element_id, bytes_arg(data), len(data))

def set_editbox_options(hwnd, element_id, readonly=False, password=False, multiline=False,
                        focus_border=0, placeholder=""):
    data = make_utf8(placeholder)
    dll.EU_SetEditBoxOptions(
        hwnd, element_id,
        1 if readonly else 0,
        1 if password else 0,
        1 if multiline else 0,
        focus_border,
        bytes_arg(data), len(data),
    )

def get_editbox_options(hwnd, element_id):
    readonly = ctypes.c_int()
    password = ctypes.c_int()
    multiline = ctypes.c_int()
    focus_border = ctypes.c_uint32()
    ok = dll.EU_GetEditBoxOptions(
        hwnd, element_id,
        ctypes.byref(readonly), ctypes.byref(password),
        ctypes.byref(multiline), ctypes.byref(focus_border),
    )
    if not ok:
        return None
    return bool(readonly.value), bool(password.value), bool(multiline.value), focus_border.value

def get_editbox_state(hwnd, element_id):
    cursor = ctypes.c_int()
    sel_start = ctypes.c_int()
    sel_end = ctypes.c_int()
    text_length = ctypes.c_int()
    ok = dll.EU_GetEditBoxState(
        hwnd, element_id,
        ctypes.byref(cursor), ctypes.byref(sel_start),
        ctypes.byref(sel_end), ctypes.byref(text_length),
    )
    if not ok:
        return None
    return cursor.value, sel_start.value, sel_end.value, text_length.value

def get_editbox_text(hwnd, element_id, buffer_size=2048):
    buf = (ctypes.c_ubyte * buffer_size)()
    written = dll.EU_GetEditBoxText(hwnd, element_id, buf, buffer_size)
    if written <= 0:
        return ""
    return bytes(buf[:written]).decode("utf-8", errors="replace")

def set_editbox_scroll(hwnd, element_id, scroll_y=0):
    dll.EU_SetEditBoxScroll(hwnd, element_id, scroll_y)

def get_editbox_scroll(hwnd, element_id):
    scroll_y = ctypes.c_int()
    max_scroll_y = ctypes.c_int()
    content_height = ctypes.c_int()
    viewport_height = ctypes.c_int()
    ok = dll.EU_GetEditBoxScroll(
        hwnd, element_id,
        ctypes.byref(scroll_y), ctypes.byref(max_scroll_y),
        ctypes.byref(content_height), ctypes.byref(viewport_height),
    )
    if not ok:
        return None
    return {
        "scroll_y": scroll_y.value,
        "max_scroll_y": max_scroll_y.value,
        "content_height": content_height.value,
        "viewport_height": viewport_height.value,
    }

def get_element_visible(hwnd, element_id):
    return bool(dll.EU_GetElementVisible(hwnd, element_id))

def get_element_enabled(hwnd, element_id):
    return bool(dll.EU_GetElementEnabled(hwnd, element_id))

def create_infobox(hwnd, parent_id, title="Info", text="", x=0, y=0, w=420, h=86):
    title_data = make_utf8(title)
    text_data = make_utf8(text)
    return dll.EU_CreateInfoBox(
        hwnd, parent_id,
        (ctypes.c_ubyte * len(title_data))(*title_data), len(title_data),
        (ctypes.c_ubyte * len(text_data))(*text_data), len(text_data),
        x, y, w, h
    )

def create_text(hwnd, parent_id, text="Text", x=0, y=0, w=200, h=28):
    data = make_utf8(text)
    return dll.EU_CreateText(hwnd, parent_id, bytes_arg(data), len(data), x, y, w, h)

def create_link(hwnd, parent_id, text="Link", x=0, y=0, w=200, h=28,
                type=0, underline=True, auto_open=False, visited=False,
                prefix_icon="", suffix_icon="", href="", target=""):
    data = make_utf8(text)
    element_id = dll.EU_CreateLink(hwnd, parent_id, bytes_arg(data), len(data), x, y, w, h)
    if element_id:
        set_link_options(hwnd, element_id, type, underline, auto_open, visited)
        if prefix_icon or suffix_icon or href or target:
            set_link_content(hwnd, element_id, prefix_icon, suffix_icon, href, target)
    return element_id

def create_icon(hwnd, parent_id, text="✓", x=0, y=0, w=36, h=36):
    data = make_utf8(text)
    return dll.EU_CreateIcon(hwnd, parent_id, bytes_arg(data), len(data), x, y, w, h)

def create_icon_button(hwnd, parent_id, icon="⋮", tooltip="", x=0, y=0, w=36, h=36):
    icon_data = make_utf8(icon)
    tip_data = make_utf8(tooltip)
    return dll.EU_CreateIconButton(
        hwnd, parent_id,
        bytes_arg(icon_data), len(icon_data),
        bytes_arg(tip_data), len(tip_data),
        x, y, w, h,
    )

def set_icon_button_icon(hwnd, element_id, icon):
    data = make_utf8(icon)
    dll.EU_SetIconButtonIcon(hwnd, element_id, bytes_arg(data), len(data))

def set_icon_button_tooltip(hwnd, element_id, tooltip):
    data = make_utf8(tooltip)
    dll.EU_SetIconButtonTooltip(hwnd, element_id, bytes_arg(data), len(data))

def set_icon_button_badge(hwnd, element_id, text="", visible=True):
    data = make_utf8(text)
    dll.EU_SetIconButtonBadge(hwnd, element_id, bytes_arg(data), len(data), 1 if visible else 0)

def set_icon_button_checked(hwnd, element_id, checked=True):
    dll.EU_SetIconButtonChecked(hwnd, element_id, 1 if checked else 0)

def get_icon_button_checked(hwnd, element_id):
    return bool(dll.EU_GetIconButtonChecked(hwnd, element_id))

def set_icon_button_dropdown(hwnd, element_id, dropdown_element_id):
    dll.EU_SetIconButtonDropdown(hwnd, element_id, dropdown_element_id)

def set_icon_button_colors(hwnd, element_id, normal_bg=0x00000000, hover_bg=0x14000000,
                           pressed_bg=0x22000000, checked_bg=0x1F000000,
                           disabled_bg=0x00000000, icon_color=0xFF3C4043,
                           disabled_icon_color=0xFF9AA0A6):
    dll.EU_SetIconButtonColors(
        hwnd, element_id, normal_bg, hover_bg, pressed_bg, checked_bg,
        disabled_bg, icon_color, disabled_icon_color,
    )

def set_icon_button_shape(hwnd, element_id, shape=1, radius=18):
    dll.EU_SetIconButtonShape(hwnd, element_id, shape, radius)

def set_icon_button_padding(hwnd, element_id, left=6, top=6, right=6, bottom=6):
    dll.EU_SetIconButtonPadding(hwnd, element_id, left, top, right, bottom)

def set_icon_button_icon_size(hwnd, element_id, size=18):
    dll.EU_SetIconButtonIconSize(hwnd, element_id, size)

def get_icon_button_state(hwnd, element_id):
    checked = ctypes.c_int()
    hovered = ctypes.c_int()
    pressed = ctypes.c_int()
    badge_visible = ctypes.c_int()
    ok = dll.EU_GetIconButtonState(
        hwnd, element_id,
        ctypes.byref(checked), ctypes.byref(hovered),
        ctypes.byref(pressed), ctypes.byref(badge_visible),
    )
    if not ok:
        return None
    return {
        "checked": bool(checked.value),
        "hovered": bool(hovered.value),
        "pressed": bool(pressed.value),
        "badge_visible": bool(badge_visible.value),
    }

def create_omnibox(hwnd, parent_id, value="", placeholder="搜索或输入网址 🔍",
                   x=0, y=0, w=520, h=36):
    value_data = make_utf8(value)
    placeholder_data = make_utf8(placeholder)
    return dll.EU_CreateOmnibox(
        hwnd, parent_id,
        bytes_arg(value_data), len(value_data),
        bytes_arg(placeholder_data), len(placeholder_data),
        x, y, w, h,
    )

def set_omnibox_value(hwnd, element_id, value):
    data = make_utf8(value)
    dll.EU_SetOmniboxValue(hwnd, element_id, bytes_arg(data), len(data))

def get_omnibox_value(hwnd, element_id, buffer_size=4096):
    needed = dll.EU_GetOmniboxValue(hwnd, element_id, None, 0)
    size = max(buffer_size, needed + 1)
    buf = (ctypes.c_ubyte * size)()
    n = dll.EU_GetOmniboxValue(hwnd, element_id, buf, size)
    return bytes(buf[:max(0, n)]).decode("utf-8", errors="replace")

def set_omnibox_placeholder(hwnd, element_id, placeholder):
    data = make_utf8(placeholder)
    dll.EU_SetOmniboxPlaceholder(hwnd, element_id, bytes_arg(data), len(data))

def set_omnibox_security_state(hwnd, element_id, state=0, label=""):
    data = make_utf8(label)
    dll.EU_SetOmniboxSecurityState(hwnd, element_id, state, bytes_arg(data), len(data))

def set_omnibox_prefix_chip(hwnd, element_id, icon="🔒", text="安全",
                            bg_color=0xFFE6F4EA, fg_color=0xFF137333):
    icon_data = make_utf8(icon)
    text_data = make_utf8(text)
    dll.EU_SetOmniboxPrefixChip(
        hwnd, element_id,
        bytes_arg(icon_data), len(icon_data),
        bytes_arg(text_data), len(text_data),
        bg_color, fg_color,
    )

def set_omnibox_action_icons(hwnd, element_id, items=None):
    if items is None:
        items = [("☆", "收藏"), ("↗", "分享")]
    data = make_utf8("|".join(f"{icon}\t{name}" for icon, name in items))
    dll.EU_SetOmniboxActionIcons(hwnd, element_id, bytes_arg(data), len(data))

def set_omnibox_suggestion_items(hwnd, element_id, items=None):
    if items is None:
        items = [
            ("搜索", "🔍", "搜索 new_emoji", "来自默认搜索", "new_emoji"),
            ("历史", "🕘", "项目文档", "本地示例", "docs"),
        ]
    data = make_utf8("\n".join("\t".join(str(v) for v in row) for row in items))
    dll.EU_SetOmniboxSuggestionItems(hwnd, element_id, bytes_arg(data), len(data))

def set_omnibox_suggestion_open(hwnd, element_id, open=True):
    dll.EU_SetOmniboxSuggestionOpen(hwnd, element_id, 1 if open else 0)

def set_omnibox_suggestion_selected(hwnd, element_id, index=0):
    dll.EU_SetOmniboxSuggestionSelected(hwnd, element_id, index)

def get_omnibox_suggestion_state(hwnd, element_id):
    open_v = ctypes.c_int()
    selected = ctypes.c_int()
    count = ctypes.c_int()
    ok = dll.EU_GetOmniboxSuggestionState(
        hwnd, element_id, ctypes.byref(open_v), ctypes.byref(selected), ctypes.byref(count)
    )
    if not ok:
        return None
    return {"open": bool(open_v.value), "selected": selected.value, "count": count.value}

def set_omnibox_commit_callback(hwnd, element_id, callback):
    dll.EU_SetOmniboxCommitCallback(hwnd, element_id, callback)

def set_omnibox_icon_button_callback(hwnd, element_id, callback):
    dll.EU_SetOmniboxIconButtonCallback(hwnd, element_id, callback)

def create_browser_viewport(hwnd, parent_id, x=0, y=0, w=900, h=520):
    return dll.EU_CreateBrowserViewport(hwnd, parent_id, x, y, w, h)

def set_browser_viewport_state(hwnd, element_id, state=0):
    dll.EU_SetBrowserViewportState(hwnd, element_id, state)

def set_browser_viewport_placeholder(hwnd, element_id, title="新标签页 🌐",
                                     desc="这里是浏览器内容区占位，可在未来接入 WebView2。",
                                     icon="🌐"):
    title_data = make_utf8(title)
    desc_data = make_utf8(desc)
    icon_data = make_utf8(icon)
    dll.EU_SetBrowserViewportPlaceholder(
        hwnd, element_id,
        bytes_arg(title_data), len(title_data),
        bytes_arg(desc_data), len(desc_data),
        bytes_arg(icon_data), len(icon_data),
    )

def set_browser_viewport_loading(hwnd, element_id, loading=True, progress=0):
    dll.EU_SetBrowserViewportLoading(hwnd, element_id, 1 if loading else 0, progress)

def set_browser_viewport_screenshot(hwnd, element_id, image_source=""):
    data = make_utf8(image_source)
    dll.EU_SetBrowserViewportScreenshot(hwnd, element_id, bytes_arg(data), len(data))

def get_browser_viewport_state(hwnd, element_id):
    state = ctypes.c_int()
    loading = ctypes.c_int()
    progress = ctypes.c_int()
    ok = dll.EU_GetBrowserViewportState(
        hwnd, element_id, ctypes.byref(state), ctypes.byref(loading), ctypes.byref(progress)
    )
    if not ok:
        return None
    return {"state": state.value, "loading": bool(loading.value), "progress": progress.value}

def set_text_options(hwnd, element_id, align=0, valign=0, wrap=True, ellipsis=False):
    dll.EU_SetTextOptions(hwnd, element_id, align, valign, 1 if wrap else 0, 1 if ellipsis else 0)

def get_text_options(hwnd, element_id):
    align = ctypes.c_int()
    valign = ctypes.c_int()
    wrap = ctypes.c_int()
    ellipsis = ctypes.c_int()
    ok = dll.EU_GetTextOptions(
        hwnd, element_id,
        ctypes.byref(align), ctypes.byref(valign),
        ctypes.byref(wrap), ctypes.byref(ellipsis),
    )
    if not ok:
        return None
    return align.value, valign.value, bool(wrap.value), bool(ellipsis.value)

def set_link_visited(hwnd, element_id, visited=True):
    dll.EU_SetLinkVisited(hwnd, element_id, 1 if visited else 0)

def get_link_visited(hwnd, element_id):
    return bool(dll.EU_GetLinkVisited(hwnd, element_id))

def set_link_options(hwnd, element_id, type=0, underline=True, auto_open=False, visited=False):
    dll.EU_SetLinkOptions(
        hwnd, element_id, int(type),
        1 if underline else 0,
        1 if auto_open else 0,
        1 if visited else 0,
    )

def get_link_options(hwnd, element_id):
    link_type = ctypes.c_int()
    underline = ctypes.c_int()
    auto_open = ctypes.c_int()
    visited = ctypes.c_int()
    ok = dll.EU_GetLinkOptions(
        hwnd, element_id,
        ctypes.byref(link_type), ctypes.byref(underline),
        ctypes.byref(auto_open), ctypes.byref(visited),
    )
    if not ok:
        return None
    return {
        "type": link_type.value,
        "underline": bool(underline.value),
        "auto_open": bool(auto_open.value),
        "visited": bool(visited.value),
    }

def set_link_content(hwnd, element_id, prefix_icon="", suffix_icon="", href="", target=""):
    prefix_data = make_utf8(prefix_icon)
    suffix_data = make_utf8(suffix_icon)
    href_data = make_utf8(href)
    target_data = make_utf8(target)
    dll.EU_SetLinkContent(
        hwnd, element_id,
        bytes_arg(prefix_data), len(prefix_data),
        bytes_arg(suffix_data), len(suffix_data),
        bytes_arg(href_data), len(href_data),
        bytes_arg(target_data), len(target_data),
    )

def get_link_content(hwnd, element_id, buffer_size=1024):
    prefix = (ctypes.c_ubyte * buffer_size)()
    suffix = (ctypes.c_ubyte * buffer_size)()
    href = (ctypes.c_ubyte * buffer_size)()
    target = (ctypes.c_ubyte * buffer_size)()
    ok = dll.EU_GetLinkContent(
        hwnd, element_id,
        prefix, buffer_size,
        suffix, buffer_size,
        href, buffer_size,
        target, buffer_size,
    )
    if not ok:
        return None

    def decode(buf):
        raw = bytes(buf)
        raw = raw.split(b"\0", 1)[0]
        return raw.decode("utf-8", errors="replace")

    return {
        "prefix_icon": decode(prefix),
        "suffix_icon": decode(suffix),
        "href": decode(href),
        "target": decode(target),
    }

def set_icon_options(hwnd, element_id, scale=1.25, rotation_degrees=0.0):
    dll.EU_SetIconOptions(hwnd, element_id, ctypes.c_float(scale), ctypes.c_float(rotation_degrees))

def get_icon_options(hwnd, element_id):
    scale = ctypes.c_float()
    rotation = ctypes.c_float()
    ok = dll.EU_GetIconOptions(hwnd, element_id, ctypes.byref(scale), ctypes.byref(rotation))
    if not ok:
        return None
    return scale.value, rotation.value

def create_space(hwnd, parent_id, x=0, y=0, w=16, h=16):
    return dll.EU_CreateSpace(hwnd, parent_id, x, y, w, h)

def set_infobox_text(hwnd, element_id, title="", body=""):
    title_data = make_utf8(title)
    body_data = make_utf8(body)
    dll.EU_SetInfoBoxText(
        hwnd, element_id,
        bytes_arg(title_data), len(title_data),
        bytes_arg(body_data), len(body_data),
    )

def set_infobox_options(hwnd, element_id, type=0, closable=False, accent=0, icon=""):
    icon_data = make_utf8(icon)
    dll.EU_SetInfoBoxOptions(
        hwnd, element_id, type, 1 if closable else 0,
        accent, bytes_arg(icon_data), len(icon_data)
    )

def set_infobox_closed(hwnd, element_id, closed=True):
    dll.EU_SetInfoBoxClosed(hwnd, element_id, 1 if closed else 0)

def get_infobox_closed(hwnd, element_id):
    return bool(dll.EU_GetInfoBoxClosed(hwnd, element_id))

def get_infobox_preferred_height(hwnd, element_id):
    return dll.EU_GetInfoBoxPreferredHeight(hwnd, element_id)

def set_space_size(hwnd, element_id, w=16, h=16):
    dll.EU_SetSpaceSize(hwnd, element_id, w, h)

def get_space_size(hwnd, element_id):
    w = ctypes.c_int()
    h = ctypes.c_int()
    ok = dll.EU_GetSpaceSize(hwnd, element_id, ctypes.byref(w), ctypes.byref(h))
    if not ok:
        return None
    return w.value, h.value

def create_container(hwnd, parent_id, x=0, y=0, w=800, h=600):
    return dll.EU_CreateContainer(hwnd, parent_id, x, y, w, h)

def set_container_flex_layout(hwnd, element_id, direction=1, gap=0, align_items=0, justify_content=0):
    dll.EU_SetContainerFlexLayout(hwnd, element_id, direction, gap, align_items, justify_content)

def set_element_flex_grow(hwnd, element_id, grow=1):
    dll.EU_SetElementFlexGrow(hwnd, element_id, grow)

def set_element_min_max_size(hwnd, element_id, min_w=0, min_h=0, max_w=0, max_h=0):
    dll.EU_SetElementMinMaxSize(hwnd, element_id, min_w, min_h, max_w, max_h)

def set_element_margin(hwnd, element_id, left=0, top=0, right=0, bottom=0):
    dll.EU_SetElementMargin(hwnd, element_id, left, top, right, bottom)

def set_element_align_self(hwnd, element_id, align_self=0):
    dll.EU_SetElementAlignSelf(hwnd, element_id, align_self)

def _create_container_region(fn, hwnd, parent_id, text="", x=0, y=0, w=0, h=0):
    data = make_utf8(text)
    return fn(hwnd, parent_id, bytes_arg(data), len(data), x, y, w, h)

def create_header(hwnd, parent_id, text="顶栏", x=0, y=0, w=0, h=60):
    return _create_container_region(dll.EU_CreateHeader, hwnd, parent_id, text, x, y, w, h)

def create_aside(hwnd, parent_id, text="侧边栏", x=0, y=0, w=200, h=0):
    return _create_container_region(dll.EU_CreateAside, hwnd, parent_id, text, x, y, w, h)

def create_main(hwnd, parent_id, text="主要区域", x=0, y=0, w=0, h=0):
    return _create_container_region(dll.EU_CreateMain, hwnd, parent_id, text, x, y, w, h)

def create_footer(hwnd, parent_id, text="底栏", x=0, y=0, w=0, h=60):
    return _create_container_region(dll.EU_CreateFooter, hwnd, parent_id, text, x, y, w, h)

def create_layout(hwnd, parent_id, orientation=0, gap=8, x=0, y=0, w=300, h=40):
    return dll.EU_CreateLayout(hwnd, parent_id, orientation, gap, x, y, w, h)

def create_border(hwnd, parent_id, x=0, y=0, w=300, h=80):
    return dll.EU_CreateBorder(hwnd, parent_id, x, y, w, h)

def set_panel_style(hwnd, element_id, bg=0, border=0, border_width=0.0, radius=0.0, padding=0):
    dll.EU_SetPanelStyle(
        hwnd, element_id, bg, border,
        ctypes.c_float(border_width), ctypes.c_float(radius), padding
    )

def get_panel_style(hwnd, element_id):
    bg = ctypes.c_uint32()
    border = ctypes.c_uint32()
    border_width = ctypes.c_float()
    radius = ctypes.c_float()
    padding = ctypes.c_int()
    ok = dll.EU_GetPanelStyle(
        hwnd, element_id,
        ctypes.byref(bg), ctypes.byref(border),
        ctypes.byref(border_width), ctypes.byref(radius),
        ctypes.byref(padding),
    )
    if not ok:
        return None
    return bg.value, border.value, border_width.value, radius.value, padding.value

def set_panel_layout(hwnd, element_id, fill_parent=False, content_layout=False):
    dll.EU_SetPanelLayout(
        hwnd, element_id,
        1 if fill_parent else 0,
        1 if content_layout else 0,
    )

def get_panel_layout(hwnd, element_id):
    fill_parent = ctypes.c_int()
    content_layout = ctypes.c_int()
    ok = dll.EU_GetPanelLayout(
        hwnd, element_id,
        ctypes.byref(fill_parent), ctypes.byref(content_layout),
    )
    if not ok:
        return None
    return bool(fill_parent.value), bool(content_layout.value)

def set_container_layout(hwnd, element_id, enabled=True, direction=0, gap=0):
    dll.EU_SetContainerLayout(hwnd, element_id, 1 if enabled else 0, direction, gap)

def get_container_layout(hwnd, element_id):
    enabled = ctypes.c_int()
    direction = ctypes.c_int()
    gap = ctypes.c_int()
    actual = ctypes.c_int()
    ok = dll.EU_GetContainerLayout(
        hwnd, element_id,
        ctypes.byref(enabled), ctypes.byref(direction),
        ctypes.byref(gap), ctypes.byref(actual),
    )
    if not ok:
        return None
    return {
        "enabled": bool(enabled.value),
        "direction": direction.value,
        "gap": gap.value,
        "actual_direction": actual.value,
    }

def set_container_region_text_options(hwnd, element_id, align=1, valign=1):
    dll.EU_SetContainerRegionTextOptions(hwnd, element_id, align, valign)

def get_container_region_text_options(hwnd, element_id):
    align = ctypes.c_int()
    valign = ctypes.c_int()
    role = ctypes.c_int()
    ok = dll.EU_GetContainerRegionTextOptions(
        hwnd, element_id,
        ctypes.byref(align), ctypes.byref(valign), ctypes.byref(role),
    )
    if not ok:
        return None
    return {
        "align": align.value,
        "valign": valign.value,
        "role": role.value,
    }

def set_button_emoji(hwnd, element_id, emoji=""):
    data = make_utf8(emoji)
    dll.EU_SetButtonEmoji(hwnd, element_id, bytes_arg(data), len(data))

def set_button_variant(hwnd, element_id, variant=0):
    dll.EU_SetButtonVariant(hwnd, element_id, variant)

def set_button_options(hwnd, element_id, variant=0, plain=False, round=False,
                       circle=False, loading=False, size=0):
    dll.EU_SetButtonOptions(
        hwnd, element_id,
        variant,
        1 if plain else 0,
        1 if round else 0,
        1 if circle else 0,
        1 if loading else 0,
        size,
    )

def get_button_options(hwnd, element_id):
    variant = ctypes.c_int()
    plain = ctypes.c_int()
    round_value = ctypes.c_int()
    circle = ctypes.c_int()
    loading = ctypes.c_int()
    size = ctypes.c_int()
    ok = dll.EU_GetButtonOptions(
        hwnd, element_id,
        ctypes.byref(variant), ctypes.byref(plain),
        ctypes.byref(round_value), ctypes.byref(circle),
        ctypes.byref(loading), ctypes.byref(size),
    )
    if not ok:
        return None
    return {
        "variant": variant.value,
        "plain": bool(plain.value),
        "round": bool(round_value.value),
        "circle": bool(circle.value),
        "loading": bool(loading.value),
        "size": size.value,
    }

def get_button_state(hwnd, element_id):
    pressed = ctypes.c_int()
    focused = ctypes.c_int()
    variant = ctypes.c_int()
    ok = dll.EU_GetButtonState(
        hwnd, element_id,
        ctypes.byref(pressed), ctypes.byref(focused), ctypes.byref(variant),
    )
    if not ok:
        return None
    return bool(pressed.value), bool(focused.value), variant.value

def set_layout_options(hwnd, element_id, orientation=0, gap=8, stretch=True, align=0, wrap=False):
    dll.EU_SetLayoutOptions(
        hwnd, element_id, orientation, gap,
        1 if stretch else 0, align, 1 if wrap else 0
    )

def get_layout_options(hwnd, element_id):
    orientation = ctypes.c_int()
    gap = ctypes.c_int()
    stretch = ctypes.c_int()
    align = ctypes.c_int()
    wrap = ctypes.c_int()
    ok = dll.EU_GetLayoutOptions(
        hwnd, element_id,
        ctypes.byref(orientation), ctypes.byref(gap),
        ctypes.byref(stretch), ctypes.byref(align), ctypes.byref(wrap),
    )
    if not ok:
        return None
    return orientation.value, gap.value, bool(stretch.value), align.value, bool(wrap.value)

def set_layout_child_weight(hwnd, layout_id, child_id, weight=0):
    dll.EU_SetLayoutChildWeight(hwnd, layout_id, child_id, weight)

def get_layout_child_weight(hwnd, layout_id, child_id):
    return dll.EU_GetLayoutChildWeight(hwnd, layout_id, child_id)

def set_border_options(hwnd, element_id, sides=15, color=0, width=1.0, radius=6.0, title=""):
    data = make_utf8(title)
    dll.EU_SetBorderOptions(
        hwnd, element_id, sides, color,
        ctypes.c_float(width), ctypes.c_float(radius),
        bytes_arg(data), len(data)
    )

def get_border_options(hwnd, element_id):
    sides = ctypes.c_int()
    color = ctypes.c_uint32()
    width = ctypes.c_float()
    radius = ctypes.c_float()
    ok = dll.EU_GetBorderOptions(
        hwnd, element_id,
        ctypes.byref(sides), ctypes.byref(color),
        ctypes.byref(width), ctypes.byref(radius),
    )
    if not ok:
        return None
    return sides.value, color.value, width.value, radius.value

def set_border_dashed(hwnd, element_id, dashed=True):
    dll.EU_SetBorderDashed(hwnd, element_id, 1 if dashed else 0)

def get_border_dashed(hwnd, element_id):
    return bool(dll.EU_GetBorderDashed(hwnd, element_id))

def set_divider_options(hwnd, element_id, direction=0, content_position=1,
                        color=0, width=1.0, dashed=False, text=""):
    data = make_utf8(text)
    dll.EU_SetDividerOptions(
        hwnd, element_id,
        direction, content_position, color,
        ctypes.c_float(width), 1 if dashed else 0,
        bytes_arg(data), len(data)
    )

def get_divider_options(hwnd, element_id):
    direction = ctypes.c_int()
    content_position = ctypes.c_int()
    color = ctypes.c_uint32()
    width = ctypes.c_float()
    dashed = ctypes.c_int()
    ok = dll.EU_GetDividerOptions(
        hwnd, element_id,
        ctypes.byref(direction), ctypes.byref(content_position),
        ctypes.byref(color), ctypes.byref(width), ctypes.byref(dashed),
    )
    if not ok:
        return None
    return direction.value, content_position.value, color.value, width.value, bool(dashed.value)

def set_divider_spacing(hwnd, element_id, margin=0, gap=8):
    dll.EU_SetDividerSpacing(hwnd, element_id, margin, gap)

def get_divider_spacing(hwnd, element_id):
    margin = ctypes.c_int()
    gap = ctypes.c_int()
    ok = dll.EU_GetDividerSpacing(hwnd, element_id, ctypes.byref(margin), ctypes.byref(gap))
    return (margin.value, gap.value) if ok else None

def set_divider_line_style(hwnd, element_id, line_style=0):
    dll.EU_SetDividerLineStyle(hwnd, element_id, line_style)

def get_divider_line_style(hwnd, element_id):
    line_style = ctypes.c_int()
    ok = dll.EU_GetDividerLineStyle(hwnd, element_id, ctypes.byref(line_style))
    return line_style.value if ok else None

def set_divider_content(hwnd, element_id, icon="", text=""):
    icon_data = make_utf8(icon)
    text_data = make_utf8(text)
    dll.EU_SetDividerContent(
        hwnd, element_id,
        bytes_arg(icon_data), len(icon_data),
        bytes_arg(text_data), len(text_data),
    )

def get_divider_content(hwnd, element_id, buffer_size=512):
    icon = (ctypes.c_ubyte * buffer_size)()
    text = (ctypes.c_ubyte * buffer_size)()
    ok = dll.EU_GetDividerContent(hwnd, element_id, icon, buffer_size, text, buffer_size)
    if not ok:
        return None
    def decode(buf):
        raw = bytes(buf).split(b"\0", 1)[0]
        return raw.decode("utf-8", errors="replace")
    return decode(icon), decode(text)

def create_checkbox(hwnd, parent_id, text="复选框", checked=False, x=0, y=0, w=220, h=30,
                    border=False, size=0):
    data = make_utf8(text)
    element_id = dll.EU_CreateCheckbox(hwnd, parent_id, bytes_arg(data), len(data),
                                       1 if checked else 0, x, y, w, h)
    if element_id and (border or size):
        set_checkbox_options(hwnd, element_id, border=border, size=size)
    return element_id

def _checkbox_group_items_data(items):
    rows = []
    for item in items:
        if isinstance(item, dict):
            text = str(item.get("text", item.get("label", item.get("value", ""))))
            value = str(item.get("value", text))
            disabled = bool(item.get("disabled", False))
        elif isinstance(item, (tuple, list)):
            text = str(item[0]) if len(item) >= 1 else ""
            value = str(item[1]) if len(item) >= 2 else text
            disabled = bool(item[2]) if len(item) >= 3 else False
        else:
            text = str(item)
            value = text
            disabled = False
        rows.append(f"{text}\t{value}\t{1 if disabled else 0}")
    return make_utf8("\n".join(rows))

def _checkbox_values_data(values):
    if values is None:
        values = []
    if isinstance(values, str):
        text = values
    else:
        text = "\n".join(str(value) for value in values)
    return make_utf8(text)

def create_checkbox_group(hwnd, parent_id, items, checked_values=None,
                          style=0, size=0, disabled=False,
                          min_checked=0, max_checked=0,
                          x=0, y=0, w=420, h=40):
    items_data = _checkbox_group_items_data(items)
    values_data = _checkbox_values_data(checked_values)
    return dll.EU_CreateCheckboxGroup(
        hwnd, parent_id,
        bytes_arg(items_data), len(items_data),
        bytes_arg(values_data), len(values_data),
        style, size, 1 if disabled else 0,
        min_checked, max_checked,
        x, y, w, h,
    )

def create_radio(hwnd, parent_id, text="单选框", checked=False, x=0, y=0, w=180, h=30,
                 value="", border=False, size=0):
    data = make_utf8(text)
    element_id = dll.EU_CreateRadio(hwnd, parent_id, bytes_arg(data), len(data),
                                    1 if checked else 0, x, y, w, h)
    if element_id:
        if value != "":
            set_radio_value(hwnd, element_id, value)
        if border or size:
            set_radio_options(hwnd, element_id, border=border, size=size)
    return element_id

def _radio_group_items_data(items):
    rows = []
    for item in items:
        if isinstance(item, dict):
            text = str(item.get("text", item.get("label", item.get("value", ""))))
            value = str(item.get("value", text))
            disabled = bool(item.get("disabled", False))
        elif isinstance(item, (tuple, list)):
            text = str(item[0]) if len(item) >= 1 else ""
            value = str(item[1]) if len(item) >= 2 else text
            disabled = bool(item[2]) if len(item) >= 3 else False
        else:
            text = str(item)
            value = text
            disabled = False
        rows.append(f"{text}\t{value}\t{1 if disabled else 0}")
    return make_utf8("\n".join(rows))

def create_radio_group(hwnd, parent_id, items, value="", style=0, size=0, disabled=False,
                       x=0, y=0, w=360, h=40):
    items_data = _radio_group_items_data(items)
    value_data = make_utf8(str(value))
    return dll.EU_CreateRadioGroup(
        hwnd, parent_id,
        bytes_arg(items_data), len(items_data),
        bytes_arg(value_data), len(value_data),
        style, size, 1 if disabled else 0,
        x, y, w, h,
    )

def create_switch(hwnd, parent_id, text="开关", checked=False, x=0, y=0, w=220, h=32):
    data = make_utf8(text)
    return dll.EU_CreateSwitch(hwnd, parent_id, bytes_arg(data), len(data),
                               1 if checked else 0, x, y, w, h)

def set_radio_group(hwnd, element_id, group):
    data = make_utf8(group)
    dll.EU_SetRadioGroup(hwnd, element_id, bytes_arg(data), len(data))

def get_radio_group(hwnd, element_id, buffer_size=256):
    buf = (ctypes.c_ubyte * buffer_size)()
    written = dll.EU_GetRadioGroup(hwnd, element_id, buf, buffer_size)
    if written <= 0:
        return ""
    data = bytes(buf[:min(written, buffer_size)])
    return data.decode("utf-8", errors="replace")

def set_radio_value(hwnd, element_id, value):
    data = make_utf8(str(value))
    dll.EU_SetRadioValue(hwnd, element_id, bytes_arg(data), len(data))

def get_radio_value(hwnd, element_id, buffer_size=256):
    buf = (ctypes.c_ubyte * buffer_size)()
    written = dll.EU_GetRadioValue(hwnd, element_id, buf, buffer_size)
    if written <= 0:
        return ""
    data = bytes(buf[:min(written, buffer_size)])
    return data.decode("utf-8", errors="replace")

def set_checkbox_options(hwnd, element_id, border=False, size=0):
    dll.EU_SetCheckboxOptions(hwnd, element_id, 1 if border else 0, size)

def get_checkbox_options(hwnd, element_id):
    border = ctypes.c_int()
    size = ctypes.c_int()
    ok = dll.EU_GetCheckboxOptions(hwnd, element_id, ctypes.byref(border), ctypes.byref(size))
    if not ok:
        return None
    return {"border": bool(border.value), "size": size.value}

def set_checkbox_group_items(hwnd, element_id, items):
    data = _checkbox_group_items_data(items)
    dll.EU_SetCheckboxGroupItems(hwnd, element_id, bytes_arg(data), len(data))

def set_checkbox_group_value(hwnd, element_id, values):
    data = _checkbox_values_data(values)
    dll.EU_SetCheckboxGroupValue(hwnd, element_id, bytes_arg(data), len(data))

def get_checkbox_group_value(hwnd, element_id, buffer_size=1024):
    buf = (ctypes.c_ubyte * buffer_size)()
    written = dll.EU_GetCheckboxGroupValue(hwnd, element_id, buf, buffer_size)
    if written <= 0:
        return []
    data = bytes(buf[:min(written, buffer_size)])
    text = data.decode("utf-8", errors="replace")
    return [value for value in text.splitlines() if value]

def set_checkbox_group_options(hwnd, element_id, disabled=False, style=0, size=0,
                               min_checked=0, max_checked=0):
    dll.EU_SetCheckboxGroupOptions(
        hwnd, element_id, 1 if disabled else 0, style, size, min_checked, max_checked
    )

def get_checkbox_group_options(hwnd, element_id):
    disabled = ctypes.c_int()
    style = ctypes.c_int()
    size = ctypes.c_int()
    min_checked = ctypes.c_int()
    max_checked = ctypes.c_int()
    ok = dll.EU_GetCheckboxGroupOptions(
        hwnd, element_id,
        ctypes.byref(disabled), ctypes.byref(style), ctypes.byref(size),
        ctypes.byref(min_checked), ctypes.byref(max_checked),
    )
    if not ok:
        return None
    return {
        "disabled": bool(disabled.value),
        "style": style.value,
        "size": size.value,
        "min_checked": min_checked.value,
        "max_checked": max_checked.value,
    }

def get_checkbox_group_state(hwnd, element_id):
    checked = ctypes.c_int()
    count = ctypes.c_int()
    disabled_count = ctypes.c_int()
    group_disabled = ctypes.c_int()
    style = ctypes.c_int()
    size = ctypes.c_int()
    min_checked = ctypes.c_int()
    max_checked = ctypes.c_int()
    hover = ctypes.c_int()
    press = ctypes.c_int()
    focus = ctypes.c_int()
    last_action = ctypes.c_int()
    ok = dll.EU_GetCheckboxGroupState(
        hwnd, element_id,
        ctypes.byref(checked), ctypes.byref(count), ctypes.byref(disabled_count),
        ctypes.byref(group_disabled), ctypes.byref(style), ctypes.byref(size),
        ctypes.byref(min_checked), ctypes.byref(max_checked),
        ctypes.byref(hover), ctypes.byref(press), ctypes.byref(focus),
        ctypes.byref(last_action),
    )
    if not ok:
        return None
    return {
        "checked_count": checked.value,
        "item_count": count.value,
        "disabled_count": disabled_count.value,
        "disabled": bool(group_disabled.value),
        "style": style.value,
        "size": size.value,
        "min_checked": min_checked.value,
        "max_checked": max_checked.value,
        "hover_index": hover.value,
        "press_index": press.value,
        "focus_index": focus.value,
        "last_action": last_action.value,
    }

def set_radio_options(hwnd, element_id, border=False, size=0):
    dll.EU_SetRadioOptions(hwnd, element_id, 1 if border else 0, size)

def get_radio_options(hwnd, element_id):
    border = ctypes.c_int()
    size = ctypes.c_int()
    ok = dll.EU_GetRadioOptions(hwnd, element_id, ctypes.byref(border), ctypes.byref(size))
    if not ok:
        return None
    return {"border": bool(border.value), "size": size.value}

def set_radio_group_items(hwnd, element_id, items):
    data = _radio_group_items_data(items)
    dll.EU_SetRadioGroupItems(hwnd, element_id, bytes_arg(data), len(data))

def set_radio_group_value(hwnd, element_id, value):
    data = make_utf8(str(value))
    dll.EU_SetRadioGroupValue(hwnd, element_id, bytes_arg(data), len(data))

def get_radio_group_value(hwnd, element_id, buffer_size=256):
    buf = (ctypes.c_ubyte * buffer_size)()
    written = dll.EU_GetRadioGroupValue(hwnd, element_id, buf, buffer_size)
    if written <= 0:
        return ""
    data = bytes(buf[:min(written, buffer_size)])
    return data.decode("utf-8", errors="replace")

def get_radio_group_selected_index(hwnd, element_id):
    return dll.EU_GetRadioGroupSelectedIndex(hwnd, element_id)

def set_radio_group_options(hwnd, element_id, disabled=False, style=0, size=0):
    dll.EU_SetRadioGroupOptions(hwnd, element_id, 1 if disabled else 0, style, size)

def get_radio_group_options(hwnd, element_id):
    disabled = ctypes.c_int()
    style = ctypes.c_int()
    size = ctypes.c_int()
    ok = dll.EU_GetRadioGroupOptions(hwnd, element_id, ctypes.byref(disabled),
                                     ctypes.byref(style), ctypes.byref(size))
    if not ok:
        return None
    return {"disabled": bool(disabled.value), "style": style.value, "size": size.value}

def get_radio_group_state(hwnd, element_id):
    selected = ctypes.c_int()
    count = ctypes.c_int()
    disabled_count = ctypes.c_int()
    group_disabled = ctypes.c_int()
    style = ctypes.c_int()
    size = ctypes.c_int()
    hover = ctypes.c_int()
    press = ctypes.c_int()
    last_action = ctypes.c_int()
    ok = dll.EU_GetRadioGroupState(
        hwnd, element_id,
        ctypes.byref(selected), ctypes.byref(count), ctypes.byref(disabled_count),
        ctypes.byref(group_disabled), ctypes.byref(style), ctypes.byref(size),
        ctypes.byref(hover), ctypes.byref(press), ctypes.byref(last_action),
    )
    if not ok:
        return None
    return {
        "selected_index": selected.value,
        "item_count": count.value,
        "disabled_count": disabled_count.value,
        "disabled": bool(group_disabled.value),
        "style": style.value,
        "size": size.value,
        "hover_index": hover.value,
        "press_index": press.value,
        "last_action": last_action.value,
    }

def set_switch_texts(hwnd, element_id, active, inactive):
    active_data = make_utf8(active)
    inactive_data = make_utf8(inactive)
    dll.EU_SetSwitchTexts(
        hwnd, element_id,
        bytes_arg(active_data), len(active_data),
        bytes_arg(inactive_data), len(inactive_data),
    )

def get_switch_options(hwnd, element_id):
    checked = ctypes.c_int()
    loading = ctypes.c_int()
    has_active = ctypes.c_int()
    has_inactive = ctypes.c_int()
    ok = dll.EU_GetSwitchOptions(
        hwnd, element_id,
        ctypes.byref(checked), ctypes.byref(loading),
        ctypes.byref(has_active), ctypes.byref(has_inactive),
    )
    if not ok:
        return None
    return bool(checked.value), bool(loading.value), bool(has_active.value), bool(has_inactive.value)

def set_switch_active_color(hwnd, element_id, color):
    dll.EU_SetSwitchActiveColor(hwnd, element_id, color)

def get_switch_active_color(hwnd, element_id):
    return dll.EU_GetSwitchActiveColor(hwnd, element_id)

def set_switch_inactive_color(hwnd, element_id, color):
    dll.EU_SetSwitchInactiveColor(hwnd, element_id, color)

def get_switch_inactive_color(hwnd, element_id):
    return dll.EU_GetSwitchInactiveColor(hwnd, element_id)

def set_switch_value(hwnd, element_id, value):
    dll.EU_SetSwitchValue(hwnd, element_id, value)

def get_switch_value(hwnd, element_id):
    return dll.EU_GetSwitchValue(hwnd, element_id)

def set_switch_size(hwnd, element_id, size):
    dll.EU_SetSwitchSize(hwnd, element_id, size)

def get_switch_size(hwnd, element_id):
    return dll.EU_GetSwitchSize(hwnd, element_id)

def create_slider(hwnd, parent_id, text="Slider", min_value=0, max_value=100, value=40,
                  x=0, y=0, w=360, h=54, step=None, show_tooltip=None):
    data = make_utf8(text)
    element_id = dll.EU_CreateSlider(hwnd, parent_id, bytes_arg(data), len(data),
                                     min_value, max_value, value, x, y, w, h)
    if element_id and (step is not None or show_tooltip is not None):
        dll.EU_SetSliderOptions(hwnd, element_id,
                                1 if step is None else step,
                                0 if show_tooltip is None else int(bool(show_tooltip)))
    return element_id

def get_slider_options(hwnd, element_id):
    min_value = ctypes.c_int()
    max_value = ctypes.c_int()
    step = ctypes.c_int()
    show_tooltip = ctypes.c_int()
    ok = dll.EU_GetSliderOptions(
        hwnd, element_id,
        ctypes.byref(min_value), ctypes.byref(max_value),
        ctypes.byref(step), ctypes.byref(show_tooltip),
    )
    if not ok:
        return None
    return min_value.value, max_value.value, step.value, bool(show_tooltip.value)

def set_slider_range_mode(hwnd, element_id, enabled=True, start_value=0, end_value=100):
    dll.EU_SetSliderRangeMode(hwnd, element_id, int(bool(enabled)), start_value, end_value)

def set_slider_range_value(hwnd, element_id, start_value, end_value):
    dll.EU_SetSliderRangeValue(hwnd, element_id, start_value, end_value)

def get_slider_range_value(hwnd, element_id):
    start_value = ctypes.c_int()
    end_value = ctypes.c_int()
    ok = dll.EU_GetSliderRangeValue(hwnd, element_id, ctypes.byref(start_value), ctypes.byref(end_value))
    if not ok:
        return None
    return start_value.value, end_value.value

def get_slider_range_mode(hwnd, element_id):
    enabled = ctypes.c_int()
    start_value = ctypes.c_int()
    end_value = ctypes.c_int()
    ok = dll.EU_GetSliderRangeMode(
        hwnd, element_id,
        ctypes.byref(enabled), ctypes.byref(start_value), ctypes.byref(end_value),
    )
    if not ok:
        return None
    return bool(enabled.value), start_value.value, end_value.value

def set_element_text(hwnd, element_id, text=""):
    data = make_utf8(text)
    dll.EU_SetElementText(hwnd, element_id, bytes_arg(data), len(data))

def get_element_text(hwnd, element_id):
    needed = dll.EU_GetElementText(hwnd, element_id, None, 0)
    if needed <= 0:
        return ""
    buf = (ctypes.c_ubyte * (needed + 1))()
    written = dll.EU_GetElementText(hwnd, element_id, buf, needed + 1)
    if written < 0:
        return ""
    size = min(written, needed)
    return bytes(buf[:size]).decode("utf-8", errors="replace")

def get_element_bounds(hwnd, element_id):
    x = ctypes.c_int()
    y = ctypes.c_int()
    w = ctypes.c_int()
    h = ctypes.c_int()
    ok = dll.EU_GetElementBounds(
        hwnd, element_id,
        ctypes.byref(x), ctypes.byref(y), ctypes.byref(w), ctypes.byref(h),
    )
    if not ok:
        return None
    return x.value, y.value, w.value, h.value

def set_element_color(hwnd, element_id, bg=0, fg=0):
    dll.EU_SetElementColor(hwnd, element_id, bg, fg)

def set_element_visible(hwnd, element_id, visible=True):
    dll.EU_SetElementVisible(hwnd, element_id, 1 if visible else 0)

def set_element_enabled(hwnd, element_id, enabled=True):
    dll.EU_SetElementEnabled(hwnd, element_id, 1 if enabled else 0)

def create_input_number(hwnd, parent_id, text="InputNumber", value=10,
                        min_value=0, max_value=100, step=1,
                        x=0, y=0, w=220, h=36):
    data = make_utf8(text)
    return dll.EU_CreateInputNumber(
        hwnd, parent_id, bytes_arg(data), len(data),
        value, min_value, max_value, step, x, y, w, h
    )

def get_input_number_options(hwnd, element_id):
    min_value = ctypes.c_int()
    max_value = ctypes.c_int()
    step = ctypes.c_int()
    ok = dll.EU_GetInputNumberOptions(
        hwnd, element_id,
        ctypes.byref(min_value), ctypes.byref(max_value), ctypes.byref(step),
    )
    if not ok:
        return None
    return min_value.value, max_value.value, step.value

def set_input_number_precision(hwnd, element_id, precision):
    dll.EU_SetInputNumberPrecision(hwnd, element_id, precision)

def set_input_number_text(hwnd, element_id, value_text):
    data = make_utf8(value_text)
    return bool(dll.EU_SetInputNumberText(hwnd, element_id, bytes_arg(data), len(data)))

def get_input_number_text(hwnd, element_id):
    needed = dll.EU_GetInputNumberText(hwnd, element_id, None, 0)
    if needed <= 0:
        return ""
    buf = (ctypes.c_ubyte * (needed + 1))()
    copied = dll.EU_GetInputNumberText(hwnd, element_id, buf, needed + 1)
    raw = bytes(buf[:min(copied, needed)])
    return raw.decode("utf-8", errors="replace")

def get_input_number_state(hwnd, element_id):
    precision = ctypes.c_int()
    editing = ctypes.c_int()
    valid = ctypes.c_int()
    can_decrease = ctypes.c_int()
    can_increase = ctypes.c_int()
    ok = dll.EU_GetInputNumberState(
        hwnd, element_id,
        ctypes.byref(precision), ctypes.byref(editing), ctypes.byref(valid),
        ctypes.byref(can_decrease), ctypes.byref(can_increase),
    )
    if not ok:
        return None
    return precision.value, bool(editing.value), bool(valid.value), bool(can_decrease.value), bool(can_increase.value)

def set_input_number_step_strictly(hwnd, element_id, strict=True):
    dll.EU_SetInputNumberStepStrictly(hwnd, element_id, 1 if strict else 0)

def get_input_number_step_strictly(hwnd, element_id):
    return bool(dll.EU_GetInputNumberStepStrictly(hwnd, element_id))

def create_input(hwnd, parent_id, value="", placeholder="请输入内容",
                 prefix="", suffix="", clearable=False,
                 x=0, y=0, w=260, h=36):
    value_data = make_utf8(value)
    placeholder_data = make_utf8(placeholder)
    prefix_data = make_utf8(prefix)
    suffix_data = make_utf8(suffix)
    return dll.EU_CreateInput(
        hwnd, parent_id,
        bytes_arg(value_data), len(value_data),
        bytes_arg(placeholder_data), len(placeholder_data),
        bytes_arg(prefix_data), len(prefix_data),
        bytes_arg(suffix_data), len(suffix_data),
        1 if clearable else 0,
        x, y, w, h
    )

def set_input_value(hwnd, element_id, value=""):
    data = make_utf8(value)
    dll.EU_SetInputValue(hwnd, element_id, bytes_arg(data), len(data))

def get_input_value(hwnd, element_id, buffer_size=2048):
    buf = (ctypes.c_ubyte * buffer_size)()
    written = dll.EU_GetInputValue(hwnd, element_id, buf, buffer_size)
    if written <= 0:
        return ""
    return bytes(buf[:written]).decode("utf-8", errors="replace")

def set_input_options(hwnd, element_id, readonly=False, password=False, multiline=False, validate_state=0):
    dll.EU_SetInputOptions(
        hwnd, element_id,
        1 if readonly else 0,
        1 if password else 0,
        1 if multiline else 0,
        validate_state,
    )

def set_input_max_length(hwnd, element_id, max_length=0):
    dll.EU_SetInputMaxLength(hwnd, element_id, max_length)

def get_input_max_length(hwnd, element_id):
    return dll.EU_GetInputMaxLength(hwnd, element_id)

def get_input_state(hwnd, element_id):
    cursor = ctypes.c_int()
    length = ctypes.c_int()
    clearable = ctypes.c_int()
    readonly = ctypes.c_int()
    password = ctypes.c_int()
    multiline = ctypes.c_int()
    validate_state = ctypes.c_int()
    ok = dll.EU_GetInputState(
        hwnd, element_id,
        ctypes.byref(cursor), ctypes.byref(length), ctypes.byref(clearable),
        ctypes.byref(readonly), ctypes.byref(password), ctypes.byref(multiline),
        ctypes.byref(validate_state),
    )
    if not ok:
        return None
    return (
        cursor.value, length.value, bool(clearable.value), bool(readonly.value),
        bool(password.value), bool(multiline.value), validate_state.value,
    )

def set_input_scroll(hwnd, element_id, scroll_y=0):
    dll.EU_SetInputScroll(hwnd, element_id, scroll_y)

def get_input_scroll(hwnd, element_id):
    scroll_y = ctypes.c_int()
    max_scroll_y = ctypes.c_int()
    content_height = ctypes.c_int()
    viewport_height = ctypes.c_int()
    ok = dll.EU_GetInputScroll(
        hwnd, element_id,
        ctypes.byref(scroll_y), ctypes.byref(max_scroll_y),
        ctypes.byref(content_height), ctypes.byref(viewport_height),
    )
    if not ok:
        return None
    return {
        "scroll_y": scroll_y.value,
        "max_scroll_y": max_scroll_y.value,
        "content_height": content_height.value,
        "viewport_height": viewport_height.value,
    }

def set_input_icons(hwnd, element_id, prefix_icon="", suffix_icon=""):
    prefix_data = make_utf8(prefix_icon)
    suffix_data = make_utf8(suffix_icon)
    dll.EU_SetInputIcons(
        hwnd, element_id,
        bytes_arg(prefix_data), len(prefix_data),
        bytes_arg(suffix_data), len(suffix_data),
    )

def get_input_icons(hwnd, element_id, buffer_size=512):
    prefix = (ctypes.c_ubyte * buffer_size)()
    suffix = (ctypes.c_ubyte * buffer_size)()
    ok = dll.EU_GetInputIcons(hwnd, element_id, prefix, buffer_size, suffix, buffer_size)
    if not ok:
        return None
    return (
        bytes(prefix).split(b"\0", 1)[0].decode("utf-8", errors="replace"),
        bytes(suffix).split(b"\0", 1)[0].decode("utf-8", errors="replace"),
    )

def set_input_visual_options(hwnd, element_id, size=0, show_password_toggle=False,
                             show_word_limit=False, autosize=False,
                             min_rows=0, max_rows=0):
    dll.EU_SetInputVisualOptions(
        hwnd, element_id,
        size, 1 if show_password_toggle else 0,
        1 if show_word_limit else 0, 1 if autosize else 0,
        min_rows, max_rows,
    )

def get_input_visual_options(hwnd, element_id):
    values = [ctypes.c_int() for _ in range(6)]
    ok = dll.EU_GetInputVisualOptions(hwnd, element_id, *(ctypes.byref(v) for v in values))
    if not ok:
        return None
    keys = ["size", "show_password_toggle", "show_word_limit", "autosize", "min_rows", "max_rows"]
    state = {key: value.value for key, value in zip(keys, values)}
    for key in ("show_password_toggle", "show_word_limit", "autosize"):
        state[key] = bool(state[key])
    return state

def set_input_selection(hwnd, element_id, start=0, end=0):
    dll.EU_SetInputSelection(hwnd, element_id, start, end)

def get_input_selection(hwnd, element_id):
    start = ctypes.c_int()
    end = ctypes.c_int()
    ok = dll.EU_GetInputSelection(hwnd, element_id, ctypes.byref(start), ctypes.byref(end))
    if not ok:
        return None
    return start.value, end.value

def set_input_context_menu_enabled(hwnd, element_id, enabled=True):
    dll.EU_SetInputContextMenuEnabled(hwnd, element_id, 1 if enabled else 0)

def get_input_context_menu_enabled(hwnd, element_id):
    return bool(dll.EU_GetInputContextMenuEnabled(hwnd, element_id))

def create_input(hwnd, parent_id, value="", placeholder="请输入内容",
                 prefix="", suffix="", clearable=False,
                 size=0, prefix_icon="", suffix_icon="",
                 password=False, show_password=False,
                 show_word_limit=False, multiline=False, autosize=False,
                 min_rows=0, max_rows=0, readonly=False, validate_state=0,
                 max_length=0,
                 x=0, y=0, w=260, h=36, context_menu=True):
    if (
        type(size) is int and
        type(prefix_icon) is int and
        type(suffix_icon) is int and
        type(password) is int and
        show_password is False and
        show_word_limit is False and
        multiline is False and
        autosize is False and
        min_rows == 0 and max_rows == 0 and
        readonly is False and validate_state == 0 and max_length == 0
    ):
        x, y, w, h = size, prefix_icon, suffix_icon, password
        size = 0
        prefix_icon = ""
        suffix_icon = ""
        password = False
    value_data = make_utf8(value)
    placeholder_data = make_utf8(placeholder)
    prefix_data = make_utf8(prefix)
    suffix_data = make_utf8(suffix)
    element_id = dll.EU_CreateInput(
        hwnd, parent_id,
        bytes_arg(value_data), len(value_data),
        bytes_arg(placeholder_data), len(placeholder_data),
        bytes_arg(prefix_data), len(prefix_data),
        bytes_arg(suffix_data), len(suffix_data),
        1 if clearable else 0,
        x, y, w, h
    )
    if not element_id:
        return 0
    password_mode = bool(password or show_password)
    if prefix_icon or suffix_icon:
        set_input_icons(hwnd, element_id, prefix_icon, suffix_icon)
    if readonly or password_mode or multiline or validate_state:
        set_input_options(hwnd, element_id, readonly=readonly, password=password_mode,
                          multiline=multiline, validate_state=validate_state)
    if size or show_password or show_word_limit or autosize or min_rows or max_rows:
        set_input_visual_options(hwnd, element_id, size=size,
                                 show_password_toggle=show_password,
                                 show_word_limit=show_word_limit,
                                 autosize=autosize, min_rows=min_rows, max_rows=max_rows)
    if max_length:
        set_input_max_length(hwnd, element_id, max_length)
    if not context_menu:
        set_input_context_menu_enabled(hwnd, element_id, False)
    return element_id

def _apply_input_group_addon(hwnd, element_id, side, addon):
    addon_type = (addon or {}).get("type", "")
    if addon_type == "text":
        set_input_group_text_addon(hwnd, element_id, side, addon.get("text", ""))
    elif addon_type == "button":
        set_input_group_button_addon(
            hwnd, element_id, side,
            emoji=addon.get("emoji", ""), text=addon.get("text", ""),
            variant=addon.get("variant", 1),
        )
    elif addon_type == "select":
        set_input_group_select_addon(
            hwnd, element_id, side,
            items=addon.get("items", []),
            selected=addon.get("selected", -1),
            placeholder=addon.get("placeholder", "请选择"),
        )

def create_input_group(hwnd, parent_id, value="", placeholder="请输入内容",
                       prepend=None, append=None,
                       size=0, clearable=False, password=False,
                       show_word_limit=False, autosize=False,
                       min_rows=0, max_rows=0,
                       x=0, y=0, w=360, h=36):
    value_data = make_utf8(value)
    placeholder_data = make_utf8(placeholder)
    element_id = dll.EU_CreateInputGroup(
        hwnd, parent_id,
        bytes_arg(value_data), len(value_data),
        bytes_arg(placeholder_data), len(placeholder_data),
        size, 1 if clearable else 0, 1 if password else 0,
        1 if show_word_limit else 0, 1 if autosize else 0,
        min_rows, max_rows,
        x, y, w, h,
    )
    if not element_id:
        return 0
    if prepend:
        _apply_input_group_addon(hwnd, element_id, 0, prepend)
    if append:
        _apply_input_group_addon(hwnd, element_id, 1, append)
    return element_id

def set_input_group_value(hwnd, element_id, value=""):
    data = make_utf8(value)
    dll.EU_SetInputGroupValue(hwnd, element_id, bytes_arg(data), len(data))

def get_input_group_value(hwnd, element_id):
    needed = dll.EU_GetInputGroupValue(hwnd, element_id, None, 0)
    if needed <= 0:
        return ""
    buf = (ctypes.c_ubyte * (needed + 1))()
    dll.EU_GetInputGroupValue(hwnd, element_id, buf, needed + 1)
    return bytes(buf[:needed]).decode("utf-8", errors="replace")

def set_input_group_options(hwnd, element_id, size=0, clearable=False, password=False,
                            show_word_limit=False, autosize=False,
                            min_rows=0, max_rows=0):
    dll.EU_SetInputGroupOptions(
        hwnd, element_id,
        size, 1 if clearable else 0, 1 if password else 0,
        1 if show_word_limit else 0, 1 if autosize else 0,
        min_rows, max_rows,
    )

def get_input_group_options(hwnd, element_id):
    values = [ctypes.c_int() for _ in range(7)]
    ok = dll.EU_GetInputGroupOptions(hwnd, element_id, *(ctypes.byref(v) for v in values))
    if not ok:
        return None
    keys = ["size", "clearable", "password", "show_word_limit", "autosize", "min_rows", "max_rows"]
    state = {key: value.value for key, value in zip(keys, values)}
    for key in ("clearable", "password", "show_word_limit", "autosize"):
        state[key] = bool(state[key])
    return state

def set_input_group_text_addon(hwnd, element_id, side, text=""):
    data = make_utf8(text)
    dll.EU_SetInputGroupTextAddon(hwnd, element_id, side, bytes_arg(data), len(data))

def set_input_group_button_addon(hwnd, element_id, side, emoji="", text="", variant=1):
    emoji_data = make_utf8(emoji)
    text_data = make_utf8(text)
    dll.EU_SetInputGroupButtonAddon(
        hwnd, element_id, side,
        bytes_arg(emoji_data), len(emoji_data),
        bytes_arg(text_data), len(text_data),
        variant,
    )

def set_input_group_select_addon(hwnd, element_id, side, items=None, selected=-1, placeholder="请选择"):
    items_data = _input_group_select_items_data(items or [])
    placeholder_data = make_utf8(placeholder)
    dll.EU_SetInputGroupSelectAddon(
        hwnd, element_id, side,
        bytes_arg(items_data), len(items_data),
        selected,
        bytes_arg(placeholder_data), len(placeholder_data),
    )

def clear_input_group_addon(hwnd, element_id, side):
    dll.EU_ClearInputGroupAddon(hwnd, element_id, side)

def get_input_group_input_element_id(hwnd, element_id):
    return dll.EU_GetInputGroupInputElementId(hwnd, element_id)

def get_input_group_addon_element_id(hwnd, element_id, side):
    return dll.EU_GetInputGroupAddonElementId(hwnd, element_id, side)

def create_input_tag(hwnd, parent_id, tags=None, placeholder="输入标签，回车提交",
                     x=0, y=0, w=360, h=84):
    if tags is None:
        tags = ["鍓嶇", "璁捐"]
    tags_data = make_utf8("|".join(tags))
    placeholder_data = make_utf8(placeholder)
    return dll.EU_CreateInputTag(
        hwnd, parent_id,
        bytes_arg(tags_data), len(tags_data),
        bytes_arg(placeholder_data), len(placeholder_data),
        x, y, w, h
    )

def set_input_tag_options(hwnd, element_id, max_count=0, allow_duplicates=False):
    dll.EU_SetInputTagOptions(hwnd, element_id, max_count, 1 if allow_duplicates else 0)

def get_input_tag_count(hwnd, element_id):
    return dll.EU_GetInputTagCount(hwnd, element_id)

def get_input_tag_options(hwnd, element_id):
    max_count = ctypes.c_int()
    allow_duplicates = ctypes.c_int()
    ok = dll.EU_GetInputTagOptions(
        hwnd, element_id, ctypes.byref(max_count), ctypes.byref(allow_duplicates)
    )
    if not ok:
        return None
    return max_count.value, bool(allow_duplicates.value)

def add_input_tag_item(hwnd, element_id, tag):
    data = make_utf8(tag)
    return bool(dll.EU_AddInputTagItem(hwnd, element_id, bytes_arg(data), len(data)))

def remove_input_tag_item(hwnd, element_id, index):
    return bool(dll.EU_RemoveInputTagItem(hwnd, element_id, index))

def set_input_tag_input_value(hwnd, element_id, value):
    data = make_utf8(value)
    dll.EU_SetInputTagInputValue(hwnd, element_id, bytes_arg(data), len(data))

def get_input_tag_input_value(hwnd, element_id):
    needed = dll.EU_GetInputTagInputValue(hwnd, element_id, None, 0)
    if needed <= 0:
        return ""
    buf = (ctypes.c_ubyte * (needed + 1))()
    dll.EU_GetInputTagInputValue(hwnd, element_id, buf, needed + 1)
    return bytes(buf[:needed]).decode("utf-8", errors="replace")

def get_input_tag_item(hwnd, element_id, index):
    needed = dll.EU_GetInputTagItem(hwnd, element_id, index, None, 0)
    if needed <= 0:
        return ""
    buf = (ctypes.c_ubyte * (needed + 1))()
    dll.EU_GetInputTagItem(hwnd, element_id, index, buf, needed + 1)
    return bytes(buf[:needed]).decode("utf-8", errors="replace")

def create_select(hwnd, parent_id, text="Select", options=None, selected=0,
                  x=0, y=0, w=220, h=36):
    if options is None:
        options = ["Option A", "Option B"]
    label_data = make_utf8(text)
    options_data = make_utf8("|".join(options))
    return dll.EU_CreateSelect(
        hwnd, parent_id,
        bytes_arg(label_data), len(label_data),
        bytes_arg(options_data), len(options_data),
        selected, x, y, w, h
    )

def set_select_options(hwnd, element_id, options=None):
    if options is None:
        options = ["选项一", "选项二"]
    data = make_utf8("|".join(options))
    dll.EU_SetSelectOptions(hwnd, element_id, bytes_arg(data), len(data))

def set_select_index(hwnd, element_id, index=0):
    dll.EU_SetSelectIndex(hwnd, element_id, index)

def get_select_index(hwnd, element_id):
    return dll.EU_GetSelectIndex(hwnd, element_id)

def set_select_open(hwnd, element_id, open=True):
    dll.EU_SetSelectOpen(hwnd, element_id, 1 if open else 0)

def get_select_open(hwnd, element_id):
    return dll.EU_GetSelectOpen(hwnd, element_id)

def set_select_search(hwnd, element_id, query=""):
    data = make_utf8(query)
    dll.EU_SetSelectSearch(hwnd, element_id, bytes_arg(data), len(data))

def set_select_option_disabled(hwnd, element_id, option_index=0, disabled=True):
    dll.EU_SetSelectOptionDisabled(hwnd, element_id, option_index, 1 if disabled else 0)

def set_select_option_alignment(hwnd, element_id, alignment=0):
    dll.EU_SetSelectOptionAlignment(hwnd, element_id, alignment)

def get_select_option_alignment(hwnd, element_id):
    return dll.EU_GetSelectOptionAlignment(hwnd, element_id)

def set_select_value_alignment(hwnd, element_id, alignment=0):
    dll.EU_SetSelectValueAlignment(hwnd, element_id, alignment)

def get_select_value_alignment(hwnd, element_id):
    return dll.EU_GetSelectValueAlignment(hwnd, element_id)

def get_select_option_count(hwnd, element_id):
    return dll.EU_GetSelectOptionCount(hwnd, element_id)

def get_select_matched_count(hwnd, element_id):
    return dll.EU_GetSelectMatchedCount(hwnd, element_id)

def get_select_option_disabled(hwnd, element_id, option_index=0):
    return dll.EU_GetSelectOptionDisabled(hwnd, element_id, option_index)

def set_select_multiple(hwnd, element_id, multiple=True):
    dll.EU_SetSelectMultiple(hwnd, element_id, 1 if multiple else 0)

def get_select_multiple(hwnd, element_id):
    return bool(dll.EU_GetSelectMultiple(hwnd, element_id))

def set_select_selected_indices(hwnd, element_id, indices=None):
    if indices is None:
        indices = []
    data = make_utf8("|".join(str(i) for i in indices))
    dll.EU_SetSelectSelectedIndices(hwnd, element_id, bytes_arg(data), len(data))

def get_select_selected_count(hwnd, element_id):
    return dll.EU_GetSelectSelectedCount(hwnd, element_id)

def get_select_selected_at(hwnd, element_id, position):
    return dll.EU_GetSelectSelectedAt(hwnd, element_id, position)

def get_select_selected_indices(hwnd, element_id):
    count = get_select_selected_count(hwnd, element_id)
    return [get_select_selected_at(hwnd, element_id, i) for i in range(count)]

def create_select_v2(hwnd, parent_id, text="SelectV2", options=None, selected=0,
                     visible_count=7, x=0, y=0, w=260, h=36):
    if options is None:
        options = [f"Option {i}" for i in range(1, 21)]
    label_data = make_utf8(text)
    options_data = make_utf8("|".join(options))
    return dll.EU_CreateSelectV2(
        hwnd, parent_id,
        bytes_arg(label_data), len(label_data),
        bytes_arg(options_data), len(options_data),
        selected, visible_count, x, y, w, h
    )

def set_select_v2_options(hwnd, element_id, options=None):
    if options is None:
        options = [f"选项 {i}" for i in range(1, 21)]
    data = make_utf8("|".join(options))
    dll.EU_SetSelectV2Options(hwnd, element_id, bytes_arg(data), len(data))

def set_select_v2_index(hwnd, element_id, index=0):
    dll.EU_SetSelectV2Index(hwnd, element_id, index)

def get_select_v2_index(hwnd, element_id):
    return dll.EU_GetSelectV2Index(hwnd, element_id)

def set_select_v2_visible_count(hwnd, element_id, visible_count=7):
    dll.EU_SetSelectV2VisibleCount(hwnd, element_id, visible_count)

def get_select_v2_visible_count(hwnd, element_id):
    return dll.EU_GetSelectV2VisibleCount(hwnd, element_id)

def set_select_v2_open(hwnd, element_id, open=True):
    dll.EU_SetSelectV2Open(hwnd, element_id, 1 if open else 0)

def get_select_v2_open(hwnd, element_id):
    return dll.EU_GetSelectV2Open(hwnd, element_id)

def set_select_v2_search(hwnd, element_id, query=""):
    data = make_utf8(query)
    dll.EU_SetSelectV2Search(hwnd, element_id, bytes_arg(data), len(data))

def set_select_v2_option_disabled(hwnd, element_id, option_index=0, disabled=True):
    dll.EU_SetSelectV2OptionDisabled(hwnd, element_id, option_index, 1 if disabled else 0)

def set_select_v2_option_alignment(hwnd, element_id, alignment=0):
    dll.EU_SetSelectV2OptionAlignment(hwnd, element_id, alignment)

def get_select_v2_option_alignment(hwnd, element_id):
    return dll.EU_GetSelectV2OptionAlignment(hwnd, element_id)

def set_select_v2_value_alignment(hwnd, element_id, alignment=0):
    dll.EU_SetSelectV2ValueAlignment(hwnd, element_id, alignment)

def get_select_v2_value_alignment(hwnd, element_id):
    return dll.EU_GetSelectV2ValueAlignment(hwnd, element_id)

def get_select_v2_option_count(hwnd, element_id):
    return dll.EU_GetSelectV2OptionCount(hwnd, element_id)

def get_select_v2_matched_count(hwnd, element_id):
    return dll.EU_GetSelectV2MatchedCount(hwnd, element_id)

def get_select_v2_option_disabled(hwnd, element_id, option_index=0):
    return dll.EU_GetSelectV2OptionDisabled(hwnd, element_id, option_index)

def set_select_v2_scroll_index(hwnd, element_id, scroll_index=0):
    dll.EU_SetSelectV2ScrollIndex(hwnd, element_id, scroll_index)

def get_select_v2_scroll_index(hwnd, element_id):
    return dll.EU_GetSelectV2ScrollIndex(hwnd, element_id)

def create_rate(hwnd, parent_id, text="Rate", value=3, max_value=5,
                x=0, y=0, w=220, h=36,
                allow_clear=None, allow_half=None, readonly=None, value_x2=None,
                colors=None, icons=None, text_items=None, show_text=None,
                show_score=None, text_color=0, score_template="{value}"):
    data = make_utf8(text)
    element_id = dll.EU_CreateRate(
        hwnd, parent_id, bytes_arg(data), len(data),
        value, max_value, x, y, w, h
    )
    if element_id and (allow_clear is not None or allow_half is not None or readonly is not None):
        dll.EU_SetRateOptions(
            hwnd, element_id,
            1 if allow_clear is None else int(bool(allow_clear)),
            0 if allow_half is None else int(bool(allow_half)),
            0 if readonly is None else int(bool(readonly)),
        )
    if element_id and value_x2 is not None:
        dll.EU_SetRateValueX2(hwnd, element_id, value_x2)
    if element_id and colors:
        set_rate_colors(hwnd, element_id, *colors)
    if element_id and icons:
        set_rate_icons(hwnd, element_id, **icons)
    if element_id and text_items:
        set_rate_text_items(hwnd, element_id, text_items)
    if element_id and (show_text is not None or show_score is not None or text_color or score_template != "{value}"):
        set_rate_display_options(
            hwnd, element_id,
            show_text=bool(show_text),
            show_score=bool(show_score),
            text_color=text_color,
            score_template=score_template,
        )
    return element_id

def set_rate_value(hwnd, element_id, value=0):
    dll.EU_SetRateValue(hwnd, element_id, value)

def get_rate_value(hwnd, element_id):
    return dll.EU_GetRateValue(hwnd, element_id)

def set_rate_max(hwnd, element_id, max_value=5):
    dll.EU_SetRateMax(hwnd, element_id, max_value)

def get_rate_max(hwnd, element_id):
    return dll.EU_GetRateMax(hwnd, element_id)

def set_rate_value_x2(hwnd, element_id, value_x2=0):
    dll.EU_SetRateValueX2(hwnd, element_id, value_x2)

def get_rate_value_x2(hwnd, element_id):
    return dll.EU_GetRateValueX2(hwnd, element_id)

def set_rate_options(hwnd, element_id, allow_clear=True, allow_half=False, readonly=False):
    dll.EU_SetRateOptions(
        hwnd, element_id,
        1 if allow_clear else 0,
        1 if allow_half else 0,
        1 if readonly else 0,
    )

def get_rate_options(hwnd, element_id):
    allow_clear = ctypes.c_int()
    allow_half = ctypes.c_int()
    readonly = ctypes.c_int()
    show_score = ctypes.c_int()
    ok = dll.EU_GetRateOptions(
        hwnd, element_id,
        ctypes.byref(allow_clear), ctypes.byref(allow_half),
        ctypes.byref(readonly), ctypes.byref(show_score)
    )
    if not ok:
        return None
    return bool(allow_clear.value), bool(allow_half.value), bool(readonly.value), bool(show_score.value)

def set_rate_texts(hwnd, element_id, low_text="待评分", high_text="已评分", show_score=True):
    low_data = make_utf8(low_text)
    high_data = make_utf8(high_text)
    dll.EU_SetRateTexts(
        hwnd, element_id,
        bytes_arg(low_data), len(low_data),
        bytes_arg(high_data), len(high_data),
        1 if show_score else 0
    )

def set_rate_change_callback(hwnd, element_id, callback):
    dll.EU_SetRateChangeCallback(hwnd, element_id, callback)

def set_rate_colors(hwnd, element_id, low_color=0, mid_color=0, high_color=0):
    dll.EU_SetRateColors(hwnd, element_id, low_color, mid_color, high_color)

def get_rate_colors(hwnd, element_id):
    low = ctypes.c_uint32()
    mid = ctypes.c_uint32()
    high = ctypes.c_uint32()
    ok = dll.EU_GetRateColors(hwnd, element_id, ctypes.byref(low), ctypes.byref(mid), ctypes.byref(high))
    if not ok:
        return None
    return low.value, mid.value, high.value

def set_rate_icons(hwnd, element_id, full_icon="★", void_icon="☆",
                   low_icon="", mid_icon="", high_icon=""):
    full_data = make_utf8(full_icon)
    void_data = make_utf8(void_icon)
    low_data = make_utf8(low_icon)
    mid_data = make_utf8(mid_icon)
    high_data = make_utf8(high_icon)
    dll.EU_SetRateIcons(
        hwnd, element_id,
        bytes_arg(full_data), len(full_data),
        bytes_arg(void_data), len(void_data),
        bytes_arg(low_data), len(low_data),
        bytes_arg(mid_data), len(mid_data),
        bytes_arg(high_data), len(high_data),
    )

def get_rate_icons(hwnd, element_id):
    buffers = [ctypes.create_string_buffer(64) for _ in range(5)]
    ptrs = [ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte)) for buffer in buffers]
    ok = dll.EU_GetRateIcons(
        hwnd, element_id,
        ptrs[0], len(buffers[0]),
        ptrs[1], len(buffers[1]),
        ptrs[2], len(buffers[2]),
        ptrs[3], len(buffers[3]),
        ptrs[4], len(buffers[4]),
    )
    if not ok:
        return None
    return tuple(buffer.value.decode("utf-8") for buffer in buffers)

def set_rate_text_items(hwnd, element_id, items):
    data = make_utf8("\n".join(items or []))
    dll.EU_SetRateTextItems(hwnd, element_id, bytes_arg(data), len(data))

def set_rate_display_options(hwnd, element_id, show_text=False, show_score=False,
                             text_color=0, score_template="{value}"):
    data = make_utf8(score_template)
    dll.EU_SetRateDisplayOptions(
        hwnd, element_id,
        1 if show_text else 0,
        1 if show_score else 0,
        text_color,
        bytes_arg(data), len(data),
    )

def get_rate_display_options(hwnd, element_id):
    show_text = ctypes.c_int()
    show_score = ctypes.c_int()
    text_color = ctypes.c_uint32()
    template = ctypes.create_string_buffer(256)
    template_ptr = ctypes.cast(template, ctypes.POINTER(ctypes.c_ubyte))
    ok = dll.EU_GetRateDisplayOptions(
        hwnd, element_id,
        ctypes.byref(show_text), ctypes.byref(show_score), ctypes.byref(text_color),
        template_ptr, len(template),
    )
    if not ok:
        return None
    return bool(show_text.value), bool(show_score.value), text_color.value, template.value.decode("utf-8")

def create_colorpicker(hwnd, parent_id, text="颜色", color=0xFF1E66F5,
                       x=0, y=0, w=220, h=36, alpha=None, open_panel=None,
                       palette=None, show_alpha=False, size=0, clearable=True):
    data = make_utf8(text)
    initial_color = 0xFF1E66F5 if color is None else color
    element_id = dll.EU_CreateColorPicker(
        hwnd, parent_id, bytes_arg(data), len(data),
        initial_color, x, y, w, h
    )
    if element_id:
        dll.EU_SetColorPickerOptions(
            hwnd, element_id,
            1 if show_alpha else 0,
            int(size),
            1 if clearable else 0,
        )
    if element_id and color is None:
        dll.EU_ClearColorPicker(hwnd, element_id)
    if element_id and palette:
        arr = (ctypes.c_uint32 * len(palette))(*palette)
        dll.EU_SetColorPickerPalette(hwnd, element_id, arr, len(palette))
    if element_id and alpha is not None:
        dll.EU_SetColorPickerAlpha(hwnd, element_id, alpha)
    if element_id and open_panel is not None:
        dll.EU_SetColorPickerOpen(hwnd, element_id, int(bool(open_panel)))
    return element_id

def set_colorpicker_color(hwnd, element_id, color=0xFF1E66F5):
    dll.EU_SetColorPickerColor(hwnd, element_id, color)

def get_colorpicker_color(hwnd, element_id):
    return dll.EU_GetColorPickerColor(hwnd, element_id)

def set_colorpicker_alpha(hwnd, element_id, alpha=255):
    dll.EU_SetColorPickerAlpha(hwnd, element_id, alpha)

def get_colorpicker_alpha(hwnd, element_id):
    return dll.EU_GetColorPickerAlpha(hwnd, element_id)

def set_colorpicker_hex(hwnd, element_id, value="#1E66F5"):
    data = make_utf8(value)
    return bool(dll.EU_SetColorPickerHex(hwnd, element_id, bytes_arg(data), len(data)))

def get_colorpicker_hex(hwnd, element_id):
    needed = dll.EU_GetColorPickerHex(hwnd, element_id, None, 0)
    if needed <= 0:
        return ""
    buf = (ctypes.c_ubyte * (needed + 1))()
    dll.EU_GetColorPickerHex(hwnd, element_id, buf, needed + 1)
    return bytes(buf[:needed]).decode("utf-8", errors="replace")

def set_colorpicker_open(hwnd, element_id, open=True):
    dll.EU_SetColorPickerOpen(hwnd, element_id, 1 if open else 0)

def get_colorpicker_open(hwnd, element_id):
    return dll.EU_GetColorPickerOpen(hwnd, element_id)

def set_colorpicker_palette(hwnd, element_id, palette=None):
    if palette is None:
        palette = [0xFF1E66F5, 0xFF43A047, 0xFFFFB300, 0xFFE53935]
    arr = (ctypes.c_uint32 * len(palette))(*palette)
    dll.EU_SetColorPickerPalette(hwnd, element_id, arr, len(palette))

def get_colorpicker_palette_count(hwnd, element_id):
    return dll.EU_GetColorPickerPaletteCount(hwnd, element_id)

def set_colorpicker_options(hwnd, element_id, show_alpha=False, size=0, clearable=True):
    dll.EU_SetColorPickerOptions(
        hwnd, element_id,
        1 if show_alpha else 0,
        int(size),
        1 if clearable else 0,
    )

def get_colorpicker_options(hwnd, element_id):
    show_alpha = ctypes.c_int()
    size = ctypes.c_int()
    clearable = ctypes.c_int()
    ok = dll.EU_GetColorPickerOptions(
        hwnd, element_id,
        ctypes.byref(show_alpha), ctypes.byref(size), ctypes.byref(clearable)
    )
    if not ok:
        return None
    return {
        "show_alpha": bool(show_alpha.value),
        "size": size.value,
        "clearable": bool(clearable.value),
    }

def clear_colorpicker(hwnd, element_id):
    dll.EU_ClearColorPicker(hwnd, element_id)

def get_colorpicker_has_value(hwnd, element_id):
    return bool(dll.EU_GetColorPickerHasValue(hwnd, element_id))

def set_colorpicker_change_callback(hwnd, element_id, callback):
    dll.EU_SetColorPickerChangeCallback(hwnd, element_id, callback)

def create_tag(hwnd, parent_id, text="标签 🏷️", tag_type=0, effect=0, closable=False,
               x=0, y=0, w=120, h=30, closed=None):
    data = make_utf8(text)
    element_id = dll.EU_CreateTag(
        hwnd, parent_id, bytes_arg(data), len(data),
        tag_type, effect, 1 if closable else 0, x, y, w, h
    )
    if element_id and closed is not None:
        dll.EU_SetTagClosed(hwnd, element_id, int(bool(closed)))
    return element_id

def set_tag_type(hwnd, element_id, tag_type=0):
    dll.EU_SetTagType(hwnd, element_id, tag_type)

def set_tag_effect(hwnd, element_id, effect=0):
    dll.EU_SetTagEffect(hwnd, element_id, effect)

def set_tag_closable(hwnd, element_id, closable=True):
    dll.EU_SetTagClosable(hwnd, element_id, 1 if closable else 0)

def set_tag_closed(hwnd, element_id, closed=True):
    dll.EU_SetTagClosed(hwnd, element_id, 1 if closed else 0)

def get_tag_closed(hwnd, element_id):
    return dll.EU_GetTagClosed(hwnd, element_id)

def get_tag_options(hwnd, element_id):
    tag_type = ctypes.c_int()
    effect = ctypes.c_int()
    closable = ctypes.c_int()
    closed = ctypes.c_int()
    ok = dll.EU_GetTagOptions(
        hwnd, element_id,
        ctypes.byref(tag_type), ctypes.byref(effect),
        ctypes.byref(closable), ctypes.byref(closed)
    )
    if not ok:
        return None
    return tag_type.value, effect.value, bool(closable.value), bool(closed.value)

def set_tag_size(hwnd, element_id, size_preset=1):
    dll.EU_SetTagSize(hwnd, element_id, size_preset)

def set_tag_theme_color(hwnd, element_id, color=0xFF409EFF):
    dll.EU_SetTagThemeColor(hwnd, element_id, color)

def get_tag_visual_options(hwnd, element_id):
    size_preset = ctypes.c_int()
    theme_color = ctypes.c_uint32()
    ok = dll.EU_GetTagVisualOptions(
        hwnd, element_id, ctypes.byref(size_preset), ctypes.byref(theme_color)
    )
    if not ok:
        return None
    return size_preset.value, theme_color.value

def set_tag_close_callback(hwnd, element_id, callback):
    dll.EU_SetTagCloseCallback(hwnd, element_id, callback)

def create_badge(hwnd, parent_id, text="Badge", value="12", max_value=99, dot=False,
                 x=0, y=0, w=180, h=34, show_zero=None, offset_x=0, offset_y=0,
                 placement=None, standalone=None, badge_type=None):
    text_data = make_utf8(text)
    value_data = make_utf8(value)
    element_id = dll.EU_CreateBadge(
        hwnd, parent_id,
        bytes_arg(text_data), len(text_data),
        bytes_arg(value_data), len(value_data),
        max_value, 1 if dot else 0, x, y, w, h
    )
    if element_id and (show_zero is not None or offset_x or offset_y):
        dll.EU_SetBadgeOptions(hwnd, element_id, int(bool(dot)),
                               1 if show_zero is None else int(bool(show_zero)),
                               offset_x, offset_y)
    if element_id and badge_type is not None:
        dll.EU_SetBadgeType(hwnd, element_id, badge_type)
    if element_id and (placement is not None or standalone is not None):
        dll.EU_SetBadgeLayoutOptions(
            hwnd, element_id,
            0 if placement is None else placement,
            0 if standalone is None else int(bool(standalone))
        )
    return element_id

def set_badge_value(hwnd, element_id, value="12"):
    data = make_utf8(value)
    dll.EU_SetBadgeValue(hwnd, element_id, bytes_arg(data), len(data))

def set_badge_max(hwnd, element_id, max_value=99):
    dll.EU_SetBadgeMax(hwnd, element_id, max_value)

def set_badge_type(hwnd, element_id, badge_type=0):
    dll.EU_SetBadgeType(hwnd, element_id, badge_type)

def set_badge_dot(hwnd, element_id, dot=True):
    dll.EU_SetBadgeDot(hwnd, element_id, 1 if dot else 0)

def set_badge_options(hwnd, element_id, dot=False, show_zero=True, offset_x=0, offset_y=0):
    dll.EU_SetBadgeOptions(
        hwnd, element_id, 1 if dot else 0, 1 if show_zero else 0, offset_x, offset_y
    )

def get_badge_hidden(hwnd, element_id):
    return dll.EU_GetBadgeHidden(hwnd, element_id)

def get_badge_options(hwnd, element_id):
    max_value = ctypes.c_int()
    dot = ctypes.c_int()
    show_zero = ctypes.c_int()
    offset_x = ctypes.c_int()
    offset_y = ctypes.c_int()
    ok = dll.EU_GetBadgeOptions(
        hwnd, element_id,
        ctypes.byref(max_value), ctypes.byref(dot), ctypes.byref(show_zero),
        ctypes.byref(offset_x), ctypes.byref(offset_y)
    )
    if not ok:
        return None
    return max_value.value, bool(dot.value), bool(show_zero.value), offset_x.value, offset_y.value

def get_badge_type(hwnd, element_id):
    return dll.EU_GetBadgeType(hwnd, element_id)

def set_badge_layout_options(hwnd, element_id, placement=0, standalone=False):
    dll.EU_SetBadgeLayoutOptions(hwnd, element_id, placement, 1 if standalone else 0)

def get_badge_layout_options(hwnd, element_id):
    placement = ctypes.c_int()
    standalone = ctypes.c_int()
    ok = dll.EU_GetBadgeLayoutOptions(hwnd, element_id, ctypes.byref(placement), ctypes.byref(standalone))
    if not ok:
        return None
    return placement.value, bool(standalone.value)

def _progress_color_stops_text(color_stops):
    if isinstance(color_stops, str):
        return color_stops
    rows = []
    for color, percentage in (color_stops or []):
        rows.append(f"0x{int(color) & 0xFFFFFFFF:08X}\t{int(percentage)}")
    return "|".join(rows)


def create_progress(hwnd, parent_id, text="Progress", percentage=70, status=0,
                    x=0, y=0, w=320, h=34,
                    progress_type=None, stroke_width=None, show_text=None,
                    text_format=None, striped=None,
                    text_inside=None, fill_color=None, track_color=None, text_color=None,
                    color_stops=None, complete_text=None, text_template=None):
    data = make_utf8(text)
    element_id = dll.EU_CreateProgress(
        hwnd, parent_id, bytes_arg(data), len(data),
        percentage, status, x, y, w, h
    )
    if element_id and (progress_type is not None or stroke_width is not None or show_text is not None):
        dll.EU_SetProgressOptions(hwnd, element_id,
                                  0 if progress_type is None else progress_type,
                                  0 if stroke_width is None else stroke_width,
                                  1 if show_text is None else int(bool(show_text)))
    if element_id and (text_format is not None or striped is not None):
        dll.EU_SetProgressFormatOptions(
            hwnd, element_id,
            0 if text_format is None else text_format,
            0 if striped is None else int(bool(striped))
        )
    if element_id and text_inside is not None:
        dll.EU_SetProgressTextInside(hwnd, element_id, 1 if text_inside else 0)
    if element_id and (fill_color is not None or track_color is not None or text_color is not None):
        dll.EU_SetProgressColors(
            hwnd, element_id,
            0 if fill_color is None else int(fill_color),
            0 if track_color is None else int(track_color),
            0 if text_color is None else int(text_color)
        )
    if element_id and color_stops is not None:
        data = make_utf8(_progress_color_stops_text(color_stops))
        dll.EU_SetProgressColorStops(hwnd, element_id, bytes_arg(data), len(data))
    if element_id and complete_text is not None:
        data = make_utf8(complete_text)
        dll.EU_SetProgressCompleteText(hwnd, element_id, bytes_arg(data), len(data))
    if element_id and text_template is not None:
        data = make_utf8(text_template)
        dll.EU_SetProgressTextTemplate(hwnd, element_id, bytes_arg(data), len(data))
    return element_id

def set_progress_percentage(hwnd, element_id, percentage=0):
    dll.EU_SetProgressPercentage(hwnd, element_id, percentage)

def get_progress_percentage(hwnd, element_id):
    return dll.EU_GetProgressPercentage(hwnd, element_id)

def set_progress_status(hwnd, element_id, status=0):
    dll.EU_SetProgressStatus(hwnd, element_id, status)

def get_progress_status(hwnd, element_id):
    return dll.EU_GetProgressStatus(hwnd, element_id)

def set_progress_show_text(hwnd, element_id, show_text=True):
    dll.EU_SetProgressShowText(hwnd, element_id, 1 if show_text else 0)

def set_progress_options(hwnd, element_id, progress_type=0, stroke_width=0, show_text=True):
    dll.EU_SetProgressOptions(hwnd, element_id, progress_type, stroke_width, 1 if show_text else 0)

def get_progress_options(hwnd, element_id):
    progress_type = ctypes.c_int()
    stroke_width = ctypes.c_int()
    show_text = ctypes.c_int()
    ok = dll.EU_GetProgressOptions(
        hwnd, element_id,
        ctypes.byref(progress_type), ctypes.byref(stroke_width), ctypes.byref(show_text)
    )
    if not ok:
        return None
    return progress_type.value, stroke_width.value, bool(show_text.value)

def set_progress_format_options(hwnd, element_id, text_format=0, striped=False):
    dll.EU_SetProgressFormatOptions(hwnd, element_id, text_format, 1 if striped else 0)

def get_progress_format_options(hwnd, element_id):
    text_format = ctypes.c_int()
    striped = ctypes.c_int()
    ok = dll.EU_GetProgressFormatOptions(
        hwnd, element_id, ctypes.byref(text_format), ctypes.byref(striped)
    )
    if not ok:
        return None
    return text_format.value, bool(striped.value)

def set_progress_text_inside(hwnd, element_id, text_inside=True):
    dll.EU_SetProgressTextInside(hwnd, element_id, 1 if text_inside else 0)

def get_progress_text_inside(hwnd, element_id):
    return bool(dll.EU_GetProgressTextInside(hwnd, element_id))

def set_progress_colors(hwnd, element_id, fill=0, track=0, text=0):
    dll.EU_SetProgressColors(hwnd, element_id, int(fill), int(track), int(text))

def get_progress_colors(hwnd, element_id):
    fill = ctypes.c_uint32()
    track = ctypes.c_uint32()
    text = ctypes.c_uint32()
    ok = dll.EU_GetProgressColors(hwnd, element_id, ctypes.byref(fill), ctypes.byref(track), ctypes.byref(text))
    return (fill.value, track.value, text.value) if ok else None

def set_progress_color_stops(hwnd, element_id, color_stops):
    data = make_utf8(_progress_color_stops_text(color_stops))
    dll.EU_SetProgressColorStops(hwnd, element_id, bytes_arg(data), len(data))

def get_progress_color_stop_count(hwnd, element_id):
    return dll.EU_GetProgressColorStopCount(hwnd, element_id)

def get_progress_color_stop(hwnd, element_id, index):
    color = ctypes.c_uint32()
    percentage = ctypes.c_int()
    ok = dll.EU_GetProgressColorStop(hwnd, element_id, index, ctypes.byref(color), ctypes.byref(percentage))
    return (color.value, percentage.value) if ok else None

def set_progress_complete_text(hwnd, element_id, text="满"):
    data = make_utf8(text)
    dll.EU_SetProgressCompleteText(hwnd, element_id, bytes_arg(data), len(data))

def get_progress_complete_text(hwnd, element_id, buffer_size=256):
    buf = (ctypes.c_ubyte * buffer_size)()
    needed = dll.EU_GetProgressCompleteText(hwnd, element_id, buf, buffer_size)
    if needed <= 0:
        return ""
    return bytes(buf[:min(needed, buffer_size - 1)]).decode("utf-8", errors="replace")

def set_progress_text_template(hwnd, element_id, text="{percent}"):
    data = make_utf8(text)
    dll.EU_SetProgressTextTemplate(hwnd, element_id, bytes_arg(data), len(data))

def get_progress_text_template(hwnd, element_id, buffer_size=256):
    buf = (ctypes.c_ubyte * buffer_size)()
    needed = dll.EU_GetProgressTextTemplate(hwnd, element_id, buf, buffer_size)
    if needed <= 0:
        return ""
    return bytes(buf[:min(needed, buffer_size - 1)]).decode("utf-8", errors="replace")

def create_avatar(hwnd, parent_id, text="A", shape=0,
                  x=0, y=0, w=44, h=44, source="", fit=None,
                  fallback_source="", icon="", error_text=""):
    data = make_utf8(text)
    element_id = dll.EU_CreateAvatar(
        hwnd, parent_id, bytes_arg(data), len(data),
        shape, x, y, w, h
    )
    if element_id and source:
        src_data = make_utf8(source)
        dll.EU_SetAvatarSource(hwnd, element_id, bytes_arg(src_data), len(src_data))
    if element_id and fallback_source:
        fallback_data = make_utf8(fallback_source)
        dll.EU_SetAvatarFallbackSource(hwnd, element_id, bytes_arg(fallback_data), len(fallback_data))
    if element_id and icon:
        icon_data = make_utf8(icon)
        dll.EU_SetAvatarIcon(hwnd, element_id, bytes_arg(icon_data), len(icon_data))
    if element_id and error_text:
        error_data = make_utf8(error_text)
        dll.EU_SetAvatarErrorText(hwnd, element_id, bytes_arg(error_data), len(error_data))
    if element_id and fit is not None:
        dll.EU_SetAvatarFit(hwnd, element_id, _image_fit_value(fit))
    return element_id

def set_avatar_shape(hwnd, element_id, shape=0):
    dll.EU_SetAvatarShape(hwnd, element_id, shape)

def set_avatar_source(hwnd, element_id, source=""):
    data = make_utf8(source)
    dll.EU_SetAvatarSource(hwnd, element_id, bytes_arg(data), len(data))

def set_avatar_fallback_source(hwnd, element_id, source=""):
    data = make_utf8(source)
    dll.EU_SetAvatarFallbackSource(hwnd, element_id, bytes_arg(data), len(data))

def set_avatar_icon(hwnd, element_id, icon=""):
    data = make_utf8(icon)
    dll.EU_SetAvatarIcon(hwnd, element_id, bytes_arg(data), len(data))

def set_avatar_error_text(hwnd, element_id, text=""):
    data = make_utf8(text)
    dll.EU_SetAvatarErrorText(hwnd, element_id, bytes_arg(data), len(data))

def set_avatar_fit(hwnd, element_id, fit=0):
    dll.EU_SetAvatarFit(hwnd, element_id, _image_fit_value(fit))

def get_avatar_image_status(hwnd, element_id):
    return dll.EU_GetAvatarImageStatus(hwnd, element_id)

def get_avatar_options(hwnd, element_id):
    shape = ctypes.c_int()
    fit = ctypes.c_int()
    ok = dll.EU_GetAvatarOptions(hwnd, element_id, ctypes.byref(shape), ctypes.byref(fit))
    if not ok:
        return None
    return shape.value, fit.value

def create_empty(hwnd, parent_id, title="暂无数据 📭", description="",
                 x=0, y=0, w=220, h=100, icon=None, action=None,
                 image="", image_size=0):
    title_data = make_utf8(title)
    desc_data = make_utf8(description)
    element_id = dll.EU_CreateEmpty(
        hwnd, parent_id,
        bytes_arg(title_data), len(title_data),
        bytes_arg(desc_data), len(desc_data),
        x, y, w, h
    )
    if element_id and (icon is not None or action is not None):
        icon_data = make_utf8("📭" if icon is None else icon)
        action_data = make_utf8("" if action is None else action)
        dll.EU_SetEmptyOptions(hwnd, element_id,
                               bytes_arg(icon_data), len(icon_data),
                               bytes_arg(action_data), len(action_data))
    if element_id and image:
        image_data = make_utf8(image)
        dll.EU_SetEmptyImage(hwnd, element_id, bytes_arg(image_data), len(image_data))
    if element_id and image_size:
        dll.EU_SetEmptyImageSize(hwnd, element_id, int(image_size))
    return element_id

def set_empty_description(hwnd, element_id, description=""):
    data = make_utf8(description)
    dll.EU_SetEmptyDescription(hwnd, element_id, bytes_arg(data), len(data))

def set_empty_options(hwnd, element_id, icon="📭", action=""):
    icon_data = make_utf8(icon)
    action_data = make_utf8(action)
    dll.EU_SetEmptyOptions(
        hwnd, element_id,
        bytes_arg(icon_data), len(icon_data),
        bytes_arg(action_data), len(action_data)
    )

def set_empty_image(hwnd, element_id, image=""):
    data = make_utf8(image)
    dll.EU_SetEmptyImage(hwnd, element_id, bytes_arg(data), len(data))

def set_empty_image_size(hwnd, element_id, image_size=0):
    dll.EU_SetEmptyImageSize(hwnd, element_id, int(image_size))

def get_empty_image_status(hwnd, element_id):
    return dll.EU_GetEmptyImageStatus(hwnd, element_id)

def get_empty_image_size(hwnd, element_id):
    return dll.EU_GetEmptyImageSize(hwnd, element_id)

def set_empty_action_clicked(hwnd, element_id, clicked=False):
    dll.EU_SetEmptyActionClicked(hwnd, element_id, 1 if clicked else 0)

def get_empty_action_clicked(hwnd, element_id):
    return dll.EU_GetEmptyActionClicked(hwnd, element_id)

def set_empty_action_callback(hwnd, element_id, callback):
    dll.EU_SetEmptyActionCallback(hwnd, element_id, callback)

def create_skeleton(hwnd, parent_id, rows=3, animated=True,
                    x=0, y=0, w=220, h=100, loading=None, show_avatar=None):
    element_id = dll.EU_CreateSkeleton(
        hwnd, parent_id, rows, 1 if animated else 0, x, y, w, h
    )
    if element_id and (loading is not None or show_avatar is not None):
        dll.EU_SetSkeletonOptions(hwnd, element_id, rows, int(bool(animated)),
                                  1 if loading is None else int(bool(loading)),
                                  1 if show_avatar is None else int(bool(show_avatar)))
    return element_id

def set_skeleton_rows(hwnd, element_id, rows=3):
    dll.EU_SetSkeletonRows(hwnd, element_id, rows)

def set_skeleton_animated(hwnd, element_id, animated=True):
    dll.EU_SetSkeletonAnimated(hwnd, element_id, 1 if animated else 0)

def set_skeleton_loading(hwnd, element_id, loading=True):
    dll.EU_SetSkeletonLoading(hwnd, element_id, 1 if loading else 0)

def set_skeleton_options(hwnd, element_id, rows=3, animated=True, loading=True, show_avatar=True):
    dll.EU_SetSkeletonOptions(
        hwnd, element_id,
        rows, 1 if animated else 0, 1 if loading else 0, 1 if show_avatar else 0
    )

def get_skeleton_loading(hwnd, element_id):
    return dll.EU_GetSkeletonLoading(hwnd, element_id)

def get_skeleton_options(hwnd, element_id):
    rows = ctypes.c_int()
    animated = ctypes.c_int()
    loading = ctypes.c_int()
    show_avatar = ctypes.c_int()
    ok = dll.EU_GetSkeletonOptions(
        hwnd, element_id,
        ctypes.byref(rows), ctypes.byref(animated),
        ctypes.byref(loading), ctypes.byref(show_avatar)
    )
    if not ok:
        return None
    return rows.value, bool(animated.value), bool(loading.value), bool(show_avatar.value)

def _description_item_to_row(item):
    if isinstance(item, dict):
        fields = [
            item.get("label", ""),
            item.get("content", item.get("value", "")),
            item.get("span", 1),
            item.get("label_icon", item.get("icon", "")),
            item.get("content_type", 0),
            item.get("tag_type", 0),
            item.get("content_align", item.get("align", 0)),
            item.get("label_bg", 0),
            item.get("content_bg", 0),
            item.get("label_fg", 0),
            item.get("content_fg", 0),
        ]
    else:
        fields = [item[0], item[1], 1, "", 0, 0, 0, 0, 0, 0, 0]
    return "\t".join(str(v) for v in fields)

def create_descriptions(hwnd, parent_id, title="📋 描述列表", items=None,
                        columns=2, bordered=True, x=0, y=0, w=420, h=110,
                        label_width=None, min_row_height=None, wrap_values=None,
                        responsive=None, last_item_span=None):
    if items is None:
        items = [("名称", "Emoji UI"), ("状态", "✅ 就绪")]
    title_data = make_utf8(title)
    legacy_rows = []
    for item in items:
        if isinstance(item, dict):
            legacy_rows.append(f"{item.get('label', '')}:{item.get('content', item.get('value', ''))}")
        else:
            legacy_rows.append(f"{item[0]}:{item[1]}")
    items_data = make_utf8("|".join(legacy_rows))
    element_id = dll.EU_CreateDescriptions(
        hwnd, parent_id,
        bytes_arg(title_data), len(title_data),
        bytes_arg(items_data), len(items_data),
        columns, 1 if bordered else 0, x, y, w, h
    )
    if element_id and (label_width is not None or min_row_height is not None or wrap_values is not None):
        dll.EU_SetDescriptionsOptions(
            hwnd, element_id, columns, 1 if bordered else 0,
            88 if label_width is None else label_width,
            28 if min_row_height is None else min_row_height,
            0 if wrap_values is None else int(bool(wrap_values)),
        )
    if element_id and (responsive is not None or last_item_span is not None):
        dll.EU_SetDescriptionsAdvancedOptions(
            hwnd, element_id,
            1 if responsive is None else int(bool(responsive)),
            0 if last_item_span is None else int(bool(last_item_span)),
        )
    if element_id and any(isinstance(item, dict) for item in items):
        set_descriptions_items_ex(hwnd, element_id, items)
    return element_id

def set_descriptions_options(hwnd, element_id, columns=2, bordered=True,
                             label_width=88, min_row_height=28, wrap_values=False):
    dll.EU_SetDescriptionsOptions(
        hwnd, element_id, columns, 1 if bordered else 0,
        label_width, min_row_height, 1 if wrap_values else 0
    )

def set_descriptions_advanced_options(hwnd, element_id, responsive=True, last_item_span=False):
    dll.EU_SetDescriptionsAdvancedOptions(
        hwnd, element_id, 1 if responsive else 0, 1 if last_item_span else 0
    )

def set_descriptions_layout(hwnd, element_id, direction=0, size=0, columns=2, bordered=True):
    dll.EU_SetDescriptionsLayout(
        hwnd, element_id, direction, size, columns, 1 if bordered else 0
    )

def set_descriptions_items_ex(hwnd, element_id, items):
    data = make_utf8("\n".join(_description_item_to_row(item) for item in items))
    dll.EU_SetDescriptionsItemsEx(hwnd, element_id, bytes_arg(data), len(data))

def set_descriptions_colors(hwnd, element_id, border=0, label_bg=0, content_bg=0,
                            label_fg=0, content_fg=0, title_fg=0):
    dll.EU_SetDescriptionsColors(
        hwnd, element_id, border, label_bg, content_bg, label_fg, content_fg, title_fg
    )

def set_descriptions_extra(hwnd, element_id, emoji="⚙️", text="操作", visible=True, variant=1):
    emoji_data = make_utf8(emoji)
    text_data = make_utf8(text)
    dll.EU_SetDescriptionsExtra(
        hwnd, element_id,
        bytes_arg(emoji_data), len(emoji_data),
        bytes_arg(text_data), len(text_data),
        1 if visible else 0, variant
    )

def get_descriptions_options(hwnd, element_id):
    values = [ctypes.c_int() for _ in range(7)]
    ok = dll.EU_GetDescriptionsOptions(hwnd, element_id, *[ctypes.byref(v) for v in values])
    if not ok:
        return None
    return (
        values[0].value, bool(values[1].value), values[2].value, values[3].value,
        bool(values[4].value), bool(values[5].value), bool(values[6].value)
    )

def get_descriptions_full_state(hwnd, element_id):
    values = [ctypes.c_int() for _ in range(8)]
    ok = dll.EU_GetDescriptionsFullState(hwnd, element_id, *[ctypes.byref(v) for v in values])
    if not ok:
        return None
    return {
        "direction": values[0].value,
        "size": values[1].value,
        "columns": values[2].value,
        "bordered": bool(values[3].value),
        "item_count": values[4].value,
        "extra_click_count": values[5].value,
        "responsive": bool(values[6].value),
        "wrap_values": bool(values[7].value),
    }

def create_table(hwnd, parent_id, columns=None, rows=None,
                 striped=True, bordered=True, x=0, y=0, w=420, h=120,
                 row_height=None, header_height=None, selectable=None,
                 sort_column=None, sort_desc=False, scroll_row=None, column_width=None):
    if columns is None:
        columns = ["名称", "状态"]
    if rows is None:
        rows = [["按钮", "✅ 完成"], ["选择器", "✅ 完成"]]
    col_data = make_utf8("|".join(columns))
    row_data = make_utf8("|".join(",".join(row) for row in rows))
    element_id = dll.EU_CreateTable(
        hwnd, parent_id,
        bytes_arg(col_data), len(col_data),
        bytes_arg(row_data), len(row_data),
        1 if striped else 0, 1 if bordered else 0, x, y, w, h
    )
    if element_id and (row_height is not None or header_height is not None or selectable is not None):
        dll.EU_SetTableOptions(
            hwnd, element_id, 1 if striped else 0, 1 if bordered else 0,
            42 if row_height is None else row_height,
            48 if header_height is None else header_height,
            1 if selectable is None else int(bool(selectable))
        )
    if element_id and sort_column is not None:
        dll.EU_SetTableSort(hwnd, element_id, sort_column, 1 if sort_desc else 0)
    if element_id and scroll_row is not None:
        dll.EU_SetTableScrollRow(hwnd, element_id, scroll_row)
    if element_id and column_width is not None:
        dll.EU_SetTableColumnWidth(hwnd, element_id, column_width)
    return element_id

def set_table_sort(hwnd, element_id, column_index=0, desc=False):
    dll.EU_SetTableSort(hwnd, element_id, column_index, 1 if desc else 0)

def set_table_scroll_row(hwnd, element_id, scroll_row=0):
    dll.EU_SetTableScrollRow(hwnd, element_id, scroll_row)

def set_table_column_width(hwnd, element_id, column_width=0):
    dll.EU_SetTableColumnWidth(hwnd, element_id, column_width)

def get_table_options(hwnd, element_id):
    values = [ctypes.c_int() for _ in range(9)]
    ok = dll.EU_GetTableOptions(hwnd, element_id, *[ctypes.byref(v) for v in values])
    if not ok:
        return None
    return (
        bool(values[0].value), bool(values[1].value), values[2].value, values[3].value,
        bool(values[4].value), values[5].value, bool(values[6].value),
        values[7].value, values[8].value
    )

TABLE_CELL_TYPES = {
    "text": 0, "index": 1, "selection": 2, "expand": 3,
    "button": 4, "buttons": 5, "combo": 6, "switch": 7,
    "select": 8, "progress": 9, "status": 10, "tag": 11,
    "popover_tag": 12,
}
TABLE_CELL_TYPE_NAMES = {value: key for key, value in TABLE_CELL_TYPES.items()}

def table_cell_type(value):
    if isinstance(value, int):
        return value
    return TABLE_CELL_TYPES.get(str(value or "text").lower(), 0)

def table_cell_type_name(value):
    if isinstance(value, str):
        return value
    return TABLE_CELL_TYPE_NAMES.get(table_cell_type(value), "text")

def table_escape(value):
    text = "" if value is None else str(value)
    return (text.replace("\\", "\\\\")
                .replace("\n", "\\n")
                .replace("\t", "\\t")
                .replace("=", "\\=")
                .replace("|", "\\|"))

def table_kv_line(fields):
    if isinstance(fields, dict):
        iterable = fields.items()
    else:
        iterable = fields or []
    parts = []
    for key, value in iterable:
        if value is None:
            continue
        if isinstance(value, bool):
            value = 1 if value else 0
        parts.append(f"{key}={table_escape(value)}")
    return "\t".join(parts)

def table_options(options=None):
    if options is None:
        return ""
    if isinstance(options, str):
        return options
    if isinstance(options, dict):
        return table_kv_line(options)
    return table_kv_line(options)

def _table_join_values(values):
    return "|".join(table_escape(v) for v in (values or []))

def _table_column_title(column, index):
    if isinstance(column, dict):
        return column.get("title", column.get("label", f"列 {index + 1}"))
    return str(column)

def _table_column_key(column, index):
    if isinstance(column, dict):
        return column.get("key", f"c{index}")
    return f"c{index}"

def table_column_line(column, index=0):
    if isinstance(column, dict):
        fields = dict(column)
        fields.setdefault("title", fields.get("label", f"列 {index + 1}"))
        fields.setdefault("key", f"c{index}")
    else:
        fields = {"title": column, "key": f"c{index}"}
    if "type" in fields:
        fields["type"] = table_cell_type_name(fields["type"])
    if "options" in fields and not isinstance(fields["options"], str):
        fields["options"] = _table_join_values(fields["options"])
    return table_kv_line(fields)

def _table_cell_payload(cell):
    if isinstance(cell, dict):
        value = cell.get("value", cell.get("text", ""))
        if value == "" and "items" in cell:
            value = cell["items"]
        if value == "" and "parts" in cell:
            value = cell["parts"]
        if isinstance(value, (list, tuple)):
            value = _table_join_values(value)
        cell_type = cell.get("type")
        options = dict(cell.get("options", {}) or {})
        for key in ("checked", "status", "value", "disabled"):
            if key in cell:
                options[key] = cell[key]
        return value, cell_type, options
    if isinstance(cell, (list, tuple)):
        return _table_join_values(cell), None, {}
    return cell, None, {}

def table_row_line(row, columns=None):
    fields = []
    column_count = len(columns or [])
    if isinstance(row, dict):
        meta_map = {
            "key": "key", "parent": "parent", "parent_key": "parent",
            "level": "level", "expanded": "expanded", "children": "children",
            "has_children": "children", "hasChildren": "haschildren", "lazy": "lazy",
            "disabled": "disabled", "bg": "bg", "fg": "fg", "align": "align",
            "font_flags": "font_flags", "font_size": "font_size",
        }
        for source, target in meta_map.items():
            if source in row:
                fields.append((target, row[source]))
        raw_cells = row.get("cells")
        if raw_cells is None:
            raw_cells = row.get("values")
        if raw_cells is not None:
            for index, cell in enumerate(raw_cells):
                value, cell_type, options = _table_cell_payload(cell)
                base = f"c{index}"
                fields.append((base, value))
                if cell_type is not None:
                    fields.append((f"{base}_type", table_cell_type_name(cell_type)))
                if options:
                    fields.append((f"{base}_options", table_options(options)))
        else:
            for index in range(column_count):
                key = _table_column_key(columns[index], index)
                value = row.get(key, row.get(f"c{index}", ""))
                fields.append((f"c{index}", value))
        existing = {name for name, _ in fields}
        for key, value in row.items():
            if key in meta_map or key in ("cells", "values", "options"):
                continue
            if key.startswith("c") and key not in existing:
                fields.append((key, value))
    else:
        for index, cell in enumerate(row or []):
            value, cell_type, options = _table_cell_payload(cell)
            base = f"c{index}"
            fields.append((base, value))
            if cell_type is not None:
                fields.append((f"{base}_type", table_cell_type_name(cell_type)))
            if options:
                fields.append((f"{base}_options", table_options(options)))
    return table_kv_line(fields)

def set_table_columns_ex(hwnd, element_id, columns):
    data = make_utf8("\n".join(table_column_line(col, i) for i, col in enumerate(columns or [])))
    dll.EU_SetTableColumnsEx(hwnd, element_id, bytes_arg(data), len(data))

def set_table_rows_ex(hwnd, element_id, rows, columns=None):
    data = make_utf8("\n".join(table_row_line(row, columns) for row in (rows or [])))
    dll.EU_SetTableRowsEx(hwnd, element_id, bytes_arg(data), len(data))

def add_table_row(hwnd, element_id, row, columns=None):
    data = make_utf8(table_row_line(row, columns))
    return dll.EU_AddTableRow(hwnd, element_id, bytes_arg(data), len(data))

def insert_table_row(hwnd, element_id, index, row, columns=None):
    data = make_utf8(table_row_line(row, columns))
    return dll.EU_InsertTableRow(hwnd, element_id, int(index), bytes_arg(data), len(data))

def delete_table_row(hwnd, element_id, index):
    return bool(dll.EU_DeleteTableRow(hwnd, element_id, int(index)))

def clear_table_rows(hwnd, element_id):
    return bool(dll.EU_ClearTableRows(hwnd, element_id))

def set_table_cell(hwnd, element_id, row, col, cell_type="text", value="", options=None):
    if isinstance(value, (list, tuple)):
        value = _table_join_values(value)
    value_data = make_utf8(str(value))
    option_data = make_utf8(table_options(options))
    dll.EU_SetTableCellEx(
        hwnd, element_id, row, col, table_cell_type(cell_type),
        bytes_arg(value_data), len(value_data),
        bytes_arg(option_data), len(option_data)
    )

def set_table_row_style(hwnd, element_id, row, bg=0, fg=0, align=-1, font_flags=-1, font_size=0):
    dll.EU_SetTableRowStyle(hwnd, element_id, row, bg, fg, align, font_flags, font_size)

def set_table_cell_style(hwnd, element_id, row, col, bg=0, fg=0, align=-1, font_flags=-1, font_size=0):
    dll.EU_SetTableCellStyle(hwnd, element_id, row, col, bg, fg, align, font_flags, font_size)

def set_table_selection_mode(hwnd, element_id, mode=1):
    dll.EU_SetTableSelectionMode(hwnd, element_id, mode)

def set_table_selected_rows(hwnd, element_id, rows):
    if isinstance(rows, str):
        spec = rows
    else:
        spec = "|".join(str(int(r)) for r in (rows or []))
    data = make_utf8(spec)
    dll.EU_SetTableSelectedRows(hwnd, element_id, bytes_arg(data), len(data))

def set_table_filter(hwnd, element_id, col, value):
    if value is None:
        dll.EU_ClearTableFilter(hwnd, element_id, col)
        return
    data = make_utf8(str(value))
    dll.EU_SetTableFilter(hwnd, element_id, col, bytes_arg(data), len(data))

def clear_table_filter(hwnd, element_id, col=-1):
    dll.EU_ClearTableFilter(hwnd, element_id, col)

def set_table_search(hwnd, element_id, value=""):
    data = make_utf8(str(value or ""))
    dll.EU_SetTableSearch(hwnd, element_id, bytes_arg(data), len(data))

def set_table_span(hwnd, element_id, row, col, rowspan=1, colspan=1):
    dll.EU_SetTableSpan(hwnd, element_id, row, col, rowspan, colspan)

def clear_table_spans(hwnd, element_id):
    dll.EU_ClearTableSpans(hwnd, element_id)

def set_table_summary(hwnd, element_id, values):
    spec = values if isinstance(values, str) else "|".join(table_escape(v) for v in (values or []))
    data = make_utf8(spec)
    dll.EU_SetTableSummary(hwnd, element_id, bytes_arg(data), len(data))

def set_table_row_expanded(hwnd, element_id, row, expanded=True):
    dll.EU_SetTableRowExpanded(hwnd, element_id, row, 1 if expanded else 0)

def set_table_tree_options(hwnd, element_id, enabled=True, indent=18, lazy=False):
    dll.EU_SetTableTreeOptions(hwnd, element_id, 1 if enabled else 0, indent, 1 if lazy else 0)

def set_table_viewport_options(hwnd, element_id, max_height=0, fixed_header=True,
                               horizontal_scroll=True, show_summary=False):
    dll.EU_SetTableViewportOptions(
        hwnd, element_id, max_height,
        1 if fixed_header else 0,
        1 if horizontal_scroll else 0,
        1 if show_summary else 0
    )

def set_table_scroll(hwnd, element_id, scroll_row=0, scroll_x=0):
    dll.EU_SetTableScroll(hwnd, element_id, scroll_row, scroll_x)

def set_table_header_drag_options(hwnd, element_id, column_resize=False, header_height_resize=False,
                                  min_col_width=48, max_col_width=720,
                                  min_header_height=34, max_header_height=180):
    dll.EU_SetTableHeaderDragOptions(
        hwnd, element_id,
        1 if column_resize else 0,
        1 if header_height_resize else 0,
        min_col_width, max_col_width, min_header_height, max_header_height,
    )

def export_table_excel(hwnd, element_id, path, flags=0):
    data = make_utf8(path)
    return bool(dll.EU_ExportTableExcel(hwnd, element_id, bytes_arg(data), len(data), flags))

def import_table_excel(hwnd, element_id, path, flags=0):
    data = make_utf8(path)
    return bool(dll.EU_ImportTableExcel(hwnd, element_id, bytes_arg(data), len(data), flags))

def set_table_double_click_edit(hwnd, element_id, enabled=True):
    dll.EU_SetTableDoubleClickEdit(hwnd, element_id, 1 if enabled else 0)

def set_table_column_double_click_edit(hwnd, element_id, col, editable):
    dll.EU_SetTableColumnDoubleClickEdit(hwnd, element_id, int(col), int(editable))

def set_table_cell_double_click_edit(hwnd, element_id, row, col, editable):
    dll.EU_SetTableCellDoubleClickEdit(hwnd, element_id, int(row), int(col), int(editable))

def get_table_cell_double_click_editable(hwnd, element_id, row, col):
    return bool(dll.EU_GetTableCellDoubleClickEditable(hwnd, element_id, int(row), int(col)))

def get_table_double_click_edit_state(hwnd, element_id):
    enabled = ctypes.c_int()
    row = ctypes.c_int()
    col = ctypes.c_int()
    ok = dll.EU_GetTableDoubleClickEditState(
        hwnd, element_id, ctypes.byref(enabled), ctypes.byref(row), ctypes.byref(col)
    )
    return None if not ok else (bool(enabled.value), row.value, col.value)

def set_table_cell_click_callback(hwnd, element_id, callback):
    dll.EU_SetTableCellClickCallback(hwnd, element_id, callback)

def set_table_cell_action_callback(hwnd, element_id, callback):
    dll.EU_SetTableCellActionCallback(hwnd, element_id, callback)

def set_table_cell_edit_callback(hwnd, element_id, callback):
    dll.EU_SetTableCellEditCallback(hwnd, element_id, callback)

_table_virtual_row_provider_refs = {}

def set_table_virtual_options(hwnd, element_id, enabled=True, row_count=0, cache_window=32):
    dll.EU_SetTableVirtualOptions(hwnd, element_id, 1 if enabled else 0, row_count, cache_window)

def set_table_virtual_row_provider(hwnd, element_id, provider):
    key = (int(hwnd), int(element_id))
    if provider is None:
        _table_virtual_row_provider_refs.pop(key, None)
        dll.EU_SetTableVirtualRowProvider(hwnd, element_id, TableVirtualRowCallback(0))
        return
    if not callable(provider):
        raise TypeError("provider must be callable or None")
    def _native(table_id, row_index, buffer, buffer_size):
        text = provider(table_id, row_index)
        data = make_utf8("" if text is None else str(text))
        needed = len(data)
        if not buffer or buffer_size <= 0:
            return needed
        n = min(needed, max(0, buffer_size - 1))
        if n > 0:
            ctypes.memmove(buffer, data, n)
        if buffer_size > 0:
            buffer[n] = 0
        return needed
    cb = TableVirtualRowCallback(_native)
    _table_virtual_row_provider_refs[key] = cb
    dll.EU_SetTableVirtualRowProvider(hwnd, element_id, cb)

def clear_table_virtual_cache(hwnd, element_id):
    dll.EU_ClearTableVirtualCache(hwnd, element_id)

def _read_table_text(fn, *args, buffer_size=4096):
    buf = ctypes.create_string_buffer(buffer_size)
    ptr = ctypes.cast(buf, ctypes.POINTER(ctypes.c_ubyte))
    needed = fn(*args, ptr, buffer_size)
    if needed >= buffer_size:
        buf = ctypes.create_string_buffer(needed + 1)
        ptr = ctypes.cast(buf, ctypes.POINTER(ctypes.c_ubyte))
        fn(*args, ptr, needed + 1)
    return buf.value.decode("utf-8", errors="replace")

def get_table_cell_value(hwnd, element_id, row, col):
    return _read_table_text(dll.EU_GetTableCellValue, hwnd, element_id, row, col)

def get_table_full_state(hwnd, element_id):
    return _read_table_text(dll.EU_GetTableFullState, hwnd, element_id)

def create_table_ex(hwnd, parent_id, columns=None, rows=None,
                    striped=True, bordered=True, x=0, y=0, w=640, h=220,
                    selection_mode=0, tree=False, lazy=False, max_height=0,
                    fixed_header=True, horizontal_scroll=True, summary=None,
                    row_height=None, header_height=None):
    if columns is None:
        columns = [
            {"title": "序号", "key": "idx", "type": "index", "width": 64, "fixed": "left", "align": "center"},
            {"title": "事项", "key": "task", "width": 170, "sortable": True, "tooltip": True},
            {"title": "状态", "key": "state", "type": "status", "width": 120, "align": "center"},
            {"title": "进度", "key": "progress", "type": "progress", "width": 150},
        ]
    if rows is None:
        rows = [
            {"cells": [{"type": "index"}, "🍜 备菜", {"type": "status", "value": "1", "options": {"status": 1}}, {"type": "progress", "value": 66}]},
            {"cells": [{"type": "index"}, "🚚 配送", {"type": "status", "value": "2", "options": {"status": 2}}, {"type": "progress", "value": 88}]},
        ]
    legacy_columns = [_table_column_title(col, i) for i, col in enumerate(columns)]
    legacy_rows = []
    for row in rows:
        if isinstance(row, dict):
            raw_cells = row.get("cells", row.get("values", []))
            legacy_rows.append([str(_table_cell_payload(cell)[0]) for cell in raw_cells])
        else:
            legacy_rows.append([str(_table_cell_payload(cell)[0]) for cell in row])
    element_id = create_table(
        hwnd, parent_id, legacy_columns, legacy_rows,
        striped, bordered, x, y, w, h,
        row_height=row_height, header_height=header_height,
        selectable=selection_mode != 0
    )
    if element_id:
        set_table_columns_ex(hwnd, element_id, columns)
        set_table_rows_ex(hwnd, element_id, rows, columns)
        set_table_selection_mode(hwnd, element_id, selection_mode)
        set_table_tree_options(hwnd, element_id, tree, 18, lazy)
        set_table_viewport_options(hwnd, element_id, max_height, fixed_header, horizontal_scroll, summary is not None)
        if summary is not None:
            set_table_summary(hwnd, element_id, summary)
    return element_id

def create_card(hwnd, parent_id, title="🧩 卡片", body="", shadow=1,
                x=0, y=0, w=280, h=140):
    title_data = make_utf8(title)
    body_data = make_utf8(body)
    return dll.EU_CreateCard(
        hwnd, parent_id,
        bytes_arg(title_data), len(title_data),
        bytes_arg(body_data), len(body_data),
        shadow, x, y, w, h
    )

def create_image_card(hwnd, parent_id, image_src="", title="🍔 图片卡片",
                      subtitle="", button_text="操作按钮", shadow=1,
                      x=0, y=0, w=280, h=240):
    card_id = create_card(hwnd, parent_id, "", "", shadow, x, y, w, h)
    set_card_body_style(hwnd, card_id, 0, 0, 0, 0, 14.0, 0, 0, False)
    image_h = max(80, min(h - 76, int(w * 0.56)))
    create_image(hwnd, card_id, image_src, title, "cover", 0, 0, w, image_h)
    create_text(hwnd, card_id, title, 14, image_h + 12, w - 28, 26)
    if subtitle:
        create_text(hwnd, card_id, subtitle, 14, image_h + 44, max(40, w - 122), 24)
    if button_text:
        create_button(hwnd, card_id, "", button_text, max(14, w - 98), image_h + 40, 84, 28, variant=5)
    return card_id

def _collapse_bool(value):
    if isinstance(value, str):
        return value.strip().lower() not in ("", "0", "false", "no", "否")
    return bool(value)

def _collapse_item_row(item):
    if isinstance(item, dict):
        fields = [
            item.get("title", item.get("label", "")),
            item.get("body", item.get("content", "")),
            item.get("icon", ""),
            item.get("suffix", item.get("right", item.get("extra", ""))),
            1 if _collapse_bool(item.get("disabled", False)) else 0,
        ]
        return "\t".join(str(v) for v in fields)
    if isinstance(item, (list, tuple)):
        fields = list(item[:5])
        while len(fields) < 5:
            fields.append("")
        fields[4] = 1 if _collapse_bool(fields[4]) else 0
        return "\t".join(str(v) for v in fields)
    return str(item)

def _collapse_indices_text(indices):
    if indices is None:
        return ""
    if isinstance(indices, int):
        return str(indices)
    return ",".join(str(int(i)) for i in indices)

def create_collapse(hwnd, parent_id, items=None, active=0, accordion=True,
                    x=0, y=0, w=360, h=180):
    if items is None:
        items = [("🎯 一致性", "保持界面风格一致。"),
                 ("💡 反馈", "提供清晰的状态变化。")]
    items_data = make_utf8("|".join(_collapse_item_row(item) for item in items))
    active_index = active[0] if isinstance(active, (list, tuple, set)) and active else active
    element_id = dll.EU_CreateCollapse(
        hwnd, parent_id,
        bytes_arg(items_data), len(items_data),
        int(active_index) if active_index is not None else -1, 1 if accordion else 0, x, y, w, h
    )
    if element_id and isinstance(active, (list, tuple, set)):
        set_collapse_active_items(hwnd, element_id, active)
    return element_id

def _timeline_placement_value(value):
    if isinstance(value, str):
        return 1 if value.lower() in ("bottom", "下方", "底部") else 0
    return int(value or 0)

def _timeline_item_row(item):
    if isinstance(item, dict):
        timestamp = item.get("timestamp", item.get("time", ""))
        content = item.get("content", "")
        item_type = item.get("type", item.get("item_type", 0))
        icon = item.get("icon", "")
        color = item.get("color", "")
        size = item.get("size", 0)
        placement = item.get("placement", "")
        card_title = item.get("card_title", item.get("title", ""))
        card_body = item.get("card_body", item.get("body", ""))
        fields = [timestamp, content, item_type, icon, color, size, placement, card_title, card_body]
    elif isinstance(item, (list, tuple)):
        fields = list(item[:9])
        while len(fields) < 3:
            fields.append("")
        while len(fields) < 9:
            fields.append("")
    else:
        fields = ["", str(item), 0, "", "", 0, "", "", ""]
    return "\t".join(str(field) for field in fields)

def create_timeline(hwnd, parent_id, items=None, x=0, y=0, w=360, h=220):
    if items is None:
        items = [("09:00", "🚀 启动", 0, "🚀"), ("10:30", "✅ 复核", 1, "✅")]
    item_rows = [_timeline_item_row(item) for item in items]
    items_data = make_utf8("|".join(item_rows))
    return dll.EU_CreateTimeline(
        hwnd, parent_id, bytes_arg(items_data), len(items_data),
        x, y, w, h
    )

def create_statistic(hwnd, parent_id, title="📊 统计数值", value="0",
                     prefix="", suffix="", x=0, y=0, w=180, h=100):
    title_data = make_utf8(title)
    value_data = make_utf8(value)
    prefix_data = make_utf8(prefix)
    suffix_data = make_utf8(suffix)
    return dll.EU_CreateStatistic(
        hwnd, parent_id,
        bytes_arg(title_data), len(title_data),
        bytes_arg(value_data), len(value_data),
        bytes_arg(prefix_data), len(prefix_data),
        bytes_arg(suffix_data), len(suffix_data),
        x, y, w, h
    )

def create_kpi_card(hwnd, parent_id, title="📌 指标", value="0", subtitle="",
                    trend="", trend_type=0, x=0, y=0, w=220, h=132):
    title_data = make_utf8(title)
    value_data = make_utf8(value)
    subtitle_data = make_utf8(subtitle)
    trend_data = make_utf8(trend)
    return dll.EU_CreateKpiCard(
        hwnd, parent_id,
        bytes_arg(title_data), len(title_data),
        bytes_arg(value_data), len(value_data),
        bytes_arg(subtitle_data), len(subtitle_data),
        bytes_arg(trend_data), len(trend_data),
        trend_type, x, y, w, h
    )

def create_trend(hwnd, parent_id, title="📈 趋势", value="0",
                 percent="", detail="", direction=0,
                 x=0, y=0, w=300, h=100):
    title_data = make_utf8(title)
    value_data = make_utf8(value)
    percent_data = make_utf8(percent)
    detail_data = make_utf8(detail)
    return dll.EU_CreateTrend(
        hwnd, parent_id,
        bytes_arg(title_data), len(title_data),
        bytes_arg(value_data), len(value_data),
        bytes_arg(percent_data), len(percent_data),
        bytes_arg(detail_data), len(detail_data),
        direction, x, y, w, h
    )

def create_status_dot(hwnd, parent_id, label="状态", description="",
                      status=0, x=0, y=0, w=240, h=44):
    label_data = make_utf8(label)
    desc_data = make_utf8(description)
    return dll.EU_CreateStatusDot(
        hwnd, parent_id,
        bytes_arg(label_data), len(label_data),
        bytes_arg(desc_data), len(desc_data),
        status, x, y, w, h
    )

def create_gauge(hwnd, parent_id, title="🎯 仪表盘", value=68,
                 caption="📍 当前状态", status=0,
                 x=0, y=0, w=240, h=220):
    title_data = make_utf8(title)
    caption_data = make_utf8(caption)
    return dll.EU_CreateGauge(
        hwnd, parent_id,
        bytes_arg(title_data), len(title_data),
        value,
        bytes_arg(caption_data), len(caption_data),
        status, x, y, w, h
    )

def create_ring_progress(hwnd, parent_id, title="⭐ 环形进度", value=72,
                         label="🎯 完成率", status=0,
                         x=0, y=0, w=220, h=220):
    title_data = make_utf8(title)
    label_data = make_utf8(label)
    return dll.EU_CreateRingProgress(
        hwnd, parent_id,
        bytes_arg(title_data), len(title_data),
        value,
        bytes_arg(label_data), len(label_data),
        status, x, y, w, h
    )

def create_bullet_progress(hwnd, parent_id, title="🧭 子弹进度",
                           description="🎯 目标进度", value=64, target=80, status=0,
                           x=0, y=0, w=360, h=110):
    title_data = make_utf8(title)
    desc_data = make_utf8(description)
    return dll.EU_CreateBulletProgress(
        hwnd, parent_id,
        bytes_arg(title_data), len(title_data),
        bytes_arg(desc_data), len(desc_data),
        value, target, status, x, y, w, h
    )

def set_kpi_card_options(hwnd, element_id, loading=False, helper=""):
    data = make_utf8(helper)
    dll.EU_SetKpiCardOptions(hwnd, element_id, 1 if loading else 0, bytes_arg(data), len(data))

def get_kpi_card_options(hwnd, element_id):
    loading = ctypes.c_int()
    trend_type = ctypes.c_int()
    ok = dll.EU_GetKpiCardOptions(hwnd, element_id, ctypes.byref(loading), ctypes.byref(trend_type))
    return (bool(loading.value), trend_type.value) if ok else None

def set_trend_options(hwnd, element_id, inverse=False, show_icon=True):
    dll.EU_SetTrendOptions(hwnd, element_id, 1 if inverse else 0, 1 if show_icon else 0)

def get_trend_direction(hwnd, element_id):
    return dll.EU_GetTrendDirection(hwnd, element_id)

def get_trend_options(hwnd, element_id):
    inverse = ctypes.c_int()
    show_icon = ctypes.c_int()
    ok = dll.EU_GetTrendOptions(hwnd, element_id, ctypes.byref(inverse), ctypes.byref(show_icon))
    return (bool(inverse.value), bool(show_icon.value)) if ok else None

def set_status_dot_options(hwnd, element_id, pulse=False, compact=False):
    dll.EU_SetStatusDotOptions(hwnd, element_id, 1 if pulse else 0, 1 if compact else 0)

def get_status_dot_status(hwnd, element_id):
    return dll.EU_GetStatusDotStatus(hwnd, element_id)

def get_status_dot_options(hwnd, element_id):
    pulse = ctypes.c_int()
    compact = ctypes.c_int()
    ok = dll.EU_GetStatusDotOptions(hwnd, element_id, ctypes.byref(pulse), ctypes.byref(compact))
    return (bool(pulse.value), bool(compact.value)) if ok else None

def set_gauge_options(hwnd, element_id, min_value=0, max_value=100,
                      warning_value=70, danger_value=90, stroke_width=12):
    dll.EU_SetGaugeOptions(
        hwnd, element_id, min_value, max_value, warning_value, danger_value, stroke_width
    )

def get_gauge_value(hwnd, element_id):
    return dll.EU_GetGaugeValue(hwnd, element_id)

def get_gauge_status(hwnd, element_id):
    return dll.EU_GetGaugeStatus(hwnd, element_id)

def get_gauge_options(hwnd, element_id):
    min_value = ctypes.c_int()
    max_value = ctypes.c_int()
    warning_value = ctypes.c_int()
    danger_value = ctypes.c_int()
    stroke_width = ctypes.c_int()
    ok = dll.EU_GetGaugeOptions(
        hwnd, element_id,
        ctypes.byref(min_value), ctypes.byref(max_value),
        ctypes.byref(warning_value), ctypes.byref(danger_value),
        ctypes.byref(stroke_width),
    )
    if not ok:
        return None
    return (min_value.value, max_value.value, warning_value.value,
            danger_value.value, stroke_width.value)

def set_ring_progress_options(hwnd, element_id, stroke_width=14, show_center=True):
    dll.EU_SetRingProgressOptions(hwnd, element_id, stroke_width, 1 if show_center else 0)

def get_ring_progress_value(hwnd, element_id):
    return dll.EU_GetRingProgressValue(hwnd, element_id)

def get_ring_progress_status(hwnd, element_id):
    return dll.EU_GetRingProgressStatus(hwnd, element_id)

def get_ring_progress_options(hwnd, element_id):
    stroke_width = ctypes.c_int()
    show_center = ctypes.c_int()
    ok = dll.EU_GetRingProgressOptions(hwnd, element_id, ctypes.byref(stroke_width), ctypes.byref(show_center))
    return (stroke_width.value, bool(show_center.value)) if ok else None

def set_bullet_progress_options(hwnd, element_id, good_threshold=80,
                                warn_threshold=60, show_target=True):
    dll.EU_SetBulletProgressOptions(
        hwnd, element_id, good_threshold, warn_threshold, 1 if show_target else 0
    )

def get_bullet_progress_value(hwnd, element_id):
    return dll.EU_GetBulletProgressValue(hwnd, element_id)

def get_bullet_progress_target(hwnd, element_id):
    return dll.EU_GetBulletProgressTarget(hwnd, element_id)

def get_bullet_progress_status(hwnd, element_id):
    return dll.EU_GetBulletProgressStatus(hwnd, element_id)

def get_bullet_progress_options(hwnd, element_id):
    good_threshold = ctypes.c_int()
    warn_threshold = ctypes.c_int()
    show_target = ctypes.c_int()
    ok = dll.EU_GetBulletProgressOptions(
        hwnd, element_id,
        ctypes.byref(good_threshold), ctypes.byref(warn_threshold),
        ctypes.byref(show_target),
    )
    return (good_threshold.value, warn_threshold.value, bool(show_target.value)) if ok else None

def _chart_data(values):
    if values is None:
        values = [("一月", 20), ("二月", 36), ("三月", 52)]
    rows = []
    for item in values:
        label = str(item[0]) if len(item) > 0 else ""
        value = item[1] if len(item) > 1 else 0
        rows.append(f"{label}\t{value}")
    return make_utf8("|".join(rows))

def _chart_series_data(series):
    if series is None:
        series = []
    chunks = []
    for values in series:
        rows = []
        for item in values:
            label = str(item[0]) if len(item) > 0 else ""
            value = item[1] if len(item) > 1 else 0
            rows.append(f"{label}\t{value}")
        chunks.append("|".join(rows))
    return make_utf8("#".join(chunks))

def create_line_chart(hwnd, parent_id, title="📈 折线趋势", points=None,
                      chart_style=0, x=0, y=0, w=360, h=220):
    title_data = make_utf8(title)
    points_data = _chart_data(points)
    return dll.EU_CreateLineChart(
        hwnd, parent_id,
        bytes_arg(title_data), len(title_data),
        bytes_arg(points_data), len(points_data),
        chart_style, x, y, w, h
    )

def create_bar_chart(hwnd, parent_id, title="📊 柱状排行", bars=None,
                     orientation=0, x=0, y=0, w=360, h=220):
    title_data = make_utf8(title)
    bars_data = _chart_data(bars)
    return dll.EU_CreateBarChart(
        hwnd, parent_id,
        bytes_arg(title_data), len(title_data),
        bytes_arg(bars_data), len(bars_data),
        orientation, x, y, w, h
    )

def create_donut_chart(hwnd, parent_id, title="🍩 环形占比", slices=None,
                       active_index=0, x=0, y=0, w=360, h=220):
    title_data = make_utf8(title)
    slices_data = _chart_data(slices)
    return dll.EU_CreateDonutChart(
        hwnd, parent_id,
        bytes_arg(title_data), len(title_data),
        bytes_arg(slices_data), len(slices_data),
        active_index, x, y, w, h
    )

def set_line_chart_options(hwnd, element_id, chart_style=0, show_axis=True,
                           show_area=False, show_tooltip=True):
    dll.EU_SetLineChartOptions(
        hwnd, element_id, chart_style, 1 if show_axis else 0,
        1 if show_area else 0, 1 if show_tooltip else 0
    )

def set_line_chart_series(hwnd, element_id, series):
    data = _chart_series_data(series)
    dll.EU_SetLineChartSeries(hwnd, element_id, bytes_arg(data), len(data))

def set_line_chart_selected(hwnd, element_id, selected_index):
    dll.EU_SetLineChartSelected(hwnd, element_id, selected_index)

def get_line_chart_point_count(hwnd, element_id):
    return dll.EU_GetLineChartPointCount(hwnd, element_id)

def get_line_chart_series_count(hwnd, element_id):
    return dll.EU_GetLineChartSeriesCount(hwnd, element_id)

def get_line_chart_selected(hwnd, element_id):
    return dll.EU_GetLineChartSelected(hwnd, element_id)

def get_line_chart_options(hwnd, element_id):
    chart_style = ctypes.c_int()
    show_axis = ctypes.c_int()
    show_area = ctypes.c_int()
    show_tooltip = ctypes.c_int()
    ok = dll.EU_GetLineChartOptions(
        hwnd, element_id,
        ctypes.byref(chart_style), ctypes.byref(show_axis),
        ctypes.byref(show_area), ctypes.byref(show_tooltip),
    )
    if not ok:
        return None
    return (chart_style.value, bool(show_axis.value), bool(show_area.value), bool(show_tooltip.value))

def set_bar_chart_options(hwnd, element_id, orientation=0,
                          show_values=True, show_axis=True):
    dll.EU_SetBarChartOptions(
        hwnd, element_id, orientation, 1 if show_values else 0, 1 if show_axis else 0
    )

def set_bar_chart_series(hwnd, element_id, series):
    data = _chart_series_data(series)
    dll.EU_SetBarChartSeries(hwnd, element_id, bytes_arg(data), len(data))

def set_bar_chart_selected(hwnd, element_id, selected_index):
    dll.EU_SetBarChartSelected(hwnd, element_id, selected_index)

def get_bar_chart_bar_count(hwnd, element_id):
    return dll.EU_GetBarChartBarCount(hwnd, element_id)

def get_bar_chart_series_count(hwnd, element_id):
    return dll.EU_GetBarChartSeriesCount(hwnd, element_id)

def get_bar_chart_selected(hwnd, element_id):
    return dll.EU_GetBarChartSelected(hwnd, element_id)

def get_bar_chart_options(hwnd, element_id):
    orientation = ctypes.c_int()
    show_values = ctypes.c_int()
    show_axis = ctypes.c_int()
    ok = dll.EU_GetBarChartOptions(
        hwnd, element_id,
        ctypes.byref(orientation), ctypes.byref(show_values), ctypes.byref(show_axis),
    )
    return (orientation.value, bool(show_values.value), bool(show_axis.value)) if ok else None

def set_donut_chart_options(hwnd, element_id, show_legend=True, ring_width=22):
    dll.EU_SetDonutChartOptions(hwnd, element_id, 1 if show_legend else 0, ring_width)

def set_donut_chart_advanced_options(hwnd, element_id, show_legend=True,
                                     ring_width=22, show_labels=True):
    dll.EU_SetDonutChartAdvancedOptions(
        hwnd, element_id, 1 if show_legend else 0, ring_width, 1 if show_labels else 0
    )

def set_donut_chart_active(hwnd, element_id, active_index):
    dll.EU_SetDonutChartActive(hwnd, element_id, active_index)

def get_donut_chart_slice_count(hwnd, element_id):
    return dll.EU_GetDonutChartSliceCount(hwnd, element_id)

def get_donut_chart_active(hwnd, element_id):
    return dll.EU_GetDonutChartActive(hwnd, element_id)

def get_donut_chart_options(hwnd, element_id):
    show_legend = ctypes.c_int()
    ring_width = ctypes.c_int()
    ok = dll.EU_GetDonutChartOptions(hwnd, element_id, ctypes.byref(show_legend), ctypes.byref(ring_width))
    return (bool(show_legend.value), ring_width.value) if ok else None

def get_donut_chart_advanced_options(hwnd, element_id):
    show_legend = ctypes.c_int()
    ring_width = ctypes.c_int()
    show_labels = ctypes.c_int()
    ok = dll.EU_GetDonutChartAdvancedOptions(
        hwnd, element_id,
        ctypes.byref(show_legend), ctypes.byref(ring_width), ctypes.byref(show_labels)
    )
    return (bool(show_legend.value), ring_width.value, bool(show_labels.value)) if ok else None

def create_divider(hwnd, parent_id, text="", direction=0, content_position=1,
                   x=0, y=0, w=420, h=32):
    data = make_utf8(text)
    return dll.EU_CreateDivider(
        hwnd, parent_id,
        bytes_arg(data), len(data),
        direction, content_position, x, y, w, h
    )

def create_calendar(hwnd, parent_id, year=2026, month=5, selected_day=1,
                    x=0, y=0, w=320, h=300):
    return dll.EU_CreateCalendar(
        hwnd, parent_id, year, month, selected_day, x, y, w, h
    )

def create_tree(hwnd, parent_id, items=None, selected=0,
                x=0, y=0, w=280, h=220):
    if items is None:
        items = [("缁勪欢", 0, True), ("鍩虹", 1, True), ("鎸夐挳", 2, True)]
    rows = []
    for item in items:
        label = str(item[0]) if len(item) > 0 else ""
        level = int(item[1]) if len(item) > 1 else 0
        expanded = item[2] if len(item) > 2 else True
        checked = item[3] if len(item) > 3 else False
        lazy = item[4] if len(item) > 4 else False
        rows.append(
            f"{label}\t{level}\t{1 if expanded else 0}\t"
            f"{1 if checked else 0}\t{1 if lazy else 0}"
        )
    data = make_utf8("|".join(rows))
    return dll.EU_CreateTree(
        hwnd, parent_id, bytes_arg(data), len(data),
        selected, x, y, w, h
    )

def create_tree_select(hwnd, parent_id, items=None, selected=0,
                       x=0, y=0, w=280, h=36):
    if items is None:
        items = [("缁勪欢", 0, True), ("鍩虹", 1, True), ("鎸夐挳", 2, True)]
    rows = []
    for item in items:
        label = str(item[0]) if len(item) > 0 else ""
        level = int(item[1]) if len(item) > 1 else 0
        expanded = item[2] if len(item) > 2 else True
        checked = item[3] if len(item) > 3 else False
        lazy = item[4] if len(item) > 4 else False
        rows.append(
            f"{label}\t{level}\t{1 if expanded else 0}\t"
            f"{1 if checked else 0}\t{1 if lazy else 0}"
        )
    data = make_utf8("|".join(rows))
    return dll.EU_CreateTreeSelect(
        hwnd, parent_id, bytes_arg(data), len(data),
        selected, x, y, w, h
    )

def _transfer_item_rows(items, props=None):
    props = props or {}
    rows = []
    if items is None:
        items = []

    def value_from(item, name, default=""):
        source = props.get(name, name)
        if isinstance(item, dict):
            return item.get(source, item.get(name, default))
        if isinstance(item, (list, tuple)):
            index = {"key": 0, "label": 1, "value": 2, "desc": 3, "pinyin": 4, "disabled": 5}.get(name, 0)
            return item[index] if len(item) > index else default
        if name in ("key", "label", "value"):
            return item
        return default

    for i, item in enumerate(items):
        key = str(value_from(item, "key", i))
        label = str(value_from(item, "label", key))
        value = str(value_from(item, "value", key))
        desc = str(value_from(item, "desc", ""))
        pinyin = str(value_from(item, "pinyin", ""))
        disabled = value_from(item, "disabled", False)
        rows.append(
            f"{key}\t{label}\t{value}\t{desc}\t{pinyin}\t{1 if disabled else 0}"
        )
    return rows

def _transfer_key_text(keys):
    if keys is None:
        keys = []
    return "|".join(str(key) for key in keys)

def create_transfer(hwnd, parent_id, left_items=None, right_items=None,
                    x=0, y=0, w=560, h=170):
    if left_items is None:
        left_items = ["列表一", "列表二", "列表三"]
    if right_items is None:
        right_items = []
    left_data = make_utf8("|".join(left_items))
    right_data = make_utf8("|".join(right_items))
    return dll.EU_CreateTransfer(
        hwnd, parent_id,
        bytes_arg(left_data), len(left_data),
        bytes_arg(right_data), len(right_data),
        x, y, w, h
    )

def create_transfer_ex(hwnd, parent_id, items=None, target_keys=None, props=None,
                       filterable=False, multiple=True, show_footer=False,
                       show_select_all=True, show_count=True, render_mode=0,
                       titles=("源列表", "目标列表"),
                         button_texts=("到左边", "到右边"),
                         fmt=("${total}", "${checked}/${total}"),
                         item_template="{label}",
                         footer_texts=("左侧操作", "右侧操作"),
                         filter_placeholder="请输入关键词 🔎",
                         x=0, y=0, w=720, h=260):
    element_id = create_transfer(hwnd, parent_id, [], [], x, y, w, h)
    set_transfer_data_ex(hwnd, element_id, items or [], target_keys or [], props=props)
    set_transfer_options(hwnd, element_id, filterable, multiple, show_footer,
                         show_select_all, show_count, render_mode)
    set_transfer_titles(hwnd, element_id, titles[0], titles[1])
    set_transfer_button_texts(hwnd, element_id, button_texts[0], button_texts[1])
    set_transfer_format(hwnd, element_id, fmt[0], fmt[1])
    set_transfer_item_template(hwnd, element_id, item_template)
    set_transfer_footer_texts(hwnd, element_id, footer_texts[0], footer_texts[1])
    set_transfer_filter_placeholder(hwnd, element_id, filter_placeholder)
    return element_id

def set_tree_items(hwnd, element_id, items=None):
    if items is None:
        items = [("缁勪欢", 0, True), ("鍩虹", 1, True), ("鎸夐挳", 2, True)]
    rows = []
    for item in items:
        label = str(item[0]) if len(item) > 0 else ""
        level = int(item[1]) if len(item) > 1 else 0
        expanded = item[2] if len(item) > 2 else True
        checked = item[3] if len(item) > 3 else False
        lazy = item[4] if len(item) > 4 else False
        rows.append(
            f"{label}\t{level}\t{1 if expanded else 0}\t"
            f"{1 if checked else 0}\t{1 if lazy else 0}"
        )
    data = make_utf8("|".join(rows))
    dll.EU_SetTreeItems(hwnd, element_id, bytes_arg(data), len(data))

def set_tree_selected(hwnd, element_id, selected_index=0):
    dll.EU_SetTreeSelected(hwnd, element_id, selected_index)

def get_tree_selected(hwnd, element_id):
    return dll.EU_GetTreeSelected(hwnd, element_id)

def set_tree_options(hwnd, element_id, show_checkbox=True, keyboard_navigation=True, lazy_mode=False):
    dll.EU_SetTreeOptions(
        hwnd, element_id,
        1 if show_checkbox else 0,
        1 if keyboard_navigation else 0,
        1 if lazy_mode else 0,
    )

def get_tree_options(hwnd, element_id):
    show_checkbox = ctypes.c_int()
    keyboard_navigation = ctypes.c_int()
    lazy_mode = ctypes.c_int()
    checked_count = ctypes.c_int()
    last_lazy_index = ctypes.c_int()
    ok = dll.EU_GetTreeOptions(
        hwnd, element_id,
        ctypes.byref(show_checkbox), ctypes.byref(keyboard_navigation),
        ctypes.byref(lazy_mode), ctypes.byref(checked_count),
        ctypes.byref(last_lazy_index),
    )
    return {
        "ok": ok,
        "show_checkbox": show_checkbox.value,
        "keyboard_navigation": keyboard_navigation.value,
        "lazy_mode": lazy_mode.value,
        "checked_count": checked_count.value,
        "last_lazy_index": last_lazy_index.value,
    }

def set_tree_item_expanded(hwnd, element_id, item_index=0, expanded=True):
    dll.EU_SetTreeItemExpanded(hwnd, element_id, item_index, 1 if expanded else 0)

def toggle_tree_item_expanded(hwnd, element_id, item_index=0):
    dll.EU_ToggleTreeItemExpanded(hwnd, element_id, item_index)

def get_tree_item_expanded(hwnd, element_id, item_index=0):
    return dll.EU_GetTreeItemExpanded(hwnd, element_id, item_index)

def set_tree_item_checked(hwnd, element_id, item_index=0, checked=True):
    dll.EU_SetTreeItemChecked(hwnd, element_id, item_index, 1 if checked else 0)

def get_tree_item_checked(hwnd, element_id, item_index=0):
    return dll.EU_GetTreeItemChecked(hwnd, element_id, item_index)

def set_tree_item_lazy(hwnd, element_id, item_index=0, lazy=True):
    dll.EU_SetTreeItemLazy(hwnd, element_id, item_index, 1 if lazy else 0)

def get_tree_item_lazy(hwnd, element_id, item_index=0):
    return dll.EU_GetTreeItemLazy(hwnd, element_id, item_index)

def get_tree_visible_count(hwnd, element_id):
    return dll.EU_GetTreeVisibleCount(hwnd, element_id)

def set_tree_select_items(hwnd, element_id, items=None):
    if items is None:
        items = [("缁勪欢", 0, True), ("鍩虹", 1, True), ("鎸夐挳", 2, True)]
    rows = []
    for item in items:
        label = str(item[0]) if len(item) > 0 else ""
        level = int(item[1]) if len(item) > 1 else 0
        expanded = item[2] if len(item) > 2 else True
        checked = item[3] if len(item) > 3 else False
        lazy = item[4] if len(item) > 4 else False
        rows.append(
            f"{label}\t{level}\t{1 if expanded else 0}\t"
            f"{1 if checked else 0}\t{1 if lazy else 0}"
        )
    data = make_utf8("|".join(rows))
    dll.EU_SetTreeSelectItems(hwnd, element_id, bytes_arg(data), len(data))

def set_tree_select_selected(hwnd, element_id, selected_index=0):
    dll.EU_SetTreeSelectSelected(hwnd, element_id, selected_index)

def get_tree_select_selected(hwnd, element_id):
    return dll.EU_GetTreeSelectSelected(hwnd, element_id)

def set_tree_select_open(hwnd, element_id, open=True):
    dll.EU_SetTreeSelectOpen(hwnd, element_id, 1 if open else 0)

def get_tree_select_open(hwnd, element_id):
    return dll.EU_GetTreeSelectOpen(hwnd, element_id)

def set_tree_select_options(hwnd, element_id, multiple=False, clearable=True, searchable=False):
    dll.EU_SetTreeSelectOptions(
        hwnd, element_id,
        1 if multiple else 0,
        1 if clearable else 0,
        1 if searchable else 0,
    )

def get_tree_select_options(hwnd, element_id):
    multiple = ctypes.c_int()
    clearable = ctypes.c_int()
    searchable = ctypes.c_int()
    selected_count = ctypes.c_int()
    matched_count = ctypes.c_int()
    ok = dll.EU_GetTreeSelectOptions(
        hwnd, element_id,
        ctypes.byref(multiple), ctypes.byref(clearable), ctypes.byref(searchable),
        ctypes.byref(selected_count), ctypes.byref(matched_count),
    )
    return {
        "ok": ok,
        "multiple": multiple.value,
        "clearable": clearable.value,
        "searchable": searchable.value,
        "selected_count": selected_count.value,
        "matched_count": matched_count.value,
    }

def set_tree_select_search(hwnd, element_id, text=""):
    data = make_utf8(text)
    dll.EU_SetTreeSelectSearch(hwnd, element_id, bytes_arg(data), len(data))

def get_tree_select_search(hwnd, element_id):
    needed = dll.EU_GetTreeSelectSearch(hwnd, element_id, None, 0)
    if needed <= 0:
        return ""
    buf = (ctypes.c_ubyte * (needed + 1))()
    copied = dll.EU_GetTreeSelectSearch(hwnd, element_id, buf, needed + 1)
    data = bytes(buf[:min(copied, needed)])
    return data.decode("utf-8", errors="replace")

def clear_tree_select(hwnd, element_id):
    dll.EU_ClearTreeSelect(hwnd, element_id)

def set_tree_select_selected_items(hwnd, element_id, indices=None):
    if indices is None:
        indices = []
    data = make_utf8("|".join(str(int(i)) for i in indices))
    dll.EU_SetTreeSelectSelectedItems(hwnd, element_id, bytes_arg(data), len(data))

def get_tree_select_selected_count(hwnd, element_id):
    return dll.EU_GetTreeSelectSelectedCount(hwnd, element_id)

def get_tree_select_selected_item(hwnd, element_id, position=0):
    return dll.EU_GetTreeSelectSelectedItem(hwnd, element_id, position)

def set_tree_select_item_expanded(hwnd, element_id, item_index=0, expanded=True):
    dll.EU_SetTreeSelectItemExpanded(hwnd, element_id, item_index, 1 if expanded else 0)

def toggle_tree_select_item_expanded(hwnd, element_id, item_index=0):
    dll.EU_ToggleTreeSelectItemExpanded(hwnd, element_id, item_index)

def get_tree_select_item_expanded(hwnd, element_id, item_index=0):
    return dll.EU_GetTreeSelectItemExpanded(hwnd, element_id, item_index)

def _tree_data_payload(data=None, options=None):
    if data is None:
        payload = {"data": []}
    elif isinstance(data, dict):
        payload = dict(data)
    elif isinstance(data, (list, tuple)):
        payload = {"data": list(data)}
    else:
        return data
    if options:
        payload.update(options)
    return payload

def _tree_node_payload(node):
    if isinstance(node, dict) and not any(k in node for k in ("data", "nodes")):
        return {"data": [node]}
    if isinstance(node, (list, tuple)):
        return {"data": list(node)}
    return node

def _tree_keys_payload(keys):
    if keys is None:
        return []
    if isinstance(keys, str):
        text = keys.strip()
        if text.startswith("[") or text.startswith("{"):
            return keys
        return [keys]
    if isinstance(keys, (list, tuple, set)):
        return list(keys)
    return [keys]

def create_tree_json(hwnd, parent_id, data=None, options=None, checked_keys=None,
                     expanded_keys=None, x=0, y=0, w=320, h=260):
    element_id = create_tree(hwnd, parent_id, [], 0, x, y, w, h)
    set_tree_data_json(hwnd, element_id, _tree_data_payload(data, options))
    if options:
        set_tree_options_json(hwnd, element_id, options)
    if checked_keys is not None:
        set_tree_checked_keys_json(hwnd, element_id, checked_keys)
    if expanded_keys is not None:
        set_tree_expanded_keys_json(hwnd, element_id, expanded_keys)
    return element_id

def set_tree_data_json(hwnd, element_id, data):
    raw = json_bytes(_tree_data_payload(data))
    dll.EU_SetTreeDataJson(hwnd, element_id, bytes_arg(raw), len(raw))

def get_tree_data_json(hwnd, element_id):
    return read_json_result(dll.EU_GetTreeDataJson, hwnd, element_id)

def set_tree_options_json(hwnd, element_id, options):
    raw = json_bytes(options or {})
    dll.EU_SetTreeOptionsJson(hwnd, element_id, bytes_arg(raw), len(raw))

def get_tree_state_json(hwnd, element_id):
    return read_json_result(dll.EU_GetTreeStateJson, hwnd, element_id)

def set_tree_checked_keys_json(hwnd, element_id, keys):
    raw = json_bytes(_tree_keys_payload(keys))
    dll.EU_SetTreeCheckedKeysJson(hwnd, element_id, bytes_arg(raw), len(raw))

def get_tree_checked_keys_json(hwnd, element_id):
    return read_json_result(dll.EU_GetTreeCheckedKeysJson, hwnd, element_id)

def set_tree_expanded_keys_json(hwnd, element_id, keys):
    raw = json_bytes(_tree_keys_payload(keys))
    dll.EU_SetTreeExpandedKeysJson(hwnd, element_id, bytes_arg(raw), len(raw))

def get_tree_expanded_keys_json(hwnd, element_id):
    return read_json_result(dll.EU_GetTreeExpandedKeysJson, hwnd, element_id)

def append_tree_node_json(hwnd, element_id, parent_key, node):
    key = make_utf8("" if parent_key is None else str(parent_key))
    raw = json_bytes(_tree_node_payload(node))
    dll.EU_AppendTreeNodeJson(hwnd, element_id, bytes_arg(key), len(key), bytes_arg(raw), len(raw))

def update_tree_node_json(hwnd, element_id, key, node):
    key_data = make_utf8(str(key))
    raw = json_bytes(_tree_node_payload(node))
    dll.EU_UpdateTreeNodeJson(hwnd, element_id, bytes_arg(key_data), len(key_data), bytes_arg(raw), len(raw))

def remove_tree_node_by_key(hwnd, element_id, key):
    key_data = make_utf8(str(key))
    dll.EU_RemoveTreeNodeByKey(hwnd, element_id, bytes_arg(key_data), len(key_data))

def _set_tree_callback(fn, factory, hwnd, element_id, name, callback):
    key = _callback_key(hwnd, element_id, name)
    if callback is None:
        _tree_callback_refs.pop(key, None)
        fn(hwnd, element_id, factory(0))
        return None
    wrapped = _wrap_callback(factory, callback)
    _tree_callback_refs[key] = wrapped
    fn(hwnd, element_id, wrapped)
    return wrapped

def set_tree_node_event_callback(hwnd, element_id, callback):
    return _set_tree_callback(dll.EU_SetTreeNodeEventCallback, TreeNodeEventCallback,
                              hwnd, element_id, "tree_event", callback)

def set_tree_lazy_load_callback(hwnd, element_id, callback):
    return _set_tree_callback(dll.EU_SetTreeLazyLoadCallback, TreeNodeEventCallback,
                              hwnd, element_id, "tree_lazy", callback)

def set_tree_drag_callback(hwnd, element_id, callback):
    return _set_tree_callback(dll.EU_SetTreeDragCallback, TreeNodeEventCallback,
                              hwnd, element_id, "tree_drag", callback)

def set_tree_allow_drag_callback(hwnd, element_id, callback):
    return _set_tree_callback(dll.EU_SetTreeAllowDragCallback, TreeNodeAllowDragCallback,
                              hwnd, element_id, "tree_allow_drag", callback)

def set_tree_allow_drop_callback(hwnd, element_id, callback):
    return _set_tree_callback(dll.EU_SetTreeAllowDropCallback, TreeNodeAllowDropCallback,
                              hwnd, element_id, "tree_allow_drop", callback)

def create_tree_select_json(hwnd, parent_id, data=None, options=None, selected_keys=None,
                            expanded_keys=None, x=0, y=0, w=320, h=38):
    element_id = create_tree_select(hwnd, parent_id, [], 0, x, y, w, h)
    set_tree_select_data_json(hwnd, element_id, _tree_data_payload(data, options))
    if options:
        set_tree_select_options_json(hwnd, element_id, options)
    if selected_keys is not None:
        set_tree_select_selected_keys_json(hwnd, element_id, selected_keys)
    if expanded_keys is not None:
        set_tree_select_expanded_keys_json(hwnd, element_id, expanded_keys)
    return element_id

def set_tree_select_data_json(hwnd, element_id, data):
    raw = json_bytes(_tree_data_payload(data))
    dll.EU_SetTreeSelectDataJson(hwnd, element_id, bytes_arg(raw), len(raw))

def get_tree_select_data_json(hwnd, element_id):
    return read_json_result(dll.EU_GetTreeSelectDataJson, hwnd, element_id)

def set_tree_select_options_json(hwnd, element_id, options):
    raw = json_bytes(options or {})
    dll.EU_SetTreeSelectOptionsJson(hwnd, element_id, bytes_arg(raw), len(raw))

def get_tree_select_state_json(hwnd, element_id):
    return read_json_result(dll.EU_GetTreeSelectStateJson, hwnd, element_id)

def set_tree_select_state_json(hwnd, element_id, state):
    if isinstance(state, dict):
        if "selectedKeys" in state:
            set_tree_select_selected_keys_json(hwnd, element_id, state["selectedKeys"])
        if "expandedKeys" in state:
            set_tree_select_expanded_keys_json(hwnd, element_id, state["expandedKeys"])
        if "searchText" in state:
            set_tree_select_search(hwnd, element_id, state["searchText"])
    set_tree_select_options_json(hwnd, element_id, state)

def set_tree_select_selected_keys_json(hwnd, element_id, keys):
    raw = json_bytes(_tree_keys_payload(keys))
    dll.EU_SetTreeSelectSelectedKeysJson(hwnd, element_id, bytes_arg(raw), len(raw))

def get_tree_select_selected_keys_json(hwnd, element_id):
    return read_json_result(dll.EU_GetTreeSelectSelectedKeysJson, hwnd, element_id)

def set_tree_select_expanded_keys_json(hwnd, element_id, keys):
    raw = json_bytes(_tree_keys_payload(keys))
    dll.EU_SetTreeSelectExpandedKeysJson(hwnd, element_id, bytes_arg(raw), len(raw))

def get_tree_select_expanded_keys_json(hwnd, element_id):
    return read_json_result(dll.EU_GetTreeSelectExpandedKeysJson, hwnd, element_id)

def append_tree_select_node_json(hwnd, element_id, parent_key, node):
    key = make_utf8("" if parent_key is None else str(parent_key))
    raw = json_bytes(_tree_node_payload(node))
    dll.EU_AppendTreeSelectNodeJson(hwnd, element_id, bytes_arg(key), len(key), bytes_arg(raw), len(raw))

def update_tree_select_node_json(hwnd, element_id, key, node):
    key_data = make_utf8(str(key))
    raw = json_bytes(_tree_node_payload(node))
    dll.EU_UpdateTreeSelectNodeJson(hwnd, element_id, bytes_arg(key_data), len(key_data), bytes_arg(raw), len(raw))

def remove_tree_select_node_by_key(hwnd, element_id, key):
    key_data = make_utf8(str(key))
    dll.EU_RemoveTreeSelectNodeByKey(hwnd, element_id, bytes_arg(key_data), len(key_data))

def set_tree_select_node_event_callback(hwnd, element_id, callback):
    return _set_tree_callback(dll.EU_SetTreeSelectNodeEventCallback, TreeNodeEventCallback,
                              hwnd, element_id, "treeselect_event", callback)

def set_tree_select_lazy_load_callback(hwnd, element_id, callback):
    return _set_tree_callback(dll.EU_SetTreeSelectLazyLoadCallback, TreeNodeEventCallback,
                              hwnd, element_id, "treeselect_lazy", callback)

def set_tree_select_drag_callback(hwnd, element_id, callback):
    return _set_tree_callback(dll.EU_SetTreeSelectDragCallback, TreeNodeEventCallback,
                              hwnd, element_id, "treeselect_drag", callback)

def set_tree_select_allow_drag_callback(hwnd, element_id, callback):
    return _set_tree_callback(dll.EU_SetTreeSelectAllowDragCallback, TreeNodeAllowDragCallback,
                              hwnd, element_id, "treeselect_allow_drag", callback)

def set_tree_select_allow_drop_callback(hwnd, element_id, callback):
    return _set_tree_callback(dll.EU_SetTreeSelectAllowDropCallback, TreeNodeAllowDropCallback,
                              hwnd, element_id, "treeselect_allow_drop", callback)

def set_transfer_items(hwnd, element_id, left_items=None, right_items=None):
    if left_items is None:
        left_items = ["列表一", "列表二", "列表三"]
    if right_items is None:
        right_items = []
    left_data = make_utf8("|".join(left_items))
    right_data = make_utf8("|".join(right_items))
    dll.EU_SetTransferItems(
        hwnd, element_id,
        bytes_arg(left_data), len(left_data),
        bytes_arg(right_data), len(right_data)
    )

def transfer_move_right(hwnd, element_id):
    dll.EU_TransferMoveRight(hwnd, element_id)

def transfer_move_left(hwnd, element_id):
    dll.EU_TransferMoveLeft(hwnd, element_id)

def transfer_move_all_right(hwnd, element_id):
    dll.EU_TransferMoveAllRight(hwnd, element_id)

def transfer_move_all_left(hwnd, element_id):
    dll.EU_TransferMoveAllLeft(hwnd, element_id)

def set_transfer_selected(hwnd, element_id, side=0, selected_index=0):
    dll.EU_SetTransferSelected(hwnd, element_id, side, selected_index)

def get_transfer_selected(hwnd, element_id, side=0):
    return dll.EU_GetTransferSelected(hwnd, element_id, side)

def get_transfer_count(hwnd, element_id, side=0):
    return dll.EU_GetTransferCount(hwnd, element_id, side)

def set_transfer_filters(hwnd, element_id, left_filter="", right_filter=""):
    left_data = make_utf8(left_filter)
    right_data = make_utf8(right_filter)
    dll.EU_SetTransferFilters(
        hwnd, element_id,
        bytes_arg(left_data), len(left_data),
        bytes_arg(right_data), len(right_data),
    )

def get_transfer_matched_count(hwnd, element_id, side=0):
    return dll.EU_GetTransferMatchedCount(hwnd, element_id, side)

def set_transfer_item_disabled(hwnd, element_id, side=0, item_index=0, disabled=True):
    dll.EU_SetTransferItemDisabled(hwnd, element_id, side, item_index, 1 if disabled else 0)

def get_transfer_item_disabled(hwnd, element_id, side=0, item_index=0):
    return dll.EU_GetTransferItemDisabled(hwnd, element_id, side, item_index)

def get_transfer_disabled_count(hwnd, element_id, side=0):
    return dll.EU_GetTransferDisabledCount(hwnd, element_id, side)

def set_transfer_data_ex(hwnd, element_id, items=None, target_keys=None, props=None):
    item_data = make_utf8("|".join(_transfer_item_rows(items or [], props=props)))
    target_data = make_utf8(_transfer_key_text(target_keys or []))
    dll.EU_SetTransferDataEx(
        hwnd, element_id,
        bytes_arg(item_data), len(item_data),
        bytes_arg(target_data), len(target_data),
    )

def set_transfer_options(hwnd, element_id, filterable=False, multiple=True,
                         show_footer=False, show_select_all=True,
                         show_count=True, render_mode=0):
    dll.EU_SetTransferOptions(
        hwnd, element_id,
        1 if filterable else 0,
        1 if multiple else 0,
        1 if show_footer else 0,
        1 if show_select_all else 0,
        1 if show_count else 0,
        int(render_mode),
    )

def get_transfer_options(hwnd, element_id):
    values = [ctypes.c_int() for _ in range(6)]
    ok = dll.EU_GetTransferOptions(hwnd, element_id, *(ctypes.byref(v) for v in values))
    if not ok:
        return None
    return {
        "filterable": bool(values[0].value),
        "multiple": bool(values[1].value),
        "show_footer": bool(values[2].value),
        "show_select_all": bool(values[3].value),
        "show_count": bool(values[4].value),
        "render_mode": values[5].value,
    }

def set_transfer_titles(hwnd, element_id, left_title="源列表", right_title="目标列表"):
    left_data = make_utf8(left_title)
    right_data = make_utf8(right_title)
    dll.EU_SetTransferTitles(
        hwnd, element_id,
        bytes_arg(left_data), len(left_data),
        bytes_arg(right_data), len(right_data),
    )

def set_transfer_button_texts(hwnd, element_id, left_text="到左边", right_text="到右边"):
    left_data = make_utf8(left_text)
    right_data = make_utf8(right_text)
    dll.EU_SetTransferButtonTexts(
        hwnd, element_id,
        bytes_arg(left_data), len(left_data),
        bytes_arg(right_data), len(right_data),
    )

def set_transfer_format(hwnd, element_id, no_checked="${total}", has_checked="${checked}/${total}"):
    no_data = make_utf8(no_checked)
    has_data = make_utf8(has_checked)
    dll.EU_SetTransferFormat(
        hwnd, element_id,
        bytes_arg(no_data), len(no_data),
        bytes_arg(has_data), len(has_data),
    )

def set_transfer_item_template(hwnd, element_id, template="{label}"):
    data = make_utf8(template)
    dll.EU_SetTransferItemTemplate(hwnd, element_id, bytes_arg(data), len(data))

def set_transfer_footer_texts(hwnd, element_id, left_text="左侧操作", right_text="右侧操作"):
    left_data = make_utf8(left_text)
    right_data = make_utf8(right_text)
    dll.EU_SetTransferFooterTexts(
        hwnd, element_id,
        bytes_arg(left_data), len(left_data),
        bytes_arg(right_data), len(right_data),
    )

def set_transfer_filter_placeholder(hwnd, element_id, text="请输入关键词 🔎"):
    data = make_utf8(text)
    dll.EU_SetTransferFilterPlaceholder(hwnd, element_id, bytes_arg(data), len(data))

def set_transfer_checked_keys(hwnd, element_id, left_keys=None, right_keys=None):
    left_data = make_utf8(_transfer_key_text(left_keys or []))
    right_data = make_utf8(_transfer_key_text(right_keys or []))
    dll.EU_SetTransferCheckedKeys(
        hwnd, element_id,
        bytes_arg(left_data), len(left_data),
        bytes_arg(right_data), len(right_data),
    )

def get_transfer_checked_count(hwnd, element_id, side=0):
    return dll.EU_GetTransferCheckedCount(hwnd, element_id, side)

def _read_utf8(fn, *args, buffer_size=2048):
    needed = fn(*args, None, 0)
    size = max(buffer_size, needed + 1)
    buf = (ctypes.c_ubyte * size)()
    written = fn(*args, buf, size)
    if written <= 0:
        return ""
    return bytes(buf[:min(written, size - 1)]).decode("utf-8", errors="replace")

def get_transfer_value_keys(hwnd, element_id, buffer_size=2048):
    return _read_utf8(dll.EU_GetTransferValueKeys, hwnd, element_id, buffer_size=buffer_size)

def get_transfer_text(hwnd, element_id, text_type=0, buffer_size=2048):
    return _read_utf8(dll.EU_GetTransferText, hwnd, element_id, text_type, buffer_size=buffer_size)

def create_autocomplete(hwnd, parent_id, value="", suggestions=None,
                        x=0, y=0, w=260, h=36):
    if suggestions is None:
        suggestions = ["鍖椾含", "涓婃捣", "骞垮窞", "娣卞湷"]
    value_data = make_utf8(value)
    suggestion_data = make_utf8("|".join(suggestions))
    return dll.EU_CreateAutocomplete(
        hwnd, parent_id,
        bytes_arg(value_data), len(value_data),
        bytes_arg(suggestion_data), len(suggestion_data),
        x, y, w, h
    )

def create_mentions(hwnd, parent_id, value="", suggestions=None,
                    x=0, y=0, w=320, h=40):
    if suggestions is None:
        suggestions = ["Alice", "Bob", "Charlie"]
    value_data = make_utf8(value)
    suggestion_data = make_utf8("|".join(suggestions))
    return dll.EU_CreateMentions(
        hwnd, parent_id,
        bytes_arg(value_data), len(value_data),
        bytes_arg(suggestion_data), len(suggestion_data),
        x, y, w, h
    )

def create_cascader(hwnd, parent_id, options=None, selected=None,
                    x=0, y=0, w=260, h=36):
    if options is None:
        options = [
            ("浙江", "杭州", "西湖区"),
            ("江苏", "南京", "玄武区"),
        ]
    if selected is None:
        selected = []
    option_rows = []
    for item in options:
        option_rows.append("/".join(str(part) for part in item))
    selected_data = make_utf8("/".join(str(part) for part in selected))
    options_data = make_utf8("|".join(option_rows))
    return dll.EU_CreateCascader(
        hwnd, parent_id,
        bytes_arg(options_data), len(options_data),
        bytes_arg(selected_data), len(selected_data),
        x, y, w, h
    )

def set_autocomplete_suggestions(hwnd, element_id, suggestions=None):
    if suggestions is None:
        suggestions = ["鍖椾含", "涓婃捣", "骞垮窞", "娣卞湷"]
    data = make_utf8("|".join(suggestions))
    dll.EU_SetAutocompleteSuggestions(hwnd, element_id, bytes_arg(data), len(data))

def set_autocomplete_value(hwnd, element_id, value=""):
    data = make_utf8(value)
    dll.EU_SetAutocompleteValue(hwnd, element_id, bytes_arg(data), len(data))

def set_autocomplete_open(hwnd, element_id, open=True):
    dll.EU_SetAutocompleteOpen(hwnd, element_id, 1 if open else 0)

def set_autocomplete_selected(hwnd, element_id, selected_index=0):
    dll.EU_SetAutocompleteSelected(hwnd, element_id, selected_index)

def set_autocomplete_async_state(hwnd, element_id, loading=True, request_id=0):
    dll.EU_SetAutocompleteAsyncState(hwnd, element_id, 1 if loading else 0, request_id)

def set_autocomplete_empty_text(hwnd, element_id, text="🫥 没有匹配建议"):
    data = make_utf8(text)
    dll.EU_SetAutocompleteEmptyText(hwnd, element_id, bytes_arg(data), len(data))

def get_autocomplete_value(hwnd, element_id):
    needed = dll.EU_GetAutocompleteValue(hwnd, element_id, None, 0)
    if needed <= 0:
        return ""
    buf = (ctypes.c_ubyte * (needed + 1))()
    copied = dll.EU_GetAutocompleteValue(hwnd, element_id, buf, needed + 1)
    data = bytes(buf[:min(copied, needed)])
    return data.decode("utf-8", errors="replace")

def get_autocomplete_open(hwnd, element_id):
    return dll.EU_GetAutocompleteOpen(hwnd, element_id)

def get_autocomplete_selected(hwnd, element_id):
    return dll.EU_GetAutocompleteSelected(hwnd, element_id)

def get_autocomplete_suggestion_count(hwnd, element_id):
    return dll.EU_GetAutocompleteSuggestionCount(hwnd, element_id)

def get_autocomplete_options(hwnd, element_id):
    open_state = ctypes.c_int()
    selected = ctypes.c_int()
    count = ctypes.c_int()
    loading = ctypes.c_int()
    request_id = ctypes.c_int()
    ok = dll.EU_GetAutocompleteOptions(
        hwnd, element_id,
        ctypes.byref(open_state), ctypes.byref(selected), ctypes.byref(count),
        ctypes.byref(loading), ctypes.byref(request_id),
    )
    return {
        "ok": ok,
        "open": open_state.value,
        "selected": selected.value,
        "count": count.value,
        "loading": loading.value,
        "request_id": request_id.value,
    }

def set_autocomplete_placeholder(hwnd, element_id, text="请输入内容"):
    data = make_utf8(text)
    dll.EU_SetAutocompletePlaceholder(hwnd, element_id, bytes_arg(data), len(data))

def get_autocomplete_placeholder(hwnd, element_id):
    needed = dll.EU_GetAutocompletePlaceholder(hwnd, element_id, None, 0)
    if needed <= 0:
        return ""
    buf = (ctypes.c_ubyte * (needed + 1))()
    dll.EU_GetAutocompletePlaceholder(hwnd, element_id, buf, needed + 1)
    return bytes(buf[:needed]).decode("utf-8", errors="replace")

def set_autocomplete_icons(hwnd, element_id, prefix_icon="", suffix_icon=""):
    prefix_data = make_utf8(prefix_icon)
    suffix_data = make_utf8(suffix_icon)
    dll.EU_SetAutocompleteIcons(
        hwnd, element_id,
        bytes_arg(prefix_data), len(prefix_data),
        bytes_arg(suffix_data), len(suffix_data),
    )

def get_autocomplete_icons(hwnd, element_id, buffer_size=512):
    prefix = (ctypes.c_ubyte * buffer_size)()
    suffix = (ctypes.c_ubyte * buffer_size)()
    ok = dll.EU_GetAutocompleteIcons(hwnd, element_id, prefix, buffer_size, suffix, buffer_size)
    if not ok:
        return None
    return (
        bytes(prefix).split(b"\0", 1)[0].decode("utf-8", errors="replace"),
        bytes(suffix).split(b"\0", 1)[0].decode("utf-8", errors="replace"),
    )

def set_autocomplete_behavior_options(hwnd, element_id, trigger_on_focus=True):
    dll.EU_SetAutocompleteBehaviorOptions(hwnd, element_id, 1 if trigger_on_focus else 0)

def get_autocomplete_behavior_options(hwnd, element_id):
    trigger = ctypes.c_int()
    ok = dll.EU_GetAutocompleteBehaviorOptions(hwnd, element_id, ctypes.byref(trigger))
    if not ok:
        return None
    return {"trigger_on_focus": bool(trigger.value)}

def create_autocomplete(hwnd, parent_id, value="", suggestions=None,
                        placeholder="请输入内容", trigger_on_focus=True,
                        prefix_icon="", suffix_icon="",
                        x=0, y=0, w=260, h=36):
    if (
        type(placeholder) is int and
        type(trigger_on_focus) is int and
        type(prefix_icon) is int and
        type(suffix_icon) is int and
        x == 0 and y == 0 and w == 260 and h == 36
    ):
        x, y, w, h = placeholder, trigger_on_focus, prefix_icon, suffix_icon
        placeholder = "请输入内容"
        trigger_on_focus = True
        prefix_icon = ""
        suffix_icon = ""
    value_data = make_utf8(value)
    suggestion_data = _autocomplete_suggestions_data(suggestions)
    element_id = dll.EU_CreateAutocomplete(
        hwnd, parent_id,
        bytes_arg(value_data), len(value_data),
        bytes_arg(suggestion_data), len(suggestion_data),
        x, y, w, h
    )
    if not element_id:
        return 0
    if placeholder:
        set_autocomplete_placeholder(hwnd, element_id, placeholder)
    if prefix_icon or suffix_icon:
        set_autocomplete_icons(hwnd, element_id, prefix_icon, suffix_icon)
    if not trigger_on_focus:
        set_autocomplete_behavior_options(hwnd, element_id, trigger_on_focus=False)
    return element_id

def set_autocomplete_suggestions(hwnd, element_id, suggestions=None):
    data = _autocomplete_suggestions_data(suggestions)
    dll.EU_SetAutocompleteSuggestions(hwnd, element_id, bytes_arg(data), len(data))

def set_mentions_value(hwnd, element_id, value=""):
    data = make_utf8(value)
    dll.EU_SetMentionsValue(hwnd, element_id, bytes_arg(data), len(data))

def set_mentions_suggestions(hwnd, element_id, suggestions=None):
    if suggestions is None:
        suggestions = ["Alice", "Bob", "Charlie"]
    data = make_utf8("|".join(suggestions))
    dll.EU_SetMentionsSuggestions(hwnd, element_id, bytes_arg(data), len(data))

def set_mentions_open(hwnd, element_id, open=True):
    dll.EU_SetMentionsOpen(hwnd, element_id, 1 if open else 0)

def set_mentions_selected(hwnd, element_id, selected_index=0):
    dll.EU_SetMentionsSelected(hwnd, element_id, selected_index)

def set_mentions_options(hwnd, element_id, trigger="@", filter_enabled=True, insert_space=True):
    data = make_utf8(trigger[:1] if trigger else "@")
    dll.EU_SetMentionsOptions(
        hwnd, element_id, bytes_arg(data), len(data),
        1 if filter_enabled else 0,
        1 if insert_space else 0,
    )

def set_mentions_filter(hwnd, element_id, text=""):
    data = make_utf8(text)
    dll.EU_SetMentionsFilter(hwnd, element_id, bytes_arg(data), len(data))

def insert_mentions_selected(hwnd, element_id):
    dll.EU_InsertMentionsSelected(hwnd, element_id)

def get_mentions_value(hwnd, element_id):
    needed = dll.EU_GetMentionsValue(hwnd, element_id, None, 0)
    if needed <= 0:
        return ""
    buf = (ctypes.c_ubyte * (needed + 1))()
    copied = dll.EU_GetMentionsValue(hwnd, element_id, buf, needed + 1)
    data = bytes(buf[:min(copied, needed)])
    return data.decode("utf-8", errors="replace")

def get_mentions_open(hwnd, element_id):
    return dll.EU_GetMentionsOpen(hwnd, element_id)

def get_mentions_selected(hwnd, element_id):
    return dll.EU_GetMentionsSelected(hwnd, element_id)

def get_mentions_suggestion_count(hwnd, element_id):
    return dll.EU_GetMentionsSuggestionCount(hwnd, element_id)

def get_mentions_options(hwnd, element_id):
    open_state = ctypes.c_int()
    selected = ctypes.c_int()
    count = ctypes.c_int()
    matched = ctypes.c_int()
    trigger = ctypes.c_int()
    ok = dll.EU_GetMentionsOptions(
        hwnd, element_id,
        ctypes.byref(open_state), ctypes.byref(selected), ctypes.byref(count),
        ctypes.byref(matched), ctypes.byref(trigger),
    )
    return {
        "ok": ok,
        "open": open_state.value,
        "selected": selected.value,
        "count": count.value,
        "matched": matched.value,
        "trigger": trigger.value,
    }

def set_cascader_options(hwnd, element_id, options=None):
    if options is None:
        options = [
            ("浙江", "杭州", "西湖区"),
            ("江苏", "南京", "玄武区"),
        ]
    option_rows = ["/".join(str(part) for part in item) for item in options]
    data = make_utf8("|".join(option_rows))
    dll.EU_SetCascaderOptions(hwnd, element_id, bytes_arg(data), len(data))

def set_cascader_value(hwnd, element_id, selected=None):
    if selected is None:
        selected = []
    data = make_utf8("/".join(str(part) for part in selected))
    dll.EU_SetCascaderValue(hwnd, element_id, bytes_arg(data), len(data))

def set_cascader_open(hwnd, element_id, open=True):
    dll.EU_SetCascaderOpen(hwnd, element_id, 1 if open else 0)

def set_cascader_advanced_options(hwnd, element_id, searchable=True, lazy_mode=False):
    dll.EU_SetCascaderAdvancedOptions(
        hwnd, element_id,
        1 if searchable else 0,
        1 if lazy_mode else 0,
    )

def set_cascader_search(hwnd, element_id, text=""):
    data = make_utf8(text)
    dll.EU_SetCascaderSearch(hwnd, element_id, bytes_arg(data), len(data))

def get_cascader_open(hwnd, element_id):
    return dll.EU_GetCascaderOpen(hwnd, element_id)

def get_cascader_option_count(hwnd, element_id):
    return dll.EU_GetCascaderOptionCount(hwnd, element_id)

def get_cascader_selected_depth(hwnd, element_id):
    return dll.EU_GetCascaderSelectedDepth(hwnd, element_id)

def get_cascader_level_count(hwnd, element_id):
    return dll.EU_GetCascaderLevelCount(hwnd, element_id)

def get_cascader_advanced_options(hwnd, element_id):
    searchable = ctypes.c_int()
    lazy_mode = ctypes.c_int()
    matched = ctypes.c_int()
    last_lazy = ctypes.c_int()
    ok = dll.EU_GetCascaderAdvancedOptions(
        hwnd, element_id,
        ctypes.byref(searchable), ctypes.byref(lazy_mode),
        ctypes.byref(matched), ctypes.byref(last_lazy),
    )
    return {
        "ok": ok,
        "searchable": searchable.value,
        "lazy_mode": lazy_mode.value,
        "matched": matched.value,
        "last_lazy_level": last_lazy.value,
    }

def create_datepicker(hwnd, parent_id, year=2026, month=5, selected_day=2,
                      x=0, y=0, w=220, h=36):
    return dll.EU_CreateDatePicker(
        hwnd, parent_id, year, month, selected_day, x, y, w, h
    )

def create_timepicker(hwnd, parent_id, hour=9, minute=30,
                      x=0, y=0, w=180, h=36):
    return dll.EU_CreateTimePicker(
        hwnd, parent_id, hour, minute, x, y, w, h
    )

def create_datetimepicker(hwnd, parent_id, year=2026, month=5, day=2,
                          hour=9, minute=30, x=0, y=0, w=260, h=36):
    return dll.EU_CreateDateTimePicker(
        hwnd, parent_id, year, month, day, hour, minute, x, y, w, h
    )

def create_time_select(hwnd, parent_id, hour=9, minute=30,
                       x=0, y=0, w=180, h=36):
    return dll.EU_CreateTimeSelect(
        hwnd, parent_id, hour, minute, x, y, w, h
    )

def set_calendar_date(hwnd, element_id, year=2026, month=5, selected_day=1):
    dll.EU_SetCalendarDate(hwnd, element_id, year, month, selected_day)

def set_calendar_range(hwnd, element_id, min_value=0, max_value=0):
    dll.EU_SetCalendarRange(hwnd, element_id, min_value, max_value)

def set_calendar_options(hwnd, element_id, today_value=0, show_today=True):
    dll.EU_SetCalendarOptions(hwnd, element_id, today_value, 1 if show_today else 0)

def calendar_move_month(hwnd, element_id, delta_months=1):
    dll.EU_CalendarMoveMonth(hwnd, element_id, delta_months)

def get_calendar_value(hwnd, element_id):
    return dll.EU_GetCalendarValue(hwnd, element_id)

def get_calendar_range(hwnd, element_id):
    min_value = ctypes.c_int()
    max_value = ctypes.c_int()
    ok = dll.EU_GetCalendarRange(hwnd, element_id, ctypes.byref(min_value), ctypes.byref(max_value))
    return (min_value.value, max_value.value) if ok else None

def get_calendar_options(hwnd, element_id):
    today_value = ctypes.c_int()
    show_today = ctypes.c_int()
    ok = dll.EU_GetCalendarOptions(hwnd, element_id, ctypes.byref(today_value), ctypes.byref(show_today))
    return (today_value.value, bool(show_today.value)) if ok else None

def set_calendar_selection_range(hwnd, element_id, start_value=0, end_value=0, enabled=True):
    dll.EU_SetCalendarSelectionRange(hwnd, element_id, start_value, end_value, 1 if enabled else 0)

def get_calendar_selection_range(hwnd, element_id):
    start_value = ctypes.c_int()
    end_value = ctypes.c_int()
    enabled = ctypes.c_int()
    ok = dll.EU_GetCalendarSelectionRange(
        hwnd, element_id,
        ctypes.byref(start_value), ctypes.byref(end_value), ctypes.byref(enabled)
    )
    return (start_value.value, end_value.value, bool(enabled.value)) if ok else None

def set_calendar_display_range(hwnd, element_id, start_value=0, end_value=0):
    dll.EU_SetCalendarDisplayRange(hwnd, element_id, start_value, end_value)

def get_calendar_display_range(hwnd, element_id):
    start_value = ctypes.c_int()
    end_value = ctypes.c_int()
    ok = dll.EU_GetCalendarDisplayRange(
        hwnd, element_id,
        ctypes.byref(start_value), ctypes.byref(end_value)
    )
    return (start_value.value, end_value.value) if ok else None

def _calendar_cell_value(value):
    text = "" if value is None else str(value)
    return text.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n")

def _calendar_cell_line(item):
    if isinstance(item, str):
        return item
    pairs = []
    for key in (
        "date", "label", "extra", "emoji", "badge", "bg", "fg", "border",
        "badge_bg", "badge_fg", "font_flags", "disabled"
    ):
        if key in item and item[key] is not None:
            pairs.append(f"{key}={_calendar_cell_value(item[key])}")
    return "\t".join(pairs)

def calendar_cell_items_spec(items):
    if isinstance(items, str):
        return items
    return "\n".join(_calendar_cell_line(item) for item in (items or []))

def set_calendar_cell_items(hwnd, element_id, items):
    spec = calendar_cell_items_spec(items)
    data = make_utf8(spec)
    dll.EU_SetCalendarCellItems(hwnd, element_id, bytes_arg(data), len(data))

def get_calendar_cell_items(hwnd, element_id):
    needed = dll.EU_GetCalendarCellItems(hwnd, element_id, None, 0)
    if needed <= 0:
        return ""
    buf = (ctypes.c_ubyte * (needed + 1))()
    copied = dll.EU_GetCalendarCellItems(hwnd, element_id, buf, needed + 1)
    return bytes(buf[:min(copied, needed)]).decode("utf-8", errors="replace")

def clear_calendar_cell_items(hwnd, element_id):
    dll.EU_ClearCalendarCellItems(hwnd, element_id)

def set_calendar_visual_options(hwnd, element_id, show_header=True, show_week_header=True,
                                label_mode=0, show_adjacent_days=True, cell_radius=8.0):
    dll.EU_SetCalendarVisualOptions(
        hwnd, element_id,
        1 if show_header else 0,
        1 if show_week_header else 0,
        label_mode,
        1 if show_adjacent_days else 0,
        float(cell_radius),
    )

def get_calendar_visual_options(hwnd, element_id):
    show_header = ctypes.c_int()
    show_week_header = ctypes.c_int()
    label_mode = ctypes.c_int()
    show_adjacent_days = ctypes.c_int()
    cell_radius = ctypes.c_float()
    ok = dll.EU_GetCalendarVisualOptions(
        hwnd, element_id,
        ctypes.byref(show_header), ctypes.byref(show_week_header),
        ctypes.byref(label_mode), ctypes.byref(show_adjacent_days),
        ctypes.byref(cell_radius),
    )
    if not ok:
        return None
    return (
        bool(show_header.value),
        bool(show_week_header.value),
        label_mode.value,
        bool(show_adjacent_days.value),
        cell_radius.value,
    )

def set_calendar_state_colors(hwnd, element_id, selected_bg=0, selected_fg=0, range_bg=0,
                              today_border=0, hover_bg=0, disabled_fg=0, adjacent_fg=0):
    dll.EU_SetCalendarStateColors(
        hwnd, element_id,
        selected_bg, selected_fg, range_bg, today_border,
        hover_bg, disabled_fg, adjacent_fg,
    )

def get_calendar_state_colors(hwnd, element_id):
    values = [ctypes.c_uint32() for _ in range(7)]
    ok = dll.EU_GetCalendarStateColors(
        hwnd, element_id,
        *(ctypes.byref(value) for value in values)
    )
    return tuple(value.value for value in values) if ok else None

def set_calendar_selected_marker(hwnd, element_id, marker=""):
    data = make_utf8(marker or "")
    dll.EU_SetCalendarSelectedMarker(hwnd, element_id, bytes_arg(data), len(data))

_calendar_change_callback_refs = {}

def set_calendar_change_callback(hwnd, element_id, callback):
    key = _callback_key(hwnd, element_id, "calendar_change")
    if callback is None:
        _calendar_change_callback_refs.pop(key, None)
        dll.EU_SetCalendarChangeCallback(hwnd, element_id, ValueCallback(0))
        return None
    wrapped = _wrap_callback(ValueCallback, callback)
    _calendar_change_callback_refs[key] = wrapped
    dll.EU_SetCalendarChangeCallback(hwnd, element_id, wrapped)
    return wrapped

def set_datepicker_date(hwnd, element_id, year=2026, month=5, selected_day=2):
    dll.EU_SetDatePickerDate(hwnd, element_id, year, month, selected_day)

def set_datepicker_range(hwnd, element_id, min_value=0, max_value=0):
    dll.EU_SetDatePickerRange(hwnd, element_id, min_value, max_value)

def set_datepicker_options(hwnd, element_id, today_value=0, show_today=True, date_format=0):
    dll.EU_SetDatePickerOptions(
        hwnd, element_id, today_value, 1 if show_today else 0, date_format
    )

def set_datepicker_open(hwnd, element_id, open=True):
    dll.EU_SetDatePickerOpen(hwnd, element_id, 1 if open else 0)

def clear_datepicker(hwnd, element_id):
    dll.EU_ClearDatePicker(hwnd, element_id)

def datepicker_select_today(hwnd, element_id):
    dll.EU_DatePickerSelectToday(hwnd, element_id)

def get_datepicker_open(hwnd, element_id):
    return dll.EU_GetDatePickerOpen(hwnd, element_id)

def get_datepicker_value(hwnd, element_id):
    return dll.EU_GetDatePickerValue(hwnd, element_id)

def datepicker_move_month(hwnd, element_id, delta_months=1):
    dll.EU_DatePickerMoveMonth(hwnd, element_id, delta_months)

def get_datepicker_range(hwnd, element_id):
    min_value = ctypes.c_int()
    max_value = ctypes.c_int()
    ok = dll.EU_GetDatePickerRange(hwnd, element_id, ctypes.byref(min_value), ctypes.byref(max_value))
    return (min_value.value, max_value.value) if ok else None

def get_datepicker_options(hwnd, element_id):
    today_value = ctypes.c_int()
    show_today = ctypes.c_int()
    date_format = ctypes.c_int()
    ok = dll.EU_GetDatePickerOptions(
        hwnd, element_id,
        ctypes.byref(today_value), ctypes.byref(show_today), ctypes.byref(date_format),
    )
    return (today_value.value, bool(show_today.value), date_format.value) if ok else None

def set_datepicker_selection_range(hwnd, element_id, start_value=0, end_value=0, enabled=True):
    dll.EU_SetDatePickerSelectionRange(
        hwnd, element_id, start_value, end_value, 1 if enabled else 0
    )

def get_datepicker_selection_range(hwnd, element_id):
    start_value = ctypes.c_int()
    end_value = ctypes.c_int()
    enabled = ctypes.c_int()
    ok = dll.EU_GetDatePickerSelectionRange(
        hwnd, element_id,
        ctypes.byref(start_value), ctypes.byref(end_value), ctypes.byref(enabled),
    )
    return (start_value.value, end_value.value, bool(enabled.value)) if ok else None

def set_datepicker_placeholder(hwnd, element_id, text):
    data = make_utf8(text)
    dll.EU_SetDatePickerPlaceholder(hwnd, element_id, bytes_arg(data), len(data))

def set_datepicker_range_separator(hwnd, element_id, sep):
    data = make_utf8(sep)
    dll.EU_SetDatePickerRangeSeparator(hwnd, element_id, bytes_arg(data), len(data))

def set_datepicker_format(hwnd, element_id, fmt):
    data = make_utf8(fmt)
    dll.EU_SetDatePickerFormat(hwnd, element_id, bytes_arg(data), len(data))

def set_datepicker_align(hwnd, element_id, align=0):
    dll.EU_SetDatePickerAlign(hwnd, element_id, align)

def set_datepicker_mode(hwnd, element_id, mode=0):
    dll.EU_SetDatePickerMode(hwnd, element_id, mode)

def get_datepicker_mode(hwnd, element_id):
    return dll.EU_GetDatePickerMode(hwnd, element_id)

def set_datepicker_multi_select(hwnd, element_id, enabled=True):
    dll.EU_SetDatePickerMultiSelect(hwnd, element_id, 1 if enabled else 0)

def get_datepicker_selected_dates(hwnd, element_id):
    needed = dll.EU_GetDatePickerSelectedDates(hwnd, element_id, None, 0)
    if needed <= 0:
        return []
    buf = (ctypes.c_ubyte * (needed + 1))()
    copied = dll.EU_GetDatePickerSelectedDates(hwnd, element_id, buf, needed + 1)
    raw = bytes(buf[:min(copied, needed)])
    return [int(s) for s in raw.decode("utf-8", errors="replace").split(",") if s]

def set_datepicker_shortcuts(hwnd, element_id, shortcuts_text):
    data = make_utf8(shortcuts_text)
    dll.EU_SetDatePickerShortcuts(hwnd, element_id, bytes_arg(data), len(data))

def create_date_range_picker(hwnd, parent_id, start=0, end=0,
                              x=0, y=0, w=360, h=42):
    return dll.EU_CreateDateRangePicker(hwnd, parent_id, start, end, x, y, w, h)

def set_date_range_picker_value(hwnd, element_id, start, end):
    dll.EU_SetDateRangePickerValue(hwnd, element_id, start, end)

def get_date_range_picker_value(hwnd, element_id):
    s = ctypes.c_int(); e = ctypes.c_int()
    if dll.EU_GetDateRangePickerValue(hwnd, element_id, ctypes.byref(s), ctypes.byref(e)):
        return (s.value, e.value)
    return None

def set_date_range_picker_range(hwnd, element_id, min_v, max_v):
    dll.EU_SetDateRangePickerRange(hwnd, element_id, min_v, max_v)

def set_date_range_picker_placeholders(hwnd, element_id, start_text, end_text):
    sd = make_utf8(start_text); ed = make_utf8(end_text)
    dll.EU_SetDateRangePickerPlaceholders(hwnd, element_id, bytes_arg(sd), len(sd), bytes_arg(ed), len(ed))

def set_date_range_picker_separator(hwnd, element_id, sep):
    data = make_utf8(sep)
    dll.EU_SetDateRangePickerSeparator(hwnd, element_id, bytes_arg(data), len(data))

def set_date_range_picker_format(hwnd, element_id, fmt=0):
    dll.EU_SetDateRangePickerFormat(hwnd, element_id, fmt)

def set_date_range_picker_align(hwnd, element_id, align=0):
    dll.EU_SetDateRangePickerAlign(hwnd, element_id, align)

def set_date_range_picker_shortcuts(hwnd, element_id, shortcuts_text):
    data = make_utf8(shortcuts_text)
    dll.EU_SetDateRangePickerShortcuts(hwnd, element_id, bytes_arg(data), len(data))

def set_date_range_picker_open(hwnd, element_id, open_state):
    dll.EU_SetDateRangePickerOpen(hwnd, element_id, 1 if open_state else 0)

def get_date_range_picker_open(hwnd, element_id):
    return bool(dll.EU_GetDateRangePickerOpen(hwnd, element_id))

def date_range_picker_clear(hwnd, element_id):
    dll.EU_DateRangePickerClear(hwnd, element_id)

def set_timepicker_time(hwnd, element_id, hour=9, minute=30):
    dll.EU_SetTimePickerTime(hwnd, element_id, hour, minute)

def set_timepicker_range(hwnd, element_id, min_value=0, max_value=2359):
    dll.EU_SetTimePickerRange(hwnd, element_id, min_value, max_value)

def set_timepicker_options(hwnd, element_id, step_minutes=10, time_format=0):
    dll.EU_SetTimePickerOptions(hwnd, element_id, step_minutes, time_format)

def set_timepicker_open(hwnd, element_id, open=True):
    dll.EU_SetTimePickerOpen(hwnd, element_id, 1 if open else 0)

def set_timepicker_scroll(hwnd, element_id, hour_scroll=0, minute_scroll=0):
    dll.EU_SetTimePickerScroll(hwnd, element_id, hour_scroll, minute_scroll)

def get_timepicker_open(hwnd, element_id):
    return dll.EU_GetTimePickerOpen(hwnd, element_id)

def get_timepicker_value(hwnd, element_id):
    return dll.EU_GetTimePickerValue(hwnd, element_id)

def get_timepicker_range(hwnd, element_id):
    min_value = ctypes.c_int()
    max_value = ctypes.c_int()
    ok = dll.EU_GetTimePickerRange(hwnd, element_id, ctypes.byref(min_value), ctypes.byref(max_value))
    return (min_value.value, max_value.value) if ok else None

def get_timepicker_options(hwnd, element_id):
    step_minutes = ctypes.c_int()
    time_format = ctypes.c_int()
    ok = dll.EU_GetTimePickerOptions(hwnd, element_id, ctypes.byref(step_minutes), ctypes.byref(time_format))
    return (step_minutes.value, time_format.value) if ok else None

def get_timepicker_scroll(hwnd, element_id):
    hour_scroll = ctypes.c_int()
    minute_scroll = ctypes.c_int()
    ok = dll.EU_GetTimePickerScroll(
        hwnd, element_id, ctypes.byref(hour_scroll), ctypes.byref(minute_scroll)
    )
    return (hour_scroll.value, minute_scroll.value) if ok else None

def set_timepicker_arrow_control(hwnd, element_id, enabled=True):
    dll.EU_SetTimePickerArrowControl(hwnd, element_id, 1 if enabled else 0)

def get_timepicker_arrow_control(hwnd, element_id):
    return bool(dll.EU_GetTimePickerArrowControl(hwnd, element_id))

def set_timepicker_range_select(hwnd, element_id, enabled=True, start_hhmm=0, end_hhmm=2359):
    dll.EU_SetTimePickerRangeSelect(hwnd, element_id, 1 if enabled else 0, start_hhmm, end_hhmm)

def set_timepicker_start_placeholder(hwnd, element_id, text="开始时间"):
    data = make_utf8(text)
    dll.EU_SetTimePickerStartPlaceholder(hwnd, element_id, bytes_arg(data), len(data))

def set_timepicker_end_placeholder(hwnd, element_id, text="结束时间"):
    data = make_utf8(text)
    dll.EU_SetTimePickerEndPlaceholder(hwnd, element_id, bytes_arg(data), len(data))

def set_timepicker_range_placeholders(hwnd, element_id, start_text="开始时间", end_text="结束时间"):
    set_timepicker_start_placeholder(hwnd, element_id, start_text)
    set_timepicker_end_placeholder(hwnd, element_id, end_text)

def set_timepicker_range_separator(hwnd, element_id, sep=" 至 "):
    data = make_utf8(sep)
    dll.EU_SetTimePickerRangeSeparator(hwnd, element_id, bytes_arg(data), len(data))

def get_timepicker_range_value(hwnd, element_id):
    st = ctypes.c_int()
    en = ctypes.c_int()
    enabled = ctypes.c_int()
    ok = dll.EU_GetTimePickerRangeValue(hwnd, element_id, ctypes.byref(st), ctypes.byref(en), ctypes.byref(enabled))
    return (st.value, en.value, bool(enabled.value)) if ok else None

def set_datetimepicker_datetime(hwnd, element_id, year=2026, month=5, day=2,
                                hour=9, minute=30):
    dll.EU_SetDateTimePickerDateTime(
        hwnd, element_id, year, month, day, hour, minute
    )

def set_datetimepicker_range(hwnd, element_id, min_date=0, max_date=0,
                             min_time=0, max_time=2359):
    dll.EU_SetDateTimePickerRange(
        hwnd, element_id, min_date, max_date, min_time, max_time
    )

def set_datetimepicker_options(hwnd, element_id, today_value=0, show_today=True,
                               minute_step=10, date_format=0):
    dll.EU_SetDateTimePickerOptions(
        hwnd, element_id, today_value, 1 if show_today else 0,
        minute_step, date_format
    )

def set_datetimepicker_open(hwnd, element_id, open=True):
    dll.EU_SetDateTimePickerOpen(hwnd, element_id, 1 if open else 0)

def clear_datetimepicker(hwnd, element_id):
    dll.EU_ClearDateTimePicker(hwnd, element_id)

def datetimepicker_select_today(hwnd, element_id):
    dll.EU_DateTimePickerSelectToday(hwnd, element_id)

def datetimepicker_select_now(hwnd, element_id):
    dll.EU_DateTimePickerSelectNow(hwnd, element_id)

def set_datetimepicker_scroll(hwnd, element_id, hour_scroll=0, minute_scroll=0):
    dll.EU_SetDateTimePickerScroll(hwnd, element_id, hour_scroll, minute_scroll)

def get_datetimepicker_open(hwnd, element_id):
    return dll.EU_GetDateTimePickerOpen(hwnd, element_id)

def get_datetimepicker_date_value(hwnd, element_id):
    return dll.EU_GetDateTimePickerDateValue(hwnd, element_id)

def get_datetimepicker_time_value(hwnd, element_id):
    return dll.EU_GetDateTimePickerTimeValue(hwnd, element_id)

def datetimepicker_move_month(hwnd, element_id, delta_months=1):
    dll.EU_DateTimePickerMoveMonth(hwnd, element_id, delta_months)

def get_datetimepicker_range(hwnd, element_id):
    min_date = ctypes.c_int()
    max_date = ctypes.c_int()
    min_time = ctypes.c_int()
    max_time = ctypes.c_int()
    ok = dll.EU_GetDateTimePickerRange(
        hwnd, element_id,
        ctypes.byref(min_date), ctypes.byref(max_date),
        ctypes.byref(min_time), ctypes.byref(max_time),
    )
    return (min_date.value, max_date.value, min_time.value, max_time.value) if ok else None

def get_datetimepicker_options(hwnd, element_id):
    today_value = ctypes.c_int()
    show_today = ctypes.c_int()
    minute_step = ctypes.c_int()
    date_format = ctypes.c_int()
    ok = dll.EU_GetDateTimePickerOptions(
        hwnd, element_id,
        ctypes.byref(today_value), ctypes.byref(show_today),
        ctypes.byref(minute_step), ctypes.byref(date_format),
    )
    return (today_value.value, bool(show_today.value), minute_step.value, date_format.value) if ok else None

def get_datetimepicker_scroll(hwnd, element_id):
    hour_scroll = ctypes.c_int()
    minute_scroll = ctypes.c_int()
    ok = dll.EU_GetDateTimePickerScroll(
        hwnd, element_id, ctypes.byref(hour_scroll), ctypes.byref(minute_scroll)
    )
    return (hour_scroll.value, minute_scroll.value) if ok else None

def set_datetimepicker_shortcuts(hwnd, element_id, shortcuts_text):
    data = make_utf8(shortcuts_text)
    dll.EU_SetDateTimePickerShortcuts(hwnd, element_id, bytes_arg(data), len(data))

def set_datetimepicker_start_placeholder(hwnd, element_id, text="开始日期时间"):
    data = make_utf8(text)
    dll.EU_SetDateTimePickerStartPlaceholder(hwnd, element_id, bytes_arg(data), len(data))

def set_datetimepicker_end_placeholder(hwnd, element_id, text="结束日期时间"):
    data = make_utf8(text)
    dll.EU_SetDateTimePickerEndPlaceholder(hwnd, element_id, bytes_arg(data), len(data))

def set_datetimepicker_range_placeholders(hwnd, element_id,
                                          start_text="开始日期时间", end_text="结束日期时间"):
    set_datetimepicker_start_placeholder(hwnd, element_id, start_text)
    set_datetimepicker_end_placeholder(hwnd, element_id, end_text)

def set_datetimepicker_default_time(hwnd, element_id, hour=9, minute=0):
    dll.EU_SetDateTimePickerDefaultTime(hwnd, element_id, hour, minute)

def set_datetimepicker_range_default_time(hwnd, element_id,
                                          start_hour=0, start_minute=0,
                                          end_hour=0, end_minute=0):
    dll.EU_SetDateTimePickerRangeDefaultTime(
        hwnd, element_id, start_hour, start_minute, end_hour, end_minute
    )

def set_datetimepicker_range_separator(hwnd, element_id, sep=" 至 "):
    data = make_utf8(sep)
    dll.EU_SetDateTimePickerRangeSeparator(hwnd, element_id, bytes_arg(data), len(data))

def set_datetimepicker_range_select(hwnd, element_id, enabled=True,
                                     start_date=0, start_time=0, end_date=0, end_time=0):
    dll.EU_SetDateTimePickerRangeSelect(hwnd, element_id, 1 if enabled else 0,
                                         start_date, start_time, end_date, end_time)

def get_datetimepicker_range_value(hwnd, element_id):
    sd = ctypes.c_int(); st = ctypes.c_int(); ed = ctypes.c_int(); et = ctypes.c_int(); en = ctypes.c_int()
    ok = dll.EU_GetDateTimePickerRangeValue(hwnd, element_id,
        ctypes.byref(sd), ctypes.byref(st), ctypes.byref(ed), ctypes.byref(et), ctypes.byref(en))
    return (sd.value, st.value, ed.value, et.value, bool(en.value)) if ok else None

def set_time_select_time(hwnd, element_id, hour=9, minute=30):
    dll.EU_SetTimeSelectTime(hwnd, element_id, hour, minute)

def set_time_select_range(hwnd, element_id, min_value=0, max_value=2359):
    dll.EU_SetTimeSelectRange(hwnd, element_id, min_value, max_value)

def set_time_select_options(hwnd, element_id, step_minutes=10, time_format=0):
    dll.EU_SetTimeSelectOptions(hwnd, element_id, step_minutes, time_format)

def set_time_select_open(hwnd, element_id, open=True):
    dll.EU_SetTimeSelectOpen(hwnd, element_id, 1 if open else 0)

def set_time_select_scroll(hwnd, element_id, scroll_row=0):
    dll.EU_SetTimeSelectScroll(hwnd, element_id, scroll_row)

def get_time_select_open(hwnd, element_id):
    return dll.EU_GetTimeSelectOpen(hwnd, element_id)

def get_time_select_value(hwnd, element_id):
    return dll.EU_GetTimeSelectValue(hwnd, element_id)

def get_time_select_range(hwnd, element_id):
    min_value = ctypes.c_int()
    max_value = ctypes.c_int()
    ok = dll.EU_GetTimeSelectRange(hwnd, element_id, ctypes.byref(min_value), ctypes.byref(max_value))
    return (min_value.value, max_value.value) if ok else None

def get_time_select_options(hwnd, element_id):
    step_minutes = ctypes.c_int()
    time_format = ctypes.c_int()
    ok = dll.EU_GetTimeSelectOptions(hwnd, element_id, ctypes.byref(step_minutes), ctypes.byref(time_format))
    return (step_minutes.value, time_format.value) if ok else None

def get_time_select_state(hwnd, element_id):
    scroll_row = ctypes.c_int()
    candidate_count = ctypes.c_int()
    group_count = ctypes.c_int()
    active_index = ctypes.c_int()
    ok = dll.EU_GetTimeSelectState(
        hwnd, element_id,
        ctypes.byref(scroll_row), ctypes.byref(candidate_count),
        ctypes.byref(group_count), ctypes.byref(active_index),
    )
    return (
        scroll_row.value,
        candidate_count.value,
        group_count.value,
        active_index.value,
    ) if ok else None

def set_time_select_placeholder(hwnd, element_id, text):
    data = make_utf8(text)
    dll.EU_SetTimeSelectPlaceholder(hwnd, element_id, bytes_arg(data), len(data))

def create_dropdown(hwnd, parent_id, text="📂 更多操作", items=None, selected=0,
                    x=0, y=0, w=180, h=36):
    if items is None:
        items = ["📄 查看详情", "> ✏️ 编辑资料", "> !🚫 删除账户"]
    text_data = make_utf8(text)
    items_data = make_utf8("|".join(items))
    return dll.EU_CreateDropdown(
        hwnd, parent_id,
        bytes_arg(text_data), len(text_data),
        bytes_arg(items_data), len(items_data),
        selected, x, y, w, h
    )

def set_dropdown_items(hwnd, element_id, items=None):
    if items is None:
        items = ["📄 查看详情", "> ✏️ 编辑资料", "> !🚫 删除账户"]
    data = make_utf8("|".join(items))
    dll.EU_SetDropdownItems(hwnd, element_id, bytes_arg(data), len(data))

def set_dropdown_selected(hwnd, element_id, selected_index=0):
    dll.EU_SetDropdownSelected(hwnd, element_id, selected_index)

def get_dropdown_selected(hwnd, element_id):
    return dll.EU_GetDropdownSelected(hwnd, element_id)

def set_dropdown_open(hwnd, element_id, open=True):
    dll.EU_SetDropdownOpen(hwnd, element_id, 1 if open else 0)

def get_dropdown_open(hwnd, element_id):
    return dll.EU_GetDropdownOpen(hwnd, element_id)

def get_dropdown_item_count(hwnd, element_id):
    return dll.EU_GetDropdownItemCount(hwnd, element_id)

def set_dropdown_disabled(hwnd, element_id, indices=None):
    if indices is None:
        indices = []
    arr_type = ctypes.c_int * len(indices)
    arr = arr_type(*indices) if indices else None
    dll.EU_SetDropdownDisabled(hwnd, element_id, arr, len(indices))

def get_dropdown_state(hwnd, element_id):
    selected = ctypes.c_int()
    count = ctypes.c_int()
    disabled = ctypes.c_int()
    level = ctypes.c_int()
    hover = ctypes.c_int()
    ok = dll.EU_GetDropdownState(
        hwnd, element_id,
        ctypes.byref(selected), ctypes.byref(count), ctypes.byref(disabled),
        ctypes.byref(level), ctypes.byref(hover)
    )
    return {
        "selected": selected.value,
        "count": count.value,
        "disabled": disabled.value,
        "level": level.value,
        "hover": hover.value,
    } if ok else None

def set_dropdown_options(hwnd, element_id, trigger_mode=0, hide_on_click=True,
                         split_button=False, button_variant=0, size=0, trigger_style=0):
    dll.EU_SetDropdownOptions(
        hwnd, element_id,
        int(trigger_mode), 1 if hide_on_click else 0,
        1 if split_button else 0, int(button_variant),
        int(size), int(trigger_style),
    )

def get_dropdown_options(hwnd, element_id):
    trigger_mode = ctypes.c_int()
    hide_on_click = ctypes.c_int()
    split_button = ctypes.c_int()
    button_variant = ctypes.c_int()
    size = ctypes.c_int()
    trigger_style = ctypes.c_int()
    ok = dll.EU_GetDropdownOptions(
        hwnd, element_id,
        ctypes.byref(trigger_mode), ctypes.byref(hide_on_click),
        ctypes.byref(split_button), ctypes.byref(button_variant),
        ctypes.byref(size), ctypes.byref(trigger_style),
    )
    return {
        "trigger_mode": trigger_mode.value,
        "hide_on_click": bool(hide_on_click.value),
        "split_button": bool(split_button.value),
        "button_variant": button_variant.value,
        "size": size.value,
        "trigger_style": trigger_style.value,
    } if ok else None

def set_dropdown_item_meta(hwnd, element_id, icons=None, commands=None, divided=None):
    icons = icons or []
    commands = commands or []
    divided = divided or []
    icons_data = make_utf8("|".join(icons))
    commands_data = make_utf8("|".join(commands))
    arr_type = ctypes.c_int * len(divided)
    arr = arr_type(*divided) if divided else None
    dll.EU_SetDropdownItemMeta(
        hwnd, element_id,
        bytes_arg(icons_data), len(icons_data),
        bytes_arg(commands_data), len(commands_data),
        arr, len(divided),
    )

def get_dropdown_item_meta(hwnd, element_id, item_index):
    icon_buf = (ctypes.c_ubyte * 256)()
    command_buf = (ctypes.c_ubyte * 256)()
    divided = ctypes.c_int()
    disabled = ctypes.c_int()
    level = ctypes.c_int()
    ok = dll.EU_GetDropdownItemMeta(
        hwnd, element_id, item_index,
        icon_buf, len(icon_buf), command_buf, len(command_buf),
        ctypes.byref(divided), ctypes.byref(disabled), ctypes.byref(level),
    )
    if not ok:
        return None
    icon = bytes(icon_buf).split(b"\0", 1)[0].decode("utf-8", errors="replace")
    command = bytes(command_buf).split(b"\0", 1)[0].decode("utf-8", errors="replace")
    return {
        "icon": icon,
        "command": command,
        "divided": bool(divided.value),
        "disabled": bool(disabled.value),
        "level": level.value,
    }

def set_dropdown_command_callback(hwnd, element_id, callback):
    dll.EU_SetDropdownCommandCallback(hwnd, element_id, callback)

def set_dropdown_main_click_callback(hwnd, element_id, callback):
    dll.EU_SetDropdownMainClickCallback(hwnd, element_id, callback)

def create_menu(hwnd, parent_id, items=None, active=0, orientation=0,
                x=0, y=0, w=420, h=48):
    if items is None:
        items = ["🏠 首页", "> 🧩 组件", "> 📚 文档"]
    items_data = make_utf8("|".join(items))
    return dll.EU_CreateMenu(
        hwnd, parent_id,
        bytes_arg(items_data), len(items_data),
        active, orientation, x, y, w, h
    )

def set_menu_items(hwnd, element_id, items=None):
    if items is None:
        items = ["🏠 首页", "> 🧩 组件", "> 📚 文档"]
    data = make_utf8("|".join(items))
    dll.EU_SetMenuItems(hwnd, element_id, bytes_arg(data), len(data))

def set_menu_active(hwnd, element_id, active_index=0):
    dll.EU_SetMenuActive(hwnd, element_id, active_index)

def get_menu_active(hwnd, element_id):
    return dll.EU_GetMenuActive(hwnd, element_id)

def set_menu_orientation(hwnd, element_id, orientation=0):
    dll.EU_SetMenuOrientation(hwnd, element_id, orientation)

def get_menu_orientation(hwnd, element_id):
    return dll.EU_GetMenuOrientation(hwnd, element_id)

def get_menu_item_count(hwnd, element_id):
    return dll.EU_GetMenuItemCount(hwnd, element_id)

def set_menu_expanded(hwnd, element_id, indices=None):
    if indices is None:
        indices = []
    arr_type = ctypes.c_int * len(indices)
    arr = arr_type(*indices) if indices else None
    dll.EU_SetMenuExpanded(hwnd, element_id, arr, len(indices))

def get_menu_state(hwnd, element_id):
    active = ctypes.c_int()
    count = ctypes.c_int()
    orientation = ctypes.c_int()
    level = ctypes.c_int()
    visible = ctypes.c_int()
    expanded = ctypes.c_int()
    hover = ctypes.c_int()
    ok = dll.EU_GetMenuState(
        hwnd, element_id,
        ctypes.byref(active), ctypes.byref(count), ctypes.byref(orientation),
        ctypes.byref(level), ctypes.byref(visible), ctypes.byref(expanded),
        ctypes.byref(hover)
    )
    return {
        "active": active.value,
        "count": count.value,
        "orientation": orientation.value,
        "level": level.value,
        "visible": visible.value,
        "expanded": expanded.value,
        "hover": hover.value,
    } if ok else None

def get_menu_active_path(hwnd, element_id):
    needed = dll.EU_GetMenuActivePath(hwnd, element_id, None, 0)
    if needed <= 0:
        return ""
    buf = (ctypes.c_ubyte * (needed + 1))()
    dll.EU_GetMenuActivePath(hwnd, element_id, buf, needed + 1)
    return bytes(buf[:needed]).decode("utf-8", errors="replace")

def set_menu_colors(hwnd, element_id, bg=0, text_color=0, active_text_color=0,
                    hover_bg=0, disabled_text_color=0, border=0):
    dll.EU_SetMenuColors(
        hwnd, element_id,
        bg, text_color, active_text_color, hover_bg, disabled_text_color, border
    )

def get_menu_colors(hwnd, element_id):
    bg = ctypes.c_uint32()
    text_color = ctypes.c_uint32()
    active_text_color = ctypes.c_uint32()
    hover_bg = ctypes.c_uint32()
    disabled_text_color = ctypes.c_uint32()
    border = ctypes.c_uint32()
    ok = dll.EU_GetMenuColors(
        hwnd, element_id,
        ctypes.byref(bg), ctypes.byref(text_color), ctypes.byref(active_text_color),
        ctypes.byref(hover_bg), ctypes.byref(disabled_text_color), ctypes.byref(border)
    )
    return (bg.value, text_color.value, active_text_color.value,
            hover_bg.value, disabled_text_color.value, border.value) if ok else None

def set_menu_collapsed(hwnd, element_id, collapsed=True):
    dll.EU_SetMenuCollapsed(hwnd, element_id, 1 if collapsed else 0)

def get_menu_collapsed(hwnd, element_id):
    return bool(dll.EU_GetMenuCollapsed(hwnd, element_id))

def set_menu_item_meta(hwnd, element_id, icons=None, group_indices=None,
                       hrefs=None, targets=None, commands=None):
    icons = icons or []
    group_indices = group_indices or []
    hrefs = hrefs or []
    targets = targets or []
    commands = commands or []
    icons_data = make_utf8("|".join(icons))
    hrefs_data = make_utf8("|".join(hrefs))
    targets_data = make_utf8("|".join(targets))
    commands_data = make_utf8("|".join(commands))
    arr_type = ctypes.c_int * len(group_indices)
    arr = arr_type(*group_indices) if group_indices else None
    dll.EU_SetMenuItemMeta(
        hwnd, element_id,
        bytes_arg(icons_data), len(icons_data),
        arr, len(group_indices),
        bytes_arg(hrefs_data), len(hrefs_data),
        bytes_arg(targets_data), len(targets_data),
        bytes_arg(commands_data), len(commands_data),
    )

def get_menu_item_meta(hwnd, element_id, item_index):
    icon_buf = (ctypes.c_ubyte * 256)()
    href_buf = (ctypes.c_ubyte * 512)()
    target_buf = (ctypes.c_ubyte * 128)()
    command_buf = (ctypes.c_ubyte * 256)()
    is_group = ctypes.c_int()
    disabled = ctypes.c_int()
    level = ctypes.c_int()
    ok = dll.EU_GetMenuItemMeta(
        hwnd, element_id, item_index,
        icon_buf, len(icon_buf),
        href_buf, len(href_buf),
        target_buf, len(target_buf),
        command_buf, len(command_buf),
        ctypes.byref(is_group), ctypes.byref(disabled), ctypes.byref(level),
    )
    if not ok:
        return None
    def read_buf(buf):
        return bytes(buf).split(b"\0", 1)[0].decode("utf-8", errors="replace")
    return {
        "icon": read_buf(icon_buf),
        "href": read_buf(href_buf),
        "target": read_buf(target_buf),
        "command": read_buf(command_buf),
        "group": bool(is_group.value),
        "disabled": bool(disabled.value),
        "level": level.value,
    }

def set_menu_select_callback(hwnd, element_id, callback):
    dll.EU_SetMenuSelectCallback(hwnd, element_id, callback)

def set_menu_item_icon(hwnd, element_id, index, icon):
    data = make_utf8(icon)
    dll.EU_SetMenuItemIcon(hwnd, element_id, index, bytes_arg(data), len(data))

def set_menu_item_shortcut(hwnd, element_id, index, shortcut):
    data = make_utf8(shortcut)
    dll.EU_SetMenuItemShortcut(hwnd, element_id, index, bytes_arg(data), len(data))

def set_menu_item_checked(hwnd, element_id, index, checked=True):
    dll.EU_SetMenuItemChecked(hwnd, element_id, index, 1 if checked else 0)

def set_menu_item_separator(hwnd, element_id, index, separator=True):
    dll.EU_SetMenuItemSeparator(hwnd, element_id, index, 1 if separator else 0)

def set_menu_item_submenu(hwnd, element_id, index, submenu_element_id):
    dll.EU_SetMenuItemSubmenu(hwnd, element_id, index, submenu_element_id)

def set_menu_popup_position(hwnd, element_id, anchor_element_id, placement=3, offset=8):
    dll.EU_SetMenuPopupPosition(hwnd, element_id, anchor_element_id, placement, offset)

def set_context_menu_callback(hwnd, element_id, callback):
    dll.EU_SetContextMenuCallback(hwnd, element_id, callback)

def create_anchor(hwnd, parent_id, items=None, active=0,
                  x=0, y=0, w=220, h=180):
    if items is None:
        items = ["📌 概览", "🧭 导航", "💬 反馈"]
    items_data = make_utf8("|".join(items))
    return dll.EU_CreateAnchor(
        hwnd, parent_id,
        bytes_arg(items_data), len(items_data),
        active, x, y, w, h
    )

def set_anchor_items(hwnd, element_id, items=None):
    if items is None:
        items = ["📌 概览", "🧭 导航", "💬 反馈"]
    data = make_utf8("|".join(items))
    dll.EU_SetAnchorItems(hwnd, element_id, bytes_arg(data), len(data))

def set_anchor_active(hwnd, element_id, active_index=0):
    dll.EU_SetAnchorActive(hwnd, element_id, active_index)

def get_anchor_active(hwnd, element_id):
    return dll.EU_GetAnchorActive(hwnd, element_id)

def get_anchor_item_count(hwnd, element_id):
    return dll.EU_GetAnchorItemCount(hwnd, element_id)

def set_anchor_targets(hwnd, element_id, positions=None):
    if positions is None:
        positions = []
    arr_type = ctypes.c_int * len(positions)
    arr = arr_type(*positions) if positions else None
    dll.EU_SetAnchorTargets(hwnd, element_id, arr, len(positions))

def set_anchor_options(hwnd, element_id, offset=0, container_id=0):
    dll.EU_SetAnchorOptions(hwnd, element_id, offset, container_id)

def set_anchor_scroll(hwnd, element_id, scroll_position=0):
    dll.EU_SetAnchorScroll(hwnd, element_id, scroll_position)

def get_anchor_state(hwnd, element_id):
    active = ctypes.c_int()
    count = ctypes.c_int()
    scroll = ctypes.c_int()
    offset = ctypes.c_int()
    target = ctypes.c_int()
    container = ctypes.c_int()
    hover = ctypes.c_int()
    ok = dll.EU_GetAnchorState(
        hwnd, element_id,
        ctypes.byref(active), ctypes.byref(count), ctypes.byref(scroll),
        ctypes.byref(offset), ctypes.byref(target), ctypes.byref(container),
        ctypes.byref(hover)
    )
    return {
        "active": active.value,
        "count": count.value,
        "scroll": scroll.value,
        "offset": offset.value,
        "target": target.value,
        "container": container.value,
        "hover": hover.value,
    } if ok else None

def create_backtop(hwnd, parent_id, text="⬆️", x=0, y=0, w=44, h=44):
    data = make_utf8(text)
    return dll.EU_CreateBacktop(
        hwnd, parent_id,
        bytes_arg(data), len(data),
        x, y, w, h
    )

def set_backtop_state(hwnd, element_id, scroll_position=0, threshold=200, target_position=0):
    dll.EU_SetBacktopState(hwnd, element_id, scroll_position, threshold, target_position)

def get_backtop_visible(hwnd, element_id):
    return dll.EU_GetBacktopVisible(hwnd, element_id)

def get_backtop_state(hwnd, element_id):
    scroll_position = ctypes.c_int()
    threshold = ctypes.c_int()
    target_position = ctypes.c_int()
    ok = dll.EU_GetBacktopState(
        hwnd, element_id,
        ctypes.byref(scroll_position), ctypes.byref(threshold), ctypes.byref(target_position),
    )
    return (scroll_position.value, threshold.value, target_position.value) if ok else None

def set_backtop_options(hwnd, element_id, scroll_position=0, threshold=200,
                        target_position=0, container_id=0, duration_ms=240):
    dll.EU_SetBacktopOptions(
        hwnd, element_id,
        scroll_position, threshold, target_position, container_id, duration_ms
    )

def set_backtop_scroll(hwnd, element_id, scroll_position=0):
    dll.EU_SetBacktopScroll(hwnd, element_id, scroll_position)

def trigger_backtop(hwnd, element_id):
    dll.EU_TriggerBacktop(hwnd, element_id)

def get_backtop_full_state(hwnd, element_id):
    scroll_position = ctypes.c_int()
    threshold = ctypes.c_int()
    target_position = ctypes.c_int()
    container_id = ctypes.c_int()
    visible = ctypes.c_int()
    duration_ms = ctypes.c_int()
    last_scroll = ctypes.c_int()
    activated_count = ctypes.c_int()
    ok = dll.EU_GetBacktopFullState(
        hwnd, element_id,
        ctypes.byref(scroll_position), ctypes.byref(threshold),
        ctypes.byref(target_position), ctypes.byref(container_id),
        ctypes.byref(visible), ctypes.byref(duration_ms),
        ctypes.byref(last_scroll), ctypes.byref(activated_count)
    )
    return {
        "scroll": scroll_position.value,
        "threshold": threshold.value,
        "target": target_position.value,
        "container": container_id.value,
        "visible": visible.value,
        "duration": duration_ms.value,
        "last_scroll": last_scroll.value,
        "activated": activated_count.value,
    } if ok else None

def create_segmented(hwnd, parent_id, items=None, active=0,
                     x=0, y=0, w=320, h=44):
    if items is None:
        items = ["日", "周", "月"]
    items_data = make_utf8("|".join(items))
    return dll.EU_CreateSegmented(
        hwnd, parent_id,
        bytes_arg(items_data), len(items_data),
        active, x, y, w, h
    )

def set_segmented_items(hwnd, element_id, items=None):
    if items is None:
        items = ["日", "周", "月"]
    data = make_utf8("|".join(items))
    dll.EU_SetSegmentedItems(hwnd, element_id, bytes_arg(data), len(data))

def set_segmented_active(hwnd, element_id, active_index=0):
    dll.EU_SetSegmentedActive(hwnd, element_id, active_index)

def get_segmented_active(hwnd, element_id):
    return dll.EU_GetSegmentedActive(hwnd, element_id)

def get_segmented_item_count(hwnd, element_id):
    return dll.EU_GetSegmentedItemCount(hwnd, element_id)

def set_segmented_disabled(hwnd, element_id, indices=None):
    if indices is None:
        indices = []
    arr_type = ctypes.c_int * len(indices)
    arr = arr_type(*indices) if indices else None
    dll.EU_SetSegmentedDisabled(hwnd, element_id, arr, len(indices))

def get_segmented_state(hwnd, element_id):
    active = ctypes.c_int()
    count = ctypes.c_int()
    disabled = ctypes.c_int()
    hover = ctypes.c_int()
    ok = dll.EU_GetSegmentedState(
        hwnd, element_id,
        ctypes.byref(active), ctypes.byref(count),
        ctypes.byref(disabled), ctypes.byref(hover)
    )
    return {
        "active": active.value,
        "count": count.value,
        "disabled": disabled.value,
        "hover": hover.value,
    } if ok else None

def create_pageheader(hwnd, parent_id, title="页面标题", subtitle="", back_text="返回",
                      x=0, y=0, w=640, h=78):
    title_data = make_utf8(title)
    subtitle_data = make_utf8(subtitle)
    back_data = make_utf8(back_text)
    return dll.EU_CreatePageHeader(
        hwnd, parent_id,
        bytes_arg(title_data), len(title_data),
        bytes_arg(subtitle_data), len(subtitle_data),
        bytes_arg(back_data), len(back_data),
        x, y, w, h
    )

def set_pageheader_breadcrumbs(hwnd, element_id, items=None):
    if items is None:
        items = ["首页", "组件", "页面头"]
    data = make_utf8("|".join(items))
    dll.EU_SetPageHeaderBreadcrumbs(hwnd, element_id, bytes_arg(data), len(data))

def set_pageheader_actions(hwnd, element_id, items=None):
    if items is None:
        items = ["🔄 刷新", "💾 保存"]
    data = make_utf8("|".join(items))
    dll.EU_SetPageHeaderActions(hwnd, element_id, bytes_arg(data), len(data))

def get_pageheader_action(hwnd, element_id):
    return dll.EU_GetPageHeaderAction(hwnd, element_id)

def set_pageheader_text(hwnd, element_id, title="页面标题", subtitle=""):
    title_data = make_utf8(title)
    subtitle_data = make_utf8(subtitle)
    dll.EU_SetPageHeaderText(
        hwnd, element_id,
        bytes_arg(title_data), len(title_data),
        bytes_arg(subtitle_data), len(subtitle_data),
    )

def set_pageheader_back_text(hwnd, element_id, text="返回"):
    data = make_utf8(text)
    dll.EU_SetPageHeaderBackText(hwnd, element_id, bytes_arg(data), len(data))

def set_pageheader_active_action(hwnd, element_id, index=0):
    dll.EU_SetPageHeaderActiveAction(hwnd, element_id, index)

def set_pageheader_breadcrumb_active(hwnd, element_id, index=0):
    dll.EU_SetPageHeaderBreadcrumbActive(hwnd, element_id, index)

def trigger_pageheader_back(hwnd, element_id):
    dll.EU_TriggerPageHeaderBack(hwnd, element_id)

def reset_pageheader_result(hwnd, element_id):
    dll.EU_ResetPageHeaderResult(hwnd, element_id)

def get_pageheader_state(hwnd, element_id):
    active_action = ctypes.c_int()
    action_count = ctypes.c_int()
    active_breadcrumb = ctypes.c_int()
    breadcrumb_count = ctypes.c_int()
    back_clicked = ctypes.c_int()
    back_hovered = ctypes.c_int()
    action_hover = ctypes.c_int()
    breadcrumb_hover = ctypes.c_int()
    ok = dll.EU_GetPageHeaderState(
        hwnd, element_id,
        ctypes.byref(active_action), ctypes.byref(action_count),
        ctypes.byref(active_breadcrumb), ctypes.byref(breadcrumb_count),
        ctypes.byref(back_clicked), ctypes.byref(back_hovered),
        ctypes.byref(action_hover), ctypes.byref(breadcrumb_hover),
    )
    return {
        "active_action": active_action.value,
        "action_count": action_count.value,
        "active_breadcrumb": active_breadcrumb.value,
        "breadcrumb_count": breadcrumb_count.value,
        "back_clicked": back_clicked.value,
        "back_hovered": back_hovered.value,
        "action_hover": action_hover.value,
        "breadcrumb_hover": breadcrumb_hover.value,
    } if ok else None

def create_affix(hwnd, parent_id, title="📌 固钉区域", body="", offset=0,
                 x=0, y=0, w=320, h=96):
    title_data = make_utf8(title)
    body_data = make_utf8(body)
    return dll.EU_CreateAffix(
        hwnd, parent_id,
        bytes_arg(title_data), len(title_data),
        bytes_arg(body_data), len(body_data),
        offset, x, y, w, h
    )

def set_affix_state(hwnd, element_id, scroll_position=0, offset=0):
    dll.EU_SetAffixState(hwnd, element_id, scroll_position, offset)

def get_affix_fixed(hwnd, element_id):
    return dll.EU_GetAffixFixed(hwnd, element_id)

def get_affix_state(hwnd, element_id):
    scroll_position = ctypes.c_int()
    offset = ctypes.c_int()
    fixed = ctypes.c_int()
    ok = dll.EU_GetAffixState(
        hwnd, element_id,
        ctypes.byref(scroll_position), ctypes.byref(offset), ctypes.byref(fixed),
    )
    return (scroll_position.value, offset.value, bool(fixed.value)) if ok else None

def set_affix_options(hwnd, element_id, scroll_position=0, offset=0,
                      container_id=0, placeholder_height=0, z_index=10):
    dll.EU_SetAffixOptions(
        hwnd, element_id,
        scroll_position, offset, container_id, placeholder_height, z_index
    )

def get_affix_options(hwnd, element_id):
    scroll_position = ctypes.c_int()
    offset = ctypes.c_int()
    fixed = ctypes.c_int()
    container_id = ctypes.c_int()
    placeholder_height = ctypes.c_int()
    fixed_top = ctypes.c_int()
    z_index = ctypes.c_int()
    ok = dll.EU_GetAffixOptions(
        hwnd, element_id,
        ctypes.byref(scroll_position), ctypes.byref(offset), ctypes.byref(fixed),
        ctypes.byref(container_id), ctypes.byref(placeholder_height),
        ctypes.byref(fixed_top), ctypes.byref(z_index),
    )
    return {
        "scroll_position": scroll_position.value,
        "offset": offset.value,
        "fixed": bool(fixed.value),
        "container_id": container_id.value,
        "placeholder_height": placeholder_height.value,
        "fixed_top": fixed_top.value,
        "z_index": z_index.value,
    } if ok else None

def create_watermark(hwnd, parent_id, content="💧 水印", gap_x=150, gap_y=92,
                     x=0, y=0, w=360, h=220):
    data = make_utf8(content)
    return dll.EU_CreateWatermark(
        hwnd, parent_id,
        bytes_arg(data), len(data),
        gap_x, gap_y, x, y, w, h
    )

def set_watermark_options(hwnd, element_id, gap_x=150, gap_y=92, rotation=-18, alpha=54):
    dll.EU_SetWatermarkOptions(hwnd, element_id, gap_x, gap_y, rotation, alpha)

def get_watermark_options(hwnd, element_id):
    gap_x = ctypes.c_int()
    gap_y = ctypes.c_int()
    rotation = ctypes.c_int()
    alpha = ctypes.c_int()
    ok = dll.EU_GetWatermarkOptions(
        hwnd, element_id,
        ctypes.byref(gap_x), ctypes.byref(gap_y),
        ctypes.byref(rotation), ctypes.byref(alpha),
    )
    return (gap_x.value, gap_y.value, rotation.value, alpha.value) if ok else None

def set_watermark_layer(hwnd, element_id, container_id=0, overlay=True, pass_through=True, z_index=0):
    dll.EU_SetWatermarkLayer(
        hwnd, element_id,
        container_id, int(bool(overlay)), int(bool(pass_through)), z_index
    )

def get_watermark_full_options(hwnd, element_id):
    gap_x = ctypes.c_int()
    gap_y = ctypes.c_int()
    rotation = ctypes.c_int()
    alpha = ctypes.c_int()
    container_id = ctypes.c_int()
    overlay = ctypes.c_int()
    pass_through = ctypes.c_int()
    z_index = ctypes.c_int()
    tile_count_x = ctypes.c_int()
    tile_count_y = ctypes.c_int()
    ok = dll.EU_GetWatermarkFullOptions(
        hwnd, element_id,
        ctypes.byref(gap_x), ctypes.byref(gap_y),
        ctypes.byref(rotation), ctypes.byref(alpha),
        ctypes.byref(container_id), ctypes.byref(overlay),
        ctypes.byref(pass_through), ctypes.byref(z_index),
        ctypes.byref(tile_count_x), ctypes.byref(tile_count_y),
    )
    return {
        "gap_x": gap_x.value,
        "gap_y": gap_y.value,
        "rotation": rotation.value,
        "alpha": alpha.value,
        "container_id": container_id.value,
        "overlay": bool(overlay.value),
        "pass_through": bool(pass_through.value),
        "z_index": z_index.value,
        "tile_count_x": tile_count_x.value,
        "tile_count_y": tile_count_y.value,
    } if ok else None

def create_tour(hwnd, parent_id, steps=None, active=0, open=True,
                x=0, y=0, w=360, h=180):
    if steps is None:
        steps = [("步骤一", "引导内容")]
    rows = []
    for step in steps:
        title = str(step[0]) if len(step) > 0 else ""
        body = str(step[1]) if len(step) > 1 else ""
        rows.append(f"{title}\t{body}")
    data = make_utf8("|".join(rows))
    return dll.EU_CreateTour(
        hwnd, parent_id,
        bytes_arg(data), len(data),
        active, 1 if open else 0,
        x, y, w, h
    )

def set_descriptions_options(hwnd, element_id, columns=2, bordered=True,
                             label_width=88, min_row_height=30, wrap_values=False):
    dll.EU_SetDescriptionsOptions(
        hwnd, element_id, columns, 1 if bordered else 0,
        label_width, min_row_height, 1 if wrap_values else 0
    )

def get_descriptions_item_count(hwnd, element_id):
    return dll.EU_GetDescriptionsItemCount(hwnd, element_id)

def set_table_empty_text(hwnd, element_id, text="📭 暂无数据"):
    data = make_utf8(text)
    dll.EU_SetTableEmptyText(hwnd, element_id, bytes_arg(data), len(data))

def set_table_selected_row(hwnd, element_id, row_index):
    dll.EU_SetTableSelectedRow(hwnd, element_id, row_index)

def get_table_selected_row(hwnd, element_id):
    return dll.EU_GetTableSelectedRow(hwnd, element_id)

def get_table_row_count(hwnd, element_id):
    return dll.EU_GetTableRowCount(hwnd, element_id)

def get_table_column_count(hwnd, element_id):
    return dll.EU_GetTableColumnCount(hwnd, element_id)

def set_table_options(hwnd, element_id, striped=True, bordered=True,
                      row_height=30, header_height=32, selectable=True):
    dll.EU_SetTableOptions(
        hwnd, element_id, 1 if striped else 0, 1 if bordered else 0,
        row_height, header_height, 1 if selectable else 0
    )

def set_card_title(hwnd, element_id, title=""):
    data = make_utf8(title)
    dll.EU_SetCardTitle(hwnd, element_id, bytes_arg(data), len(data))

def set_card_body(hwnd, element_id, body=""):
    data = make_utf8(body)
    dll.EU_SetCardBody(hwnd, element_id, bytes_arg(data), len(data))

def set_card_footer(hwnd, element_id, footer=""):
    data = make_utf8(footer)
    dll.EU_SetCardFooter(hwnd, element_id, bytes_arg(data), len(data))

def set_card_items(hwnd, element_id, items=None):
    if items is None:
        items = []
    data = make_utf8("|".join(str(item) for item in items))
    dll.EU_SetCardItems(hwnd, element_id, bytes_arg(data), len(data))

def get_card_item_count(hwnd, element_id):
    return dll.EU_GetCardItemCount(hwnd, element_id)

def set_card_actions(hwnd, element_id, actions=None):
    if actions is None:
        actions = []
    data = make_utf8("|".join(actions))
    dll.EU_SetCardActions(hwnd, element_id, bytes_arg(data), len(data))

def get_card_action(hwnd, element_id):
    return dll.EU_GetCardAction(hwnd, element_id)

def reset_card_action(hwnd, element_id):
    dll.EU_ResetCardAction(hwnd, element_id)

def set_card_options(hwnd, element_id, shadow=1, hoverable=True):
    dll.EU_SetCardOptions(hwnd, element_id, shadow, 1 if hoverable else 0)

def set_card_style(hwnd, element_id, bg=0, border=0, border_width=1.0,
                   radius=4.0, padding=18):
    dll.EU_SetCardStyle(
        hwnd, element_id, bg, border,
        ctypes.c_float(border_width), ctypes.c_float(radius), padding
    )

def get_card_style(hwnd, element_id):
    bg = ctypes.c_uint32()
    border = ctypes.c_uint32()
    border_width = ctypes.c_float()
    radius = ctypes.c_float()
    padding = ctypes.c_int()
    ok = dll.EU_GetCardStyle(
        hwnd, element_id,
        ctypes.byref(bg), ctypes.byref(border),
        ctypes.byref(border_width), ctypes.byref(radius),
        ctypes.byref(padding)
    )
    return (bg.value, border.value, border_width.value, radius.value, padding.value) if ok else None

def set_card_body_style(hwnd, element_id, pad_left=18, pad_top=14, pad_right=18,
                        pad_bottom=14, font_size=14.0, item_gap=0,
                        item_padding_y=0, divider=False):
    dll.EU_SetCardBodyStyle(
        hwnd, element_id,
        pad_left, pad_top, pad_right, pad_bottom,
        ctypes.c_float(font_size), item_gap, item_padding_y,
        1 if divider else 0
    )

def get_card_body_style(hwnd, element_id):
    pad_left = ctypes.c_int()
    pad_top = ctypes.c_int()
    pad_right = ctypes.c_int()
    pad_bottom = ctypes.c_int()
    font_size = ctypes.c_float()
    item_gap = ctypes.c_int()
    item_padding_y = ctypes.c_int()
    divider = ctypes.c_int()
    ok = dll.EU_GetCardBodyStyle(
        hwnd, element_id,
        ctypes.byref(pad_left), ctypes.byref(pad_top),
        ctypes.byref(pad_right), ctypes.byref(pad_bottom),
        ctypes.byref(font_size), ctypes.byref(item_gap),
        ctypes.byref(item_padding_y), ctypes.byref(divider)
    )
    if not ok:
        return None
    return {
        "pad_left": pad_left.value,
        "pad_top": pad_top.value,
        "pad_right": pad_right.value,
        "pad_bottom": pad_bottom.value,
        "font_size": font_size.value,
        "item_gap": item_gap.value,
        "item_padding_y": item_padding_y.value,
        "divider": bool(divider.value),
    }

def get_card_options(hwnd, element_id):
    shadow = ctypes.c_int()
    hoverable = ctypes.c_int()
    action_count = ctypes.c_int()
    ok = dll.EU_GetCardOptions(
        hwnd, element_id,
        ctypes.byref(shadow), ctypes.byref(hoverable), ctypes.byref(action_count)
    )
    return (shadow.value, bool(hoverable.value), action_count.value) if ok else None

def get_collapse_item_count(hwnd, element_id):
    return dll.EU_GetCollapseItemCount(hwnd, element_id)

def set_collapse_items_ex(hwnd, element_id, items):
    data = make_utf8("|".join(_collapse_item_row(item) for item in (items or [])))
    dll.EU_SetCollapseItemsEx(hwnd, element_id, bytes_arg(data), len(data))

def set_collapse_active_items(hwnd, element_id, indices):
    data = make_utf8(_collapse_indices_text(indices))
    dll.EU_SetCollapseActiveItems(hwnd, element_id, bytes_arg(data), len(data))

def get_collapse_active_items(hwnd, element_id, buffer_size=256):
    buf = (ctypes.c_ubyte * buffer_size)()
    needed = dll.EU_GetCollapseActiveItems(hwnd, element_id, buf, buffer_size)
    raw = bytes(buf[:min(needed, buffer_size - 1)]).decode("utf-8", errors="replace")
    if not raw:
        return []
    return [int(item) for item in raw.replace("|", ",").replace(";", ",").split(",") if item.strip()]

def set_collapse_options(hwnd, element_id, accordion=True, allow_collapse=True,
                         disabled_indices=None, animated=True):
    if disabled_indices is None:
        disabled_indices = []
    data = make_utf8(",".join(str(i) for i in disabled_indices))
    dll.EU_SetCollapseAdvancedOptions(
        hwnd, element_id, 1 if accordion else 0, 1 if allow_collapse else 0,
        1 if animated else 0,
        bytes_arg(data), len(data)
    )

def get_collapse_options(hwnd, element_id):
    accordion = ctypes.c_int()
    allow_collapse = ctypes.c_int()
    animated = ctypes.c_int()
    disabled_count = ctypes.c_int()
    ok = dll.EU_GetCollapseOptions(
        hwnd, element_id,
        ctypes.byref(accordion), ctypes.byref(allow_collapse),
        ctypes.byref(animated), ctypes.byref(disabled_count)
    )
    return (
        bool(accordion.value),
        bool(allow_collapse.value),
        bool(animated.value),
        disabled_count.value,
    ) if ok else None

def get_collapse_state_json(hwnd, element_id):
    return read_json_result(dll.EU_GetCollapseStateJson, hwnd, element_id)

def set_timeline_options(hwnd, element_id, position=0, show_time=True):
    dll.EU_SetTimelineOptions(hwnd, element_id, position, 1 if show_time else 0)

def set_timeline_advanced_options(hwnd, element_id, position=0, show_time=True,
                                  reverse=False, default_placement="top"):
    dll.EU_SetTimelineAdvancedOptions(
        hwnd, element_id, int(position), 1 if show_time else 0,
        1 if reverse else 0, _timeline_placement_value(default_placement)
    )

def get_timeline_item_count(hwnd, element_id):
    return dll.EU_GetTimelineItemCount(hwnd, element_id)

def get_timeline_options(hwnd, element_id):
    position = ctypes.c_int()
    show_time = ctypes.c_int()
    ok = dll.EU_GetTimelineOptions(hwnd, element_id, ctypes.byref(position), ctypes.byref(show_time))
    return (position.value, bool(show_time.value)) if ok else None

def get_timeline_advanced_options(hwnd, element_id):
    position = ctypes.c_int()
    show_time = ctypes.c_int()
    reverse = ctypes.c_int()
    default_placement = ctypes.c_int()
    ok = dll.EU_GetTimelineAdvancedOptions(
        hwnd, element_id,
        ctypes.byref(position), ctypes.byref(show_time),
        ctypes.byref(reverse), ctypes.byref(default_placement)
    )
    return {
        "position": position.value,
        "show_time": bool(show_time.value),
        "reverse": bool(reverse.value),
        "default_placement": "bottom" if default_placement.value == 1 else "top",
    } if ok else None

def set_statistic_format(hwnd, element_id, title="📊 统计数值", prefix="", suffix=""):
    title_data = make_utf8(title)
    prefix_data = make_utf8(prefix)
    suffix_data = make_utf8(suffix)
    dll.EU_SetStatisticFormat(
        hwnd, element_id,
        bytes_arg(title_data), len(title_data),
        bytes_arg(prefix_data), len(prefix_data),
        bytes_arg(suffix_data), len(suffix_data),
    )

def set_statistic_options(hwnd, element_id, precision=-1, animated=True):
    dll.EU_SetStatisticOptions(hwnd, element_id, precision, 1 if animated else 0)

def get_statistic_options(hwnd, element_id):
    precision = ctypes.c_int()
    animated = ctypes.c_int()
    ok = dll.EU_GetStatisticOptions(hwnd, element_id, ctypes.byref(precision), ctypes.byref(animated))
    return (precision.value, bool(animated.value)) if ok else None

def set_statistic_number_options(hwnd, element_id, precision=-1, animated=True,
                                 group_separator=False, group_separator_text=",",
                                 decimal_separator="."):
    group_data = make_utf8(group_separator_text)
    decimal_data = make_utf8(decimal_separator)
    dll.EU_SetStatisticNumberOptions(
        hwnd, element_id,
        precision, 1 if animated else 0, 1 if group_separator else 0,
        bytes_arg(group_data), len(group_data),
        bytes_arg(decimal_data), len(decimal_data),
    )

def set_statistic_affix_options(hwnd, element_id, prefix="", suffix="",
                                prefix_color=0, suffix_color=0, value_color=0,
                                suffix_clickable=False):
    prefix_data = make_utf8(prefix)
    suffix_data = make_utf8(suffix)
    dll.EU_SetStatisticAffixOptions(
        hwnd, element_id,
        bytes_arg(prefix_data), len(prefix_data),
        bytes_arg(suffix_data), len(suffix_data),
        prefix_color, suffix_color, value_color,
        1 if suffix_clickable else 0,
    )

def set_statistic_display_text(hwnd, element_id, text):
    data = make_utf8(text)
    dll.EU_SetStatisticDisplayText(hwnd, element_id, bytes_arg(data), len(data))

def set_statistic_countdown(hwnd, element_id, target_unix_ms, format_text=""):
    data = make_utf8(format_text)
    dll.EU_SetStatisticCountdown(hwnd, element_id, int(target_unix_ms), bytes_arg(data), len(data))

def set_statistic_countdown_state(hwnd, element_id, paused):
    dll.EU_SetStatisticCountdownState(hwnd, element_id, 1 if paused else 0)

def add_statistic_countdown_time(hwnd, element_id, delta_ms):
    dll.EU_AddStatisticCountdownTime(hwnd, element_id, int(delta_ms))

def set_statistic_finish_callback(hwnd, element_id, callback):
    dll.EU_SetStatisticFinishCallback(hwnd, element_id, callback)

def set_statistic_suffix_click_callback(hwnd, element_id, callback):
    dll.EU_SetStatisticSuffixClickCallback(hwnd, element_id, callback)

def get_statistic_full_state(hwnd, element_id):
    mode = ctypes.c_int()
    precision = ctypes.c_int()
    animated = ctypes.c_int()
    group = ctypes.c_int()
    paused = ctypes.c_int()
    finished = ctypes.c_int()
    suffix_clicks = ctypes.c_int()
    remaining = ctypes.c_longlong()
    ok = dll.EU_GetStatisticFullState(
        hwnd, element_id,
        ctypes.byref(mode), ctypes.byref(precision), ctypes.byref(animated),
        ctypes.byref(group), ctypes.byref(paused), ctypes.byref(finished),
        ctypes.byref(suffix_clicks), ctypes.byref(remaining),
    )
    if not ok:
        return None
    return {
        "mode": mode.value,
        "precision": precision.value,
        "animated": bool(animated.value),
        "group_separator": bool(group.value),
        "countdown_paused": bool(paused.value),
        "countdown_finished": bool(finished.value),
        "suffix_click_count": suffix_clicks.value,
        "remaining_ms": remaining.value,
    }

def set_tour_steps(hwnd, element_id, steps):
    rows = []
    for step in steps:
        title = str(step[0]) if len(step) > 0 else ""
        body = str(step[1]) if len(step) > 1 else ""
        rows.append(f"{title}\t{body}")
    data = make_utf8("|".join(rows))
    dll.EU_SetTourSteps(hwnd, element_id, bytes_arg(data), len(data))

def set_tour_options(hwnd, element_id, open=True, mask=True, target=(0, 0, 0, 0)):
    x, y, w, h = target
    dll.EU_SetTourOptions(hwnd, element_id, 1 if open else 0, 1 if mask else 0, x, y, w, h)

def set_tour_target_element(hwnd, element_id, target_element_id, padding=8):
    dll.EU_SetTourTargetElement(hwnd, element_id, target_element_id, padding)

def set_tour_mask_behavior(hwnd, element_id, pass_through=False, close_on_mask=True):
    dll.EU_SetTourMaskBehavior(
        hwnd, element_id, 1 if pass_through else 0, 1 if close_on_mask else 0
    )

def set_tour_active(hwnd, element_id, active_index=0):
    dll.EU_SetTourActive(hwnd, element_id, active_index)

def set_tour_open(hwnd, element_id, open=True):
    dll.EU_SetTourOpen(hwnd, element_id, 1 if open else 0)

def get_tour_active(hwnd, element_id):
    return dll.EU_GetTourActive(hwnd, element_id)

def get_tour_open(hwnd, element_id):
    return dll.EU_GetTourOpen(hwnd, element_id)

def get_tour_step_count(hwnd, element_id):
    return dll.EU_GetTourStepCount(hwnd, element_id)

def get_tour_options(hwnd, element_id):
    open_value = ctypes.c_int()
    mask = ctypes.c_int()
    x = ctypes.c_int()
    y = ctypes.c_int()
    w = ctypes.c_int()
    h = ctypes.c_int()
    ok = dll.EU_GetTourOptions(
        hwnd, element_id,
        ctypes.byref(open_value), ctypes.byref(mask),
        ctypes.byref(x), ctypes.byref(y), ctypes.byref(w), ctypes.byref(h),
    )
    return (bool(open_value.value), bool(mask.value), x.value, y.value, w.value, h.value) if ok else None

def get_tour_full_state(hwnd, element_id):
    active = ctypes.c_int()
    count = ctypes.c_int()
    open_value = ctypes.c_int()
    mask = ctypes.c_int()
    x = ctypes.c_int()
    y = ctypes.c_int()
    w = ctypes.c_int()
    h = ctypes.c_int()
    target_element = ctypes.c_int()
    mask_passthrough = ctypes.c_int()
    close_on_mask = ctypes.c_int()
    last_action = ctypes.c_int()
    change_count = ctypes.c_int()
    ok = dll.EU_GetTourFullState(
        hwnd, element_id,
        ctypes.byref(active), ctypes.byref(count),
        ctypes.byref(open_value), ctypes.byref(mask),
        ctypes.byref(x), ctypes.byref(y), ctypes.byref(w), ctypes.byref(h),
        ctypes.byref(target_element), ctypes.byref(mask_passthrough),
        ctypes.byref(close_on_mask), ctypes.byref(last_action), ctypes.byref(change_count),
    )
    return {
        "active": active.value,
        "count": count.value,
        "open": bool(open_value.value),
        "mask": bool(mask.value),
        "target": (x.value, y.value, w.value, h.value),
        "target_element_id": target_element.value,
        "mask_passthrough": bool(mask_passthrough.value),
        "close_on_mask": bool(close_on_mask.value),
        "last_action": last_action.value,
        "change_count": change_count.value,
    } if ok else None

IMAGE_FIT_VALUES = {
    "contain": 0,
    "cover": 1,
    "fill": 2,
    "none": 3,
    "scale-down": 4,
    "scale_down": 4,
}

def _image_fit_value(fit):
    if isinstance(fit, str):
        return IMAGE_FIT_VALUES.get(fit.strip().lower(), 0)
    return int(fit)

def create_image(hwnd, parent_id, src="", alt="图片", fit=0,
                 x=0, y=0, w=220, h=180):
    src_data = make_utf8(src)
    alt_data = make_utf8(alt)
    return dll.EU_CreateImage(
        hwnd, parent_id,
        bytes_arg(src_data), len(src_data),
        bytes_arg(alt_data), len(alt_data),
        _image_fit_value(fit), x, y, w, h
    )

def create_carousel(hwnd, parent_id, items=None, active=0, indicator_position=0,
                    x=0, y=0, w=420, h=220):
    if items is None:
        items = ["第一层", "第二层", "第三层"]
    items_data = make_utf8("|".join(items))
    return dll.EU_CreateCarousel(
        hwnd, parent_id,
        bytes_arg(items_data), len(items_data),
        active, indicator_position, x, y, w, h
    )

def create_upload(hwnd, parent_id, title="📤 点击或拖拽文件到此处上传", tip="",
                  files=None, x=0, y=0, w=360, h=220):
    if files is None:
        files = []
    title_data = make_utf8(title)
    tip_data = make_utf8(tip)
    files_data = make_utf8("|".join(files))
    return dll.EU_CreateUpload(
        hwnd, parent_id,
        bytes_arg(title_data), len(title_data),
        bytes_arg(tip_data), len(tip_data),
        bytes_arg(files_data), len(files_data),
        x, y, w, h
    )

def _infinite_scroll_items_data(items):
    rows = []
    for item in items or []:
        if isinstance(item, dict):
            title = str(item.get("title", item.get("text", "")))
            subtitle = str(item.get("subtitle", item.get("desc", "")))
            tag = str(item.get("tag", ""))
            rows.append("\t".join([title, subtitle, tag]).rstrip("\t"))
        elif isinstance(item, (list, tuple)):
            values = [str(v) for v in item[:3]]
            rows.append("\t".join(values))
        else:
            rows.append(str(item))
    return make_utf8("\n".join(rows))

def create_infinite_scroll(hwnd, parent_id, items=None,
                           x=0, y=0, w=360, h=260):
    if items is None:
        items = [
            ("📌 待办事项", "打开窗口后可直接滚动加载更多", "进行中"),
            ("🧾 审批记录", "列表项支持标题、副标题和标签", "已同步"),
            ("📦 发货提醒", "接近底部会触发加载回调", "今日"),
        ]
    data = _infinite_scroll_items_data(items)
    return dll.EU_CreateInfiniteScroll(
        hwnd, parent_id, bytes_arg(data), len(data), x, y, w, h
    )

def set_image_source(hwnd, element_id, src="", alt="图片"):
    src_data = make_utf8(src)
    alt_data = make_utf8(alt)
    dll.EU_SetImageSource(
        hwnd, element_id,
        bytes_arg(src_data), len(src_data),
        bytes_arg(alt_data), len(alt_data)
    )

def set_image_fit(hwnd, element_id, fit):
    dll.EU_SetImageFit(hwnd, element_id, _image_fit_value(fit))

def set_image_preview(hwnd, element_id, open=True):
    dll.EU_SetImagePreview(hwnd, element_id, 1 if open else 0)

def set_image_preview_enabled(hwnd, element_id, enabled=True):
    dll.EU_SetImagePreviewEnabled(hwnd, element_id, 1 if enabled else 0)

def set_image_preview_transform(hwnd, element_id, scale_percent=100, offset_x=0, offset_y=0):
    dll.EU_SetImagePreviewTransform(hwnd, element_id, scale_percent, offset_x, offset_y)

def set_image_cache_enabled(hwnd, element_id, enabled=True):
    dll.EU_SetImageCacheEnabled(hwnd, element_id, 1 if enabled else 0)

def set_image_lazy(hwnd, element_id, lazy=True):
    dll.EU_SetImageLazy(hwnd, element_id, 1 if lazy else 0)

def set_image_placeholder(hwnd, element_id, icon="🖼️", text="图片加载中",
                          fg=0, bg=0):
    icon_data = make_utf8(icon)
    text_data = make_utf8(text)
    dll.EU_SetImagePlaceholder(
        hwnd, element_id,
        bytes_arg(icon_data), len(icon_data),
        bytes_arg(text_data), len(text_data),
        fg, bg
    )

def set_image_error_content(hwnd, element_id, icon="⚠️", text="图片加载失败",
                            fg=0, bg=0):
    icon_data = make_utf8(icon)
    text_data = make_utf8(text)
    dll.EU_SetImageErrorContent(
        hwnd, element_id,
        bytes_arg(icon_data), len(icon_data),
        bytes_arg(text_data), len(text_data),
        fg, bg
    )

def set_image_preview_list(hwnd, element_id, sources=None, selected_index=0):
    if sources is None:
        sources = []
    data = make_utf8("|".join(str(item) for item in sources))
    dll.EU_SetImagePreviewList(
        hwnd, element_id,
        bytes_arg(data), len(data),
        selected_index
    )

def set_image_preview_index(hwnd, element_id, index=0):
    dll.EU_SetImagePreviewIndex(hwnd, element_id, index)

def get_image_preview_open(hwnd, element_id):
    return dll.EU_GetImagePreviewOpen(hwnd, element_id)

def get_image_options(hwnd, element_id):
    fit = ctypes.c_int()
    preview_enabled = ctypes.c_int()
    preview_open = ctypes.c_int()
    status = ctypes.c_int()
    ok = dll.EU_GetImageOptions(
        hwnd, element_id,
        ctypes.byref(fit), ctypes.byref(preview_enabled),
        ctypes.byref(preview_open), ctypes.byref(status),
    )
    return (fit.value, bool(preview_enabled.value), bool(preview_open.value), status.value) if ok else None

def get_image_full_options(hwnd, element_id):
    fit = ctypes.c_int()
    preview_enabled = ctypes.c_int()
    preview_open = ctypes.c_int()
    status = ctypes.c_int()
    scale_percent = ctypes.c_int()
    offset_x = ctypes.c_int()
    offset_y = ctypes.c_int()
    cache_enabled = ctypes.c_int()
    reload_count = ctypes.c_int()
    bitmap_width = ctypes.c_int()
    bitmap_height = ctypes.c_int()
    ok = dll.EU_GetImageFullOptions(
        hwnd, element_id,
        ctypes.byref(fit), ctypes.byref(preview_enabled),
        ctypes.byref(preview_open), ctypes.byref(status),
        ctypes.byref(scale_percent), ctypes.byref(offset_x), ctypes.byref(offset_y),
        ctypes.byref(cache_enabled), ctypes.byref(reload_count),
        ctypes.byref(bitmap_width), ctypes.byref(bitmap_height),
    )
    return {
        "fit": fit.value,
        "preview_enabled": bool(preview_enabled.value),
        "preview_open": bool(preview_open.value),
        "status": status.value,
        "scale_percent": scale_percent.value,
        "offset_x": offset_x.value,
        "offset_y": offset_y.value,
        "cache_enabled": bool(cache_enabled.value),
        "reload_count": reload_count.value,
        "bitmap_width": bitmap_width.value,
        "bitmap_height": bitmap_height.value,
    } if ok else None

def get_image_advanced_options(hwnd, element_id):
    fit = ctypes.c_int()
    lazy = ctypes.c_int()
    preview_enabled = ctypes.c_int()
    preview_open = ctypes.c_int()
    preview_index = ctypes.c_int()
    preview_count = ctypes.c_int()
    status = ctypes.c_int()
    scale_percent = ctypes.c_int()
    offset_x = ctypes.c_int()
    offset_y = ctypes.c_int()
    ok = dll.EU_GetImageAdvancedOptions(
        hwnd, element_id,
        ctypes.byref(fit), ctypes.byref(lazy), ctypes.byref(preview_enabled),
        ctypes.byref(preview_open), ctypes.byref(preview_index), ctypes.byref(preview_count),
        ctypes.byref(status), ctypes.byref(scale_percent),
        ctypes.byref(offset_x), ctypes.byref(offset_y),
    )
    return {
        "fit": fit.value,
        "lazy": bool(lazy.value),
        "preview_enabled": bool(preview_enabled.value),
        "preview_open": bool(preview_open.value),
        "preview_index": preview_index.value,
        "preview_count": preview_count.value,
        "status": status.value,
        "scale_percent": scale_percent.value,
        "offset_x": offset_x.value,
        "offset_y": offset_y.value,
    } if ok else None

def set_carousel_items(hwnd, element_id, items):
    data = make_utf8("|".join(items))
    dll.EU_SetCarouselItems(hwnd, element_id, bytes_arg(data), len(data))

def set_carousel_active(hwnd, element_id, active_index):
    dll.EU_SetCarouselActive(hwnd, element_id, active_index)

def set_carousel_options(hwnd, element_id, loop=True, indicator_position=0,
                         show_arrows=True, show_indicators=True):
    dll.EU_SetCarouselOptions(
        hwnd, element_id,
        1 if loop else 0,
        indicator_position,
        1 if show_arrows else 0,
        1 if show_indicators else 0,
    )

def set_carousel_behavior(hwnd, element_id, trigger_mode="click", arrow_mode="always",
                          direction="horizontal", carousel_type="normal",
                          pause_on_hover=False):
    dll.EU_SetCarouselBehavior(
        hwnd, element_id,
        _carousel_trigger_value(trigger_mode),
        _carousel_arrow_value(arrow_mode),
        _carousel_direction_value(direction),
        _carousel_type_value(carousel_type),
        1 if pause_on_hover else 0,
    )

def get_carousel_behavior(hwnd, element_id):
    trigger_mode = ctypes.c_int()
    arrow_mode = ctypes.c_int()
    direction = ctypes.c_int()
    carousel_type = ctypes.c_int()
    pause_on_hover = ctypes.c_int()
    ok = dll.EU_GetCarouselBehavior(
        hwnd, element_id,
        ctypes.byref(trigger_mode), ctypes.byref(arrow_mode),
        ctypes.byref(direction), ctypes.byref(carousel_type),
        ctypes.byref(pause_on_hover),
    )
    return {
        "trigger_mode": trigger_mode.value,
        "arrow_mode": arrow_mode.value,
        "direction": direction.value,
        "carousel_type": carousel_type.value,
        "pause_on_hover": bool(pause_on_hover.value),
    } if ok else None

def set_carousel_visual(hwnd, element_id, text_color=0, text_alpha=255, text_font_size=0,
                        odd_bg=0, even_bg=0, panel_bg=0,
                        active_indicator=0, inactive_indicator=0,
                        card_scale_percent=82):
    dll.EU_SetCarouselVisual(
        hwnd, element_id,
        int(text_color) & 0xFFFFFFFF,
        int(text_alpha),
        int(text_font_size),
        int(odd_bg) & 0xFFFFFFFF,
        int(even_bg) & 0xFFFFFFFF,
        int(panel_bg) & 0xFFFFFFFF,
        int(active_indicator) & 0xFFFFFFFF,
        int(inactive_indicator) & 0xFFFFFFFF,
        int(card_scale_percent),
    )

def get_carousel_visual(hwnd, element_id):
    text_color = ctypes.c_uint32()
    text_alpha = ctypes.c_int()
    text_font_size = ctypes.c_int()
    odd_bg = ctypes.c_uint32()
    even_bg = ctypes.c_uint32()
    panel_bg = ctypes.c_uint32()
    active_indicator = ctypes.c_uint32()
    inactive_indicator = ctypes.c_uint32()
    card_scale_percent = ctypes.c_int()
    ok = dll.EU_GetCarouselVisual(
        hwnd, element_id,
        ctypes.byref(text_color), ctypes.byref(text_alpha), ctypes.byref(text_font_size),
        ctypes.byref(odd_bg), ctypes.byref(even_bg), ctypes.byref(panel_bg),
        ctypes.byref(active_indicator), ctypes.byref(inactive_indicator),
        ctypes.byref(card_scale_percent),
    )
    return {
        "text_color": text_color.value,
        "text_alpha": text_alpha.value,
        "text_font_size": text_font_size.value,
        "odd_bg": odd_bg.value,
        "even_bg": even_bg.value,
        "panel_bg": panel_bg.value,
        "active_indicator": active_indicator.value,
        "inactive_indicator": inactive_indicator.value,
        "card_scale_percent": card_scale_percent.value,
    } if ok else None

def set_carousel_autoplay(hwnd, element_id, enabled=True, interval_ms=3000):
    dll.EU_SetCarouselAutoplay(hwnd, element_id, 1 if enabled else 0, interval_ms)

def set_carousel_animation(hwnd, element_id, transition_ms=260):
    dll.EU_SetCarouselAnimation(hwnd, element_id, transition_ms)

def carousel_advance(hwnd, element_id, delta=1):
    dll.EU_CarouselAdvance(hwnd, element_id, delta)

def carousel_tick(hwnd, element_id, elapsed_ms=33):
    dll.EU_CarouselTick(hwnd, element_id, elapsed_ms)

def get_carousel_options(hwnd, element_id):
    loop = ctypes.c_int()
    indicator_position = ctypes.c_int()
    show_arrows = ctypes.c_int()
    show_indicators = ctypes.c_int()
    autoplay = ctypes.c_int()
    interval_ms = ctypes.c_int()
    ok = dll.EU_GetCarouselOptions(
        hwnd, element_id,
        ctypes.byref(loop), ctypes.byref(indicator_position),
        ctypes.byref(show_arrows), ctypes.byref(show_indicators),
        ctypes.byref(autoplay), ctypes.byref(interval_ms),
    )
    return (
        bool(loop.value), indicator_position.value,
        bool(show_arrows.value), bool(show_indicators.value),
        bool(autoplay.value), interval_ms.value,
    ) if ok else None

def get_carousel_full_state(hwnd, element_id):
    active_index = ctypes.c_int()
    previous_index = ctypes.c_int()
    item_count = ctypes.c_int()
    loop = ctypes.c_int()
    indicator_position = ctypes.c_int()
    show_arrows = ctypes.c_int()
    show_indicators = ctypes.c_int()
    autoplay = ctypes.c_int()
    interval_ms = ctypes.c_int()
    autoplay_tick = ctypes.c_int()
    autoplay_elapsed_ms = ctypes.c_int()
    transition_ms = ctypes.c_int()
    transition_progress = ctypes.c_int()
    transition_direction = ctypes.c_int()
    last_action = ctypes.c_int()
    change_count = ctypes.c_int()
    ok = dll.EU_GetCarouselFullState(
        hwnd, element_id,
        ctypes.byref(active_index), ctypes.byref(previous_index),
        ctypes.byref(item_count), ctypes.byref(loop),
        ctypes.byref(indicator_position),
        ctypes.byref(show_arrows), ctypes.byref(show_indicators),
        ctypes.byref(autoplay), ctypes.byref(interval_ms),
        ctypes.byref(autoplay_tick), ctypes.byref(autoplay_elapsed_ms),
        ctypes.byref(transition_ms), ctypes.byref(transition_progress),
        ctypes.byref(transition_direction),
        ctypes.byref(last_action), ctypes.byref(change_count),
    )
    return {
        "active_index": active_index.value,
        "previous_index": previous_index.value,
        "item_count": item_count.value,
        "loop": bool(loop.value),
        "indicator_position": indicator_position.value,
        "show_arrows": bool(show_arrows.value),
        "show_indicators": bool(show_indicators.value),
        "autoplay": bool(autoplay.value),
        "interval_ms": interval_ms.value,
        "autoplay_tick": autoplay_tick.value,
        "autoplay_elapsed_ms": autoplay_elapsed_ms.value,
        "transition_ms": transition_ms.value,
        "transition_progress": transition_progress.value,
        "transition_direction": transition_direction.value,
        "last_action": last_action.value,
        "change_count": change_count.value,
    } if ok else None

def set_upload_files(hwnd, element_id, files):
    data = make_utf8("|".join(files))
    dll.EU_SetUploadFiles(hwnd, element_id, bytes_arg(data), len(data))

def set_upload_file_items(hwnd, element_id, items):
    rows = []
    for item in items:
        name = str(item[0]) if len(item) > 0 else ""
        status = int(item[1]) if len(item) > 1 else 1
        progress = int(item[2]) if len(item) > 2 else 100
        path = str(item[3]) if len(item) > 3 else name
        thumbnail = str(item[4]) if len(item) > 4 else path
        size = int(item[5]) if len(item) > 5 else 0
        rows.append(f"{name}\t{status}\t{progress}\t{path}\t{thumbnail}\t{size}")
    data = make_utf8("|".join(rows))
    dll.EU_SetUploadFileItems(hwnd, element_id, bytes_arg(data), len(data))

def set_upload_options(hwnd, element_id, multiple=True, auto_upload=False):
    dll.EU_SetUploadOptions(hwnd, element_id, 1 if multiple else 0, 1 if auto_upload else 0)

def set_upload_style(hwnd, element_id, style_mode=5, show_file_list=True,
                     show_tip=True, show_actions=True, drop_enabled=False):
    dll.EU_SetUploadStyle(
        hwnd, element_id, int(style_mode),
        1 if show_file_list else 0,
        1 if show_tip else 0,
        1 if show_actions else 0,
        1 if drop_enabled else 0,
    )

def get_upload_style(hwnd, element_id):
    values = [ctypes.c_int() for _ in range(5)]
    ok = dll.EU_GetUploadStyle(hwnd, element_id, *(ctypes.byref(v) for v in values))
    if not ok:
        return None
    keys = ["style_mode", "show_file_list", "show_tip", "show_actions", "drop_enabled"]
    result = {key: value.value for key, value in zip(keys, values)}
    for key in keys[1:]:
        result[key] = bool(result[key])
    return result

def set_upload_texts(hwnd, element_id, title="", tip="", trigger="", submit=""):
    title_data = make_utf8(title)
    tip_data = make_utf8(tip)
    trigger_data = make_utf8(trigger)
    submit_data = make_utf8(submit)
    dll.EU_SetUploadTexts(
        hwnd, element_id,
        bytes_arg(title_data), len(title_data),
        bytes_arg(tip_data), len(tip_data),
        bytes_arg(trigger_data), len(trigger_data),
        bytes_arg(submit_data), len(submit_data),
    )

def set_upload_constraints(hwnd, element_id, limit=0, max_size_kb=0, accept=""):
    accept_data = make_utf8(accept)
    dll.EU_SetUploadConstraints(
        hwnd, element_id, int(limit), int(max_size_kb),
        bytes_arg(accept_data), len(accept_data),
    )

def get_upload_constraints(hwnd, element_id):
    limit = ctypes.c_int()
    max_size_kb = ctypes.c_int()
    needed = dll.EU_GetUploadConstraints(
        hwnd, element_id, ctypes.byref(limit), ctypes.byref(max_size_kb), None, 0
    )
    accept = ""
    if needed > 0:
        buf = (ctypes.c_ubyte * (needed + 1))()
        dll.EU_GetUploadConstraints(
            hwnd, element_id, ctypes.byref(limit), ctypes.byref(max_size_kb), buf, needed + 1
        )
        accept = bytes(buf[:needed]).decode("utf-8", errors="replace")
    return {"limit": limit.value, "max_size_kb": max_size_kb.value, "accept": accept}

def set_upload_preview_open(hwnd, element_id, index=0, open=True):
    dll.EU_SetUploadPreviewOpen(hwnd, element_id, int(index), 1 if open else 0)

def get_upload_preview_state(hwnd, element_id):
    index = ctypes.c_int()
    open_value = ctypes.c_int()
    ok = dll.EU_GetUploadPreviewState(hwnd, element_id, ctypes.byref(index), ctypes.byref(open_value))
    return {"file_index": index.value, "open": bool(open_value.value)} if ok else None

def set_upload_selected_files(hwnd, element_id, files):
    data = make_utf8("|".join(files))
    dll.EU_SetUploadSelectedFiles(hwnd, element_id, bytes_arg(data), len(data))

def open_upload_file_dialog(hwnd, element_id):
    return dll.EU_OpenUploadFileDialog(hwnd, element_id)

def start_upload(hwnd, element_id, index=-1):
    return dll.EU_StartUpload(hwnd, element_id, index)

def retry_upload_file(hwnd, element_id, index):
    dll.EU_RetryUploadFile(hwnd, element_id, index)

def remove_upload_file(hwnd, element_id, index):
    dll.EU_RemoveUploadFile(hwnd, element_id, index)

def clear_upload_files(hwnd, element_id):
    dll.EU_ClearUploadFiles(hwnd, element_id)

def get_upload_file_status(hwnd, element_id, index):
    status = ctypes.c_int()
    progress = ctypes.c_int()
    ok = dll.EU_GetUploadFileStatus(
        hwnd, element_id, index,
        ctypes.byref(status), ctypes.byref(progress),
    )
    return (status.value, progress.value) if ok else None

def get_upload_selected_files(hwnd, element_id):
    needed = dll.EU_GetUploadSelectedFiles(hwnd, element_id, None, 0)
    if needed <= 0:
        return ""
    buf = (ctypes.c_ubyte * (needed + 1))()
    dll.EU_GetUploadSelectedFiles(hwnd, element_id, buf, needed + 1)
    return bytes(buf[:needed]).decode("utf-8", errors="replace")

def get_upload_file_name(hwnd, element_id, index):
    needed = dll.EU_GetUploadFileName(hwnd, element_id, index, None, 0)
    if needed <= 0:
        return ""
    buf = (ctypes.c_ubyte * (needed + 1))()
    dll.EU_GetUploadFileName(hwnd, element_id, index, buf, needed + 1)
    return bytes(buf[:needed]).decode("utf-8", errors="replace")

def get_upload_full_state(hwnd, element_id):
    values = [ctypes.c_int() for _ in range(13)]
    ok = dll.EU_GetUploadFullState(
        hwnd, element_id,
        *(ctypes.byref(v) for v in values)
    )
    if not ok:
        return None
    keys = [
        "file_count", "selected_count", "last_selected_count",
        "upload_request_count", "retry_count", "remove_count",
        "last_action", "waiting_count", "uploading_count",
        "success_count", "failed_count", "multiple", "auto_upload",
    ]
    result = {key: value.value for key, value in zip(keys, values)}
    result["multiple"] = bool(result["multiple"])
    result["auto_upload"] = bool(result["auto_upload"])
    return result

def set_upload_select_callback(hwnd, element_id, callback):
    dll.EU_SetUploadSelectCallback(hwnd, element_id, callback)

def set_upload_action_callback(hwnd, element_id, callback):
    dll.EU_SetUploadActionCallback(hwnd, element_id, callback)

def set_infinite_scroll_items(hwnd, element_id, items):
    data = _infinite_scroll_items_data(items)
    dll.EU_SetInfiniteScrollItems(hwnd, element_id, bytes_arg(data), len(data))

def append_infinite_scroll_items(hwnd, element_id, items):
    data = _infinite_scroll_items_data(items)
    dll.EU_AppendInfiniteScrollItems(hwnd, element_id, bytes_arg(data), len(data))

def clear_infinite_scroll_items(hwnd, element_id):
    dll.EU_ClearInfiniteScrollItems(hwnd, element_id)

def set_infinite_scroll_state(hwnd, element_id, loading=False, no_more=False, disabled=False):
    dll.EU_SetInfiniteScrollState(
        hwnd, element_id,
        1 if loading else 0,
        1 if no_more else 0,
        1 if disabled else 0,
    )

def set_infinite_scroll_options(hwnd, element_id, item_height=54, gap=8, threshold=60,
                                style_mode=0, show_scrollbar=True, show_index=False):
    dll.EU_SetInfiniteScrollOptions(
        hwnd, element_id, item_height, gap, threshold, style_mode,
        1 if show_scrollbar else 0, 1 if show_index else 0,
    )

def set_infinite_scroll_texts(hwnd, element_id,
                              loading_text="加载中...",
                              no_more_text="没有更多了",
                              empty_text="暂无数据"):
    loading_data = make_utf8(loading_text)
    no_more_data = make_utf8(no_more_text)
    empty_data = make_utf8(empty_text)
    dll.EU_SetInfiniteScrollTexts(
        hwnd, element_id,
        bytes_arg(loading_data), len(loading_data),
        bytes_arg(no_more_data), len(no_more_data),
        bytes_arg(empty_data), len(empty_data),
    )

def set_infinite_scroll_scroll(hwnd, element_id, scroll_y=0):
    dll.EU_SetInfiniteScrollScroll(hwnd, element_id, scroll_y)

def get_infinite_scroll_full_state(hwnd, element_id):
    values = [ctypes.c_int() for _ in range(15)]
    ok = dll.EU_GetInfiniteScrollFullState(
        hwnd, element_id,
        *(ctypes.byref(v) for v in values)
    )
    if not ok:
        return None
    keys = [
        "item_count", "scroll_y", "max_scroll", "content_height", "viewport_height",
        "loading", "no_more", "disabled", "load_count", "change_count",
        "last_action", "threshold", "style_mode", "show_scrollbar", "show_index",
    ]
    result = {key: value.value for key, value in zip(keys, values)}
    result["loading"] = bool(result["loading"])
    result["no_more"] = bool(result["no_more"])
    result["disabled"] = bool(result["disabled"])
    result["show_scrollbar"] = bool(result["show_scrollbar"])
    result["show_index"] = bool(result["show_index"])
    return result

def set_infinite_scroll_load_callback(hwnd, element_id, callback):
    dll.EU_SetInfiniteScrollLoadCallback(hwnd, element_id, callback)

def create_breadcrumb(hwnd, parent_id, items=None, separator="/", current=-1,
                      x=0, y=0, w=420, h=32):
    if items is None:
        items = ["🏠 首页", "组件", "导航"]
    items_data = make_utf8("|".join(items))
    sep_data = make_utf8(separator)
    return dll.EU_CreateBreadcrumb(
        hwnd, parent_id,
        bytes_arg(items_data), len(items_data),
        bytes_arg(sep_data), len(sep_data),
        current, x, y, w, h
    )

def create_tabs(hwnd, parent_id, items=None, active=0, tab_type=0,
                x=0, y=0, w=420, h=40):
    if items is None:
        items = ["用户", "配置", "角色"]
    items_data = make_utf8("|".join(items))
    return dll.EU_CreateTabs(
        hwnd, parent_id, bytes_arg(items_data), len(items_data),
        active, tab_type, x, y, w, h
    )

def set_tabs_chrome_mode(hwnd, element_id, enabled=True):
    dll.EU_SetTabsChromeMode(hwnd, element_id, 1 if enabled else 0)

def get_tabs_chrome_mode(hwnd, element_id):
    return bool(dll.EU_GetTabsChromeMode(hwnd, element_id))

def set_tabs_item_icon(hwnd, element_id, index, icon):
    data = make_utf8(icon)
    dll.EU_SetTabsItemIcon(hwnd, element_id, index, bytes_arg(data), len(data))

def set_tabs_item_loading(hwnd, element_id, index, loading=True):
    dll.EU_SetTabsItemLoading(hwnd, element_id, index, 1 if loading else 0)

def set_tabs_item_pinned(hwnd, element_id, index, pinned=True):
    dll.EU_SetTabsItemPinned(hwnd, element_id, index, 1 if pinned else 0)

def set_tabs_item_muted(hwnd, element_id, index, muted=True):
    dll.EU_SetTabsItemMuted(hwnd, element_id, index, 1 if muted else 0)

def set_tabs_item_closable(hwnd, element_id, index, closable=True):
    dll.EU_SetTabsItemClosable(hwnd, element_id, index, 1 if closable else 0)

def set_tabs_item_chrome_state(hwnd, element_id, index, loading=False, pinned=False,
                               muted=False, alerting=False):
    dll.EU_SetTabsItemChromeState(
        hwnd, element_id, index,
        1 if loading else 0, 1 if pinned else 0,
        1 if muted else 0, 1 if alerting else 0,
    )

def get_tabs_item_chrome_state(hwnd, element_id, index):
    loading = ctypes.c_int()
    pinned = ctypes.c_int()
    muted = ctypes.c_int()
    alerting = ctypes.c_int()
    ok = dll.EU_GetTabsItemChromeState(
        hwnd, element_id, index,
        ctypes.byref(loading), ctypes.byref(pinned),
        ctypes.byref(muted), ctypes.byref(alerting),
    )
    if not ok:
        return None
    return {
        "loading": bool(loading.value),
        "pinned": bool(pinned.value),
        "muted": bool(muted.value),
        "alerting": bool(alerting.value),
    }

def set_tabs_chrome_metrics(hwnd, element_id, min_width=96, max_width=220,
                            pinned_width=48, height=36, overlap=12):
    dll.EU_SetTabsChromeMetrics(hwnd, element_id, min_width, max_width, pinned_width, height, overlap)

def set_tabs_new_button_visible(hwnd, element_id, visible=True):
    dll.EU_SetTabsNewButtonVisible(hwnd, element_id, 1 if visible else 0)

def set_tabs_drag_options(hwnd, element_id, reorder_enabled=True, detach_enabled=False):
    dll.EU_SetTabsDragOptions(hwnd, element_id, 1 if reorder_enabled else 0, 1 if detach_enabled else 0)

def set_tabs_reorder_callback(hwnd, element_id, callback):
    dll.EU_SetTabsReorderCallback(hwnd, element_id, callback)

def _tabs_item_to_line(item):
    if isinstance(item, dict):
        label = item.get("label", "")
        name = item.get("name", "")
        content = item.get("content", "")
        icon = item.get("icon", "")
        disabled = "1" if item.get("disabled", False) else "0"
        closable = "1" if item.get("closable", True) else "0"
        return "\t".join([label, name, content, icon, disabled, closable])
    values = list(item)
    while len(values) < 6:
        values.append("")
    values[4] = "1" if bool(values[4]) else "0"
    values[5] = "1" if (values[5] == "" or bool(values[5])) else "0"
    return "\t".join(str(v) for v in values[:6])

def create_tabs_ex(hwnd, parent_id, items=None, active=0, tab_type=0, tab_position=0,
                   closable=False, addable=False, editable=False, content_visible=True,
                   x=0, y=0, w=520, h=220):
    if items is None:
        items = [
            {"label": "用户管理", "name": "users", "content": "👥 用户管理内容", "icon": "👥"},
            {"label": "配置管理", "name": "config", "content": "⚙️ 配置管理内容", "icon": "⚙️"},
        ]
    labels = [item.get("label", "") if isinstance(item, dict) else str(item[0]) for item in items]
    element_id = create_tabs(hwnd, parent_id, labels, active, tab_type, x, y, w, h)
    set_tabs_items_ex(hwnd, element_id, items)
    set_tabs_position(hwnd, element_id, tab_position)
    set_tabs_options(hwnd, element_id, tab_type, closable, addable)
    set_tabs_editable(hwnd, element_id, editable)
    set_tabs_content_visible(hwnd, element_id, content_visible)
    return element_id

def create_pagination(hwnd, parent_id, total=120, page_size=10, current=1,
                      x=0, y=0, w=420, h=40):
    return dll.EU_CreatePagination(
        hwnd, parent_id, total, page_size, current, x, y, w, h
    )

def create_steps(hwnd, parent_id, items=None, active=1,
                 x=0, y=0, w=420, h=80,
                 space=None, align_center=False, simple=False,
                 finish_status=2, process_status=1):
    if items is None:
        items = ["开始", "处理", "完成"]
    items_data = make_utf8("|".join(items))
    element_id = dll.EU_CreateSteps(
        hwnd, parent_id, bytes_arg(items_data), len(items_data),
        active, x, y, w, h
    )
    if element_id and (space is not None or align_center or simple or
                       finish_status != 2 or process_status != 1):
        set_steps_options(
            hwnd, element_id,
            0 if space is None else int(space),
            align_center=align_center,
            simple=simple,
            finish_status=finish_status,
            process_status=process_status,
        )
    return element_id

def set_breadcrumb_items(hwnd, element_id, items):
    data = make_utf8("|".join(items))
    dll.EU_SetBreadcrumbItems(hwnd, element_id, bytes_arg(data), len(data))

def set_breadcrumb_separator(hwnd, element_id, separator=">"):
    data = make_utf8(separator)
    dll.EU_SetBreadcrumbSeparator(hwnd, element_id, bytes_arg(data), len(data))

def set_breadcrumb_current(hwnd, element_id, index):
    dll.EU_SetBreadcrumbCurrent(hwnd, element_id, index)

def trigger_breadcrumb_click(hwnd, element_id, index):
    dll.EU_TriggerBreadcrumbClick(hwnd, element_id, index)

def get_breadcrumb_state(hwnd, element_id):
    current = ctypes.c_int()
    count = ctypes.c_int()
    ok = dll.EU_GetBreadcrumbState(
        hwnd, element_id,
        ctypes.byref(current), ctypes.byref(count),
    )
    return (current.value, count.value) if ok else None

def get_breadcrumb_item(hwnd, element_id, index):
    needed = dll.EU_GetBreadcrumbItem(hwnd, element_id, index, None, 0)
    if needed <= 0:
        return ""
    buf = (ctypes.c_ubyte * (needed + 1))()
    dll.EU_GetBreadcrumbItem(hwnd, element_id, index, buf, needed + 1)
    return bytes(buf[:needed]).decode("utf-8", errors="replace")

def get_breadcrumb_full_state(hwnd, element_id):
    values = [ctypes.c_int() for _ in range(7)]
    ok = dll.EU_GetBreadcrumbFullState(
        hwnd, element_id,
        *(ctypes.byref(v) for v in values)
    )
    if not ok:
        return None
    keys = [
        "current_index", "item_count", "hover_index", "press_index",
        "last_clicked_index", "click_count", "last_action",
    ]
    return {key: value.value for key, value in zip(keys, values)}

def set_breadcrumb_select_callback(hwnd, element_id, callback):
    dll.EU_SetBreadcrumbSelectCallback(hwnd, element_id, callback)

def set_tabs_items(hwnd, element_id, items):
    data = make_utf8("|".join(items))
    dll.EU_SetTabsItems(hwnd, element_id, bytes_arg(data), len(data))

def set_tabs_items_ex(hwnd, element_id, items):
    data = make_utf8("|".join(_tabs_item_to_line(item) for item in items))
    dll.EU_SetTabsItemsEx(hwnd, element_id, bytes_arg(data), len(data))

def set_tabs_type(hwnd, element_id, tab_type):
    dll.EU_SetTabsType(hwnd, element_id, tab_type)

def set_tabs_position(hwnd, element_id, tab_position):
    if isinstance(tab_position, str):
        tab_position = {"top": 0, "right": 1, "bottom": 2, "left": 3}.get(tab_position, 0)
    dll.EU_SetTabsPosition(hwnd, element_id, tab_position)

def set_tabs_header_align(hwnd, element_id, align=0):
    if isinstance(align, str):
        align = {"left": 0, "center": 1, "right": 2, "左": 0, "中": 1, "右": 2}.get(align, 0)
    dll.EU_SetTabsHeaderAlign(hwnd, element_id, align)

def set_tabs_active(hwnd, element_id, active):
    dll.EU_SetTabsActive(hwnd, element_id, active)

def set_tabs_active_name(hwnd, element_id, name):
    data = make_utf8(name)
    dll.EU_SetTabsActiveName(hwnd, element_id, bytes_arg(data), len(data))

def set_tabs_options(hwnd, element_id, tab_type=0, closable=False, addable=False):
    dll.EU_SetTabsOptions(hwnd, element_id, tab_type, int(bool(closable)), int(bool(addable)))

def set_tabs_editable(hwnd, element_id, editable=True):
    dll.EU_SetTabsEditable(hwnd, element_id, int(bool(editable)))

def set_tabs_content_visible(hwnd, element_id, visible=True):
    dll.EU_SetTabsContentVisible(hwnd, element_id, int(bool(visible)))

def add_tabs_item(hwnd, element_id, text):
    data = make_utf8(text)
    dll.EU_AddTabsItem(hwnd, element_id, bytes_arg(data), len(data))

def close_tabs_item(hwnd, element_id, index):
    dll.EU_CloseTabsItem(hwnd, element_id, index)

def set_tabs_scroll(hwnd, element_id, offset):
    dll.EU_SetTabsScroll(hwnd, element_id, offset)

def tabs_scroll(hwnd, element_id, delta):
    dll.EU_TabsScroll(hwnd, element_id, delta)

def get_tabs_state(hwnd, element_id):
    active = ctypes.c_int()
    count = ctypes.c_int()
    tab_type = ctypes.c_int()
    ok = dll.EU_GetTabsState(
        hwnd, element_id,
        ctypes.byref(active), ctypes.byref(count), ctypes.byref(tab_type),
    )
    return (active.value, count.value, tab_type.value) if ok else None

def get_tabs_header_align(hwnd, element_id):
    return dll.EU_GetTabsHeaderAlign(hwnd, element_id)

def get_tabs_item(hwnd, element_id, index):
    needed = dll.EU_GetTabsItem(hwnd, element_id, index, None, 0)
    if needed <= 0:
        return ""
    buf = (ctypes.c_ubyte * (needed + 1))()
    dll.EU_GetTabsItem(hwnd, element_id, index, buf, needed + 1)
    return bytes(buf[:needed]).decode("utf-8", errors="replace")

def get_tabs_active_name(hwnd, element_id):
    needed = dll.EU_GetTabsActiveName(hwnd, element_id, None, 0)
    if needed <= 0:
        return ""
    buf = (ctypes.c_ubyte * (needed + 1))()
    dll.EU_GetTabsActiveName(hwnd, element_id, buf, needed + 1)
    return bytes(buf[:needed]).decode("utf-8", errors="replace")

def get_tabs_item_content(hwnd, element_id, index):
    needed = dll.EU_GetTabsItemContent(hwnd, element_id, index, None, 0)
    if needed <= 0:
        return ""
    buf = (ctypes.c_ubyte * (needed + 1))()
    dll.EU_GetTabsItemContent(hwnd, element_id, index, buf, needed + 1)
    return bytes(buf[:needed]).decode("utf-8", errors="replace")

def get_tabs_full_state(hwnd, element_id):
    values = [ctypes.c_int() for _ in range(18)]
    ok = dll.EU_GetTabsFullState(
        hwnd, element_id,
        *(ctypes.byref(v) for v in values)
    )
    if not ok:
        return None
    keys = [
        "active_index", "item_count", "tab_type", "closable", "addable",
        "scroll_offset", "max_scroll_offset", "hover_index", "press_index",
        "hover_part", "press_part", "last_closed_index", "last_added_index",
        "close_count", "add_count", "select_count", "scroll_count", "last_action",
    ]
    return {key: value.value for key, value in zip(keys, values)}

def get_tabs_full_state_ex(hwnd, element_id):
    values = [ctypes.c_int() for _ in range(23)]
    ok = dll.EU_GetTabsFullStateEx(
        hwnd, element_id,
        *(ctypes.byref(v) for v in values)
    )
    if not ok:
        return None
    keys = [
        "active_index", "item_count", "tab_type", "closable", "addable",
        "scroll_offset", "max_scroll_offset", "hover_index", "press_index",
        "hover_part", "press_part", "last_closed_index", "last_added_index",
        "close_count", "add_count", "select_count", "scroll_count", "last_action",
        "tab_position", "editable", "content_visible", "active_disabled", "active_closable",
    ]
    return {key: value.value for key, value in zip(keys, values)}

def set_tabs_change_callback(hwnd, element_id, callback):
    dll.EU_SetTabsChangeCallback(hwnd, element_id, callback)

def set_tabs_close_callback(hwnd, element_id, callback):
    dll.EU_SetTabsCloseCallback(hwnd, element_id, callback)

def set_tabs_add_callback(hwnd, element_id, callback):
    dll.EU_SetTabsAddCallback(hwnd, element_id, callback)

def set_pagination(hwnd, element_id, total, page_size, current_page):
    dll.EU_SetPagination(hwnd, element_id, total, page_size, current_page)

def set_pagination_current(hwnd, element_id, current_page):
    dll.EU_SetPaginationCurrent(hwnd, element_id, current_page)

def set_pagination_page_size(hwnd, element_id, page_size):
    dll.EU_SetPaginationPageSize(hwnd, element_id, page_size)

def set_pagination_options(hwnd, element_id, show_jumper=True, show_size_changer=True, visible_page_count=7):
    dll.EU_SetPaginationOptions(
        hwnd, element_id,
        int(bool(show_jumper)), int(bool(show_size_changer)), int(visible_page_count),
    )

def set_pagination_advanced_options(hwnd, element_id, background=False, small=False, hide_on_single_page=False):
    dll.EU_SetPaginationAdvancedOptions(
        hwnd, element_id,
        int(bool(background)), int(bool(small)), int(bool(hide_on_single_page)),
    )

def set_pagination_page_size_options(hwnd, element_id, sizes):
    values = [int(v) for v in sizes]
    arr = (ctypes.c_int * len(values))(*values) if values else None
    dll.EU_SetPaginationPageSizeOptions(hwnd, element_id, arr, len(values))

def set_pagination_jump_page(hwnd, element_id, jump_page):
    dll.EU_SetPaginationJumpPage(hwnd, element_id, jump_page)

def trigger_pagination_jump(hwnd, element_id):
    dll.EU_TriggerPaginationJump(hwnd, element_id)

def next_pagination_page_size(hwnd, element_id):
    dll.EU_NextPaginationPageSize(hwnd, element_id)

def get_pagination_state(hwnd, element_id):
    total = ctypes.c_int()
    page_size = ctypes.c_int()
    current = ctypes.c_int()
    page_count = ctypes.c_int()
    ok = dll.EU_GetPaginationState(
        hwnd, element_id,
        ctypes.byref(total), ctypes.byref(page_size),
        ctypes.byref(current), ctypes.byref(page_count),
    )
    return (total.value, page_size.value, current.value, page_count.value) if ok else None

def get_pagination_full_state(hwnd, element_id):
    values = [ctypes.c_int() for _ in range(14)]
    ok = dll.EU_GetPaginationFullState(
        hwnd, element_id,
        *(ctypes.byref(v) for v in values)
    )
    if not ok:
        return None
    keys = [
        "total", "page_size", "current_page", "page_count",
        "jump_page", "visible_page_count", "show_jumper", "show_size_changer",
        "hover_part", "press_part", "change_count", "size_change_count",
        "jump_count", "last_action",
    ]
    return {key: value.value for key, value in zip(keys, values)}

def get_pagination_advanced_options(hwnd, element_id):
    background = ctypes.c_int()
    small = ctypes.c_int()
    hide_on_single_page = ctypes.c_int()
    ok = dll.EU_GetPaginationAdvancedOptions(
        hwnd, element_id,
        ctypes.byref(background), ctypes.byref(small), ctypes.byref(hide_on_single_page),
    )
    if not ok:
        return None
    return {
        "background": bool(background.value),
        "small": bool(small.value),
        "hide_on_single_page": bool(hide_on_single_page.value),
    }

def set_pagination_change_callback(hwnd, element_id, callback):
    dll.EU_SetPaginationChangeCallback(hwnd, element_id, callback)

def set_steps_detail_items(hwnd, element_id, items):
    rows = []
    for item in items:
        title = str(item[0]) if len(item) > 0 else ""
        desc = str(item[1]) if len(item) > 1 else ""
        rows.append(f"{title}\t{desc}")
    data = make_utf8("|".join(rows))
    dll.EU_SetStepsDetailItems(hwnd, element_id, bytes_arg(data), len(data))

def set_steps_icon_items(hwnd, element_id, items):
    rows = []
    for item in items:
        if isinstance(item, dict):
            title = str(item.get("title", ""))
            desc = str(item.get("description", item.get("desc", "")))
            icon = str(item.get("icon", ""))
        else:
            title = str(item[0]) if len(item) > 0 else ""
            desc = str(item[1]) if len(item) > 1 else ""
            icon = str(item[2]) if len(item) > 2 else ""
        rows.append(f"{title}\t{desc}\t{icon}")
    data = make_utf8("|".join(rows))
    dll.EU_SetStepsIconItems(hwnd, element_id, bytes_arg(data), len(data))

def set_steps_direction(hwnd, element_id, direction):
    dll.EU_SetStepsDirection(hwnd, element_id, direction)

def set_steps_active(hwnd, element_id, active):
    dll.EU_SetStepsActive(hwnd, element_id, active)

def set_steps_options(hwnd, element_id, space=0, align_center=False, simple=False,
                      finish_status=2, process_status=1):
    dll.EU_SetStepsOptions(
        hwnd, element_id, int(space),
        1 if align_center else 0,
        1 if simple else 0,
        int(finish_status), int(process_status),
    )

def get_steps_options(hwnd, element_id):
    values = [ctypes.c_int() for _ in range(5)]
    ok = dll.EU_GetStepsOptions(
        hwnd, element_id,
        *(ctypes.byref(v) for v in values)
    )
    if not ok:
        return None
    keys = ["space", "align_center", "simple", "finish_status", "process_status"]
    data = {key: value.value for key, value in zip(keys, values)}
    data["align_center"] = bool(data["align_center"])
    data["simple"] = bool(data["simple"])
    return data

def set_steps_statuses(hwnd, element_id, statuses):
    values = [int(v) for v in statuses]
    arr = (ctypes.c_int * len(values))(*values) if values else None
    dll.EU_SetStepsStatuses(hwnd, element_id, arr, len(values))

def trigger_steps_click(hwnd, element_id, index):
    dll.EU_TriggerStepsClick(hwnd, element_id, index)

def get_steps_state(hwnd, element_id):
    active = ctypes.c_int()
    count = ctypes.c_int()
    direction = ctypes.c_int()
    ok = dll.EU_GetStepsState(
        hwnd, element_id,
        ctypes.byref(active), ctypes.byref(count), ctypes.byref(direction),
    )
    return (active.value, count.value, direction.value) if ok else None

def get_steps_item(hwnd, element_id, index, text_kind=0):
    needed = dll.EU_GetStepsItem(hwnd, element_id, index, text_kind, None, 0)
    if needed <= 0:
        return ""
    buf = (ctypes.c_ubyte * (needed + 1))()
    dll.EU_GetStepsItem(hwnd, element_id, index, text_kind, buf, needed + 1)
    return bytes(buf[:needed]).decode("utf-8", errors="replace")

def get_steps_full_state(hwnd, element_id):
    values = [ctypes.c_int() for _ in range(11)]
    ok = dll.EU_GetStepsFullState(
        hwnd, element_id,
        *(ctypes.byref(v) for v in values)
    )
    if not ok:
        return None
    keys = [
        "active_index", "item_count", "direction", "hover_index", "press_index",
        "last_clicked_index", "click_count", "change_count", "last_action",
        "active_status", "failed_count",
    ]
    return {key: value.value for key, value in zip(keys, values)}

def get_steps_visual_state(hwnd, element_id):
    values = [ctypes.c_int() for _ in range(6)]
    ok = dll.EU_GetStepsVisualState(
        hwnd, element_id,
        *(ctypes.byref(v) for v in values)
    )
    if not ok:
        return None
    keys = ["space", "align_center", "simple", "finish_status", "process_status", "icon_count"]
    data = {key: value.value for key, value in zip(keys, values)}
    data["align_center"] = bool(data["align_center"])
    data["simple"] = bool(data["simple"])
    return data

def set_steps_change_callback(hwnd, element_id, callback):
    dll.EU_SetStepsChangeCallback(hwnd, element_id, callback)

def create_alert(hwnd, parent_id, title="提示", description="", alert_type=0,
                 effect=0, closable=True, x=0, y=0, w=420, h=52):
    title_data = make_utf8(title)
    desc_data = make_utf8(description)
    return dll.EU_CreateAlert(
        hwnd, parent_id,
        bytes_arg(title_data), len(title_data),
        bytes_arg(desc_data), len(desc_data),
        alert_type, effect, 1 if closable else 0, x, y, w, h
    )

def create_alert_ex(hwnd, parent_id, title="提示", description="", alert_type=0,
                    effect=0, closable=True, show_icon=True, center=False,
                    wrap_description=False, close_text="", x=0, y=0, w=420, h=52):
    title_data = make_utf8(title)
    desc_data = make_utf8(description)
    close_data = make_utf8(close_text)
    return dll.EU_CreateAlertEx(
        hwnd, parent_id,
        bytes_arg(title_data), len(title_data),
        bytes_arg(desc_data), len(desc_data),
        alert_type, effect, 1 if closable else 0,
        1 if show_icon else 0, 1 if center else 0, 1 if wrap_description else 0,
        bytes_arg(close_data), len(close_data),
        x, y, w, h
    )

def get_alert_options(hwnd, element_id):
    alert_type = ctypes.c_int()
    effect = ctypes.c_int()
    closable = ctypes.c_int()
    closed = ctypes.c_int()
    ok = dll.EU_GetAlertOptions(
        hwnd, element_id,
        ctypes.byref(alert_type), ctypes.byref(effect),
        ctypes.byref(closable), ctypes.byref(closed),
    )
    return (alert_type.value, effect.value, bool(closable.value), bool(closed.value)) if ok else None

def set_alert_description(hwnd, element_id, description):
    data = make_utf8(description)
    dll.EU_SetAlertDescription(hwnd, element_id, bytes_arg(data), len(data))

def set_alert_type(hwnd, element_id, alert_type):
    dll.EU_SetAlertType(hwnd, element_id, alert_type)

def set_alert_effect(hwnd, element_id, effect):
    dll.EU_SetAlertEffect(hwnd, element_id, effect)

def set_alert_closable(hwnd, element_id, closable):
    dll.EU_SetAlertClosable(hwnd, element_id, int(bool(closable)))

def set_alert_advanced_options(hwnd, element_id, show_icon=True, center=False, wrap_description=False):
    dll.EU_SetAlertAdvancedOptions(
        hwnd, element_id,
        1 if show_icon else 0,
        1 if center else 0,
        1 if wrap_description else 0,
    )

def get_alert_advanced_options(hwnd, element_id):
    show_icon = ctypes.c_int()
    center = ctypes.c_int()
    wrap_description = ctypes.c_int()
    ok = dll.EU_GetAlertAdvancedOptions(
        hwnd, element_id,
        ctypes.byref(show_icon), ctypes.byref(center), ctypes.byref(wrap_description),
    )
    return (bool(show_icon.value), bool(center.value), bool(wrap_description.value)) if ok else None

def set_alert_close_text(hwnd, element_id, close_text):
    data = make_utf8(close_text)
    dll.EU_SetAlertCloseText(hwnd, element_id, bytes_arg(data), len(data))

def get_alert_text(hwnd, element_id, text_type=0):
    needed = dll.EU_GetAlertText(hwnd, element_id, text_type, None, 0)
    if needed <= 0:
        return ""
    buf = (ctypes.c_ubyte * (needed + 1))()
    dll.EU_GetAlertText(hwnd, element_id, text_type, buf, needed + 1)
    return bytes(buf[:needed]).decode("utf-8", errors="replace")

def set_alert_closed(hwnd, element_id, closed):
    dll.EU_SetAlertClosed(hwnd, element_id, int(bool(closed)))

def trigger_alert_close(hwnd, element_id):
    dll.EU_TriggerAlertClose(hwnd, element_id)

def get_alert_full_state(hwnd, element_id):
    values = [ctypes.c_int() for _ in range(8)]
    ok = dll.EU_GetAlertFullState(
        hwnd, element_id,
        *(ctypes.byref(v) for v in values)
    )
    if not ok:
        return None
    keys = [
        "alert_type", "effect", "closable", "closed",
        "close_hover", "close_down", "close_count", "last_action",
    ]
    return {key: value.value for key, value in zip(keys, values)}

def set_alert_close_callback(hwnd, element_id, callback):
    dll.EU_SetAlertCloseCallback(hwnd, element_id, callback)

def create_result(hwnd, parent_id, title="结果", subtitle="", result_type=0,
                  x=0, y=0, w=260, h=170):
    title_data = make_utf8(title)
    subtitle_data = make_utf8(subtitle)
    return dll.EU_CreateResult(
        hwnd, parent_id,
        bytes_arg(title_data), len(title_data),
        bytes_arg(subtitle_data), len(subtitle_data),
        result_type, x, y, w, h
    )

def get_result_options(hwnd, element_id):
    result_type = ctypes.c_int()
    action_count = ctypes.c_int()
    last_action = ctypes.c_int()
    ok = dll.EU_GetResultOptions(
        hwnd, element_id,
        ctypes.byref(result_type), ctypes.byref(action_count), ctypes.byref(last_action),
    )
    return (result_type.value, action_count.value, last_action.value) if ok else None

def set_result_subtitle(hwnd, element_id, subtitle):
    data = make_utf8(subtitle)
    dll.EU_SetResultSubtitle(hwnd, element_id, bytes_arg(data), len(data))

def set_result_type(hwnd, element_id, result_type):
    dll.EU_SetResultType(hwnd, element_id, result_type)

def set_result_extra_content(hwnd, element_id, content):
    data = make_utf8(content)
    dll.EU_SetResultExtraContent(hwnd, element_id, bytes_arg(data), len(data))

def trigger_result_action(hwnd, element_id, action_index):
    dll.EU_TriggerResultAction(hwnd, element_id, action_index)

def get_result_text(hwnd, element_id, text_kind=0):
    needed = dll.EU_GetResultText(hwnd, element_id, text_kind, None, 0)
    if needed <= 0:
        return ""
    buf = (ctypes.c_ubyte * (needed + 1))()
    dll.EU_GetResultText(hwnd, element_id, text_kind, buf, needed + 1)
    return bytes(buf[:needed]).decode("utf-8", errors="replace")

def get_result_action_text(hwnd, element_id, action_index):
    needed = dll.EU_GetResultActionText(hwnd, element_id, action_index, None, 0)
    if needed <= 0:
        return ""
    buf = (ctypes.c_ubyte * (needed + 1))()
    dll.EU_GetResultActionText(hwnd, element_id, action_index, buf, needed + 1)
    return bytes(buf[:needed]).decode("utf-8", errors="replace")

def get_result_full_state(hwnd, element_id):
    values = [ctypes.c_int() for _ in range(8)]
    ok = dll.EU_GetResultFullState(
        hwnd, element_id,
        *(ctypes.byref(v) for v in values)
    )
    if not ok:
        return None
    keys = [
        "result_type", "action_count", "last_action", "hover_action",
        "press_action", "action_click_count", "last_action_source",
        "has_extra_content",
    ]
    return {key: value.value for key, value in zip(keys, values)}

def set_result_action_callback(hwnd, element_id, callback):
    dll.EU_SetResultActionCallback(hwnd, element_id, callback)

def create_notification(hwnd, parent_id, title="通知", body="",
                        notify_type=0, closable=True, x=0, y=0, w=320, h=96):
    title_data = make_utf8(title)
    body_data = make_utf8(body)
    return dll.EU_CreateNotification(
        hwnd, parent_id,
        bytes_arg(title_data), len(title_data),
        bytes_arg(body_data), len(body_data),
        notify_type, 1 if closable else 0, x, y, w, h
    )

def show_message(hwnd, text, message_type=0, closable=False, center=False,
                 rich=False, duration_ms=3000, offset=20):
    data = make_utf8(text)
    return dll.EU_ShowMessage(
        hwnd, bytes_arg(data), len(data),
        message_type, 1 if closable else 0, 1 if center else 0, 1 if rich else 0,
        duration_ms, offset
    )

def message_success(hwnd, text, **kwargs):
    return show_message(hwnd, text, message_type=1, **kwargs)

def message_warning(hwnd, text, **kwargs):
    return show_message(hwnd, text, message_type=2, **kwargs)

def message_error(hwnd, text, **kwargs):
    return show_message(hwnd, text, message_type=3, **kwargs)

def message_info(hwnd, text, **kwargs):
    return show_message(hwnd, text, message_type=0, **kwargs)

def set_message_text(hwnd, element_id, text):
    data = make_utf8(text)
    dll.EU_SetMessageText(hwnd, element_id, bytes_arg(data), len(data))

def set_message_options(hwnd, element_id, message_type=0, closable=False,
                        center=False, rich=False, duration_ms=3000, offset=20):
    dll.EU_SetMessageOptions(
        hwnd, element_id, message_type, 1 if closable else 0,
        1 if center else 0, 1 if rich else 0, duration_ms, offset
    )

def set_message_closed(hwnd, element_id, closed=True):
    dll.EU_SetMessageClosed(hwnd, element_id, 1 if closed else 0)

def get_message_options(hwnd, element_id):
    values = [ctypes.c_int() for _ in range(7)]
    ok = dll.EU_GetMessageOptions(hwnd, element_id, *(ctypes.byref(v) for v in values))
    return tuple(v.value for v in values) if ok else None

def get_message_full_state(hwnd, element_id):
    values = [ctypes.c_int() for _ in range(15)]
    ok = dll.EU_GetMessageFullState(hwnd, element_id, *(ctypes.byref(v) for v in values))
    if not ok:
        return None
    keys = [
        "message_type", "closable", "center", "rich", "duration_ms", "closed",
        "close_hover", "close_down", "close_count", "last_action",
        "timer_elapsed_ms", "timer_running", "stack_index", "stack_gap", "offset",
    ]
    return {key: value.value for key, value in zip(keys, values)}

def trigger_message_close(hwnd, element_id):
    dll.EU_TriggerMessageClose(hwnd, element_id)

def set_message_close_callback(hwnd, element_id, callback):
    dll.EU_SetMessageCloseCallback(hwnd, element_id, callback)

def _placement_value(position):
    if isinstance(position, int):
        return position
    return {
        "top-right": 0,
        "bottom-right": 1,
        "bottom-left": 2,
        "top-left": 3,
    }.get(str(position), 0)

def show_notification(hwnd, title="通知", message="", notify_type=0, closable=True,
                      duration_ms=4500, position="top-right", offset=20,
                      rich=False, w=330, h=96):
    title_data = make_utf8(title)
    body_data = make_utf8(message)
    return dll.EU_ShowNotification(
        hwnd,
        bytes_arg(title_data), len(title_data),
        bytes_arg(body_data), len(body_data),
        notify_type, 1 if closable else 0, duration_ms,
        _placement_value(position), offset, 1 if rich else 0, w, h
    )

def notify_success(hwnd, title="成功", message="", **kwargs):
    return show_notification(hwnd, title, message, notify_type=1, **kwargs)

def notify_warning(hwnd, title="警告", message="", **kwargs):
    return show_notification(hwnd, title, message, notify_type=2, **kwargs)

def notify_error(hwnd, title="错误", message="", **kwargs):
    return show_notification(hwnd, title, message, notify_type=3, **kwargs)

def notify_info(hwnd, title="消息", message="", **kwargs):
    return show_notification(hwnd, title, message, notify_type=0, **kwargs)

def get_notification_options(hwnd, element_id):
    notify_type = ctypes.c_int()
    closable = ctypes.c_int()
    duration_ms = ctypes.c_int()
    closed = ctypes.c_int()
    ok = dll.EU_GetNotificationOptions(
        hwnd, element_id,
        ctypes.byref(notify_type), ctypes.byref(closable),
        ctypes.byref(duration_ms), ctypes.byref(closed),
    )
    return (notify_type.value, bool(closable.value), duration_ms.value, bool(closed.value)) if ok else None

def set_notification_body(hwnd, element_id, body):
    data = make_utf8(body)
    dll.EU_SetNotificationBody(hwnd, element_id, bytes_arg(data), len(data))

def set_notification_type(hwnd, element_id, notify_type):
    dll.EU_SetNotificationType(hwnd, element_id, notify_type)

def set_notification_closable(hwnd, element_id, closable=True):
    dll.EU_SetNotificationClosable(hwnd, element_id, 1 if closable else 0)

def set_notification_placement(hwnd, element_id, position="top-right", offset=20):
    dll.EU_SetNotificationPlacement(hwnd, element_id, _placement_value(position), offset)

def set_notification_rich_mode(hwnd, element_id, rich=True):
    dll.EU_SetNotificationRichMode(hwnd, element_id, 1 if rich else 0)

def set_notification_options(hwnd, element_id, notify_type=0, closable=True, duration_ms=0):
    dll.EU_SetNotificationOptions(hwnd, element_id, notify_type, 1 if closable else 0, duration_ms)

def set_notification_closed(hwnd, element_id, closed=True):
    dll.EU_SetNotificationClosed(hwnd, element_id, 1 if closed else 0)

def set_notification_stack(hwnd, element_id, stack_index=0, stack_gap=12):
    dll.EU_SetNotificationStack(hwnd, element_id, stack_index, stack_gap)

def trigger_notification_close(hwnd, element_id):
    dll.EU_TriggerNotificationClose(hwnd, element_id)

def get_notification_text(hwnd, element_id, text_kind=0):
    needed = dll.EU_GetNotificationText(hwnd, element_id, text_kind, None, 0)
    if needed <= 0:
        return ""
    buf = (ctypes.c_ubyte * (needed + 1))()
    dll.EU_GetNotificationText(hwnd, element_id, text_kind, buf, needed + 1)
    return bytes(buf[:needed]).decode("utf-8", errors="replace")

def get_notification_full_state(hwnd, element_id):
    values = [ctypes.c_int() for _ in range(12)]
    ok = dll.EU_GetNotificationFullState(
        hwnd, element_id,
        *(ctypes.byref(v) for v in values)
    )
    if not ok:
        return None
    keys = [
        "notify_type", "closable", "duration_ms", "closed",
        "close_hover", "close_down", "close_count", "last_action",
        "timer_elapsed_ms", "timer_running", "stack_index", "stack_gap",
    ]
    return {key: value.value for key, value in zip(keys, values)}

def get_notification_full_state_ex(hwnd, element_id):
    values = [ctypes.c_int() for _ in range(15)]
    ok = dll.EU_GetNotificationFullStateEx(
        hwnd, element_id,
        *(ctypes.byref(v) for v in values)
    )
    if not ok:
        return None
    keys = [
        "notify_type", "closable", "duration_ms", "closed",
        "close_hover", "close_down", "close_count", "last_action",
        "timer_elapsed_ms", "timer_running", "stack_index", "stack_gap",
        "placement", "offset", "rich",
    ]
    return {key: value.value for key, value in zip(keys, values)}

def set_notification_close_callback(hwnd, element_id, callback):
    dll.EU_SetNotificationCloseCallback(hwnd, element_id, callback)

def create_loading(hwnd, parent_id, text="加载中", active=True,
                   x=0, y=0, w=220, h=130):
    text_data = make_utf8(text)
    return dll.EU_CreateLoading(
        hwnd, parent_id,
        bytes_arg(text_data), len(text_data),
        1 if active else 0, x, y, w, h
    )

def _loading_spinner_type(spinner):
    if isinstance(spinner, str):
        key = spinner.strip().lower()
        return {
            "dots": 0,
            "dot": 0,
            "default": 0,
            "el-icon-loading": 1,
            "arc": 1,
            "circle": 1,
            "pulse": 2,
            "pulse-dots": 2,
        }.get(key, 0)
    try:
        value = int(spinner)
    except Exception:
        return 0
    return max(0, min(2, value))

def set_loading_text(hwnd, element_id, text="加载中"):
    data = make_utf8(text)
    dll.EU_SetLoadingText(hwnd, element_id, bytes_arg(data), len(data))

def set_loading_options(hwnd, element_id, active=True, fullscreen=False, progress=-1):
    dll.EU_SetLoadingOptions(hwnd, element_id, 1 if active else 0, 1 if fullscreen else 0, progress)

def set_loading_style(hwnd, element_id, background=0, spinner_color=0, text_color=0,
                      spinner="dots", lock_input=False):
    dll.EU_SetLoadingStyle(
        hwnd, element_id,
        background, spinner_color, text_color,
        _loading_spinner_type(spinner), 1 if lock_input else 0,
    )

def get_loading_options(hwnd, element_id):
    active = ctypes.c_int()
    fullscreen = ctypes.c_int()
    progress = ctypes.c_int()
    ok = dll.EU_GetLoadingOptions(
        hwnd, element_id,
        ctypes.byref(active), ctypes.byref(fullscreen), ctypes.byref(progress),
    )
    return (bool(active.value), bool(fullscreen.value), progress.value) if ok else None

def set_loading_target(hwnd, element_id, target_element_id=0, padding=0):
    dll.EU_SetLoadingTarget(hwnd, element_id, target_element_id, padding)

def get_loading_text(hwnd, element_id):
    needed = dll.EU_GetLoadingText(hwnd, element_id, None, 0)
    if needed <= 0:
        return ""
    buf = (ctypes.c_ubyte * (needed + 1))()
    dll.EU_GetLoadingText(hwnd, element_id, buf, needed + 1)
    return bytes(buf[:needed]).decode("utf-8", errors="replace")

def get_loading_style(hwnd, element_id):
    background = ctypes.c_uint32()
    spinner_color = ctypes.c_uint32()
    text_color = ctypes.c_uint32()
    spinner_type = ctypes.c_int()
    lock_input = ctypes.c_int()
    ok = dll.EU_GetLoadingStyle(
        hwnd, element_id,
        ctypes.byref(background), ctypes.byref(spinner_color),
        ctypes.byref(text_color), ctypes.byref(spinner_type),
        ctypes.byref(lock_input),
    )
    if not ok:
        return None
    return {
        "background": background.value,
        "spinner_color": spinner_color.value,
        "text_color": text_color.value,
        "spinner_type": spinner_type.value,
        "lock_input": bool(lock_input.value),
    }

def show_loading(hwnd, target_element_id=0, text="加载中", fullscreen=False,
                 lock_input=False, background=0, spinner_color=0, text_color=0,
                 spinner="dots"):
    data = make_utf8(text)
    return dll.EU_ShowLoading(
        hwnd, target_element_id,
        bytes_arg(data), len(data),
        1 if fullscreen else 0, 1 if lock_input else 0,
        background, spinner_color, text_color,
        _loading_spinner_type(spinner),
    )

def close_loading(hwnd, element_id):
    return bool(dll.EU_CloseLoading(hwnd, element_id))

def get_loading_full_state(hwnd, element_id):
    values = [ctypes.c_int() for _ in range(9)]
    ok = dll.EU_GetLoadingFullState(
        hwnd, element_id,
        *(ctypes.byref(v) for v in values)
    )
    if not ok:
        return None
    keys = [
        "active", "fullscreen", "progress", "target_element_id",
        "target_padding", "animation_angle", "tick_count",
        "timer_running", "last_action",
    ]
    return {key: value.value for key, value in zip(keys, values)}

def set_result_actions(hwnd, element_id, actions):
    data = make_utf8("|".join(actions))
    dll.EU_SetResultActions(hwnd, element_id, bytes_arg(data), len(data))

def create_dialog(hwnd, title="对话框", body="", modal=True, closable=True,
                  w=460, h=250):
    title_data = make_utf8(title)
    body_data = make_utf8(body)
    return dll.EU_CreateDialog(
        hwnd,
        bytes_arg(title_data), len(title_data),
        bytes_arg(body_data), len(body_data),
        1 if modal else 0, 1 if closable else 0,
        w, h
    )

def set_dialog_title(hwnd, element_id, title=""):
    data = make_utf8(title)
    dll.EU_SetDialogTitle(hwnd, element_id, bytes_arg(data), len(data))

def set_dialog_body(hwnd, element_id, body=""):
    data = make_utf8(body)
    dll.EU_SetDialogBody(hwnd, element_id, bytes_arg(data), len(data))

def set_dialog_options(hwnd, element_id, open=True, modal=True, closable=True,
                       close_on_mask=False, draggable=True, w=460, h=250):
    dll.EU_SetDialogOptions(
        hwnd, element_id,
        1 if open else 0, 1 if modal else 0, 1 if closable else 0,
        1 if close_on_mask else 0, 1 if draggable else 0,
        w, h
    )

def set_dialog_advanced_options(hwnd, element_id, width_mode=0, width_value=460,
                                center=False, footer_center=False,
                                content_padding=20, footer_height=58):
    dll.EU_SetDialogAdvancedOptions(
        hwnd, element_id,
        width_mode, width_value,
        1 if center else 0, 1 if footer_center else 0,
        content_padding, footer_height,
    )

def get_dialog_advanced_options(hwnd, element_id):
    values = [ctypes.c_int() for _ in range(9)]
    ok = dll.EU_GetDialogAdvancedOptions(
        hwnd, element_id,
        *(ctypes.byref(value) for value in values)
    )
    if not ok:
        return None
    keys = [
        "width_mode", "width_value", "center", "footer_center",
        "content_padding", "footer_height", "content_parent_id",
        "footer_parent_id", "close_pending",
    ]
    state = {key: value.value for key, value in zip(keys, values)}
    for key in ("center", "footer_center", "close_pending"):
        state[key] = bool(state[key])
    return state

def get_dialog_content_parent(hwnd, element_id):
    return dll.EU_GetDialogContentParent(hwnd, element_id)

def get_dialog_footer_parent(hwnd, element_id):
    return dll.EU_GetDialogFooterParent(hwnd, element_id)

def set_dialog_before_close_callback(hwnd, element_id, callback):
    dll.EU_SetDialogBeforeCloseCallback(hwnd, element_id, callback)

def confirm_dialog_close(hwnd, element_id, allow=True):
    dll.EU_ConfirmDialogClose(hwnd, element_id, 1 if allow else 0)

def get_dialog_options(hwnd, element_id):
    open_value = ctypes.c_int()
    modal = ctypes.c_int()
    closable = ctypes.c_int()
    close_on_mask = ctypes.c_int()
    draggable = ctypes.c_int()
    width = ctypes.c_int()
    height = ctypes.c_int()
    ok = dll.EU_GetDialogOptions(
        hwnd, element_id,
        ctypes.byref(open_value), ctypes.byref(modal), ctypes.byref(closable),
        ctypes.byref(close_on_mask), ctypes.byref(draggable),
        ctypes.byref(width), ctypes.byref(height),
    )
    return (
        bool(open_value.value), bool(modal.value), bool(closable.value),
        bool(close_on_mask.value), bool(draggable.value), width.value, height.value,
    ) if ok else None

def set_dialog_buttons(hwnd, element_id, buttons):
    data = make_utf8("|".join(buttons))
    dll.EU_SetDialogButtons(hwnd, element_id, bytes_arg(data), len(data))

def trigger_dialog_button(hwnd, element_id, button_index):
    dll.EU_TriggerDialogButton(hwnd, element_id, button_index)

def get_dialog_text(hwnd, element_id, text_kind=0):
    needed = dll.EU_GetDialogText(hwnd, element_id, text_kind, None, 0)
    if needed <= 0:
        return ""
    buf = (ctypes.c_ubyte * (needed + 1))()
    dll.EU_GetDialogText(hwnd, element_id, text_kind, buf, needed + 1)
    return bytes(buf[:needed]).decode("utf-8", errors="replace")

def get_dialog_button_text(hwnd, element_id, button_index):
    needed = dll.EU_GetDialogButtonText(hwnd, element_id, button_index, None, 0)
    if needed <= 0:
        return ""
    buf = (ctypes.c_ubyte * (needed + 1))()
    dll.EU_GetDialogButtonText(hwnd, element_id, button_index, buf, needed + 1)
    return bytes(buf[:needed]).decode("utf-8", errors="replace")

def get_dialog_full_state(hwnd, element_id):
    values = [ctypes.c_int() for _ in range(17)]
    ok = dll.EU_GetDialogFullState(
        hwnd, element_id,
        *(ctypes.byref(v) for v in values)
    )
    if not ok:
        return None
    keys = [
        "open", "modal", "closable", "close_on_mask", "draggable",
        "width", "height", "button_count", "active_button", "last_button",
        "button_click_count", "close_count", "last_action", "offset_x",
        "offset_y", "hover_part", "press_part",
    ]
    return {key: value.value for key, value in zip(keys, values)}

def set_dialog_button_callback(hwnd, element_id, callback):
    dll.EU_SetDialogButtonCallback(hwnd, element_id, callback)

def create_drawer(hwnd, title="Drawer", body="", placement=1,
                  modal=True, closable=True, size=300):
    title_data = make_utf8(title)
    body_data = make_utf8(body)
    return dll.EU_CreateDrawer(
        hwnd,
        bytes_arg(title_data), len(title_data),
        bytes_arg(body_data), len(body_data),
        placement, 1 if modal else 0, 1 if closable else 0,
        size
    )

def set_drawer_title(hwnd, element_id, title=""):
    data = make_utf8(title)
    dll.EU_SetDrawerTitle(hwnd, element_id, bytes_arg(data), len(data))

def set_drawer_body(hwnd, element_id, body=""):
    data = make_utf8(body)
    dll.EU_SetDrawerBody(hwnd, element_id, bytes_arg(data), len(data))

def set_drawer_options(hwnd, element_id, placement=1, open=True,
                       modal=True, closable=True, close_on_mask=False, size=300):
    dll.EU_SetDrawerOptions(
        hwnd, element_id,
        placement, 1 if open else 0,
        1 if modal else 0, 1 if closable else 0,
        1 if close_on_mask else 0, size
    )

def set_drawer_advanced_options(hwnd, element_id, show_header=True, show_close=True,
                                close_on_escape=True, content_padding=20,
                                footer_height=58, size_mode=0, size_value=0):
    dll.EU_SetDrawerAdvancedOptions(
        hwnd, element_id,
        1 if show_header else 0,
        1 if show_close else 0,
        1 if close_on_escape else 0,
        content_padding,
        footer_height,
        size_mode,
        size_value,
    )

def get_drawer_advanced_options(hwnd, element_id):
    values = [ctypes.c_int() for _ in range(10)]
    ok = dll.EU_GetDrawerAdvancedOptions(
        hwnd, element_id,
        *(ctypes.byref(value) for value in values)
    )
    if not ok:
        return None
    keys = [
        "show_header", "show_close", "close_on_escape", "content_padding",
        "footer_height", "size_mode", "size_value", "content_parent_id",
        "footer_parent_id", "close_pending",
    ]
    state = {key: value.value for key, value in zip(keys, values)}
    for key in ("show_header", "show_close", "close_on_escape", "close_pending"):
        state[key] = bool(state[key])
    return state

def get_drawer_content_parent(hwnd, element_id):
    return dll.EU_GetDrawerContentParent(hwnd, element_id)

def get_drawer_footer_parent(hwnd, element_id):
    return dll.EU_GetDrawerFooterParent(hwnd, element_id)

def set_drawer_before_close_callback(hwnd, element_id, callback):
    dll.EU_SetDrawerBeforeCloseCallback(hwnd, element_id, callback)

def confirm_drawer_close(hwnd, element_id, allow=True):
    dll.EU_ConfirmDrawerClose(hwnd, element_id, 1 if allow else 0)

def get_drawer_options(hwnd, element_id):
    placement = ctypes.c_int()
    open_value = ctypes.c_int()
    modal = ctypes.c_int()
    closable = ctypes.c_int()
    close_on_mask = ctypes.c_int()
    size = ctypes.c_int()
    ok = dll.EU_GetDrawerOptions(
        hwnd, element_id,
        ctypes.byref(placement), ctypes.byref(open_value),
        ctypes.byref(modal), ctypes.byref(closable),
        ctypes.byref(close_on_mask), ctypes.byref(size),
    )
    return (
        placement.value, bool(open_value.value), bool(modal.value),
        bool(closable.value), bool(close_on_mask.value), size.value,
    ) if ok else None

def set_drawer_open(hwnd, element_id, open=True):
    dll.EU_SetDrawerOpen(hwnd, element_id, 1 if open else 0)

def set_drawer_animation(hwnd, element_id, duration_ms=180):
    dll.EU_SetDrawerAnimation(hwnd, element_id, duration_ms)

def trigger_drawer_close(hwnd, element_id):
    dll.EU_TriggerDrawerClose(hwnd, element_id)

def get_drawer_text(hwnd, element_id, text_kind=0, buffer_size=2048):
    buf = (ctypes.c_ubyte * buffer_size)()
    written = dll.EU_GetDrawerText(hwnd, element_id, text_kind, buf, buffer_size)
    if written <= 0:
        return ""
    return bytes(buf[:written]).decode("utf-8", errors="replace")

def get_drawer_full_state(hwnd, element_id):
    values = [ctypes.c_int() for _ in range(14)]
    ok = dll.EU_GetDrawerFullState(
        hwnd, element_id,
        *[ctypes.byref(value) for value in values],
    )
    if not ok:
        return None
    keys = [
        "placement", "open", "modal", "closable", "close_on_mask", "size",
        "animation_progress", "animation_ms", "tick_count", "timer_running",
        "close_count", "last_action", "hover_part", "press_part",
    ]
    state = {key: value.value for key, value in zip(keys, values)}
    for key in ("open", "modal", "closable", "close_on_mask", "timer_running"):
        state[key] = bool(state[key])
    return state

def set_drawer_close_callback(hwnd, element_id, callback):
    dll.EU_SetDrawerCloseCallback(hwnd, element_id, callback)

def create_tooltip(hwnd, parent_id, label="文字提示", content="", placement=2,
                   x=0, y=0, w=140, h=36):
    label_data = make_utf8(label)
    content_data = make_utf8(content)
    return dll.EU_CreateTooltip(
        hwnd, parent_id,
        bytes_arg(label_data), len(label_data),
        bytes_arg(content_data), len(content_data),
        placement, x, y, w, h
    )

def set_tooltip_content(hwnd, element_id, content=""):
    data = make_utf8(content)
    dll.EU_SetTooltipContent(hwnd, element_id, bytes_arg(data), len(data))

def set_tooltip_options(hwnd, element_id, placement=2, open=False, max_width=280):
    dll.EU_SetTooltipOptions(hwnd, element_id, placement, 1 if open else 0, max_width)

def get_tooltip_options(hwnd, element_id):
    placement = ctypes.c_int()
    open_value = ctypes.c_int()
    max_width = ctypes.c_int()
    ok = dll.EU_GetTooltipOptions(
        hwnd, element_id,
        ctypes.byref(placement), ctypes.byref(open_value), ctypes.byref(max_width),
    )
    return (placement.value, bool(open_value.value), max_width.value) if ok else None

def set_tooltip_open(hwnd, element_id, open=True):
    dll.EU_SetTooltipOpen(hwnd, element_id, 1 if open else 0)

def set_tooltip_behavior(hwnd, element_id, show_delay=220, hide_delay=120,
                         trigger_mode=0, show_arrow=True):
    dll.EU_SetTooltipBehavior(
        hwnd, element_id, show_delay, hide_delay,
        _trigger_mode_value(trigger_mode), 1 if show_arrow else 0,
    )

def set_tooltip_advanced_options(hwnd, element_id, placement="top", effect="dark",
                                 disabled=False, show_arrow=True, offset=8,
                                 max_width=280):
    effect_value = 1 if effect == "light" else int(effect) if isinstance(effect, int) else 0
    dll.EU_SetTooltipAdvancedOptions(
        hwnd, element_id,
        _extended_placement_value(placement, "top"),
        effect_value,
        1 if disabled else 0,
        1 if show_arrow else 0,
        offset,
        max_width,
    )

def get_tooltip_advanced_options(hwnd, element_id):
    values = [ctypes.c_int() for _ in range(6)]
    ok = dll.EU_GetTooltipAdvancedOptions(
        hwnd, element_id,
        *(ctypes.byref(value) for value in values)
    )
    if not ok:
        return None
    keys = ["placement", "effect", "disabled", "show_arrow", "offset", "max_width"]
    state = {key: value.value for key, value in zip(keys, values)}
    for key in ("disabled", "show_arrow"):
        state[key] = bool(state[key])
    return state

def trigger_tooltip(hwnd, element_id, open=True):
    dll.EU_TriggerTooltip(hwnd, element_id, 1 if open else 0)

def get_tooltip_text(hwnd, element_id, text_kind=0, buffer_size=2048):
    buf = (ctypes.c_ubyte * buffer_size)()
    written = dll.EU_GetTooltipText(hwnd, element_id, text_kind, buf, buffer_size)
    if written <= 0:
        return ""
    return bytes(buf[:written]).decode("utf-8", errors="replace")

def get_tooltip_full_state(hwnd, element_id):
    values = [ctypes.c_int() for _ in range(16)]
    ok = dll.EU_GetTooltipFullState(
        hwnd, element_id,
        *[ctypes.byref(value) for value in values],
    )
    if not ok:
        return None
    keys = [
        "placement", "open", "max_width", "show_arrow", "show_delay",
        "hide_delay", "trigger_mode", "timer_running", "timer_phase",
        "open_count", "close_count", "last_action",
        "popup_x", "popup_y", "popup_w", "popup_h",
    ]
    state = {key: value.value for key, value in zip(keys, values)}
    for key in ("open", "show_arrow", "timer_running"):
        state[key] = bool(state[key])
    return state

def create_popover(hwnd, parent_id, label="弹出框", title="弹出框",
                   content="", placement=3, x=0, y=0, w=140, h=36):
    label_data = make_utf8(label)
    title_data = make_utf8(title)
    content_data = make_utf8(content)
    return dll.EU_CreatePopover(
        hwnd, parent_id,
        bytes_arg(label_data), len(label_data),
        bytes_arg(title_data), len(title_data),
        bytes_arg(content_data), len(content_data),
        placement, x, y, w, h
    )

def set_popover_title(hwnd, element_id, title=""):
    data = make_utf8(title)
    dll.EU_SetPopoverTitle(hwnd, element_id, bytes_arg(data), len(data))

def set_popover_content(hwnd, element_id, content=""):
    data = make_utf8(content)
    dll.EU_SetPopoverContent(hwnd, element_id, bytes_arg(data), len(data))

def set_popover_options(hwnd, element_id, placement=3, open=False,
                        popup_width=250, popup_height=132, closable=True):
    dll.EU_SetPopoverOptions(
        hwnd, element_id, placement, 1 if open else 0,
        popup_width, popup_height, 1 if closable else 0
    )

def set_popover_advanced_options(hwnd, element_id, placement="bottom", open=False,
                                 popup_width=250, popup_height=132,
                                 closable=True):
    dll.EU_SetPopoverAdvancedOptions(
        hwnd, element_id,
        _extended_placement_value(placement, "bottom"),
        1 if open else 0,
        popup_width, popup_height,
        1 if closable else 0,
    )

def set_popover_behavior(hwnd, element_id, trigger_mode="click",
                         close_on_outside=True, show_arrow=True, offset=8):
    dll.EU_SetPopoverBehavior(
        hwnd, element_id,
        _trigger_mode_value(trigger_mode),
        1 if close_on_outside else 0,
        1 if show_arrow else 0,
        offset,
    )

def get_popover_behavior(hwnd, element_id):
    values = [ctypes.c_int() for _ in range(4)]
    ok = dll.EU_GetPopoverBehavior(
        hwnd, element_id,
        *(ctypes.byref(value) for value in values)
    )
    if not ok:
        return None
    keys = ["trigger_mode", "close_on_outside", "show_arrow", "offset"]
    state = {key: value.value for key, value in zip(keys, values)}
    for key in ("close_on_outside", "show_arrow"):
        state[key] = bool(state[key])
    return state

def get_popover_content_parent(hwnd, element_id):
    return dll.EU_GetPopoverContentParent(hwnd, element_id)

def get_popover_options(hwnd, element_id):
    placement = ctypes.c_int()
    open_value = ctypes.c_int()
    popup_width = ctypes.c_int()
    popup_height = ctypes.c_int()
    closable = ctypes.c_int()
    ok = dll.EU_GetPopoverOptions(
        hwnd, element_id,
        ctypes.byref(placement), ctypes.byref(open_value),
        ctypes.byref(popup_width), ctypes.byref(popup_height), ctypes.byref(closable),
    )
    return (
        placement.value, bool(open_value.value),
        popup_width.value, popup_height.value, bool(closable.value),
    ) if ok else None

def set_popover_open(hwnd, element_id, open=True):
    dll.EU_SetPopoverOpen(hwnd, element_id, 1 if open else 0)

def trigger_popover(hwnd, element_id, open=True):
    dll.EU_TriggerPopover(hwnd, element_id, 1 if open else 0)

def get_popover_text(hwnd, element_id, text_kind=0, buffer_size=2048):
    buf = (ctypes.c_ubyte * buffer_size)()
    written = dll.EU_GetPopoverText(hwnd, element_id, text_kind, buf, buffer_size)
    if written <= 0:
        return ""
    return bytes(buf[:written]).decode("utf-8", errors="replace")

def get_popover_full_state(hwnd, element_id):
    values = [ctypes.c_int() for _ in range(14)]
    ok = dll.EU_GetPopoverFullState(
        hwnd, element_id,
        *[ctypes.byref(value) for value in values],
    )
    if not ok:
        return None
    keys = [
        "placement", "open", "popup_width", "popup_height", "closable",
        "open_count", "close_count", "last_action", "focus_part",
        "close_hover", "popup_x", "popup_y", "popup_w", "popup_h",
    ]
    state = {key: value.value for key, value in zip(keys, values)}
    for key in ("open", "closable", "close_hover"):
        state[key] = bool(state[key])
    return state

def set_popover_action_callback(hwnd, element_id, callback):
    dll.EU_SetPopoverActionCallback(hwnd, element_id, callback)

def set_popover_anchor_element(hwnd, element_id, anchor_element_id):
    dll.EU_SetPopoverAnchorElement(hwnd, element_id, anchor_element_id)

def set_popover_arrow(hwnd, element_id, visible=True, size=10):
    dll.EU_SetPopoverArrow(hwnd, element_id, 1 if visible else 0, size)

def set_popover_elevation(hwnd, element_id, level=2):
    dll.EU_SetPopoverElevation(hwnd, element_id, level)

def set_popover_auto_placement(hwnd, element_id, enabled=True):
    dll.EU_SetPopoverAutoPlacement(hwnd, element_id, 1 if enabled else 0)

def set_popover_dismiss_behavior(hwnd, element_id, close_on_outside=True, close_on_escape=True):
    dll.EU_SetPopoverDismissBehavior(hwnd, element_id, 1 if close_on_outside else 0, 1 if close_on_escape else 0)

def set_popup_anchor_element(hwnd, popup_id, anchor_element_id):
    dll.EU_SetPopupAnchorElement(hwnd, popup_id, anchor_element_id)

def set_popup_placement(hwnd, popup_id, placement=4, offset_x=0, offset_y=0):
    dll.EU_SetPopupPlacement(hwnd, popup_id, placement, offset_x, offset_y)

def set_popup_open(hwnd, popup_id, open=True):
    dll.EU_SetPopupOpen(hwnd, popup_id, 1 if open else 0)

def get_popup_open(hwnd, popup_id):
    return bool(dll.EU_GetPopupOpen(hwnd, popup_id))

def set_popup_dismiss_behavior(hwnd, popup_id, close_on_outside=True, close_on_escape=True):
    dll.EU_SetPopupDismissBehavior(hwnd, popup_id, 1 if close_on_outside else 0, 1 if close_on_escape else 0)

def _popup_trigger_value(trigger):
    if isinstance(trigger, str):
        return {
            "click": 0,
            "left": 0,
            "left_click": 0,
            "right": 1,
            "right_click": 1,
            "context": 1,
            "hover": 2,
            "focus": 3,
            "manual": 4,
        }.get(trigger, 0)
    try:
        value = int(trigger)
    except (TypeError, ValueError):
        value = 0
    return max(0, min(4, value))

def set_element_popup(hwnd, element_id, popup_id, trigger="click"):
    dll.EU_SetElementPopup(hwnd, element_id, popup_id, _popup_trigger_value(trigger))

def clear_element_popup(hwnd, element_id, trigger="click"):
    dll.EU_ClearElementPopup(hwnd, element_id, _popup_trigger_value(trigger))

def get_element_popup(hwnd, element_id, trigger="click"):
    return dll.EU_GetElementPopup(hwnd, element_id, _popup_trigger_value(trigger))

def create_popconfirm(hwnd, parent_id, label="气泡确认", title="确认操作",
                      content="", confirm="确定", cancel="取消", placement=3,
                      x=0, y=0, w=150, h=36):
    label_data = make_utf8(label)
    title_data = make_utf8(title)
    content_data = make_utf8(content)
    confirm_data = make_utf8(confirm)
    cancel_data = make_utf8(cancel)
    return dll.EU_CreatePopconfirm(
        hwnd, parent_id,
        bytes_arg(label_data), len(label_data),
        bytes_arg(title_data), len(title_data),
        bytes_arg(content_data), len(content_data),
        bytes_arg(confirm_data), len(confirm_data),
        bytes_arg(cancel_data), len(cancel_data),
        placement, x, y, w, h
    )

def set_popconfirm_content(hwnd, element_id, title="", content=""):
    title_data = make_utf8(title)
    content_data = make_utf8(content)
    dll.EU_SetPopconfirmContent(
        hwnd, element_id,
        bytes_arg(title_data), len(title_data),
        bytes_arg(content_data), len(content_data)
    )

def set_popconfirm_options(hwnd, element_id, placement=3, open=False,
                           popup_width=286, popup_height=146):
    dll.EU_SetPopconfirmOptions(
        hwnd, element_id, placement, 1 if open else 0, popup_width, popup_height
    )

def set_popconfirm_advanced_options(hwnd, element_id, placement="top", open=False,
                                    popup_width=286, popup_height=146,
                                    trigger_mode="click",
                                    close_on_outside=True, show_arrow=True,
                                    offset=8):
    dll.EU_SetPopconfirmAdvancedOptions(
        hwnd, element_id,
        _extended_placement_value(placement, "top"),
        1 if open else 0,
        popup_width, popup_height,
        _trigger_mode_value(trigger_mode),
        1 if close_on_outside else 0,
        1 if show_arrow else 0,
        offset,
    )

def get_popconfirm_options(hwnd, element_id):
    placement = ctypes.c_int()
    open_value = ctypes.c_int()
    popup_width = ctypes.c_int()
    popup_height = ctypes.c_int()
    result = ctypes.c_int()
    ok = dll.EU_GetPopconfirmOptions(
        hwnd, element_id,
        ctypes.byref(placement), ctypes.byref(open_value),
        ctypes.byref(popup_width), ctypes.byref(popup_height), ctypes.byref(result),
    )
    return (
        placement.value, bool(open_value.value),
        popup_width.value, popup_height.value, result.value,
    ) if ok else None

def set_popconfirm_open(hwnd, element_id, open=True):
    dll.EU_SetPopconfirmOpen(hwnd, element_id, 1 if open else 0)

def set_popconfirm_buttons(hwnd, element_id, confirm="确定 ✅", cancel="取消 ❌"):
    confirm_data = make_utf8(confirm)
    cancel_data = make_utf8(cancel)
    dll.EU_SetPopconfirmButtons(
        hwnd, element_id,
        bytes_arg(confirm_data), len(confirm_data),
        bytes_arg(cancel_data), len(cancel_data)
    )

def set_popconfirm_icon(hwnd, element_id, icon="!", color=0xFFE6A23C, visible=True):
    data = make_utf8(icon)
    dll.EU_SetPopconfirmIcon(
        hwnd, element_id,
        bytes_arg(data), len(data),
        color,
        1 if visible else 0,
    )

def get_popconfirm_icon(hwnd, element_id):
    needed = dll.EU_GetPopconfirmIcon(hwnd, element_id, None, 0, None, None)
    if needed <= 0:
        icon = ""
    else:
        buf = (ctypes.c_ubyte * (needed + 1))()
        color = ctypes.c_uint32()
        visible = ctypes.c_int()
        dll.EU_GetPopconfirmIcon(
            hwnd, element_id, buf, needed + 1,
            ctypes.byref(color), ctypes.byref(visible),
        )
        return {
            "icon": bytes(buf[:needed]).decode("utf-8", errors="replace"),
            "color": color.value,
            "visible": bool(visible.value),
        }
    color = ctypes.c_uint32()
    visible = ctypes.c_int()
    dll.EU_GetPopconfirmIcon(hwnd, element_id, None, 0,
                             ctypes.byref(color), ctypes.byref(visible))
    return {"icon": icon, "color": color.value, "visible": bool(visible.value)}

def trigger_popconfirm_result(hwnd, element_id, result=True):
    dll.EU_TriggerPopconfirmResult(hwnd, element_id, 1 if result else 0)

def get_popconfirm_text(hwnd, element_id, text_kind=0, buffer_size=2048):
    buf = (ctypes.c_ubyte * buffer_size)()
    written = dll.EU_GetPopconfirmText(hwnd, element_id, text_kind, buf, buffer_size)
    if written <= 0:
        return ""
    return bytes(buf[:written]).decode("utf-8", errors="replace")

def get_popconfirm_full_state(hwnd, element_id):
    values = [ctypes.c_int() for _ in range(15)]
    ok = dll.EU_GetPopconfirmFullState(
        hwnd, element_id,
        *[ctypes.byref(value) for value in values],
    )
    if not ok:
        return None
    keys = [
        "placement", "open", "popup_width", "popup_height", "result",
        "confirm_count", "cancel_count", "result_action", "focus_part",
        "hover_button", "press_button", "popup_x", "popup_y", "popup_w", "popup_h",
    ]
    state = {key: value.value for key, value in zip(keys, values)}
    state["open"] = bool(state["open"])
    return state

def set_popconfirm_result_callback(hwnd, element_id, callback):
    dll.EU_SetPopconfirmResultCallback(hwnd, element_id, callback)

def show_messagebox(hwnd, title="鎻愮ず", text="", confirm="纭畾"):
    title_data = make_utf8(title)
    text_data = make_utf8(text)
    confirm_data = make_utf8(confirm)
    return dll.EU_ShowMessageBox(
        hwnd,
        (ctypes.c_ubyte * len(title_data))(*title_data), len(title_data),
        (ctypes.c_ubyte * len(text_data))(*text_data), len(text_data),
        (ctypes.c_ubyte * len(confirm_data))(*confirm_data), len(confirm_data),
        on_messagebox_result
    )

def show_confirmbox(hwnd, title="纭", text="", confirm="纭畾", cancel="鍙栨秷"):
    title_data = make_utf8(title)
    text_data = make_utf8(text)
    confirm_data = make_utf8(confirm)
    cancel_data = make_utf8(cancel)
    return dll.EU_ShowConfirmBox(
        hwnd,
        (ctypes.c_ubyte * len(title_data))(*title_data), len(title_data),
        (ctypes.c_ubyte * len(text_data))(*text_data), len(text_data),
        (ctypes.c_ubyte * len(confirm_data))(*confirm_data), len(confirm_data),
        (ctypes.c_ubyte * len(cancel_data))(*cancel_data), len(cancel_data),
        on_messagebox_result
    )

# 鈹€鈹€ Callbacks 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

def show_alert_box(hwnd, title="提示", text="", confirm="确定",
                   box_type=0, center=False, rich=False, callback=None):
    return show_msgbox(hwnd, title, text, confirm, "", box_type,
                       False, center, rich, False, callback)

def show_confirm_box(hwnd, title="提示", text="", confirm="确定", cancel="取消",
                     box_type=0, center=False, rich=False,
                     distinguish_cancel_and_close=False, callback=None):
    return show_msgbox(hwnd, title, text, confirm, cancel, box_type,
                       True, center, rich, distinguish_cancel_and_close, callback)

def show_msgbox(hwnd, title="消息", text="", confirm="确定", cancel="取消",
                box_type=0, show_cancel=True, center=False, rich=False,
                distinguish_cancel_and_close=False, callback=None):
    title_data = make_utf8(title)
    text_data = make_utf8(text)
    confirm_data = make_utf8(confirm)
    cancel_data = make_utf8(cancel)
    cb = callback or on_messagebox_ex_result
    return dll.EU_ShowMessageBoxEx(
        hwnd,
        bytes_arg(title_data), len(title_data),
        bytes_arg(text_data), len(text_data),
        bytes_arg(confirm_data), len(confirm_data),
        bytes_arg(cancel_data), len(cancel_data),
        box_type, 1 if show_cancel else 0, 1 if center else 0, 1 if rich else 0,
        1 if distinguish_cancel_and_close else 0,
        cb
    )

def show_prompt_box(hwnd, title="提示", text="", placeholder="请输入内容", value="",
                    pattern="", error="输入内容格式不正确",
                    confirm="确定", cancel="取消", box_type=0, center=False,
                    rich=False, distinguish_cancel_and_close=False, callback=None):
    title_data = make_utf8(title)
    text_data = make_utf8(text)
    placeholder_data = make_utf8(placeholder)
    value_data = make_utf8(value)
    pattern_data = make_utf8(pattern)
    error_data = make_utf8(error)
    confirm_data = make_utf8(confirm)
    cancel_data = make_utf8(cancel)
    cb = callback or on_messagebox_ex_result
    return dll.EU_ShowPromptBox(
        hwnd,
        bytes_arg(title_data), len(title_data),
        bytes_arg(text_data), len(text_data),
        bytes_arg(placeholder_data), len(placeholder_data),
        bytes_arg(value_data), len(value_data),
        bytes_arg(pattern_data), len(pattern_data),
        bytes_arg(error_data), len(error_data),
        bytes_arg(confirm_data), len(confirm_data),
        bytes_arg(cancel_data), len(cancel_data),
        box_type, 1 if center else 0, 1 if rich else 0,
        1 if distinguish_cancel_and_close else 0,
        cb
    )

def set_messagebox_before_close(hwnd, element_id, delay_ms=0, loading_text="执行中..."):
    data = make_utf8(loading_text)
    dll.EU_SetMessageBoxBeforeClose(hwnd, element_id, delay_ms, bytes_arg(data), len(data))

def set_messagebox_input(hwnd, element_id, value="", placeholder="", pattern="", error=""):
    value_data = make_utf8(value)
    placeholder_data = make_utf8(placeholder)
    pattern_data = make_utf8(pattern)
    error_data = make_utf8(error)
    dll.EU_SetMessageBoxInput(
        hwnd, element_id,
        bytes_arg(value_data), len(value_data),
        bytes_arg(placeholder_data), len(placeholder_data),
        bytes_arg(pattern_data), len(pattern_data),
        bytes_arg(error_data), len(error_data),
    )

def get_messagebox_input(hwnd, element_id):
    needed = dll.EU_GetMessageBoxInput(hwnd, element_id, None, 0)
    if needed <= 0:
        return ""
    buf = (ctypes.c_ubyte * (needed + 1))()
    dll.EU_GetMessageBoxInput(hwnd, element_id, buf, needed + 1)
    return bytes(buf[:needed]).decode("utf-8", errors="replace")

def get_messagebox_full_state(hwnd, element_id):
    values = [ctypes.c_int() for _ in range(10)]
    ok = dll.EU_GetMessageBoxFullState(hwnd, element_id, *(ctypes.byref(v) for v in values))
    if not ok:
        return None
    keys = [
        "box_type", "show_cancel", "center", "rich", "distinguish",
        "prompt", "confirm_loading", "input_error_visible",
        "last_action", "timer_elapsed_ms",
    ]
    return {key: value.value for key, value in zip(keys, values)}

g_hwnd = None
g_message_button_id = 0
g_confirm_button_id = 0
g_light_theme_button_id = 0
g_dark_theme_button_id = 0
g_system_theme_button_id = 0
g_link_id = 0
g_checkbox_id = 0
g_radio_a_id = 0
g_radio_b_id = 0
g_switch_id = 0
g_slider_id = 0
g_input_number_id = 0
g_select_id = 0
g_rate_id = 0
g_colorpicker_id = 0
g_tag_id = 0
g_badge_id = 0
g_progress_id = 0
g_avatar_id = 0
g_empty_id = 0
g_skeleton_id = 0
g_descriptions_id = 0
g_table_id = 0
g_breadcrumb_id = 0
g_tabs_id = 0
g_pagination_id = 0
g_steps_id = 0

@ResizeCallback
def on_resize(hwnd, width, height):
    print(f"[Resize] {width}x{height}")

@CloseCallback
def on_close(hwnd):
    print("[Close] Window closing")
    dll.EU_DestroyWindow(hwnd)

@ClickCallback
def on_button_click(btn_id):
    print(f"[Click] Button #{btn_id} clicked!")
    if btn_id == g_message_button_id:
        mid = show_messagebox(
            g_hwnd,
            "消息提示 😊",
            "这是 Element 风格的 MessageBox 弹窗，支持中文和 emoji：🚀 ✅ 🎉。",
            "知道了"
        )
        print(f"[MessageBox] shown #{mid}")
    elif btn_id == g_confirm_button_id:
        mid = show_confirmbox(
            g_hwnd,
            "确认操作 ❌",
            "确认框同样支持复杂 emoji，点击按钮后会通过回调返回结果。",
            "确定 ✅",
            "取消 ❌"
        )
        print(f"[ConfirmBox] shown #{mid}")
    elif btn_id == g_light_theme_button_id:
        dll.EU_SetThemeMode(g_hwnd, 0)
        print(f"[Theme] switched to light -> {dll.EU_GetThemeMode(g_hwnd)}")
    elif btn_id == g_dark_theme_button_id:
        dll.EU_SetThemeMode(g_hwnd, 1)
        print(f"[Theme] switched to dark -> {dll.EU_GetThemeMode(g_hwnd)}")
    elif btn_id == g_system_theme_button_id:
        dll.EU_SetThemeMode(g_hwnd, 2)
        print(f"[Theme] switched to system -> {dll.EU_GetThemeMode(g_hwnd)}")
    elif btn_id == g_link_id:
        mid = show_messagebox(
            g_hwnd,
            "Link 点击事件 🔗",
            "这是 Basic/Link 组件触发的 MessageBox，文本和弹窗都支持 emoji。",
            "收到"
        )
        print(f"[Link] shown message #{mid}")
    elif btn_id in (g_checkbox_id, g_radio_a_id, g_radio_b_id, g_switch_id, g_slider_id):
        print(
            "[Form] "
            f"checkbox={dll.EU_GetCheckboxChecked(g_hwnd, g_checkbox_id)}, "
            f"radioA={dll.EU_GetRadioChecked(g_hwnd, g_radio_a_id)}, "
            f"radioB={dll.EU_GetRadioChecked(g_hwnd, g_radio_b_id)}, "
            f"switch={dll.EU_GetSwitchChecked(g_hwnd, g_switch_id)}, "
            f"slider={dll.EU_GetSliderValue(g_hwnd, g_slider_id)}"
        )
    elif btn_id in (g_input_number_id, g_select_id, g_rate_id, g_colorpicker_id):
        color = dll.EU_GetColorPickerColor(g_hwnd, g_colorpicker_id) & 0xFFFFFFFF
        print(
            "[Enhanced] "
            f"input={dll.EU_GetInputNumberValue(g_hwnd, g_input_number_id)}, "
            f"select={dll.EU_GetSelectIndex(g_hwnd, g_select_id)}, "
            f"rate={dll.EU_GetRateValue(g_hwnd, g_rate_id)}, "
            f"color=0x{color:08X}"
        )
    elif btn_id in (g_tag_id, g_badge_id, g_progress_id, g_avatar_id):
        print(
            "[Display] "
            f"progress={dll.EU_GetProgressPercentage(g_hwnd, g_progress_id)}"
        )
    elif btn_id in (g_empty_id, g_skeleton_id, g_descriptions_id, g_table_id):
        print("[Data] Empty/Skeleton/Descriptions/Table clicked")
    elif btn_id in (g_breadcrumb_id, g_tabs_id, g_pagination_id, g_steps_id):
        print(
            "[Navigation] "
            f"tabs={dll.EU_GetTabsActive(g_hwnd, g_tabs_id)}, "
            f"page={dll.EU_GetPaginationCurrent(g_hwnd, g_pagination_id)}, "
            f"steps={dll.EU_GetStepsActive(g_hwnd, g_steps_id)}"
        )

@MessageBoxCallback
def on_messagebox_result(messagebox_id, result):
    label = {1: "confirm", 0: "cancel", -1: "close"}.get(result, str(result))
    print(f"[MessageBox] #{messagebox_id} result: {label}")

@MessageBoxExCallback
def on_messagebox_ex_result(messagebox_id, action, value_ptr, value_len):
    label = {1: "confirm", 0: "cancel", -1: "close"}.get(action, str(action))
    value = ""
    if value_ptr and value_len > 0:
        value = ctypes.string_at(value_ptr, value_len).decode("utf-8", errors="replace")
    print(f"[MessageBoxEx] #{messagebox_id} action={label} value={value}")

# 鈹€鈹€ Test 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

