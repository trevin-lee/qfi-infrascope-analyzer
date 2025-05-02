# QFI Analyzer

A Python tool for analyzing and visualizing Quantum Focus Instruments (QFI) Infrascope data from text files.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

The QFI Analyzer processes text files containing QFI data in a specific format. The file should contain metadata in the header (lines starting with #) followed by comma-separated pixel values.

### Sample Data Format

```text
#Lens_Name: 4x MWIR
#Sensor_Name: MWIR-512
#Date: 04/04/2025
#FovX: 3239
#FovY: 2552
#Width: 640
#Height: 512
#StartFrame: 160
#EndFrame: 162
#Frames: 3
#StartTime: 16010.92
#EndTime: 16210.92

45.0913,45.1154,45.0823,...
```

### Basic Usage

```python
from qfi_analyzer import QFIAnalyzer

# Initialize the analyzer with a data file
analyzer = QFIAnalyzer("path/to/your/data.txt", verbose=True)

# Generate a GIF animation
analyzer.generate_gif(
    save_to="./output",
    file_name="qfi_video.gif",
    fps=30
)

# Generate individual frame images
analyzer.generate_image(
    save_to="./output",
    file_name="qfi_frame.png"
)

# Get pixel value at specific position
value = analyzer.get_pixel_value(frame=0, height=100, width=100)

# Get frame statistics
max_value = analyzer.maximum_value_in_frame(frame=0)
min_value = analyzer.minimum_value_in_frame(frame=0)
avg_value = analyzer.average_value_in_frame(frame=0)

# Get entire frame data
frame_data = analyzer.get_frame(frame=0)
```

### Features

- Parse QFI data files with metadata and pixel arrays
- Generate GIF animations from the data using Pillow
- Create individual frame images
- Access pixel values at specific positions
- Calculate frame statistics (max, min, average)
- Extract complete frame data

### Frame Analysis Methods

The analyzer provides several methods for analyzing frame data:

- `get_pixel_value(frame, height, width)`: Get value at specific position
- `maximum_value_in_frame(frame)`: Get maximum value in frame
- `minimum_value_in_frame(frame)`: Get minimum value in frame
- `average_value_in_frame(frame)`: Get average value in frame
- `get_frame(frame)`: Get complete frame data as numpy array

### Output

The analyzer can generate:
- GIF animations (.gif) using Pillow
- Individual frame images (.png)
- Frame statistics and pixel data

## Requirements

- Python 3.6+
- numpy>=1.21.0
- matplotlib>=3.4.0
- pillow>=9.0.0

## Error Handling

The analyzer includes comprehensive error handling for:
- File not found errors
- Invalid metadata format
- Pixel count mismatches
- Out of bounds frame/position access
- Missing pixel array data
- Invalid file extensions
