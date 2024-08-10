# Custom Digital Filter Designer 

## Overview
This desktop application allows users to design custom digital filters by placing zeros and poles on the z-plane. The application provides a visual interface to create and modify filters and analyze their frequency response. Additionally, users can apply the designed filter to a signal and observe the filtering process in real-time. 
![Real-Time Filtering](https://github.com/user-attachments/assets/d8fe692b-9325-4174-bde5-5f37f37d9a5a)
## Features

### 1. Z-Plane Plot with Unit Circle
- **Interactive Z-Plane Plot**: A graphical representation of the z-plane, complete with a unit circle. Users can place zeros and poles directly on the plot.
- **Modify Zeros/Poles**:
  - Drag and drop existing zeros/poles to new positions.
  - Click on a zero or pole to delete it.
  - Clear all zeros, all poles, or both.
  - Optionally add conjugates for complex zeros/poles.

### 2. Frequency Response Visualization
- **Magnitude Response Plot**: A graph that displays the magnitude response of the filter based on the current placement of zeros and poles.
- **Phase Response Plot**: A graph showing the phase response corresponding to the filter design.

### 3. Real-Time Filtering
![Real-Time Filtering](https://github.com/user-attachments/assets/91702ed8-2f17-4101-8955-7a31d847a251)
- **Signal Processing**: Apply the designed filter to a lengthy signal (minimum 10,000 points) and visualize the filtering process in real-time.
- **Time Progress Graphs**:
  - View the progress of the original signal over time.
  - Observe the filtered signal as the filter is applied point by point.
- **Speed Control**: Adjust the processing speed of the filtering using a slider, ranging from 1 point per second to 100 points per second.
- **Real-Time Signal Input**:
  - Generate a real-time signal by moving the mouse within a small area.
  - The x- or y-coordinate of the mouse controls the input signal's frequency content (faster motion → higher frequencies, slower motion → lower frequencies).

### 4. Phase Correction with All-Pass Filters
- **All-Pass Filter Library**:
  - Visualize and select from a library of pre-built all-pass filters, with details on their zero-pole placement and phase response.
- **Custom All-Pass Filter Creation**:
  - Create a custom all-pass filter by specifying an arbitrary parameter “a.” The application will calculate and display its phase response and integrate it into the library.
- **Enable/Disable All-Pass Filters**: Manage the added all-pass filters through a drop-down menu or checkboxes.

## Getting Started
1. **Install the Application**: Follow the installation instructions specific to your operating system.
2. **Launch the Application**: Open the application from your desktop or application menu.
3. **Design Your Filter**: Use the z-plane plot to place zeros and poles, then modify them as needed.
4. **Analyze Frequency Response**: Observe the corresponding magnitude and phase responses on the provided plots.
5. **Apply the Filter**: Load or generate a signal and apply the designed filter in real-time, adjusting the processing speed as needed.
6. **Phase Correction**: If necessary, use the all-pass filter library or create a custom all-pass filter to correct the phase response.

---

Feel free to reach out for support or additional information. Happy filtering!
