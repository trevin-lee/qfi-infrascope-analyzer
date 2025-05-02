from typing import Dict, Any, Optional
import os
from pathlib import Path

import numpy as np
from numpy.typing import NDArray
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.animation import PillowWriter

class QFIAnalyzer:
    """
    A class for analyzing QFI (Quantum Fisher Information) data from text files.
    
    This class parses QFI data files containing metadata and pixel arrays, and provides
    methods for visualization and analysis of the data.
    """

    def __init__(self, file_path: str, verbose: bool = False):
        """
        Initialize the QFI Analyzer.

        Args:
            file_path: Path to the QFI data file
            verbose: Whether to print debug information
        """
        self.verbose = verbose
        self.file_path = file_path

        self.metadata: Dict[str, Any] = {}
        self.pixel_array: Optional[NDArray] = None

        try:
            with open(self.file_path, 'r') as f:
                self.text_file_lines = f.readlines()
        except FileNotFoundError:
            raise FileNotFoundError(f"QFI data file not found: {file_path}")
        except Exception as e:
            raise RuntimeError(f"Error reading QFI data file: {str(e)}")

        self._parse_metadata()
        self._parse_pixel_array()

    def _parse_metadata(self) -> None:
        """
        Parse metadata from the text file lines.
        
        Metadata is expected to be in the format: #Key: Value
        """
        for line in self.text_file_lines:
            line = line.strip()
            if line.startswith("#"):
                try:
                    parts = line[1:].split(":", 1)
                    if len(parts) == 2:
                        key, value = parts[0].strip(), parts[1].strip()
                        self.metadata[key] = value
                except Exception as e:
                    if self.verbose:
                        print(f"Warning: Failed to parse metadata line: {line}")
                        print(f"Error: {str(e)}")

        if self.verbose:
            print("Parsed Metadata:")
            for key, value in self.metadata.items():
                print(f"{key}: {value}")

    def _parse_pixel_array(self) -> None:
        """
        Parse pixel array data from the text file lines.
        
        The pixel data is expected to be comma-separated values.
        """
        data_lines = []
        for line in self.text_file_lines:
            line = line.strip()
            if not line.startswith("#") and line:
                data_lines.append(line)

        try:
            data_string = "".join(data_lines)
            pixel_strings = [s for s in data_string.split(",") if s]
            pixels = np.array(list(map(float, pixel_strings)))

            width = int(self.metadata.get('Width'))
            height = int(self.metadata.get('Height'))
            frames = int(self.metadata.get('Frames'))

            expected_pixels = width * height * frames

            if self.verbose:
                print(
                    f"Expected pixels (Width x Height x Frames): "
                    f"{width} x {height} x {frames} = {expected_pixels}"
                )
                print(f"Total pixels found in file: {pixels.size}")

            if pixels.size != expected_pixels:
                raise ValueError(
                    f"Pixel count ({pixels.size}) does not match "
                    f"expected size ({expected_pixels}). "
                    f"This may be due to a mismatch between the metadata and "
                    f"the number of pixel values in the file."
                )

            self.pixel_array = pixels.reshape((frames, height, width))
        except Exception as e:
            raise RuntimeError(f"Error parsing pixel array: {str(e)}")

    def generate_gif(
            self, 
            save_to: str = "./", 
            file_name: str = "qfi_video.gif", 
            fps: int = 30
        ) -> None:
        """
        Generate a gif animation from the pixel array.

        Args:
            save_to: Directory to save the gif
            file_name: Name of the output file
            fps: Frames per second
        """
        if not self.pixel_array is not None:
            raise RuntimeError("No pixel array data available")
        
        if not file_name.endswith(".gif"):
            print(
                f"Warning: File name must have a .gif extension. "
                f"Changing to {file_name}.gif"
            )
            file_name = f"{file_name}.gif"

        save_path = Path(save_to)
        save_path.mkdir(parents=True, exist_ok=True)

        fig, ax = plt.subplots()
        im = ax.imshow(self.pixel_array[0], cmap='viridis')
        plt.colorbar(im)

        def update(frame_index):
            """Update function for animation."""
            im.set_data(self.pixel_array[frame_index])
            ax.set_title(f"Frame {frame_index+1}")
            return [im]

        ani = animation.FuncAnimation(
            fig, 
            update, 
            frames=self.pixel_array.shape[0], 
            interval=1000//fps, 
            blit=False
        )

        output_path = save_path / file_name
        writer = PillowWriter(fps=fps)
        ani.save(str(output_path), writer=writer)
        plt.close(fig)

        print(f"Saved gif to {save_path / file_name}")

    def generate_image(
            self, 
            save_to: str = "./", 
            frame: int = 0,
            file_name: str = "qfi_frame.png"
        ) -> None:
        """
        Generate individual frame image from the pixel array.

        Args:
            save_to: Directory to save the image
        """

        if not file_name.endswith(".png"):
            print(
                f"Warning: File name must have a .png extension. "
                f"Changing to {file_name}.png"
            )
            file_name = f"{file_name}.png"

        if not self.pixel_array is not None:
            raise RuntimeError("No pixel array data available")

        save_path = Path(save_to)
        save_path.mkdir(parents=True, exist_ok=True)

        plt.imshow(self.pixel_array[frame], cmap='viridis')
        plt.colorbar()
        plt.savefig(save_path / file_name)
        plt.close()

        print(f"Saved image to {save_path / file_name}")
        

    def get_pixel_value(self, frame: int, height: int, width: int) -> float:
        """
        Get the pixel value at a specific position.

        Args:
            frame: Frame index
            height: Height position
            width: Width position

        Returns:
            float: Pixel value at the specified position

        Raises:
            ValueError: If the indices are out of bounds
        """

        if not self.pixel_array is not None:
            raise RuntimeError("No pixel array data available")

        metadata_height = int(self.metadata.get('Height'))
        metadata_width = int(self.metadata.get('Width'))
        metadata_frames = int(self.metadata.get('Frames'))

        if height >= metadata_height:
            raise ValueError(
                f"Height ({height}) is greater than or "
                f"equal to the maximum allowed height ({metadata_height})."
            )

        if width >= metadata_width:
            raise ValueError(
                f"Width ({width}) is greater than or "
                f"equal to the maximum allowed width ({metadata_width})."
            )

        if frame >= metadata_frames:
            raise ValueError(
                f"Frame ({frame}) is greater than or "
                f"equal to the maximum allowed frame ({metadata_frames})."
            )

        return self.pixel_array[frame, height, width]
    
    def maximum_value_in_frame(self, frame: int) -> float:
        """
        Get the maximum pixel value in a specific frame.

        Args:
            frame: Frame index  

        Returns:
            float: Maximum pixel value in the specified frame

        Raises:
            RuntimeError: If no pixel array data is available
        """
        if not self.pixel_array is not None:
            raise RuntimeError("No pixel array data available")

        return np.max(self.pixel_array[frame])
    
    def minimum_value_in_frame(self, frame: int) -> float:
        """
        Get the minimum pixel value in a specific frame.

        Args:
            frame: Frame index  

        Returns:
            float: Minimum pixel value in the specified frame

        Raises:
            RuntimeError: If no pixel array data is available
        """
        if not self.pixel_array is not None:
            raise RuntimeError("No pixel array data available")

        return np.min(self.pixel_array[frame])
    
    def average_value_in_frame(self, frame: int) -> float:
        """
        Get the average pixel value in a specific frame.

        Args:
            frame: Frame index

        Returns:
            float: Average pixel value in the specified frame

        Raises:
            RuntimeError: If no pixel array data is available
        """
        if not self.pixel_array is not None:
            raise RuntimeError("No pixel array data available")

        return np.mean(self.pixel_array[frame])
    
    def get_frame_array(self, frame: int) -> NDArray:
        """
        Get a specific frame from the pixel array.

        Args:
            frame: Frame index

        Returns:
            NDArray: The specified frame from the pixel array

        Raises:
            RuntimeError: If no pixel array data is available
        """ 
        if not self.pixel_array is not None:
            raise RuntimeError("No pixel array data available")

        return self.pixel_array[frame]
    
        
    

    
    
