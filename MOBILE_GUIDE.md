# Mobile Development Quick Start Guide

## Quick Setup for Android

### 1. Install Dependencies (Ubuntu/Debian)
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3-pip build-essential git python3 python3-dev
sudo apt-get install -y libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
sudo apt-get install -y libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev

# Install Python dependencies
pip3 install kivy buildozer pillow
```

### 2. Install Android SDK
```bash
# Download Android Studio
wget https://developer.android.com/studio/command-line/linux

# Or install via package manager
sudo apt-get install android-studio

# Set environment variables
export ANDROID_HOME=$HOME/Android/Sdk
export ANDROID_NDK_HOME=$ANDROID_HOME/ndk/19.2.5345600
export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools
```

### 3. Build and Deploy
```bash
# Initialize buildozer (if not already done)
buildozer init

# Build debug APK
buildozer android debug

# Deploy to connected device
buildozer android debug deploy

# Run on device
buildozer android debug deploy run
```

## Quick Setup for iOS

### 1. Install Xcode
- Download and install Xcode from App Store
- Install Command Line Tools: `xcode-select --install`

### 2. Install Kivy-iOS
```bash
pip3 install kivy-ios
```

### 3. Build for iOS
```bash
# Build the toolchain
toolchain build kivy

# Run on simulator
toolchain run kivy

# Or build for device (requires developer account)
toolchain build kivy --device
```

## Testing on Mobile

### Android Testing
1. Enable Developer Options on your Android device
2. Enable USB Debugging
3. Connect device via USB
4. Run: `buildozer android debug deploy run`

### iOS Testing
1. Open Xcode
2. Connect iOS device
3. Trust the developer certificate
4. Run: `toolchain run kivy`

## Mobile Optimization Checklist

### UI/UX
- [ ] Touch targets are at least 44dp
- [ ] Font sizes are readable on small screens
- [ ] Buttons have proper spacing
- [ ] Scrolling works smoothly
- [ ] No horizontal scrolling needed

### Performance
- [ ] Images are optimized for mobile
- [ ] Grid rendering is efficient
- [ ] Memory usage is reasonable
- [ ] App starts quickly
- [ ] No lag during gameplay

### Platform Specific
- [ ] Android: Status bar handling
- [ ] iOS: Safe area considerations
- [ ] Both: Orientation handling
- [ ] Both: Touch input responsiveness

## Common Issues and Solutions

### Buildozer Issues
```bash
# Clean build
buildozer android clean

# Update buildozer
pip install --upgrade buildozer

# Check dependencies
buildozer android debug -v
```

### Android SDK Issues
```bash
# Accept licenses
yes | sdkmanager --licenses

# Install specific API level
sdkmanager "platforms;android-28"

# Update SDK tools
sdkmanager --update
```

### Performance Issues
- Reduce image sizes
- Use efficient data structures
- Profile memory usage
- Test on actual devices

## Development Workflow

1. **Desktop Development**: Use `python main.py` for quick testing
2. **Mobile Testing**: Use `buildozer android debug deploy run` for Android
3. **Iterative Development**: Make changes, test on desktop, then mobile
4. **Performance Testing**: Always test on actual devices

## Useful Commands

```bash
# Check connected devices
adb devices

# Install APK manually
adb install bin/shatteredworlds-0.1-debug.apk

# View logs
adb logcat | grep python

# Clean and rebuild
buildozer android clean
buildozer android debug

# Update dependencies
buildozer android update
```

## Tips for Mobile Development

1. **Test Early, Test Often**: Don't wait until the end to test on mobile
2. **Use Real Devices**: Emulators don't always catch mobile-specific issues
3. **Optimize for Touch**: Design for finger input, not mouse
4. **Consider Battery**: Mobile games should be battery-friendly
5. **Handle Interruptions**: Pause game when app goes to background

## Next Steps

1. Add sound effects and music
2. Implement save/load functionality
3. Add more unit types and abilities
4. Create multiple battle maps
5. Add multiplayer features
6. Implement in-app purchases (if monetizing) 