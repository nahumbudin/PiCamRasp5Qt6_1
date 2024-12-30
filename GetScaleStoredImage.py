import numpy as np
from PIL import Image
from numpy import asarray


def get_scale_stored_image(image_file_full_path):
    captured_image_file = Image.open(image_file_full_path)
    image_array = asarray(captured_image_file)

    # Convert rgb to bgr
    image_array = image_array[..., ::-1].copy()
    # Captured image shape is 4056x3040. Pad to fit display shape of 1200x800
    padded_image = np.empty([3040, 5056, 3], dtype=np.uint8)
    padded_image[:, :] = np.array([64, 64, 64])
    padded_image[0:3040, 500:4556] = image_array

    return padded_image
