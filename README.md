# wheelOfOpportunity
a fair and balanced spinning wheel of picking people

# Wheel of Opportunity - Spinning Wheel Application

## Description

This Python application provides a visual spinning wheel to randomly select a name from a user-provided list. It also allows users to enter Change Request (CR) numbers and assign the selected name to a chosen CR. The application features a Minecraft-inspired visual theme, animations, and firework effects upon selection.

## Features

*   **Spinning Wheel:** A visually animated wheel divided into slices, one for each entered name.
*   **Name Input:** Enter names one by one into the designated input box (bottom-left).
*   **CR Input:** Enter Change Request numbers/identifiers into a separate input box (bottom-right).
*   **CR List:** Displays the last 8 entered CRs. Clicking a CR in this list selects it for assignment.
*   **Assignment:** When the wheel stops, the selected name is automatically assigned to the currently selected CR (if any). Assignments are displayed in a dedicated box.
*   **Visual Theme:** Minecraft-inspired colors and blocky UI elements.
*   **Animation:** Smooth spinning animation with friction.
*   **Celebration:** Firework particle effects appear when the wheel selects a name.

## Requirements

*   Python 3.x
*   Pygame library

## Installation

1.  **Install Python:** If you don't have Python installed, download and install it from [python.org](https://www.python.org/).
2.  **Install Pygame:** Open your terminal or command prompt and run:
    ```bash
    pip install pygame
    ```

## How to Run

1.  Navigate to the directory containing the `spinning_wheel.py` file in your terminal. For example:
    ```bash
    cd c:\Users\Public\code\wheel
    ```
2.  Run the script using Python:
    ```bash
    python spinning_wheel.py
    ```

## How to Use

1.  **Enter Names:** Click inside the bottom-left input box (labeled "TYPE NAMES HERE:") and type a name. Press `Enter` after each name.
2.  **Enter CRs:** Click inside the bottom-right input box (labeled "ENTER CR:") and type a CR identifier. Press `Enter` after each CR. The list will only keep the latest 8 CRs entered.
3.  **Select CR:** Click on a CR listed in the "CRs:" box (top-right) to select it for the next assignment. The selected CR will be highlighted.
4.  **Spin the Wheel:** Press the `Spacebar` to start spinning the wheel.
5.  **Assignment:** When the wheel stops, the selected name will be displayed in the top-left instructions and assigned to the currently selected CR in the "Assignments:" box (middle-right).
6.  **Quit:** Close the application window.