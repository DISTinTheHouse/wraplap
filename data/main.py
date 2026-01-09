import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

# Configuration       
cloudinary.config( 
    cloud_name = "dokxn1l41", 
    api_key = "234721354322735", 
    api_secret = "OAuX0WH2j8cUGq1lsyfB36y1VBQ", # Click 'View API Keys' above to copy your API secret
    secure=True
)

# Upload an image
upload_result = cloudinary.uploader.upload("https://images.pokemontcg.io/sm3/20_hires.png",
                                           public_id="Charizard")
print(upload_result["secure_url"])

# Optimize delivery by resizing and applying auto-format and auto-quality
optimize_url, _ = cloudinary_url("Charizard", fetch_format="auto", quality="auto")
print(optimize_url)

# Transform the image: auto-crop to square aspect_ratio
auto_crop_url, _ = cloudinary_url("Charizard", width=500, height=500, crop="auto", gravity="auto")
print(auto_crop_url)