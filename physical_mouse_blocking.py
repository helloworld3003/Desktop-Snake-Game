import ctypes
from ctypes import wintypes
import threading
import time

# --- Windows API Setup ---
user32 = ctypes.windll.user32
WH_MOUSE_LL = 14
LLMHF_INJECTED = 0x00000001 # Flag that identifies if an input is from a script
LLMHF_LOWER_IL_INJECTED = 0x00000002 # Sometimes injected by lower integrity

# Use LRESULT for 64-bit compatibility
LRESULT = wintypes.LPARAM

# Define the C-structure for the mouse hook
class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [("pt", wintypes.POINT),
                ("mouseData", wintypes.DWORD),
                ("flags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.c_void_p)]

HOOKPROC = ctypes.WINFUNCTYPE(LRESULT, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)

# Explicitly defining argument types and return types to prevent 64-bit OverflowError
user32.CallNextHookEx.argtypes = [wintypes.HHOOK, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM]
user32.CallNextHookEx.restype = LRESULT

user32.SetWindowsHookExW.argtypes = [ctypes.c_int, HOOKPROC, wintypes.HINSTANCE, wintypes.DWORD]
user32.SetWindowsHookExW.restype = wintypes.HHOOK

user32.UnhookWindowsHookEx.argtypes = [wintypes.HHOOK]
user32.UnhookWindowsHookEx.restype = wintypes.BOOL


class MouseBlocker:
    def __init__(self):
        self.hook_id = None
        self.pointer = HOOKPROC(self.hook_proc) # Keep reference in memory
        self.thread = None

    def hook_proc(self, nCode, wParam, lParam):
        if nCode >= 0:
            hook_struct = ctypes.cast(lParam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
            
            # Allow injected events (from PyAutoGUI) to pass through
            is_injected = (hook_struct.flags & LLMHF_INJECTED) or (hook_struct.flags & LLMHF_LOWER_IL_INJECTED)
            if not is_injected:
                return 1 # Block physical interaction!
                
        # Let PyAutoGUI's injected inputs pass through normally
        return user32.CallNextHookEx(self.hook_id, nCode, wParam, lParam)

    def _message_loop(self):
        self.hook_id = user32.SetWindowsHookExW(WH_MOUSE_LL, self.pointer, None, 0)
        msg = wintypes.MSG()
        # A Windows message loop is required to keep the hook listening
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

    def start(self):
        # Run the hook in a background thread so our main script can keep going
        self.thread = threading.Thread(target=self._message_loop, daemon=True)
        self.thread.start()
        time.sleep(0.5) # Give the OS a split second to register the hook

    def stop(self):
        if self.hook_id:
            user32.UnhookWindowsHookEx(self.hook_id)
            self.hook_id = None
