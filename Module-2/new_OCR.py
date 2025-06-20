import easyocr

reader = easyocr.Reader(['en'], gpu=True)

def ocr(frame):
    results = reader.readtext(frame)
    return results  # <-- Add this line
