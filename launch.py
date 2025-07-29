#!/usr/bin/env python3
"""
Shattered Worlds Skirmish - Mobile Game Launcher
This script handles mobile-specific initialization and launches the game.
"""

import os
import sys
from kivy.utils import platform

def setup_mobile_environment():
    """Set up mobile-specific environment variables and configurations."""
    if platform == 'android':
        # Android-specific setup
        os.environ['KIVY_GL_BACKEND'] = 'sdl2'
        os.environ['KIVY_WINDOW'] = 'sdl2'
        
        # Set up Android permissions (handled in buildozer.spec)
        print("Running on Android - mobile optimizations enabled")
        
    elif platform == 'ios':
        # iOS-specific setup
        os.environ['KIVY_GL_BACKEND'] = 'sdl2'
        print("Running on iOS - mobile optimizations enabled")
        
    else:
        # Desktop setup
        print("Running on desktop platform")

def main():
    """Main launcher function."""
    print("Shattered Worlds Skirmish - Starting...")
    
    # Set up mobile environment
    setup_mobile_environment()
    
    # Import and run the main app
    try:
        from main import VillageGameApp
        app = VillageGameApp()
        app.run()
    except ImportError as e:
        print(f"Error importing main app: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error running app: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 