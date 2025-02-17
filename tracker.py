tracking_url = "https://grabify.link/OW45BJ"
image_url = "./bird.jpg"

html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Tracking Image</title>
</head>
<body>
    <a href="{tracking_url}" style="display:none;">
        <img src="{image_url}" alt="Tracking Image" style="display:none;">
    </a>
</body>
</html>
"""

with open("tracking_image.html", "w") as file:
    file.write(html_content)

print("HTML file with tracking image created successfully.")
