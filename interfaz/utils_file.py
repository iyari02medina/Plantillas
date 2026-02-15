def optimize_and_save_file(file_obj, destination_folder, base_filename):
    """
    Saves a file to destination_folder with base_filename + extension.
    Optimizes images (resizes to 1600px max, converts to JPG, compresses <1MB).
    Optimizes PDFs (compresses using pypdf if available).
    
    Returns:
        tuple: (final_filename_with_extension, status_message_or_None)
    """
    import os
    from werkzeug.utils import secure_filename
    from PIL import Image
    
    original_filename = secure_filename(file_obj.filename)
    ext = os.path.splitext(original_filename)[1].lower()
    
    # 0. Determine Target Filename with Uniqueness
    target_ext = ext
    if ext in ['.jpg', '.jpeg', '.png', '.webp', '.bmp']:
        target_ext = '.jpg'
        
    candidate_name = f"{base_filename}{target_ext}"
    candidate_path = os.path.join(destination_folder, candidate_name)
    
    counter = 1
    while os.path.exists(candidate_path):
        candidate_name = f"{base_filename}_{counter}{target_ext}"
        candidate_path = os.path.join(destination_folder, candidate_name)
        counter += 1
        
    final_filename = candidate_name
    save_path = candidate_path

    # 1. Image Logic
    if ext in ['.jpg', '.jpeg', '.png', '.webp', '.bmp']:
        try:
            # save_path and final_filename are already set above
            
            img = Image.open(file_obj)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
                
            # Resize
            max_dim = 1600
            if img.width > max_dim or img.height > max_dim:
                img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
            
            # Compress Loop < 1MB
            target_size = 1024 * 1024
            quality = 90
            step = 10
            min_quality = 30
            
            # Initial Save
            img.save(save_path, "JPEG", quality=quality, optimize=True, dpi=(150, 150))
            
            while os.path.getsize(save_path) > target_size and quality > min_quality:
                quality -= step
                img.save(save_path, "JPEG", quality=quality, optimize=True, dpi=(150, 150))
                
            return final_filename, "Imagen optimizada"
        except Exception as e:
            print(f"Error optimizing image: {e}")
            # Fallback
            final_filename = f"{base_filename}{ext}"
            save_path = os.path.join(destination_folder, final_filename)
            file_obj.seek(0)
            file_obj.save(save_path)
            return final_filename, "Error optimizando imagen (guardado original)"

    # 2. PDF Logic
    elif ext == '.pdf':
        file_obj.save(save_path)
        
        # Compress if > 1MB
        try:
            if os.path.getsize(save_path) > 1 * 1024 * 1024:
                import pypdf
                reader = pypdf.PdfReader(save_path)
                writer = pypdf.PdfWriter()
                for page in reader.pages:
                    writer.add_page(page)
                writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)
                
                temp_path = save_path + ".temp"
                with open(temp_path, "wb") as f:
                    writer.write(f)
                
                if os.path.getsize(temp_path) < os.path.getsize(save_path):
                    os.replace(temp_path, save_path)
                    return final_filename, "PDF comprimido"
                else:
                    os.remove(temp_path)
                    return final_filename, "PDF guardado (compresión no efectiva)"
            return final_filename, "PDF guardado"
        except ImportError:
            return final_filename, "PDF guardado (pypdf no instalado)"
        except Exception as e:
            print(f"Error compressing PDF: {e}")
            return final_filename, "PDF guardado (error al comprimir)"

    # 3. Other files
    else:
        file_obj.save(save_path)
        return final_filename, "Archivo guardado"
