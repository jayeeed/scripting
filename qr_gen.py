import qrcode
import pandas as pd
import os
import re

# Input CSV file and output directory
input_csv = "qr.csv"
output_dir = "qr_codes"

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)


# Function to sanitize filenames
def sanitize_filename(filename):
    # Remove invalid characters for filenames
    return re.sub(r'[<>:"/\\|?*]', "_", filename)


# Read data from CSV
df = pd.read_csv(input_csv)

# Generate QR codes
for index, row in df.iterrows():
    data = row["data"]  # Column name in the CSV
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=1,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Create a sanitized filename and save the image
    sanitized_filename = sanitize_filename(data)
    filename = os.path.join(output_dir, f"{sanitized_filename}.png")
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)
    print(f"Generated QR code for: {data} -> {filename}")

print(f"QR codes saved in '{output_dir}'")
