import subprocess
import sys
import os
import venv

def run_command(command, cwd=None):
    """Helper function to run shell commands."""
    try:
        print(f"Executing: {' '.join(command)}")
        result = subprocess.run(command, check=True, cwd=cwd, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}", file=sys.stderr)
        print(f"Stdout: {e.stdout}", file=sys.stderr)
        print(f"Stderr: {e.stderr}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print(f"Error: Command not found. Please ensure '{command[0]}' is in your PATH.", file=sys.stderr)
        return False

def main():
    print("Starting JARVIS AI dependency installation...")

    # Determine Python executable
    python_executable = sys.executable
    print(f"Using Python executable: {python_executable}")

    # Create a virtual environment
    venv_dir = "venv"
    if not os.path.exists(venv_dir):
        print(f"Creating virtual environment in '{venv_dir}'...")
        venv.create(venv_dir, with_pip=True, symlinks=True)
        print("Virtual environment created.")
    else:
        print(f"Virtual environment '{venv_dir}' already exists.")

    # Determine pip executable within the virtual environment
    if sys.platform == "win32":
        pip_executable = os.path.join(venv_dir, "Scripts", "pip.exe")
    else:
        pip_executable = os.path.join(venv_dir, "bin", "pip")

    if not os.path.exists(pip_executable):
        print(f"Error: pip executable not found at {pip_executable}. Please check your virtual environment setup.", file=sys.stderr)
        sys.exit(1)

    # Upgrade pip
    print("Upgrading pip...")
    if not run_command([pip_executable, "install", "--upgrade", "pip"]):
        print("Failed to upgrade pip. Please try again manually.", file=sys.stderr)
        sys.exit(1)

    # Install dependencies from requirements.txt
    requirements_file = "requirements.txt"
    if not os.path.exists(requirements_file):
        print(f"Error: '{requirements_file}' not found. Please ensure it exists in the project root.", file=sys.stderr)
        sys.exit(1)

    print(f"Installing dependencies from '{requirements_file}'...")
    if not run_command([pip_executable, "install", "-r", requirements_file]):
        print("Failed to install dependencies. Please check 'requirements.txt' and your internet connection.", file=sys.stderr)
        sys.exit(1)

    print("\nSetting up directories...")
    try:
        from scripts.setup_directories import setup_directories
        setup_directories()
    except ImportError:
        # If import fails, create directories manually
        import os
        directories = ["data", "data/chroma_db", "data/vision_cache", "data/ethical_violations", 
                      "data/feedback_logs", "data/scraping_logs", "data/self_correction_log", 
                      "data/video_datasets", "logs"]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        print("✓ Directories created")

    print("\nDependency installation complete.")
    print(f"To activate the virtual environment, run:")
    if sys.platform == "win32":
        print(f"  For Command Prompt: {venv_dir}\\Scripts\\activate.bat")
        print(f"  For PowerShell: .\\{venv_dir}\\Scripts\\Activate.ps1")
    else:
        print(f"  source {venv_dir}/bin/activate")
    print("\nAfter activating, you can run JARVIS AI using 'python main.py --mode <mode>'.")
    print("Remember to configure your API keys in config.yaml.")

if __name__ == "__main__":
    main()
