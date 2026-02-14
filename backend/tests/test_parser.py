from modules.prescription_parser import parse_prescription
from modules.ocr import extract_text_from_image

text = extract_text_from_image("d:\\vs code\\Medical_Chatbot\\backend\\tests\\original.jpg")

result = parse_prescription(text)

print(result)
