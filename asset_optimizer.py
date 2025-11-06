"""
Asset Optimization Module
Handles image compression, optimization, and lazy loading
"""

from PIL import Image
import os
from io import BytesIO

class ImageOptimizer:
    """Image compression and optimization handler"""
    
    # Default settings
    MAX_SIZE = (1920, 1920)  # Max dimensions
    THUMBNAIL_SIZE = (400, 400)  # Thumbnail dimensions
    QUALITY = 85  # JPEG quality (0-100)
    THUMBNAIL_QUALITY = 75
    
    @staticmethod
    def optimize_image(image_file, output_path, max_size=None, quality=None):
        """
        Optimize and compress an image
        
        Args:
            image_file: File object or path to image
            output_path: Where to save optimized image
            max_size: Tuple (width, height) for max dimensions
            quality: JPEG quality (0-100)
            
        Returns:
            dict: Information about optimization (original_size, new_size, compression_ratio)
        """
        if max_size is None:
            max_size = ImageOptimizer.MAX_SIZE
        if quality is None:
            quality = ImageOptimizer.QUALITY
            
        # Open image
        if isinstance(image_file, str):
            img = Image.open(image_file)
            original_size = os.path.getsize(image_file)
        else:
            img = Image.open(image_file)
            image_file.seek(0, 2)  # Seek to end
            original_size = image_file.tell()
            image_file.seek(0)  # Reset
        
        # Convert RGBA to RGB if needed (for JPEG)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Resize if larger than max_size
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save optimized image
        img.save(output_path, 'JPEG', quality=quality, optimize=True)
        
        # Get new size
        new_size = os.path.getsize(output_path)
        compression_ratio = (1 - new_size / original_size) * 100 if original_size > 0 else 0
        
        return {
            'original_size': original_size,
            'new_size': new_size,
            'compression_ratio': round(compression_ratio, 2),
            'dimensions': img.size
        }
    
    @staticmethod
    def create_thumbnail(image_path, thumbnail_path, size=None, quality=None):
        """
        Create thumbnail from image
        
        Args:
            image_path: Path to original image
            thumbnail_path: Where to save thumbnail
            size: Tuple (width, height) for thumbnail
            quality: JPEG quality
            
        Returns:
            dict: Thumbnail information
        """
        if size is None:
            size = ImageOptimizer.THUMBNAIL_SIZE
        if quality is None:
            quality = ImageOptimizer.THUMBNAIL_QUALITY
            
        img = Image.open(image_path)
        
        # Convert RGBA to RGB if needed
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Create thumbnail
        img.thumbnail(size, Image.Resampling.LANCZOS)
        img.save(thumbnail_path, 'JPEG', quality=quality, optimize=True)
        
        return {
            'size': os.path.getsize(thumbnail_path),
            'dimensions': img.size
        }
    
    @staticmethod
    def validate_image(image_file, max_file_size=5*1024*1024):
        """
        Validate image file
        
        Args:
            image_file: File object
            max_file_size: Maximum file size in bytes (default 5MB)
            
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            # Check file size
            image_file.seek(0, 2)
            file_size = image_file.tell()
            image_file.seek(0)
            
            if file_size > max_file_size:
                max_mb = max_file_size / (1024 * 1024)
                return False, f'Dosya boyutu {max_mb}MB\'dan küçük olmalıdır'
            
            # Try to open and validate image
            img = Image.open(image_file)
            img.verify()
            image_file.seek(0)
            
            # Check format
            allowed_formats = ['JPEG', 'JPG', 'PNG', 'GIF', 'WEBP']
            if img.format not in allowed_formats:
                return False, f'Sadece şu formatlar destekleniyor: {", ".join(allowed_formats)}'
            
            return True, None
            
        except Exception as e:
            return False, f'Geçersiz görsel dosyası: {str(e)}'

def get_optimization_recommendations():
    """
    Get recommendations for asset optimization
    
    Returns:
        dict: Optimization recommendations and guidelines
    """
    return {
        'images': {
            'compression': 'Use WebP format for better compression (20-30% smaller than JPEG)',
            'lazy_loading': 'Already implemented via ui-utils.js - Images load as they enter viewport',
            'responsive': 'Consider srcset for different screen sizes',
            'cdn': 'Use CDN for static assets to reduce server load'
        },
        'css': {
            'minification': 'Minify CSS in production (reduces file size by ~20%)',
            'critical_css': 'Inline critical CSS, defer non-critical',
            'unused': 'Remove unused Tailwind classes with PurgeCSS'
        },
        'javascript': {
            'minification': 'Minify JS files in production',
            'bundling': 'Bundle multiple JS files to reduce HTTP requests',
            'defer': 'Use defer/async attributes for non-critical scripts'
        },
        'caching': {
            'browser': 'Set Cache-Control headers for static assets',
            'service_worker': 'Implement service worker for offline caching',
            'etag': 'Use ETags for cache validation'
        },
        'cdn_setup': {
            'cloudflare': 'Free tier available - Easy setup with DNS change',
            'cloudinary': 'Image-specific CDN with transformation on-the-fly',
            'aws_cloudfront': 'Enterprise solution - Integrates with S3'
        }
    }
