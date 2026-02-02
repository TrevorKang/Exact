"""
Scripts for MP4 files's support
Reference: https://github.com/DeepMicroscopy/Exact/commit/4d52b614fa41328bf08367d99e088c1e838fb05a

"""
import openslide
from openslide import OpenSlideError
import numpy as np
import cv2
from PIL import Image
try :
    from util.enums import FrameType
except ImportError:
    from enums import FrameType

import matplotlib.pyplot as plt


class ReadableMP4Dataset(openslide.ImageSlide):
    def __init__(self, filename):
        self.slide_path = filename
        cap = cv2.VideoCapture(filename)
        if not cap.isOpened():
            raise OpenSlideError(f"Could not open video file: {filename}")
        # Get video properties
        self._width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self._height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.numberOfLayers = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))    # total number of frames
        self.fps = cap.get(cv2.CAP_PROP_FPS)

        # Video codec info
        fourcc = int(self.cap.get(cv2.CAP_PROP_FOURCC))
        self.codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])

        cap.release()

        self._dimensions = (self._width, self._height)
    
    def __reduce__(self):
        return (self.__class__, (self.slide_path,))
    
    @property
    def dimensions(self):
        return self._dimensions

    @property
    def frame_descriptors(self) -> list[str]:
        """ returns a list of strings, used as descriptor for each frame
        """
        return ['%.2f' % (x/self.fps) for x in range(self.nFrames)]

    @property
    def frame_type(self):
        return FrameType.TIMESERIES

    @property
    def default_frame(self) -> list[str]:
        return 0

    @property 
    def nFrames(self):
        return self.numberOfLayers
    
    @property
    def level_dimensions(self):
        return (self.dimensions,)

    @property
    def level_count(self):
        return 1 


    def get_thumbnail(self, size):
        return self.read_region((0,0),0, self.dimensions).resize(size)
    
    def read_region(self, location, level, size, frame=0):
        """
        Reads a region from a specific video frame. 
        Return a PIL.Image containing the contents of the region.

        location: (x, y) tuple giving the top left pixel in the level 0
                  reference frame.
        level:    the level number.
        size:     (width, height) tuple giving the region size.
        frame:    the frame index to read from the video.

        """
        if level != 0:
            raise OpenSlideError("Only level 0 is supported for video files.")
        
        if any(s < 0 for s in size):
            raise OpenSlideError(f"Size {size} must be non-negative")

        # Clamp frame index
        frame = max(0, min(frame, self.numberOfLayers - 1))

        # Re-open capture for the read (or use a pooled capture for performance)
        cap = cv2.VideoCapture(self.slide_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame)
        success, img = cap.read()
        cap.release()

        if not success:
            # Return a transparent tile if frame read fails
            return Image.new("RGBA", size, (0, 0, 0, 0))

        # Convert BGR (OpenCV) to RGBA (OpenSlide/PIL)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
        
        # Calculate boundaries (handling out-of-bounds requests)
        x, y = location
        w, h = size
        
        # Create the transparent canvas
        tile = Image.new("RGBA", size, (0, 0, 0, 0))
        
        # Calculate crop boundaries within the source image
        img_h, img_w = img_rgb.shape[:2]
        
        # Source coordinates
        src_x1 = max(0, min(x, img_w))
        src_y1 = max(0, min(y, img_h))
        src_x2 = max(0, min(x + w, img_w))
        src_y2 = max(0, min(y + h, img_h))
        
        # Destination coordinates (where to paste on the tile)
        dst_x1 = max(0, -x) if x < 0 else 0
        dst_y1 = max(0, -y) if y < 0 else 0
        
        # Extract the crop using numpy slicing
        crop_data = img_rgb[src_y1:src_y2, src_x1:src_x2]
        
        if crop_data.size > 0:
            crop_img = Image.fromarray(crop_data)
            tile.paste(crop_img, (dst_x1, dst_y1))
            
        return tile

    def get_duration(self):
        """Get the length of the video in seconds."""
        return self.numberOfLayers / self.fps if self.fps > 0 else 0
    
    def time_to_frame(self, time_seconds: float) -> int:
        """Convert time in seconds to frame index."""
        frame_idx = int(time_seconds * self.fps)
        return max(0, min(frame_idx, self.numberOfFrames - 1))

    def frame_to_time(self, frame_idx: int) -> float:
        """Convert frame index to time in seconds."""
        return frame_idx / self.fps if self.fps > 0 else 0
    
if __name__ == "__main__":
    video_path = "./test_mp4/test.mp4"
    slide = ReadableMP4Dataset(video_path)
    print(f"Video dimensions: {slide.dimensions}")
    print(f"Number of frames: {slide.nFrames}")
    thumbnail = slide.get_thumbnail((256, 256))
    
    plt.imshow(thumbnail)
    plt.axis('off')
    plt.savefig('thumbnail.png', bbox_inches='tight')
    print("Saved to thumbnail.png")