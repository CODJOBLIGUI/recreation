/**
 * EDITIONS RECREATION - SCRIPT PRINCIPAL
 * Gere les fonctionnalites communes a toutes les pages
 */

(function() {
    'use strict';

    // ========================================
    // VARIABLES GLOBALES
    // ========================================

    const hamburgerMenu = document.getElementById('hamburger-menu');
    const searchIcon = document.getElementById('search-icon');
    const navMenuBtn = document.getElementById('nav-menu-btn');
    const navigation = document.querySelector('.header__nav');
    const navDrawer = document.getElementById('nav-drawer');
    const navDrawerClose = document.getElementById('nav-drawer-close');
    const navDrawerBackdrop = navDrawer ? navDrawer.querySelector('.nav-drawer__backdrop') : null;

    // ========================================
    // MENU MOBILE (HAMBURGER)
    // ========================================

    if (hamburgerMenu) {
        hamburgerMenu.addEventListener('click', function() {
            // Toggle du menu
            navigation.classList.toggle('active');
            this.classList.toggle('active');

            // Mettre a jour aria-expanded
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            this.setAttribute('aria-expanded', !isExpanded);
        });
    }

    function openNavDrawer() {
        if (!navDrawer || !navMenuBtn) {
            return;
        }
        navDrawer.classList.add('is-open');
        navDrawer.setAttribute('aria-hidden', 'false');
        navMenuBtn.setAttribute('aria-expanded', 'true');
        document.body.classList.add('nav-drawer-open');
    }

    function closeNavDrawer() {
        if (!navDrawer || !navMenuBtn) {
            return;
        }
        navDrawer.classList.remove('is-open');
        navDrawer.setAttribute('aria-hidden', 'true');
        navMenuBtn.setAttribute('aria-expanded', 'false');
        document.body.classList.remove('nav-drawer-open');
    }

    if (navMenuBtn) {
        navMenuBtn.addEventListener('click', function() {
            if (navDrawer && navDrawer.classList.contains('is-open')) {
                closeNavDrawer();
            } else {
                openNavDrawer();
            }
        });
    }

    if (navDrawerClose) {
        navDrawerClose.addEventListener('click', closeNavDrawer);
    }

    if (navDrawerBackdrop) {
        navDrawerBackdrop.addEventListener('click', closeNavDrawer);
    }

    if (navDrawer) {
        navDrawer.addEventListener('click', function(event) {
            const link = event.target.closest('a');
            if (link && navDrawer.contains(link)) {
                closeNavDrawer();
            }
        });
    }

    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            closeNavDrawer();
        }
    });

    // ========================================
    // HEADER STICKY
    // ========================================

    const header = document.querySelector('.header');

    window.addEventListener('scroll', function() {
        if (!header) {
            return;
        }

        const currentScroll = window.pageYOffset;

        // Ajouter/retirer la classe sticky
        if (currentScroll > 100) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });

    // ========================================
    // RECHERCHE ENTETE
    // ========================================

    if (searchIcon) {
        searchIcon.addEventListener('click', function() {
            const catalogueSearchInput = document.getElementById('search-input');

            // Sur la page catalogue: aller directement sur la barre et la focus.
            if (catalogueSearchInput) {
                catalogueSearchInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
                catalogueSearchInput.focus();
                return;
            }

            // Sur les autres pages: rediriger vers le catalogue au niveau de la barre de recherche.
            const searchUrl = this.getAttribute('data-search-url') || '/catalogue/';
            window.location.href = `${searchUrl}#search-input`;
        });
    }

    // ========================================
    // GESTION DES ONGLETS (TABS)
    // ========================================

    const tabsButtons = document.querySelectorAll('.tabs__btn');

    if (tabsButtons.length > 0) {
        tabsButtons.forEach(button => {
            button.addEventListener('click', function() {
                const category = this.getAttribute('data-category');

                // Retirer la classe active de tous les boutons
                tabsButtons.forEach(btn => {
                    btn.classList.remove('active');
                    btn.setAttribute('aria-pressed', 'false');
                });

                // Ajouter la classe active au bouton clique
                this.classList.add('active');
                this.setAttribute('aria-pressed', 'true');

                // Filtrer les livres
                filterBooksByCategory(category);
            });
        });
    }

    /**
     * Filtre les livres par categorie
     * @param {string} category - Categorie a afficher
     */
    function filterBooksByCategory(category) {
        const newReleasesSection = document.querySelector('.new-releases');
        if (!newReleasesSection) {
            return;
        }

        const bookCards = newReleasesSection.querySelectorAll('.book-card');

        bookCards.forEach(card => {
            const bookCategory = card.getAttribute('data-category');

            if (category === 'toutes' || bookCategory === category) {
                card.style.display = 'block';
                // Animation d'apparition
                setTimeout(() => {
                    card.style.opacity = '1';
                    card.style.transform = 'scale(1)';
                }, 10);
            } else {
                card.style.opacity = '0';
                card.style.transform = 'scale(0.9)';
                setTimeout(() => {
                    card.style.display = 'none';
                }, 300);
            }
        });
    }

    // ========================================
    // SMOOTH SCROLL POUR LES ANCRES
    // ========================================

    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');

            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);

                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });

    // ========================================
    // LAZY LOADING DES IMAGES
    // ========================================

    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src || img.src;
                    img.classList.add('loaded');
                    observer.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img[loading="lazy"]').forEach(img => {
            imageObserver.observe(img);
        });
    }

    // ========================================
    // PUBLICITÉ MODALE (ROTATION + TIMING)
    // ========================================

    const adsDataEl = document.getElementById('ads-data');
    if (adsDataEl) {
        let ads = [];
        try {
            ads = JSON.parse(adsDataEl.textContent || '[]');
        } catch (err) {
            ads = [];
        }

        const modal = document.getElementById('ad-modal');
        const linkEl = modal ? modal.querySelector('[data-ad-link]') : null;
        const imgEl = modal ? modal.querySelector('[data-ad-image]') : null;
        const textEl = modal ? modal.querySelector('[data-ad-text]') : null;
        const closeEls = modal ? modal.querySelectorAll('[data-ad-close]') : [];

        const scheduleMinutes = [5, 15, 30];
        const startKey = 'adSessionStart';
        const countKey = 'adShowCount';
        let isShowing = false;

        const now = Date.now();
        let sessionStart = parseInt(sessionStorage.getItem(startKey) || '0', 10);
        if (!sessionStart) {
            sessionStart = now;
            sessionStorage.setItem(startKey, String(sessionStart));
        }
        let showCount = parseInt(sessionStorage.getItem(countKey) || '0', 10) || 0;

        const pickAd = () => {
            if (!ads.length) return null;
            const total = ads.reduce((sum, ad) => sum + Math.max(1, parseInt(ad.weight || 1, 10)), 0);
            let roll = Math.random() * total;
            for (const ad of ads) {
                roll -= Math.max(1, parseInt(ad.weight || 1, 10));
                if (roll <= 0) return ad;
            }
            return ads[0];
        };

        const closeAd = () => {
            if (!modal) return;
            modal.classList.remove('is-visible');
            modal.setAttribute('aria-hidden', 'true');
            isShowing = false;
            showCount += 1;
            sessionStorage.setItem(countKey, String(showCount));
            scheduleNext();
        };

        const renderAd = (ad) => {
            if (!modal || !ad) return;
            if (imgEl) {
                imgEl.src = ad.image || '';
                imgEl.alt = ad.title || 'Publicité';
            }
            if (linkEl) {
                linkEl.href = ad.link_url || '#';
            }
            if (textEl) {
                if (ad.text) {
                    textEl.textContent = ad.text;
                    textEl.style.display = 'block';
                } else {
                    textEl.textContent = '';
                    textEl.style.display = 'none';
                }
            }
        };

        const showAd = () => {
            if (!modal || !ads.length || isShowing) return;
            const ad = pickAd();
            if (!ad) return;
            renderAd(ad);
            modal.classList.add('is-visible');
            modal.setAttribute('aria-hidden', 'false');
            isShowing = true;
        };

        const scheduleNext = () => {
            if (showCount >= scheduleMinutes.length) return;
            const target = sessionStart + scheduleMinutes[showCount] * 60 * 1000;
            const delay = Math.max(0, target - Date.now());
            window.setTimeout(showAd, delay);
        };

        closeEls.forEach((btn) => btn.addEventListener('click', closeAd));
        if (linkEl) {
            linkEl.addEventListener('click', () => {
                closeAd();
            });
        }

        scheduleNext();
    }

    // ========================================
    // INITIALISATION AU CHARGEMENT
    // ========================================

    document.addEventListener('DOMContentLoaded', function() {
        console.log('Editions Recreation - Site charge');

        // Ajouter des classes pour les animations
        document.body.classList.add('loaded');
    });

})();
