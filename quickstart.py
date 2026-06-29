#!/usr/bin/env python3
"""
Quick Start Setup Wizard for OneDrive Audit Tool
Guides users through initial setup
"""

import os
import sys
import json
from pathlib import Path


class SetupWizard:
    """Interactive setup wizard"""

    def __init__(self):
        self.client_id = None
        self.setup_complete = False

    def print_header(self, title):
        """Print formatted header"""
        print("\n" + "=" * 60)
        print(f"  {title}")
        print("=" * 60)

    def print_section(self, title):
        """Print section header"""
        print(f"\n--- {title} ---\n")

    def input_prompt(self, prompt, required=True, default=None):
        """Get user input with validation"""
        while True:
            if default:
                user_input = input(f"{prompt} [{default}]: ").strip() or default
            else:
                user_input = input(f"{prompt}: ").strip()

            if user_input or not required:
                return user_input
            print("This field is required.")

    def step_1_welcome(self):
        """Welcome screen"""
        self.print_header("OneDrive Audit & Organization Tool")
        print("""
Welcome to the OneDrive Audit Tool setup wizard!

This tool will help you:
  • Scan your OneDrive folder structure
  • Find and remove duplicate files
  • Organize files by type or date
  • Generate detailed audit reports

Let's get started!
        """)

    def step_2_check_requirements(self):
        """Check system requirements"""
        self.print_section("Checking Requirements")

        # Check Python version
        py_version = sys.version_info
        if py_version.major >= 3 and py_version.minor >= 8:
            print(f"✓ Python {py_version.major}.{py_version.minor} - OK")
        else:
            print(f"✗ Python 3.8+ required (you have {py_version.major}.{py_version.minor})")
            return False

        # Check dependencies
        try:
            import msal
            print("✓ msal - OK")
        except ImportError:
            print("✗ msal not installed")
            print("  Run: pip install -r requirements.txt")
            return False

        try:
            import requests
            print("✓ requests - OK")
        except ImportError:
            print("✗ requests not installed")
            print("  Run: pip install -r requirements.txt")
            return False

        return True

    def step_3_azure_setup(self):
        """Guide through Azure setup"""
        self.print_section("Azure App Registration")

        print("""
To use this tool, you need to register an app in Azure.

Follow these steps:
1. Go to https://portal.azure.com/
2. Search for "App registrations" and click
3. Click "New registration"
4. Fill in:
   • Name: OneDrive Audit Tool
   • Redirect URI: http://localhost
   • Click "Register"

5. In the app page:
   • Copy the "Application (client) ID" - you'll need this
   • Go to "API permissions"
   • Click "Add a permission"
   • Select "Microsoft Graph"
   • Choose "Delegated permissions"
   • Search and add: "Files.ReadWrite.All"
   • Search and add: "offline_access"
   • Click "Grant admin consent"

Ready? (y/n): """, end="")

        if input().strip().lower() != "y":
            print("Setup cancelled.")
            return False

        self.client_id = self.input_prompt(
            "Enter your Client ID",
            required=True
        )

        return True

    def step_4_save_config(self):
        """Save configuration"""
        self.print_section("Saving Configuration")

        env_file = Path(".env")
        if env_file.exists():
            response = input(".env already exists. Overwrite? (y/n): ").strip().lower()
            if response != "y":
                print("Skipping .env creation")
                return True

        env_content = f"ONEDRIVE_CLIENT_ID={self.client_id}\nLOG_LEVEL=INFO\n"
        with open(".env", "w") as f:
            f.write(env_content)

        print("✓ Configuration saved to .env")
        return True

    def step_5_test_setup(self):
        """Test the setup"""
        self.print_section("Testing Setup")

        os.environ["ONEDRIVE_CLIENT_ID"] = self.client_id

        try:
            from onedrive_audit import OneDriveAuditor
            print("✓ OneDrive Audit module loaded")

            auditor = OneDriveAuditor(self.client_id)
            print("✓ OneDrive Auditor initialized")

            print("\nSetup test complete!")
            return True
        except Exception as e:
            print(f"✗ Setup test failed: {str(e)}")
            return False

    def step_6_next_steps(self):
        """Show next steps"""
        self.print_section("Setup Complete!")

        print("""
Your OneDrive Audit Tool is ready to use!

Next steps:

1. Run interactive mode:
   python onedrive_audit.py

2. Run command-line audit:
   python cli.py --full-audit

3. Try examples:
   python examples.py

4. Read documentation:
   - README.md - Full documentation
   - setup_guide.md - Detailed setup instructions

Common commands:
   • Scan: python cli.py --scan
   • Find duplicates: python cli.py --find-duplicates
   • Remove duplicates: python cli.py --remove-duplicates
   • Organize by type: python cli.py --organize type
   • Organize by date: python cli.py --organize date

For more help, visit:
https://github.com/yourusername/New-Project-2024

Happy auditing! 🎉
        """)

    def run(self):
        """Run the wizard"""
        try:
            self.step_1_welcome()

            if not self.step_2_check_requirements():
                print("\nPlease install missing requirements and try again.")
                return False

            if not self.step_3_azure_setup():
                return False

            if not self.step_4_save_config():
                return False

            if not self.step_5_test_setup():
                print("\nSetup test failed. Please check your configuration.")
                return False

            self.step_6_next_steps()
            self.setup_complete = True
            return True

        except KeyboardInterrupt:
            print("\n\nSetup cancelled by user.")
            return False
        except Exception as e:
            print(f"\n\nSetup error: {str(e)}")
            return False


def main():
    """Main entry point"""
    wizard = SetupWizard()
    success = wizard.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
