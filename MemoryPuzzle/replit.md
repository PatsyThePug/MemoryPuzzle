# Memory Card Game

## Overview

This is a memory card matching game built with Python and Pygame. The game presents a 4x4 grid of cards that players flip to find matching pairs. The application features a simple graphical interface with card flip animations and color-coded pairs for an engaging memory challenge experience.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Game Engine Architecture
- **Framework**: Built on Pygame for 2D graphics and game loop management
- **Game State**: Single-threaded game loop with FPS-controlled rendering at 60 FPS
- **Grid System**: 4x4 static grid layout with fixed card positioning using coordinate calculations

### Rendering System
- **Graphics**: 2D sprite-based rendering using Pygame's drawing primitives
- **Animation**: Simple flip animation system using progress-based interpolation
- **Color Palette**: Predefined color scheme with primary colors and variations for card identification

### Game Logic Architecture
- **Card Management**: Object-oriented card system with individual state tracking (flipped, matched, animation)
- **Pair Matching**: ID-based pairing system where each card has a unique pair_id for match validation
- **Game Flow**: Event-driven input handling with mouse interaction for card selection

### Data Structures
- **Card Class**: Encapsulates card properties including position, color, state, and animation progress
- **Grid Layout**: Mathematical positioning system using card size and margin constants
- **State Management**: Boolean flags for card states (is_flipped, is_matched) with animation timing

## External Dependencies

### Core Libraries
- **Pygame**: Primary game development framework for graphics, input handling, and game loop
- **Random**: Built-in Python module for card shuffling and game randomization
- **Time**: Built-in Python module for timing and animation control
- **Sys**: Built-in Python module for system operations and game exit handling

### System Requirements
- **Python**: Requires Python runtime environment
- **Display**: Windowed application requiring 800x600 pixel display capability
- **Input**: Mouse input support for card interaction