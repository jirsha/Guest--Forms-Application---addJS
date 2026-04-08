// File upload validation - using centralized configuration
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('profile_picture');
    const profileForm = document.getElementById('profileForm');
    
    // Get configuration from window object (set by Flask template)
    const config = window.UPLOAD_CONFIG || {
        max_file_size_mb: 5,
        max_file_size_bytes: 5 * 1024 * 1024,
        allowed_extensions: ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp']
    };
    
    const maxSizeMB = config.max_file_size_mb;
    const maxSizeBytes = config.max_file_size_bytes;
    
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            const fileError = document.getElementById('file-error');
            const fileInfo = document.getElementById('file-info');
            
            // Reset displays
            if (fileError) fileError.style.display = 'none';
            if (fileInfo) fileInfo.style.display = 'none';
            if (fileError) fileError.innerHTML = '';
            if (fileInfo) fileInfo.innerHTML = '';
            
            if (file) {
                // Check file size
                const fileSizeMB = file.size / (1024 * 1024);
                
                if (file.size > maxSizeBytes) {
                    if (fileError) {
                        fileError.style.display = 'block';
                        fileError.innerHTML = `
                            <strong>File too large!</strong><br>
                            Your file is ${fileSizeMB.toFixed(2)}MB.<br>
                            Maximum allowed size is ${maxSizeMB}MB.<br>
                            Please compress your image or choose a smaller file.
                        `;
                    }
                    // Clear the file input to prevent submission
                    e.target.value = '';
                } else {
                    // Show file info
                    const fileType = file.type.split('/')[1].toUpperCase();
                    if (fileInfo) {
                        fileInfo.style.display = 'block';
                        fileInfo.innerHTML = `
                            ✅ File selected: ${file.name}<br>
                            Size: ${fileSizeMB.toFixed(2)}MB (within ${maxSizeMB}MB limit)<br>
                            Type: ${fileType}
                        `;
                    }
                }
            }
        });
    }
    
    // Additional client-side validation before form submission
    if (profileForm) {
        profileForm.addEventListener('submit', function(e) {
            const fileInput = document.getElementById('profile_picture');
            if (fileInput) {
                const file = fileInput.files[0];
                
                if (file && file.size > maxSizeBytes) {
                    e.preventDefault();
                    const fileError = document.getElementById('file-error');
                    if (fileError) {
                        fileError.style.display = 'block';
                        fileError.innerHTML = `
                            <strong>Cannot submit!</strong><br>
                            The selected file is too large. Please choose a smaller image (max ${maxSizeMB}MB).
                        `;
                        fileError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                }
            }
        });
    }
});