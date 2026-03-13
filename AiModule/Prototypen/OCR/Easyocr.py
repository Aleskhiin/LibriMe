import easyocr
import torch
import os

def check_gpu():
    """
    Checks if a CUDA-compatible GPU is available.

    Returns:
        bool: True if GPU is available, False otherwise.
    """
    use_gpu = torch.cuda.is_available()
    print(f"Using GPU: {use_gpu}")
    return use_gpu

def create_reader(language_list, use_gpu):
    """
    Creates an EasyOCR reader for the specified languages.

    Args:
        language_list (list): List of language codes (e.g., ['de']).
        use_gpu (bool): Whether to use GPU acceleration.

    Returns:
        easyocr.Reader: Initialized OCR reader.
    """
    return easyocr.Reader(language_list, gpu=use_gpu)

def run_ocr(reader, image_path):
    """
    Runs OCR on the specified image using the provided reader.

    Args:
        reader (easyocr.Reader): OCR reader instance.
        image_path (str): Path to the image file.

    Returns:
        list: OCR results containing bounding boxes, text, and confidence scores.
    """
    return reader.readtext(image_path, detail=1)

def print_results(results):
    """
    Prints the OCR results to the console.

    Args:
        results (list): List of tuples containing bounding box, text, and confidence.
    """
    for (bbox, text, prob) in results:
        print(f"Detected: {text} (Confidence: {prob:.2f})")

def main():
    image_path = os.path.join("Image", "example3.png")
    use_gpu = check_gpu()
    reader = create_reader(['de'], use_gpu)
    results = run_ocr(reader, image_path)
    print_results(results)

if __name__ == "__main__":
    main()