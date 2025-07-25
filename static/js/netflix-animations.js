// Netflix-style animations for KrishiMitra
document.addEventListener('DOMContentLoaded', function() {
    initializeNetflixAnimations();
});

function initializeNetflixAnimations() {
    const cropCards = document.querySelectorAll('.netflix-card, .crop-card');
    
    cropCards.forEach(card => {
        setupCardHoverEffects(card);
        setupVideoPreview(card);
    });
    
    // Initialize intersection observer for scroll animations
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver(handleIntersection, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });
        
        cropCards.forEach(card => {
            observer.observe(card);
        });
    }
    
    // Initialize staggered animations
    setupStaggeredAnimations();
}

function setupCardHoverEffects(card) {
    let hoverTimeout;
    let isHovered = false;
    
    card.addEventListener('mouseenter', function() {
        if (isHovered) return;
        isHovered = true;
        
        // Clear any existing timeout
        clearTimeout(hoverTimeout);
        
        // Add immediate hover class
        card.classList.add('netflix-hover');
        
        // Delay the scale and video effects
        hoverTimeout = setTimeout(() => {
            if (isHovered) {
                card.classList.add('netflix-scale');
                showVideoPreview(card);
                addCardShadow(card);
                showCardDetails(card);
            }
        }, 300);
    });
    
    card.addEventListener('mouseleave', function() {
        isHovered = false;
        clearTimeout(hoverTimeout);
        
        // Remove all hover effects
        card.classList.remove('netflix-hover', 'netflix-scale');
        hideVideoPreview(card);
        removeCardShadow(card);
        hideCardDetails(card);
    });
    
    // Add CSS classes for animations
    card.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
}

function setupVideoPreview(card) {
    const imageContainer = card.querySelector('.crop-card-image');
    if (!imageContainer) return;
    
    // Create video element
    const video = document.createElement('video');
    video.className = 'netflix-video-preview';
    video.muted = true;
    video.loop = true;
    video.playsInline = true;
    video.preload = 'none';
    
    // Set video source (placeholder for now - in production, this would come from crop data)
    video.innerHTML = `
        <source src="https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4" type="video/mp4">
        <source src="https://www.w3schools.com/html/mov_bbb.mp4" type="video/mp4">
    `;
    
    // Style the video
    video.style.cssText = `
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        opacity: 0;
        transition: opacity 0.5s ease;
        z-index: 2;
    `;
    
    imageContainer.appendChild(video);
    
    // Store reference for later use
    card._netflixVideo = video;
    
    // Preload video on first hover
    let videoPreloaded = false;
    card.addEventListener('mouseenter', function() {
        if (!videoPreloaded) {
            video.load();
            videoPreloaded = true;
        }
    });
}

function showVideoPreview(card) {
    const video = card._netflixVideo;
    if (!video) return;
    
    // Start playing the video
    video.play().then(() => {
        video.style.opacity = '1';
        
        // Add video controls overlay
        addVideoControls(card);
    }).catch(error => {
        console.log('Video autoplay failed:', error);
        // Fallback to showing play button
        showPlayButton(card);
    });
}

function hideVideoPreview(card) {
    const video = card._netflixVideo;
    if (!video) return;
    
    video.style.opacity = '0';
    video.pause();
    
    // Remove video controls
    removeVideoControls(card);
    hidePlayButton(card);
}

function addVideoControls(card) {
    const existingControls = card.querySelector('.netflix-video-controls');
    if (existingControls) return;
    
    const controls = document.createElement('div');
    controls.className = 'netflix-video-controls';
    controls.style.cssText = `
        position: absolute;
        bottom: 10px;
        right: 10px;
        display: flex;
        gap: 8px;
        z-index: 10;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;
    
    // Play/Pause button
    const playButton = document.createElement('button');
    playButton.className = 'netflix-control-btn';
    playButton.innerHTML = '<i class="fas fa-pause"></i>';
    playButton.style.cssText = `
        background: rgba(0, 0, 0, 0.8);
        color: white;
        border: none;
        border-radius: 50%;
        width: 35px;
        height: 35px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 12px;
    `;
    
    playButton.addEventListener('click', function(e) {
        e.stopPropagation();
        const video = card._netflixVideo;
        if (video.paused) {
            video.play();
            playButton.innerHTML = '<i class="fas fa-pause"></i>';
        } else {
            video.pause();
            playButton.innerHTML = '<i class="fas fa-play"></i>';
        }
    });
    
    // Volume button
    const volumeButton = document.createElement('button');
    volumeButton.className = 'netflix-control-btn';
    volumeButton.innerHTML = '<i class="fas fa-volume-mute"></i>';
    volumeButton.style.cssText = playButton.style.cssText;
    
    volumeButton.addEventListener('click', function(e) {
        e.stopPropagation();
        const video = card._netflixVideo;
        video.muted = !video.muted;
        volumeButton.innerHTML = video.muted ? 
            '<i class="fas fa-volume-mute"></i>' : 
            '<i class="fas fa-volume-up"></i>';
    });
    
    // Fullscreen button
    const fullscreenButton = document.createElement('button');
    fullscreenButton.className = 'netflix-control-btn';
    fullscreenButton.innerHTML = '<i class="fas fa-expand"></i>';
    fullscreenButton.style.cssText = playButton.style.cssText;
    
    fullscreenButton.addEventListener('click', function(e) {
        e.stopPropagation();
        const video = card._netflixVideo;
        if (video.requestFullscreen) {
            video.requestFullscreen();
        }
    });
    
    controls.appendChild(playButton);
    controls.appendChild(volumeButton);
    controls.appendChild(fullscreenButton);
    
    const imageContainer = card.querySelector('.crop-card-image');
    if (imageContainer) {
        imageContainer.appendChild(controls);
    }
    
    // Show controls on hover
    setTimeout(() => {
        controls.style.opacity = '1';
    }, 100);
}

function removeVideoControls(card) {
    const controls = card.querySelector('.netflix-video-controls');
    if (controls) {
        controls.remove();
    }
}

function showPlayButton(card) {
    const existingButton = card.querySelector('.netflix-play-button');
    if (existingButton) return;
    
    const playButton = document.createElement('div');
    playButton.className = 'netflix-play-button';
    playButton.innerHTML = '<i class="fas fa-play"></i>';
    playButton.style.cssText = `
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: rgba(0, 0, 0, 0.8);
        color: white;
        border: none;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        z-index: 10;
        font-size: 20px;
        transition: all 0.3s ease;
        animation: pulse 2s infinite;
    `;
    
    playButton.addEventListener('click', function(e) {
        e.stopPropagation();
        const video = card._netflixVideo;
        if (video) {
            video.play();
            playButton.style.display = 'none';
        }
    });
    
    const imageContainer = card.querySelector('.crop-card-image');
    if (imageContainer) {
        imageContainer.appendChild(playButton);
    }
}

function hidePlayButton(card) {
    const playButton = card.querySelector('.netflix-play-button');
    if (playButton) {
        playButton.remove();
    }
}

function addCardShadow(card) {
    card.style.boxShadow = '0 25px 50px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(255, 255, 255, 0.1)';
    card.style.zIndex = '10';
}

function removeCardShadow(card) {
    card.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.1)';
    card.style.zIndex = '1';
}

function showCardDetails(card) {
    const content = card.querySelector('.crop-card-content');
    if (!content) return;
    
    // Add enhanced details
    const existingDetails = card.querySelector('.netflix-enhanced-details');
    if (existingDetails) return;
    
    const details = document.createElement('div');
    details.className = 'netflix-enhanced-details';
    details.style.cssText = `
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
        color: white;
        padding: 20px;
        transform: translateY(100%);
        transition: transform 0.3s ease;
        z-index: 5;
    `;
    
    // Get crop data from the card
    const cropName = card.querySelector('.crop-card-title')?.textContent || 'Unknown Crop';
    const cropInfo = card.querySelector('.crop-card-info')?.textContent || 'No info available';
    
    details.innerHTML = `
        <h4 style="margin: 0 0 8px 0; font-size: 1.2rem;">${cropName}</h4>
        <p style="margin: 0 0 12px 0; font-size: 0.9rem; opacity: 0.9;">${cropInfo}</p>
        <div style="display: flex; gap: 8px; margin-top: 12px;">
            <button class="netflix-action-btn" style="background: white; color: black; border: none; padding: 8px 16px; border-radius: 4px; font-weight: 600; cursor: pointer;">
                <i class="fas fa-play me-1"></i> View Details
            </button>
            <button class="netflix-action-btn" style="background: rgba(255, 255, 255, 0.3); color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: 600; cursor: pointer;">
                <i class="fas fa-plus me-1"></i> Add to Cart
            </button>
        </div>
    `;
    
    card.appendChild(details);
    
    // Animate in
    setTimeout(() => {
        details.style.transform = 'translateY(0)';
    }, 100);
}

function hideCardDetails(card) {
    const details = card.querySelector('.netflix-enhanced-details');
    if (details) {
        details.style.transform = 'translateY(100%)';
        setTimeout(() => {
            details.remove();
        }, 300);
    }
}

function handleIntersection(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('netflix-visible');
            
            // Add staggered animation delay
            const cards = Array.from(entry.target.parentElement.children);
            const index = cards.indexOf(entry.target);
            entry.target.style.animationDelay = `${index * 0.1}s`;
        }
    });
}

function setupStaggeredAnimations() {
    const style = document.createElement('style');
    style.textContent = `
        .netflix-card,
        .crop-card {
            opacity: 0;
            transform: translateY(30px);
            animation: netflixFadeInUp 0.6s ease-out forwards;
        }
        
        .netflix-card.netflix-visible,
        .crop-card.netflix-visible {
            animation: netflixFadeInUp 0.6s ease-out forwards;
        }
        
        .netflix-card.netflix-hover {
            transform: translateY(-5px);
        }
        
        .netflix-card.netflix-scale {
            transform: scale(1.05) translateY(-10px);
        }
        
        @keyframes netflixFadeInUp {
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes pulse {
            0% { transform: translate(-50%, -50%) scale(1); }
            50% { transform: translate(-50%, -50%) scale(1.1); }
            100% { transform: translate(-50%, -50%) scale(1); }
        }
        
        .netflix-video-preview {
            border-radius: inherit;
        }
        
        .netflix-control-btn:hover {
            background: rgba(0, 0, 0, 0.9) !important;
            transform: scale(1.1);
        }
        
        .netflix-action-btn:hover {
            opacity: 0.8;
            transform: scale(1.05);
        }
        
        /* Responsive adjustments */
        @media (max-width: 768px) {
            .netflix-card.netflix-scale,
            .crop-card.netflix-scale {
                transform: scale(1.02) translateY(-5px);
            }
            
            .netflix-enhanced-details {
                padding: 15px;
            }
            
            .netflix-video-controls {
                bottom: 5px;
                right: 5px;
            }
            
            .netflix-control-btn {
                width: 30px !important;
                height: 30px !important;
                font-size: 10px !important;
            }
        }
        
        /* Accessibility improvements */
        @media (prefers-reduced-motion: reduce) {
            .netflix-card,
            .crop-card,
            .netflix-video-preview,
            .netflix-enhanced-details {
                animation: none !important;
                transition: none !important;
            }
        }
    `;
    
    document.head.appendChild(style);
}

// Initialize cards that are already visible
function initializeVisibleCards() {
    const cards = document.querySelectorAll('.netflix-card, .crop-card');
    cards.forEach(card => {
        const rect = card.getBoundingClientRect();
        if (rect.top < window.innerHeight && rect.bottom > 0) {
            card.classList.add('netflix-visible');
        }
    });
}

// Advanced hover effects for grid layouts
function setupGridHoverEffects() {
    const grids = document.querySelectorAll('.crop-grid, .products-grid');
    
    grids.forEach(grid => {
        const cards = grid.querySelectorAll('.netflix-card, .crop-card, .product-card');
        
        cards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                // Dim other cards
                cards.forEach(otherCard => {
                    if (otherCard !== card) {
                        otherCard.style.opacity = '0.7';
                        otherCard.style.transform = 'scale(0.95)';
                    }
                });
            });
            
            card.addEventListener('mouseleave', function() {
                // Restore other cards
                cards.forEach(otherCard => {
                    otherCard.style.opacity = '1';
                    otherCard.style.transform = 'scale(1)';
                });
            });
        });
    });
}

// Initialize everything when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeVisibleCards();
    setupGridHoverEffects();
    
    // Re-initialize when new content is loaded
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        const newCards = node.querySelectorAll('.netflix-card, .crop-card');
                        newCards.forEach(card => {
                            setupCardHoverEffects(card);
                            setupVideoPreview(card);
                        });
                    }
                });
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});

// Export for external use
window.NetflixAnimations = {
    initializeNetflixAnimations,
    setupCardHoverEffects,
    setupVideoPreview,
    showVideoPreview,
    hideVideoPreview
};
