# For Windows PowerShell:
docker run -it --env-file ./.env -v "$((Get-Location).Path -replace '\\', '/')/pdf:/app/pdf" -v "$((Get-Location).Path -replace '\\', '/')/images:/app/images" myproject

# For Windows CMD:
docker run -it --env-file ./.env -v "%cd%/pdf:/app/pdf" -v "%cd%/images:/app/images" myproject

# For Linux/Mac:
docker run -it --env-file ./.env -v "$(pwd)/pdf:/app/pdf" -v "$(pwd)/images:/app/images" myproject

# Alternative for Windows (using absolute path):
# Replace C:/Users/YourUsername with your actual path
docker run -it --env-file ./.env -v "C:/Users/aswin/Documents/oneNote_AI/pdf:/app/pdf" -v "C:/Users/aswin/Documents/oneNote_AI/images:/app/images" myproject


# JJ : 
docker run -it --env-file ./.env -v "%cd%/pdf:/app/pdf" -v "%cd%/images:/app/images" myproject

