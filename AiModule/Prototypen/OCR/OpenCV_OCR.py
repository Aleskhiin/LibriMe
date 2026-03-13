import shutil
import platform
import cv2
from matplotlib import pyplot as plt
import os
import pytesseract

# Set the path to the Tesseract executable



def configure_tesseract():
    """
    Configures the Tesseract executable path based on the operating system.
    Supports Windows, Linux, and macOS.
    Raises an error if Tesseract is not found.
    """
    system = platform.system()  # <- This calls the function from the module

    if system == "Windows":
        path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        pytesseract.pytesseract.tesseract_cmd = path
        if not shutil.which(path):
            print("Warning: Default Tesseract path not found. Please verify installation.")

    elif system in ["Linux", "Darwin"]:  # Linux or macOS
        tesseract_path = shutil.which("tesseract")
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        else:
            raise FileNotFoundError(
                "Tesseract not found. Please install it:\n"
                "- Linux: sudo apt install tesseract-ocr\n"
                "- macOS: brew install tesseract"
            )
    else:
        raise OSError(f"Unsupported operating system: {system}")




def load_image(image_path: str):
    """
    Loads an image from the specified path and converts it to RGB format.

    Args:
        image_path (str): Path to the image file.

    Returns:
        tuple: Original BGR image and RGB image.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at: {os.path.abspath(image_path)}")
    
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image, image_rgb

def convert_to_grayscale(image):
    """
    Converts a BGR image to grayscale.

    Args:
        image: BGR image.

    Returns:
        Grayscale image.
    """
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def show_image_cv2(window_name: str, image):
    """
    Displays an image using Matplotlib instead of OpenCV (cv2.imshow),
    because GUI support may not be available.
    """
    plt.figure(figsize=(10, 6))
    if len(image.shape) == 2:  # Grayscale
        plt.imshow(image, cmap='gray')
    else:
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.title(window_name)
    plt.axis("off")
    plt.show()


def show_image_matplotlib(image, title: str, cmap=None):
    """
    Displays an image using Matplotlib.

    Args:
        image: Image to display.
        title (str): Title of the plot.
        cmap: Optional colormap (e.g., 'gray').
    """
    plt.figure(figsize=(10, 6))
    plt.imshow(image, cmap=cmap)
    plt.title(title)
    plt.axis("off")
    plt.show()

def extract_text(image_rgb):
    """
    Extracts text from an RGB image using Tesseract OCR.

    Args:
        image_rgb: RGB image.

    Returns:
        str: Extracted text.
    """
    return pytesseract.image_to_string(image_rgb)

def draw_text_boxes(image_rgb):
    """
    Draws bounding boxes around detected text in an RGB image.

    Args:
        image_rgb: RGB image.

    Returns:
        Image with bounding boxes.
    """
    data = pytesseract.image_to_data(image_rgb, output_type=pytesseract.Output.DICT)
    n_boxes = len(data['level'])
    for i in range(n_boxes):
        x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
        cv2.rectangle(image_rgb, (x, y), (x + w, y + h), (255, 0, 0), 2)
    return image_rgb

if __name__ == "__main__":
    configure_tesseract()
    # Basisverzeichnis = Ordner des aktuellen Skripts
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Bildpfad dynamisch ermitteln
    image_path = os.path.join(base_dir, "Images", "example3.png")
    
    print(f"Looking for image at: {image_path}")

    image, image_rgb = load_image(image_path)
    gray = convert_to_grayscale(image)

    show_image_cv2("Grayscale Image", gray)
    show_image_matplotlib(image_rgb, "Original Image")

    text = extract_text(image_rgb)
    print("Extracted Text:\n")
    print(text)

    boxed_image = draw_text_boxes(image_rgb)
    show_image_matplotlib(boxed_image, "Image with Text Bounding Boxes")

