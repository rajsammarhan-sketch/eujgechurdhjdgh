import os
import subprocess
import sys
import shutil
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_inputs():
    """Validate user inputs before proceeding"""
    if not CRD_SSH_Code or CRD_SSH_Code.strip() == "":
        logger.error("Please enter a valid Chrome Remote Desktop SSH code")
        return False
    
    if len(str(Pin)) < 6:
        logger.error("PIN must be at least 6 digits")
        return False
        
    return True

def run_command(command, use_shell=False, check_result=True):
    """Execute command with proper error handling"""
    try:
        if use_shell:
            result = subprocess.run(command, shell=True, check=check_result, 
                                  capture_output=True, text=True)
        else:
            result = subprocess.run(command, check=check_result, 
                                  capture_output=True, text=True)
        
        if result.returncode != 0 and check_result:
            logger.error(f"Command failed: {command}")
            logger.error(f"Error: {result.stderr}")
            return False
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {command} - {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error running command: {command} - {e}")
        return False

# User Configuration
try:
    CRD_SSH_Code = input("Google CRD SSH Code: ").strip()
except KeyboardInterrupt:
    print("\nOperation cancelled by user")
    sys.exit(1)

username = "user"
password = "root"
Pin = 123456

# Validate inputs
if not validate_inputs():
    sys.exit(1)

class CRDSetup:
    def __init__(self, user):
        """Initialize and run the complete setup process"""
        logger.info("Starting Chrome Remote Desktop setup...")
        
        # Update package list first
        self.update_system()
        
        # Create user and setup permissions
        self.setup_user(user)
        
        # Install components
        if not self.install_crd():
            logger.error("Failed to install Chrome Remote Desktop")
            return
            
        if not self.install_desktop_environment():
            logger.error("Failed to install desktop environment")
            return
            
        self.install_google_chrome()
        self.install_python()
        self.install_selenium_webdriver()
        self.install_qbittorrent()
        self.change_wallpaper()
        
        # Finalize setup
        self.finish(user)

    def update_system(self):
        """Update system packages"""
        logger.info("Updating system packages...")
        run_command("apt update", use_shell=True)

    def setup_user(self, user):
        """Create user and setup basic permissions"""
        logger.info(f"Setting up user: {user}")
        
        # Create user if doesn't exist
        run_command(f"id {user} || useradd -m {user}", use_shell=True, check_result=False)
        
        # Add to sudo group
        run_command(f"usermod -aG sudo {user}", use_shell=True)
        
        # Set password
        run_command(f"echo '{user}:{password}' | chpasswd", use_shell=True)
        
        # Change default shell to bash
        run_command("sed -i 's/\/bin\/sh/\/bin\/bash/g' /etc/passwd", use_shell=True)

    def install_crd(self):
        """Install Chrome Remote Desktop"""
        logger.info("Installing Chrome Remote Desktop...")
        
        # Download and install CRD
        commands = [
            "wget -q https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb",
            "dpkg -i chrome-remote-desktop_current_amd64.deb",
            "apt install -f -y"
        ]
        
        for cmd in commands:
            if not run_command(cmd, use_shell=True, check_result=False):
                logger.warning(f"Command may have failed: {cmd}")
        
        logger.info("Chrome Remote Desktop installation completed!")
        return True

    def install_desktop_environment(self):
        """Install XFCE4 desktop environment"""
        logger.info("Installing Desktop Environment...")
        
        # Set non-interactive mode
        os.environ['DEBIAN_FRONTEND'] = 'noninteractive'
        
        commands = [
            "apt install -y xfce4 desktop-base xfce4-terminal",
            "apt install -y xscreensaver dbus-x11",
            "apt remove -y gnome-terminal",
            "service lightdm stop",
            "service dbus start"
        ]
        
        for cmd in commands:
            run_command(cmd, use_shell=True, check_result=False)
        
        # Setup CRD session
        session_cmd = 'echo "exec /etc/X11/Xsession /usr/bin/xfce4-session" > /etc/chrome-remote-desktop-session'
        run_command(session_cmd, use_shell=True, check_result=False)
        
        logger.info("XFCE4 Desktop Environment installed!")
        return True

    def install_google_chrome(self):
        """Install Google Chrome browser"""
        logger.info("Installing Google Chrome...")
        
        commands = [
            "wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb",
            "dpkg -i google-chrome-stable_current_amd64.deb",
            "apt install -f -y"
        ]
        
        for cmd in commands:
            run_command(cmd, use_shell=True, check_result=False)
        
        logger.info("Google Chrome installed!")

    def install_python(self):
        """Install Python and pip"""
        logger.info("Installing Python and pip...")
        run_command("apt install -y python3 python3-pip", use_shell=True, check_result=False)
        logger.info("Python installed!")

    def install_selenium_webdriver(self):
        """Install Selenium WebDriver"""
        logger.info("Installing Selenium WebDriver...")
        
        commands = [
            "pip3 install selenium",
            "apt install -y chromium-chromedriver"
        ]
        
        for cmd in commands:
            run_command(cmd, use_shell=True, check_result=False)
        
        logger.info("Selenium WebDriver installed!")

    def install_qbittorrent(self):
        """Install qBittorrent"""
        logger.info("Installing qBittorrent...")
        run_command("apt install -y qbittorrent", use_shell=True, check_result=False)
        logger.info("qBittorrent installed!")

    def change_wallpaper(self):
        """Setup custom wallpapers"""
        logger.info("Setting up wallpapers...")
        
        wallpaper_dir = "/etc/alternatives/desktop-theme/wallpaper/contents/images/"
        run_command(f"mkdir -p {wallpaper_dir}", use_shell=True, check_result=False)
        
        wallpaper_resolutions = ["3200x2000", "3840x2160", "5120x2880"]
        base_url = "https://gitlab.com/chamod12/gcrd_deb_codesandbox.io_rdp/-/raw/main/walls"
        
        for resolution in wallpaper_resolutions:
            url = f"{base_url}/{resolution}.svg"
            output_path = f"{wallpaper_dir}{resolution}.svg"
            cmd = f"curl -s -L -o {output_path} {url}"
            run_command(cmd, use_shell=True, check_result=False)
        
        logger.info("Wallpapers configured!")

    def finish(self, user):
        """Finalize Chrome Remote Desktop setup"""
        logger.info("Finalizing setup...")
        
        # Add user to chrome-remote-desktop group
        run_command(f"usermod -aG chrome-remote-desktop {user}", use_shell=True, check_result=False)
        
        # Start Chrome Remote Desktop with the provided code
        crd_command = f"{CRD_SSH_Code} --pin={Pin}"
        run_command(f"su - {user} -c '{crd_command}'", use_shell=True, check_result=False)
        
        # Start the service
        run_command("systemctl start chrome-remote-desktop", use_shell=True, check_result=False)
        
        # Display connection information
        print("\n" + "="*60)
        print("CHROME REMOTE DESKTOP SETUP COMPLETE")
        print("="*60)
        print(f"PIN: {Pin}")
        print(f"Username: {username}")
        print(f"Password: {password}")
        print("="*60)
        print("\nSetup complete! Chrome Remote Desktop is now running.")
        print("You can now connect using Chrome Remote Desktop.")
        print("\nPress Ctrl+C to exit this script.")
        
        # Keep script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Script terminated by user")
            print("\nExiting...")

def main():
    """Main execution function"""
    try:
        # Validate environment
        if os.geteuid() != 0:
            logger.error("This script must be run as root")
            sys.exit(1)
        
        # Start setup
        CRDSetup(username)
        
    except KeyboardInterrupt:
        logger.info("Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()