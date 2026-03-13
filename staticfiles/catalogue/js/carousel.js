/**
 * CARROUSEL HERO
 * Gère le défilement automatique et manuel des slides
 */

(function() {
    'use strict';
    
    // ========================================
    // VARIABLES
    // ========================================
    
    const carousel = document.querySelector('.hero__carousel');
    
    if (!carousel) return; // Sortir si pas de carrousel
    
    const slides = carousel.querySelectorAll('.hero__slide');
    const prevBtn = document.getElementById('hero-prev');
    const nextBtn = document.getElementById('hero-next');
    
    let currentSlide = 0;
    let autoplayInterval;
    const autoplayDelay = 5000; // 5 secondes
    
    // ========================================
    // FONCTIONS
    // ========================================
    
    /**
     * Affiche un slide spécifique
     * @param {number} index - Index du slide à afficher
     */
    function showSlide(index) {
        // Gérer les limites
        if (index < 0) {
            currentSlide = slides.length - 1;
        } else if (index >= slides.length) {
            currentSlide = 0;
        } else {
            currentSlide = index;
        }
        
        // Retirer la classe active de tous les slides
        slides.forEach(slide => {
            slide.classList.remove('active');
        });
        
        // Ajouter la classe active au slide actuel
        slides[currentSlide].classList.add('active');
    }
    
    /**
     * Affiche le slide suivant
     */
    function nextSlide() {
        showSlide(currentSlide + 1);
    }
    
    /**
     * Affiche le slide précédent
     */
    function prevSlide() {
        showSlide(currentSlide - 1);
    }
    
    /**
     * Démarre le défilement automatique
     */
    function startAutoplay() {
        autoplayInterval = setInterval(nextSlide, autoplayDelay);
    }
    
    /**
     * Arrête le défilement automatique
     */
    function stopAutoplay() {
        clearInterval(autoplayInterval);
    }
    
    // ========================================
    // EVENT LISTENERS
    // ========================================
    
    // Boutons navigation
    if (prevBtn) {
        prevBtn.addEventListener('click', function() {
            prevSlide();
            stopAutoplay();
            startAutoplay(); // Redémarrer après interaction
        });
    }
    
    if (nextBtn) {
        nextBtn.addEventListener('click', function() {
            nextSlide();
            stopAutoplay();
            startAutoplay();
        });
    }
    
    // Support tactile pour mobile
    let touchStartX = 0;
    let touchEndX = 0;
    
    carousel.addEventListener('touchstart', function(e) {
        touchStartX = e.changedTouches[0].screenX;
    });
    
    carousel.addEventListener('touchend', function(e) {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    });
    
    function handleSwipe() {
        const swipeThreshold = 50;
        const diff = touchStartX - touchEndX;
        
        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0) {
                // Swipe gauche - slide suivant
                nextSlide();
            } else {
                // Swipe droite - slide précédent
                prevSlide();
            }
            stopAutoplay();
            startAutoplay();
        }
    }
    
    // Pause au survol
    carousel.addEventListener('mouseenter', stopAutoplay);
    carousel.addEventListener('mouseleave', startAutoplay);
    
    // ========================================
    // INITIALISATION
    // ========================================
    
    // Démarrer l'autoplay si plusieurs slides
    if (slides.length > 1) {
        startAutoplay();
    }
    
})();