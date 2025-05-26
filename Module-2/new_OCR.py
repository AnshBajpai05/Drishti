import easyocr

reader = easyocr.Reader(['en'], gpu=False)

def ocr(frame):
    results = reader.readtext(frame)
    return results  # <-- Add this line

