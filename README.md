# Shattered Worlds Skirmish Game

A tactical turn-based mobile game built with Python and Kivy.

## Features

- **Multi-Unit Combat**: Select and manage your army of units
- **Turn-Based Tactics**: Strategic combat with alternating turns
- **Custom Dice System**: Each unit type has unique dice for combat
- **Unit Types**:
  - **Warrior**: Balanced fighter with standard dice
  - **Runeguard**: Defensive specialist with more shields
  - **Arcane Archer**: Offensive ranged unit with more swords
  - **Cleric**: Support unit that can heal allies
- **Pulse Resource**: Special abilities powered by Pulse points
- **Village Upgrades**: Unlock new features and abilities
- **Save System**: Persistent army and progress

## Installation

### For Android Users

1. Download the latest APK from the [Releases](https://github.com/yourusername/shattered-worlds-skirmish/releases) page
2. Enable "Install from Unknown Sources" in your Android settings
3. Install the APK file

### For Developers

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/shattered-worlds-skirmish.git
   cd shattered-worlds-skirmish
   ```

2. Install dependencies:
   ```bash
   pip install kivy pillow
   ```

3. Run the game:
   ```bash
   python main.py
   ```

## Building for Android

The project uses GitHub Actions to automatically build APKs. Every push to the main branch triggers a new build.

To build manually:
1. Install buildozer: `pip install buildozer`
2. Run: `buildozer android debug`

## Game Controls

- **Tap units** to select them
- **Tap highlighted tiles** to move or attack
- **Use action buttons** (Stay, Pass, Info, Cancel) for unit actions
- **Special abilities** are available when you have enough Pulse points

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 