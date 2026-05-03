"""
Test script for new_emoji.dll 鈥?verify window creation, Basic controls, Panel/Button/EditBox/
InfoBox/MessageBox, emoji rendering, theme switching, and zero-flicker resize behavior.
"""
import ctypes
from ctypes import wintypes
import sys
import os
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

DLL_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "bin", "x64", "Release", "new_emoji.dll"
))

# Load DLL
dll = ctypes.WinDLL(DLL_PATH)

# 鈹€鈹€ Callback types 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
ClickCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int)
ResizeCallback = ctypes.WINFUNCTYPE(None, wintypes.HWND, ctypes.c_int, ctypes.c_int)
CloseCallback  = ctypes.WINFUNCTYPE(None, wintypes.HWND)
MessageBoxCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int, ctypes.c_int)
TextCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int)
ValueCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int)

# 鈹€鈹€ Export signatures 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

def ptr(s): return ctypes.c_char_p(s) if isinstance(s, bytes) else ctypes.c_char_p(s.encode('utf-8'))

dll.EU_CreateWindow.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                 ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                 ctypes.c_uint32]
dll.EU_CreateWindow.restype = wintypes.HWND

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

dll.EU_CreateSpace.argtypes = [wintypes.HWND, ctypes.c_int,
                               ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateSpace.restype = ctypes.c_int

dll.EU_CreateContainer.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateContainer.restype = ctypes.c_int

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

dll.EU_CreateRadio.argtypes = [wintypes.HWND, ctypes.c_int,
                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                               ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateRadio.restype = ctypes.c_int

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

dll.EU_CreateScrollbar.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                   ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateScrollbar.restype = ctypes.c_int

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

dll.EU_SetElementColor.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_uint32, ctypes.c_uint32]
dll.EU_SetElementText.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetElementBounds.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetElementVisible.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetElementVisible.restype = ctypes.c_int
dll.EU_GetElementEnabled.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetElementEnabled.restype = ctypes.c_int
dll.EU_SetTextOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetTextOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                  ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTextOptions.restype = ctypes.c_int
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
dll.EU_SetButtonEmoji.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetButtonVariant.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetButtonState.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                  ctypes.POINTER(ctypes.c_int)]
dll.EU_GetButtonState.restype = ctypes.c_int
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

dll.EU_GetEditBoxText.argtypes = [wintypes.HWND, ctypes.c_int,
                                   ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetEditBoxText.restype = ctypes.c_int
dll.EU_SetEditBoxTextCallback.argtypes = [wintypes.HWND, ctypes.c_int, TextCallback]
dll.EU_SetElementFocus.argtypes = [wintypes.HWND, ctypes.c_int]

dll.EU_SetCheckboxChecked.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetCheckboxChecked.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetCheckboxChecked.restype = ctypes.c_int
dll.EU_SetCheckboxIndeterminate.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetCheckboxIndeterminate.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetCheckboxIndeterminate.restype = ctypes.c_int
dll.EU_SetRadioChecked.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetRadioChecked.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetRadioChecked.restype = ctypes.c_int
dll.EU_SetRadioGroup.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetRadioGroup.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetRadioGroup.restype = ctypes.c_int
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
dll.EU_SetAvatarShape.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetAvatarSource.argtypes = [wintypes.HWND, ctypes.c_int,
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
dll.EU_SetDescriptionsOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                          ctypes.c_int, ctypes.c_int,
                                          ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetDescriptionsItemCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDescriptionsItemCount.restype = ctypes.c_int
dll.EU_SetDescriptionsAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetDescriptionsOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                          ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                          ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                          ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                          ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDescriptionsOptions.restype = ctypes.c_int
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
dll.EU_SetCardBody.argtypes = [wintypes.HWND, ctypes.c_int,
                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetCardFooter.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetCardActions.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetCardAction.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetCardAction.restype = ctypes.c_int
dll.EU_ResetCardAction.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_SetCardShadow.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetCardOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetCardOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                  ctypes.POINTER(ctypes.c_int)]
dll.EU_GetCardOptions.restype = ctypes.c_int
dll.EU_SetCollapseItems.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetCollapseActive.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetCollapseActive.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetCollapseActive.restype = ctypes.c_int
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
dll.EU_SetTimelineItems.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTimelineOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetTimelineItemCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTimelineItemCount.restype = ctypes.c_int
dll.EU_GetTimelineOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTimelineOptions.restype = ctypes.c_int
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
dll.EU_SetAutocompleteSuggestions.argtypes = [wintypes.HWND, ctypes.c_int,
                                              ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetAutocompleteValue.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
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
dll.EU_SetCarouselItems.argtypes = [wintypes.HWND, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetCarouselActive.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetCarouselOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                      ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
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
dll.EU_SetScrollbarValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetScrollbarRange.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetScrollbarOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetScrollbarWheelStep.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_BindScrollbarContent.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_ScrollbarScroll.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_ScrollbarWheel.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetScrollbarValue.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetScrollbarValue.restype = ctypes.c_int
dll.EU_GetScrollbarMaxValue.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetScrollbarMaxValue.restype = ctypes.c_int
dll.EU_GetScrollbarOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetScrollbarOptions.restype = ctypes.c_int
dll.EU_GetScrollbarFullState.argtypes = [
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
dll.EU_GetScrollbarFullState.restype = ctypes.c_int
dll.EU_SetScrollbarChangeCallback.argtypes = [wintypes.HWND, ctypes.c_int, ValueCallback]
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
dll.EU_SetTabsActive.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTabsType.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTabsOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_AddTabsItem.argtypes = [wintypes.HWND, ctypes.c_int,
                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_CloseTabsItem.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTabsScroll.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_TabsScroll.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetTabsActive.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTabsActive.restype = ctypes.c_int
dll.EU_GetTabsItemCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTabsItemCount.restype = ctypes.c_int
dll.EU_GetTabsState.argtypes = [wintypes.HWND, ctypes.c_int,
                                ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTabsState.restype = ctypes.c_int
dll.EU_GetTabsItem.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int,
                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTabsItem.restype = ctypes.c_int
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
dll.EU_SetTabsChangeCallback.argtypes = [wintypes.HWND, ctypes.c_int, ValueCallback]
dll.EU_SetTabsCloseCallback.argtypes = [wintypes.HWND, ctypes.c_int, ValueCallback]
dll.EU_SetTabsAddCallback.argtypes = [wintypes.HWND, ctypes.c_int, ValueCallback]
dll.EU_SetPagination.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetPaginationCurrent.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetPaginationPageSize.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetPaginationOptions.argtypes = [wintypes.HWND, ctypes.c_int,
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
dll.EU_SetPaginationChangeCallback.argtypes = [wintypes.HWND, ctypes.c_int, ValueCallback]
dll.EU_SetStepsItems.argtypes = [wintypes.HWND, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetStepsDetailItems.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetStepsActive.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetStepsDirection.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
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
dll.EU_SetStepsChangeCallback.argtypes = [wintypes.HWND, ctypes.c_int, ValueCallback]
dll.EU_SetAlertDescription.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetAlertType.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetAlertEffect.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetAlertClosable.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
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
dll.EU_SetNotificationBody.argtypes = [wintypes.HWND, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetNotificationType.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetNotificationClosable.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
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
dll.EU_SetNotificationCloseCallback.argtypes = [wintypes.HWND, ctypes.c_int, ValueCallback]
dll.EU_SetLoadingActive.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetLoadingOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                     ctypes.c_int, ctypes.c_int, ctypes.c_int]
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
dll.EU_SetPopconfirmOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetPopconfirmOptions.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.c_int, ctypes.c_int,
                                        ctypes.c_int, ctypes.c_int]
dll.EU_SetPopconfirmContent.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetPopconfirmButtons.argtypes = [wintypes.HWND, ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
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
    return (ctypes.c_ubyte * len(data))(*data)

def create_window(title="New Emoji Test", x=300, y=200, w=800, h=600):
    data = make_utf8(title)
    hwnd = dll.EU_CreateWindow(
        (ctypes.c_ubyte * len(data))(*data), len(data),
        x, y, w, h,
        0xFF181825  # titlebar color
    )
    return hwnd

def create_panel(hwnd, parent_id=0, x=0, y=0, w=800, h=600, color=0):
    pid = dll.EU_CreatePanel(hwnd, parent_id, x, y, w, h)
    if color:
        dll.EU_SetElementColor(hwnd, pid, color, 0xFFFFFFFF)
    return pid

def create_button(hwnd, parent_id, emoji="", text="Button", x=0, y=0, w=200, h=40):
    e_data = make_utf8(emoji)
    t_data = make_utf8(text)
    return dll.EU_CreateButton(
        hwnd, parent_id,
        (ctypes.c_ubyte * len(e_data))(*e_data), len(e_data),
        (ctypes.c_ubyte * len(t_data))(*t_data), len(t_data),
        x, y, w, h
    )

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

def create_link(hwnd, parent_id, text="Link", x=0, y=0, w=200, h=28):
    data = make_utf8(text)
    return dll.EU_CreateLink(hwnd, parent_id, bytes_arg(data), len(data), x, y, w, h)

def create_icon(hwnd, parent_id, text="✓", x=0, y=0, w=36, h=36):
    data = make_utf8(text)
    return dll.EU_CreateIcon(hwnd, parent_id, bytes_arg(data), len(data), x, y, w, h)

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

def set_button_emoji(hwnd, element_id, emoji=""):
    data = make_utf8(emoji)
    dll.EU_SetButtonEmoji(hwnd, element_id, bytes_arg(data), len(data))

def set_button_variant(hwnd, element_id, variant=0):
    dll.EU_SetButtonVariant(hwnd, element_id, variant)

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

def create_checkbox(hwnd, parent_id, text="复选框", checked=False, x=0, y=0, w=220, h=30):
    data = make_utf8(text)
    return dll.EU_CreateCheckbox(hwnd, parent_id, bytes_arg(data), len(data),
                                 1 if checked else 0, x, y, w, h)

def create_radio(hwnd, parent_id, text="单选框", checked=False, x=0, y=0, w=180, h=30):
    data = make_utf8(text)
    return dll.EU_CreateRadio(hwnd, parent_id, bytes_arg(data), len(data),
                              1 if checked else 0, x, y, w, h)

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
                allow_clear=None, allow_half=None, readonly=None, value_x2=None):
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

def create_colorpicker(hwnd, parent_id, text="Color", color=0xFF1E66F5,
                       x=0, y=0, w=220, h=36, alpha=None, open_panel=None,
                       palette=None):
    data = make_utf8(text)
    element_id = dll.EU_CreateColorPicker(
        hwnd, parent_id, bytes_arg(data), len(data),
        color, x, y, w, h
    )
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
                 placement=None, standalone=None):
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

def set_badge_layout_options(hwnd, element_id, placement=0, standalone=False):
    dll.EU_SetBadgeLayoutOptions(hwnd, element_id, placement, 1 if standalone else 0)

def get_badge_layout_options(hwnd, element_id):
    placement = ctypes.c_int()
    standalone = ctypes.c_int()
    ok = dll.EU_GetBadgeLayoutOptions(hwnd, element_id, ctypes.byref(placement), ctypes.byref(standalone))
    if not ok:
        return None
    return placement.value, bool(standalone.value)

def create_progress(hwnd, parent_id, text="Progress", percentage=70, status=0,
                    x=0, y=0, w=320, h=34,
                    progress_type=None, stroke_width=None, show_text=None,
                    text_format=None, striped=None):
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

def create_avatar(hwnd, parent_id, text="A", shape=0,
                  x=0, y=0, w=44, h=44, source="", fit=None):
    data = make_utf8(text)
    element_id = dll.EU_CreateAvatar(
        hwnd, parent_id, bytes_arg(data), len(data),
        shape, x, y, w, h
    )
    if element_id and source:
        src_data = make_utf8(source)
        dll.EU_SetAvatarSource(hwnd, element_id, bytes_arg(src_data), len(src_data))
    if element_id and fit is not None:
        dll.EU_SetAvatarFit(hwnd, element_id, fit)
    return element_id

def set_avatar_shape(hwnd, element_id, shape=0):
    dll.EU_SetAvatarShape(hwnd, element_id, shape)

def set_avatar_source(hwnd, element_id, source=""):
    data = make_utf8(source)
    dll.EU_SetAvatarSource(hwnd, element_id, bytes_arg(data), len(data))

def set_avatar_fit(hwnd, element_id, fit=0):
    dll.EU_SetAvatarFit(hwnd, element_id, fit)

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
                 x=0, y=0, w=220, h=100, icon=None, action=None):
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

def create_descriptions(hwnd, parent_id, title="📋 描述列表", items=None,
                        columns=2, bordered=True, x=0, y=0, w=420, h=110,
                        label_width=None, min_row_height=None, wrap_values=None,
                        responsive=None, last_item_span=None):
    if items is None:
        items = [("名称", "Emoji UI"), ("状态", "✅ 就绪")]
    title_data = make_utf8(title)
    items_data = make_utf8("|".join(f"{k}:{v}" for k, v in items))
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

def get_descriptions_options(hwnd, element_id):
    values = [ctypes.c_int() for _ in range(7)]
    ok = dll.EU_GetDescriptionsOptions(hwnd, element_id, *[ctypes.byref(v) for v in values])
    if not ok:
        return None
    return (
        values[0].value, bool(values[1].value), values[2].value, values[3].value,
        bool(values[4].value), bool(values[5].value), bool(values[6].value)
    )

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
            30 if row_height is None else row_height,
            32 if header_height is None else header_height,
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

def create_collapse(hwnd, parent_id, items=None, active=0, accordion=True,
                    x=0, y=0, w=360, h=180):
    if items is None:
        items = [("🎯 一致性", "保持界面风格一致。"),
                 ("💡 反馈", "提供清晰的状态变化。")]
    items_data = make_utf8("|".join(f"{title}:{body}" for title, body in items))
    return dll.EU_CreateCollapse(
        hwnd, parent_id,
        bytes_arg(items_data), len(items_data),
        active, 1 if accordion else 0, x, y, w, h
    )

def create_timeline(hwnd, parent_id, items=None, x=0, y=0, w=360, h=220):
    if items is None:
        items = [("09:00", "🚀 启动", 0, "🚀"), ("10:30", "✅ 复核", 1, "✅")]
    item_rows = []
    for item in items:
        if len(item) >= 4:
            item_rows.append(f"{item[0]}\t{item[1]}\t{item[2]}\t{item[3]}")
        elif len(item) >= 3:
            item_rows.append(f"{item[0]}\t{item[1]}\t{item[2]}")
        else:
            item_rows.append(f"{item[0]}\t{item[1]}\t0")
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

def set_card_footer(hwnd, element_id, footer=""):
    data = make_utf8(footer)
    dll.EU_SetCardFooter(hwnd, element_id, bytes_arg(data), len(data))

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

def set_timeline_options(hwnd, element_id, position=0, show_time=True):
    dll.EU_SetTimelineOptions(hwnd, element_id, position, 1 if show_time else 0)

def get_timeline_item_count(hwnd, element_id):
    return dll.EU_GetTimelineItemCount(hwnd, element_id)

def get_timeline_options(hwnd, element_id):
    position = ctypes.c_int()
    show_time = ctypes.c_int()
    ok = dll.EU_GetTimelineOptions(hwnd, element_id, ctypes.byref(position), ctypes.byref(show_time))
    return (position.value, bool(show_time.value)) if ok else None

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

def create_image(hwnd, parent_id, src="", alt="图片", fit=0,
                 x=0, y=0, w=220, h=180):
    src_data = make_utf8(src)
    alt_data = make_utf8(alt)
    return dll.EU_CreateImage(
        hwnd, parent_id,
        bytes_arg(src_data), len(src_data),
        bytes_arg(alt_data), len(alt_data),
        fit, x, y, w, h
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

def create_scrollbar(hwnd, parent_id, value=0, max_value=100, orientation=1,
                     x=0, y=0, w=18, h=160):
    return dll.EU_CreateScrollbar(
        hwnd, parent_id, value, max_value, orientation, x, y, w, h
    )

def set_image_source(hwnd, element_id, src="", alt="图片"):
    src_data = make_utf8(src)
    alt_data = make_utf8(alt)
    dll.EU_SetImageSource(
        hwnd, element_id,
        bytes_arg(src_data), len(src_data),
        bytes_arg(alt_data), len(alt_data)
    )

def set_image_preview(hwnd, element_id, open=True):
    dll.EU_SetImagePreview(hwnd, element_id, 1 if open else 0)

def set_image_preview_enabled(hwnd, element_id, enabled=True):
    dll.EU_SetImagePreviewEnabled(hwnd, element_id, 1 if enabled else 0)

def set_image_preview_transform(hwnd, element_id, scale_percent=100, offset_x=0, offset_y=0):
    dll.EU_SetImagePreviewTransform(hwnd, element_id, scale_percent, offset_x, offset_y)

def set_image_cache_enabled(hwnd, element_id, enabled=True):
    dll.EU_SetImageCacheEnabled(hwnd, element_id, 1 if enabled else 0)

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
        rows.append(f"{name}\t{status}\t{progress}\t{path}")
    data = make_utf8("|".join(rows))
    dll.EU_SetUploadFileItems(hwnd, element_id, bytes_arg(data), len(data))

def set_upload_options(hwnd, element_id, multiple=True, auto_upload=False):
    dll.EU_SetUploadOptions(hwnd, element_id, 1 if multiple else 0, 1 if auto_upload else 0)

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

def set_scrollbar_wheel_step(hwnd, element_id, step=20):
    dll.EU_SetScrollbarWheelStep(hwnd, element_id, step)

def bind_scrollbar_content(hwnd, element_id, target_element_id, content_size, viewport_size):
    dll.EU_BindScrollbarContent(hwnd, element_id, target_element_id, content_size, viewport_size)

def scrollbar_scroll(hwnd, element_id, delta=1):
    dll.EU_ScrollbarScroll(hwnd, element_id, delta)

def scrollbar_wheel(hwnd, element_id, wheel_delta):
    dll.EU_ScrollbarWheel(hwnd, element_id, wheel_delta)

def get_scrollbar_options(hwnd, element_id):
    value = ctypes.c_int()
    max_value = ctypes.c_int()
    page_size = ctypes.c_int()
    orientation = ctypes.c_int()
    auto_hide = ctypes.c_int()
    wheel_step = ctypes.c_int()
    ok = dll.EU_GetScrollbarOptions(
        hwnd, element_id,
        ctypes.byref(value), ctypes.byref(max_value), ctypes.byref(page_size),
        ctypes.byref(orientation), ctypes.byref(auto_hide), ctypes.byref(wheel_step),
    )
    return (
        value.value, max_value.value, page_size.value,
        orientation.value, bool(auto_hide.value), wheel_step.value,
    ) if ok else None

def get_scrollbar_full_state(hwnd, element_id):
    values = [ctypes.c_int() for _ in range(15)]
    ok = dll.EU_GetScrollbarFullState(
        hwnd, element_id,
        *(ctypes.byref(v) for v in values)
    )
    if not ok:
        return None
    keys = [
        "value", "max_value", "page_size", "orientation", "auto_hide",
        "wheel_step", "bound_element_id", "content_size", "viewport_size",
        "content_offset", "wheel_event_count", "drag_event_count",
        "change_count", "last_action", "last_wheel_delta",
    ]
    result = {key: value.value for key, value in zip(keys, values)}
    result["auto_hide"] = bool(result["auto_hide"])
    return result

def set_scrollbar_change_callback(hwnd, element_id, callback):
    dll.EU_SetScrollbarChangeCallback(hwnd, element_id, callback)

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

def create_pagination(hwnd, parent_id, total=120, page_size=10, current=1,
                      x=0, y=0, w=420, h=40):
    return dll.EU_CreatePagination(
        hwnd, parent_id, total, page_size, current, x, y, w, h
    )

def create_steps(hwnd, parent_id, items=None, active=1,
                 x=0, y=0, w=420, h=80):
    if items is None:
        items = ["开始", "处理", "完成"]
    items_data = make_utf8("|".join(items))
    return dll.EU_CreateSteps(
        hwnd, parent_id, bytes_arg(items_data), len(items_data),
        active, x, y, w, h
    )

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

def set_tabs_type(hwnd, element_id, tab_type):
    dll.EU_SetTabsType(hwnd, element_id, tab_type)

def set_tabs_active(hwnd, element_id, active):
    dll.EU_SetTabsActive(hwnd, element_id, active)

def set_tabs_options(hwnd, element_id, tab_type=0, closable=False, addable=False):
    dll.EU_SetTabsOptions(hwnd, element_id, tab_type, int(bool(closable)), int(bool(addable)))

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

def get_tabs_item(hwnd, element_id, index):
    needed = dll.EU_GetTabsItem(hwnd, element_id, index, None, 0)
    if needed <= 0:
        return ""
    buf = (ctypes.c_ubyte * (needed + 1))()
    dll.EU_GetTabsItem(hwnd, element_id, index, buf, needed + 1)
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

def set_steps_direction(hwnd, element_id, direction):
    dll.EU_SetStepsDirection(hwnd, element_id, direction)

def set_steps_active(hwnd, element_id, active):
    dll.EU_SetStepsActive(hwnd, element_id, active)

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

def set_loading_options(hwnd, element_id, active=True, fullscreen=False, progress=-1):
    dll.EU_SetLoadingOptions(hwnd, element_id, 1 if active else 0, 1 if fullscreen else 0, progress)

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

def create_dialog(hwnd, title="Dialog", body="", modal=True, closable=True,
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

def create_tooltip(hwnd, parent_id, label="Tooltip", content="", placement=2,
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
        trigger_mode, 1 if show_arrow else 0,
    )

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

def create_popover(hwnd, parent_id, label="Popover", title="Popover",
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

def create_popconfirm(hwnd, parent_id, label="Popconfirm", title="Confirm",
                      content="", confirm="OK", cancel="Cancel", placement=3,
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

# 鈹€鈹€ Test 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

def main():
    global g_hwnd, g_message_button_id, g_confirm_button_id
    global g_light_theme_button_id, g_dark_theme_button_id, g_system_theme_button_id
    global g_link_id
    global g_checkbox_id, g_radio_a_id, g_radio_b_id, g_switch_id, g_slider_id
    global g_input_number_id, g_select_id, g_rate_id, g_colorpicker_id
    global g_tag_id, g_badge_id, g_progress_id, g_avatar_id
    global g_empty_id, g_skeleton_id, g_descriptions_id, g_table_id
    global g_breadcrumb_id, g_tabs_id, g_pagination_id, g_steps_id

    print("Creating window...")
    hwnd = create_window("馃榾 New Emoji UI Test 馃帀", 200, 80, 920, 1420)
    if not hwnd:
        print("ERROR: Failed to create window!")
        return
    print(f"Window created: 0x{hwnd:08X}")
    g_hwnd = hwnd
    print(f"Initial theme mode: {dll.EU_GetThemeMode(hwnd)}")

    dll.EU_SetWindowResizeCallback(hwnd, on_resize)
    dll.EU_SetWindowCloseCallback(hwnd, on_close)

    # Root-level Container fills the client area below the D2D title bar.
    # Avoid wrapping the demo in a fixed-height Panel, otherwise lower controls
    # can be clipped on high-DPI screens.
    content_id = create_container(hwnd, 0, 0, 0, 900, 1370)
    print(f"Container: #{content_id}")

    # MessageBox button
    btn_id = create_button(hwnd, content_id, "💬", " MessageBox ",
                           20, 20, 240, 50)
    dll.EU_SetElementClickCallback(hwnd, btn_id, on_button_click)
    g_message_button_id = btn_id
    print(f"Button: #{btn_id}")

    # ConfirmBox button
    btn2_id = create_button(hwnd, content_id, "❌", " ConfirmBox ",
                            280, 20, 240, 50)
    dll.EU_SetElementClickCallback(hwnd, btn2_id, on_button_click)
    g_confirm_button_id = btn2_id
    print(f"Button 2: #{btn2_id}")

    # Edit box
    eb_id = create_editbox(hwnd, content_id, 20, 90, 500, 36)
    print(f"EditBox: #{eb_id}")

    # Element-style info box
    info_id = create_infobox(
        hwnd, content_id,
        "DPI 自适应信息框",
        "这是一个单独封装的 InfoBox 控件，会跟随窗口 DPI 缩放，并保持 Element 风格绘制。",
        20, 146, 620, 92
    )
    print(f"InfoBox: #{info_id}")

    # Theme buttons
    light_id = create_button(hwnd, content_id, "☀️", " Light ",
                             20, 258, 130, 40)
    dark_id = create_button(hwnd, content_id, "🌙", " Dark ",
                            160, 258, 130, 40)
    system_id = create_button(hwnd, content_id, "🖥️", " System ",
                              300, 258, 150, 40)
    dll.EU_SetElementClickCallback(hwnd, light_id, on_button_click)
    dll.EU_SetElementClickCallback(hwnd, dark_id, on_button_click)
    dll.EU_SetElementClickCallback(hwnd, system_id, on_button_click)
    g_light_theme_button_id = light_id
    g_dark_theme_button_id = dark_id
    g_system_theme_button_id = system_id
    print(f"Theme buttons: light={light_id}, dark={dark_id}, system={system_id}")

    # Basic component slice: Text / Link / Icon / Space / Container / Layout / Border
    basic_title_id = create_text(
        hwnd, content_id,
        "Basic 组件：Text / Link / Icon / Space / Container / Layout / Border",
        20, 318, 780, 26
    )
    icon_id = create_icon(hwnd, content_id, "✓", 20, 354, 42, 42)
    text_id = create_text(
        hwnd, content_id,
        "Text 支持中文和 emoji cluster：🚀 ✅ 🎉",
        72, 356, 590, 40
    )
    link_id = create_link(
        hwnd, content_id,
        "Link 点击弹出 MessageBox 🚀",
        20, 402, 320, 30
    )
    dll.EU_SetElementClickCallback(hwnd, link_id, on_button_click)
    g_link_id = link_id

    border_id = create_border(hwnd, content_id, 20, 442, 620, 72)
    border_text_id = create_text(
        hwnd, border_id,
        "Border 是独立控件文件，子 Text 在边框内部绘制。",
        12, 14, 580, 28
    )

    layout_id = create_layout(hwnd, content_id, 0, 10, 20, 532, 620, 42)
    layout_icon_id = create_icon(hwnd, layout_id, "馃З", 0, 0, 38, 36)
    layout_text_id = create_text(hwnd, layout_id, "Layout 横向排列", 0, 0, 150, 36)
    space_id = create_space(hwnd, layout_id, 0, 0, 22, 36)
    layout_button_id = create_button(hwnd, layout_id, "✓", " Child Button ", 0, 0, 150, 36)
    dll.EU_SetElementBounds(hwnd, layout_id, 20, 532, 620, 42)
    print(
        "Basic components: "
        f"text={basic_title_id}/{text_id}, icon={icon_id}, link={link_id}, "
        f"border={border_id}/{border_text_id}, layout={layout_id}, "
        f"layout children={layout_icon_id},{layout_text_id},{space_id},{layout_button_id}"
    )

    form_title_id = create_text(
        hwnd, content_id,
        "Form 组件：Checkbox / Radio / Switch / Slider",
        20, 592, 780, 26
    )
    checkbox_id = create_checkbox(
        hwnd, content_id,
        "Checkbox 已选中 ✓",
        True, 20, 628, 260, 30
    )
    radio_a_id = create_radio(
        hwnd, content_id,
        "Radio 选项 A",
        True, 20, 668, 140, 30
    )
    radio_b_id = create_radio(
        hwnd, content_id,
        "Radio 选项 B",
        False, 180, 668, 140, 30
    )
    switch_id = create_switch(
        hwnd, content_id,
        "Switch 开关",
        False, 20, 708, 220, 32
    )
    slider_id = create_slider(
        hwnd, content_id,
        "Slider 数值",
        0, 100, 42, 20, 756, 420, 58
    )
    for form_id in (checkbox_id, radio_a_id, radio_b_id, switch_id, slider_id):
        dll.EU_SetElementClickCallback(hwnd, form_id, on_button_click)
    g_checkbox_id = checkbox_id
    g_radio_a_id = radio_a_id
    g_radio_b_id = radio_b_id
    g_switch_id = switch_id
    g_slider_id = slider_id
    print(
        "Form components: "
        f"title={form_title_id}, checkbox={checkbox_id}, radio={radio_a_id}/{radio_b_id}, "
        f"switch={switch_id}, slider={slider_id}"
    )

    enhanced_title_id = create_text(
        hwnd, content_id,
        "Enhanced inputs: InputNumber / Select / Rate / ColorPicker",
        470, 592, 360, 26
    )
    input_number_id = create_input_number(
        hwnd, content_id,
        "InputNumber", 18, 0, 120, 3,
        470, 628, 320, 36
    )
    select_id = create_select(
        hwnd, content_id,
        "Select", ["Small", "Medium", "Large"], 1,
        470, 676, 320, 36
    )
    rate_id = create_rate(
        hwnd, content_id,
        "Rate", 4, 5,
        470, 724, 320, 36
    )
    colorpicker_id = create_colorpicker(
        hwnd, content_id,
        "ColorPicker", 0xFF1E66F5,
        470, 772, 320, 36
    )
    for enhanced_id in (input_number_id, select_id, rate_id, colorpicker_id):
        dll.EU_SetElementClickCallback(hwnd, enhanced_id, on_button_click)
    g_input_number_id = input_number_id
    g_select_id = select_id
    g_rate_id = rate_id
    g_colorpicker_id = colorpicker_id
    print(
        "Enhanced components: "
        f"title={enhanced_title_id}, input={input_number_id}, "
        f"select={select_id}, rate={rate_id}, color={colorpicker_id}"
    )

    display_title_id = create_text(
        hwnd, content_id,
        "Display: Tag / Badge / Progress / Avatar",
        470, 830, 360, 26
    )
    tag_id = create_tag(
        hwnd, content_id,
        "Tag closable", 1, 0, True,
        470, 866, 150, 30
    )
    tag_dark_id = create_tag(
        hwnd, content_id,
        "Warning", 3, 1, False,
        636, 866, 120, 30
    )
    badge_id = create_badge(
        hwnd, content_id,
        "Badge messages", "128", 99, False,
        470, 908, 260, 34
    )
    progress_id = create_progress(
        hwnd, content_id,
        "Progress", 68, 0,
        470, 956, 320, 34
    )
    avatar_id = create_avatar(
        hwnd, content_id,
        "UI", 0,
        470, 1000, 48, 48
    )
    avatar_square_id = create_avatar(
        hwnd, content_id,
        "馃榾", 1,
        532, 1000, 48, 48
    )
    for display_id in (tag_id, tag_dark_id, badge_id, progress_id, avatar_id, avatar_square_id):
        dll.EU_SetElementClickCallback(hwnd, display_id, on_button_click)
    g_tag_id = tag_id
    g_badge_id = badge_id
    g_progress_id = progress_id
    g_avatar_id = avatar_id
    print(
        "Display components: "
        f"title={display_title_id}, tag={tag_id}/{tag_dark_id}, "
        f"badge={badge_id}, progress={progress_id}, avatar={avatar_id}/{avatar_square_id}"
    )

    data_title_id = create_text(
        hwnd, content_id,
        "Data display: Empty / Skeleton / Descriptions / Table",
        20, 830, 420, 26
    )
    empty_id = create_empty(
        hwnd, content_id,
        "No Data", "Empty state",
        20, 862, 200, 82
    )
    skeleton_id = create_skeleton(
        hwnd, content_id,
        3, True,
        232, 862, 208, 82
    )
    descriptions_id = create_descriptions(
        hwnd, content_id,
        "Descriptions",
        [("Name", "Element UI"), ("DPI", "Ready"), ("Theme", "Light/Dark"), ("Emoji", "OK")],
        2, True,
        20, 954, 420, 72
    )
    table_id = create_table(
        hwnd, content_id,
        ["Component", "State", "Note"],
        [["Table", "Done", "Data"], ["Empty", "Done", "State"], ["Skeleton", "Done", "Loading"]],
        True, True,
        20, 1038, 420, 88
    )
    for data_id in (empty_id, skeleton_id, descriptions_id, table_id):
        dll.EU_SetElementClickCallback(hwnd, data_id, on_button_click)
    g_empty_id = empty_id
    g_skeleton_id = skeleton_id
    g_descriptions_id = descriptions_id
    g_table_id = table_id
    print(
        "Data display components: "
        f"title={data_title_id}, empty={empty_id}, skeleton={skeleton_id}, "
        f"descriptions={descriptions_id}, table={table_id}"
    )

    nav_title_id = create_text(
        hwnd, content_id,
        "Navigation: Breadcrumb / Tabs / Pagination / Steps",
        470, 1060, 360, 26
    )
    breadcrumb_id = create_breadcrumb(
        hwnd, content_id,
        ["Home", "Components", "Navigation"], "/", 2,
        470, 1092, 360, 32
    )
    tabs_id = create_tabs(
        hwnd, content_id,
        ["User", "Config", "Role"], 1, 0,
        470, 1134, 360, 40
    )
    pagination_id = create_pagination(
        hwnd, content_id,
        86, 10, 3,
        470, 1188, 360, 40
    )
    steps_id = create_steps(
        hwnd, content_id,
        ["Start", "Build", "Ship"], 1,
        470, 1240, 360, 78
    )
    for nav_id in (breadcrumb_id, tabs_id, pagination_id, steps_id):
        dll.EU_SetElementClickCallback(hwnd, nav_id, on_button_click)
    g_breadcrumb_id = breadcrumb_id
    g_tabs_id = tabs_id
    g_pagination_id = pagination_id
    g_steps_id = steps_id
    print(
        "Navigation components: "
        f"title={nav_title_id}, breadcrumb={breadcrumb_id}, tabs={tabs_id}, "
        f"pagination={pagination_id}, steps={steps_id}"
    )

    # Show window
    dll.EU_ShowWindow(hwnd, 1)
    print("\nWindow is now visible.")
    print("Try: clicking Light/Dark/System theme buttons, form/enhanced controls, fast resizing, typing emoji in the edit box, clicking message boxes.")
    print("Verify: NO FLICKER during resize.")
    print("\nWindow will close after 60 seconds, or close it manually.")
    print("Press Ctrl+C to exit early.\n")

    # Message loop
    start = time.time()
    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    PM_REMOVE = 1
    WM_QUIT = 0x0012
    WM_DESTROY = 0x0002
    running = True
    while time.time() - start < 60:
        try:
            handled = False
            while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, PM_REMOVE):
                handled = True
                if msg.message in (WM_QUIT, WM_DESTROY):
                    running = False
                    break
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
            if not running:
                break
            if not handled:
                time.sleep(0.01)
        except Exception:
            time.sleep(0.01)

    print("Test complete.")

if __name__ == '__main__':
    main()
