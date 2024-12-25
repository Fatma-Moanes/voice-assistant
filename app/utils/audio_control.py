import platform
import subprocess

from app.utils.logger import get_logger

logger = get_logger()


def mute_mic():
    """
    Mute the microphone on the current system.
    """
    system = platform.system()
    try:
        if system == "Windows":
            from ctypes import POINTER, cast

            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

            devices = AudioUtilities.GetMicrophoneDevices()
            if devices:
                device = devices[0]
                interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                volume.SetMute(1, None)
                logger.info("Microphone muted.")
            else:
                logger.warning("No microphone devices found to mute.")
        
        elif system == "Darwin":
            # macOS: Use AppleScript to mute
            subprocess.call(["osascript", "-e", "set volume input muted true"])
            logger.info("Microphone muted on macOS.")
        
        elif system == "Linux":
            # Linux: Use amixer to mute
            subprocess.call(["amixer", "set", "Capture", "nocap"])
            logger.info("Microphone muted on Linux.")
        
        else:
            logger.error(f"Unsupported OS for muting microphone: {system}")
    
    except Exception as e:
        logger.error(f"Failed to mute microphone: {e}")

def unmute_mic():
    """
    Unmute the microphone on the current system.
    """
    system = platform.system()
    try:
        if system == "Windows":
            # from ctypes import cast, POINTER
            # from comtypes import CLSCTX_ALL
            # # from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

            # devices = AudioUtilities.GetMicrophoneDevices()
            # if devices:
            #     device = devices[0]
            #     interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            #     volume = cast(interface, POINTER(IAudioEndpointVolume))
            #     volume.SetMute(0, None)
            #     logger.info("Microphone unmuted.")
            # else:
            #     logger.warning("No microphone devices found to unmute.")
            logger.warning("Unmuting microphone is not supported on Windows.")
        
        elif system == "Darwin":
            # macOS: Use AppleScript to unmute
            subprocess.call(["osascript", "-e", "set volume input muted false"])
            logger.info("Microphone unmuted on macOS.")
        
        elif system == "Linux":
            # Linux: Use amixer to unmute
            subprocess.call(["amixer", "set", "Capture", "cap"])
            logger.info("Microphone unmuted on Linux.")
        
        else:
            logger.error(f"Unsupported OS for unmuting microphone: {system}")
    
    except Exception as e:
        logger.error(f"Failed to unmute microphone: {e}")
