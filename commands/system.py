import subprocess
import os
import platform
from typing import Optional, Dict, Any
from jarvis.core.config import settings

class SystemController:
    """System control operations"""

    def __init__(self):
        self.system = platform.system()
        self.user_home = os.path.expanduser("~")

    def open_app(self, app_name: str) -> Dict[str, Any]:
        """Open an application"""
        try:
            if self.system == "Darwin":  # macOS
                result = subprocess.run(
                    ["open", "-a", app_name],
                    capture_output=True,
                    text=True
                )
            elif self.system == "Linux":
                result = subprocess.run(
                    [app_name],
                    capture_output=True,
                    text=True
                )
            elif self.system == "Windows":
                result = subprocess.run(
                    ["start", app_name],
                    shell=True,
                    capture_output=True,
                    text=True
                )
            else:
                return {"success": False, "message": "Unsupported operating system"}

            return {
                "success": True,
                "message": f"Opening {app_name}",
                "app": app_name
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to open {app_name}: {str(e)}"
            }

    def close_app(self, app_name: str) -> Dict[str, Any]:
        """Close an application"""
        try:
            if self.system == "Darwin":  # macOS
                result = subprocess.run(
                    ["pkill", "-x", app_name],
                    capture_output=True,
                    text=True
                )
            elif self.system == "Linux":
                result = subprocess.run(
                    ["pkill", app_name],
                    capture_output=True,
                    text=True
                )
            elif self.system == "Windows":
                result = subprocess.run(
                    ["taskkill", "/IM", f"{app_name}.exe"],
                    capture_output=True,
                    text=True
                )
            else:
                return {"success": False, "message": "Unsupported operating system"}

            return {
                "success": True,
                "message": f"Closing {app_name}",
                "app": app_name
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to close {app_name}: {str(e)}"
            }

    def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute a terminal command"""
        try:
            # Safety check - prevent dangerous commands
            dangerous_commands = ["rm -rf /", "format", "del /f", "shutdown /s"]
            if any(cmd in command.lower() for cmd in dangerous_commands):
                return {
                    "success": False,
                    "message": "Cannot execute potentially dangerous command without confirmation"
                }

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )

            return {
                "success": True,
                "message": f"Command executed: {command}",
                "output": result.stdout,
                "error": result.stderr if result.stderr else None
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "message": "Command timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to execute command: {str(e)}"
            }

    def open_file(self, file_path: str) -> Dict[str, Any]:
        """Open a file with default application"""
        try:
            # Expand ~ to home directory
            file_path = os.path.expanduser(file_path)

            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "message": f"File not found: {file_path}"
                }

            if self.system == "Darwin":
                subprocess.run(["open", file_path])
            elif self.system == "Linux":
                subprocess.run(["xdg-open", file_path])
            elif self.system == "Windows":
                os.startfile(file_path)

            return {
                "success": True,
                "message": f"Opening {file_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to open file: {str(e)}"
            }

    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            "system": self.system,
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "user_home": self.user_home
        }

    def set_volume(self, level: int) -> Dict[str, Any]:
        """Set system volume (0-100)"""
        try:
            if self.system == "Darwin":
                subprocess.run(["osascript", "-e", f"set volume output volume {level}"])
            elif self.system == "Linux":
                subprocess.run(["amixer", "set", "Master", f"{level}%"])
            elif self.system == "Windows":
                # Requires additional setup on Windows
                return {"success": False, "message": "Volume control not available on Windows"}

            return {
                "success": True,
                "message": f"Volume set to {level}%"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to set volume: {str(e)}"
            }

system_controller = SystemController()
