/**
 * FILTRES CATALOGUE
 * Gere la recherche, les filtres et le tri des livres
 */

(function() {
    'use strict';

    // ========================================
    // VARIABLES
    // ========================================

    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('catalogue-search-btn');
    const categoryFilter = document.getElementById('category-filter');
    const versionFilter = document.getElementById('version-filter');
    const languageFilter = document.getElementById('language-filter');
    const sortFilter = document.getElementById('sort-filter');

    // ========================================
    // RECHERCHE
    // ========================================

    if (searchInput) {
        // Declencher la recherche uniquement apres validation (Entree).
        searchInput.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                const searchTerm = this.value.trim();
                performSearch(searchTerm);
            }
        });
    }

    if (searchButton) {
        searchButton.addEventListener('click', function() {
            const searchTerm = searchInput ? searchInput.value.trim() : '';
            performSearch(searchTerm);
        });
    }

    /**
     * Effectue la recherche
     * @param {string} term - Terme de recherche
     */
    function performSearch(term) {
        // Construire l'URL avec les parametres
        const params = new URLSearchParams(window.location.search);

        if (term) {
            params.set('search', term);
        } else {
            params.delete('search');
        }

        // Recharger la page avec les nouveaux parametres
        window.location.search = params.toString();
    }

    // ========================================
    // FILTRES
    // ========================================

    if (categoryFilter) {
        categoryFilter.addEventListener('change', function() {
            const params = new URLSearchParams(window.location.search);

            if (this.value) {
                params.set('categorie', this.value);
            } else {
                params.delete('categorie');
            }

            window.location.search = params.toString();
        });
    }
    
    if (versionFilter) {
        versionFilter.addEventListener('change', function() {
            const params = new URLSearchParams(window.location.search);
            
            if (this.value) {
                params.set('version', this.value);
            } else {
                params.delete('version');
            }
            
            window.location.search = params.toString();
        });
    }
    
    if (languageFilter) {
        languageFilter.addEventListener('change', function() {
            const params = new URLSearchParams(window.location.search);
            
            if (this.value) {
                params.set('langue', this.value);
            } else {
                params.delete('langue');
            }
            
            window.location.search = params.toString();
        });
    }

    // ========================================
    // TRI
    // ========================================

    if (sortFilter) {
        sortFilter.addEventListener('change', function() {
            const params = new URLSearchParams(window.location.search);
            params.set('sort', this.value);
            window.location.search = params.toString();
        });
    }

    // ========================================
    // MODAL DETAILS LIVRE
    // ========================================

    const modal = document.getElementById('book-modal');
    const modalBody = document.getElementById('modal-body');
    const modalClose = document.querySelector('.modal__close');
    const modalOverlay = document.querySelector('.modal__overlay');

    // Ouvrir le modal au clic sur un livre
    document.querySelectorAll('[data-book-id]').forEach(button => {
        button.addEventListener('click', function() {
            const bookId = this.getAttribute('data-book-id');
            loadBookDetails(bookId);
        });
    });

    function formatAuteurs(auteursList) {
        if (!auteursList || auteursList.length === 0) {
            return '';
        }
        if (auteursList.length === 1) {
            return auteursList[0].nom;
        }
        if (auteursList.length === 2) {
            return `${auteursList[0].nom} et ${auteursList[1].nom}`;
        }
        const noms = auteursList.map(a => a.nom);
        return `${noms.slice(0, -1).join(', ')} et ${noms[noms.length - 1]}`;
    }

    /**
     * Charge les details d'un livre via AJAX
     * @param {number} bookId - ID du livre
     */
    function loadBookDetails(bookId) {
        if (!modal || !modalBody) {
            return;
        }

        // Afficher le modal
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';

        // Loader
        modalBody.innerHTML = '<div class="loader">Chargement...</div>';

        // Recuperer les details via l'API Django
        fetch(window.DJANGO_URLS.livreDetailJson(bookId))
            .then(response => response.json())
            .then(data => {
                displayBookDetails(data);
            })
            .catch(error => {
                console.error('Erreur:', error);
                modalBody.innerHTML = '<p>Erreur lors du chargement des details.</p>';
            });
    }

    /**
     * Affiche les details du livre dans le modal
     * @param {Object} livre - Donnees du livre
     */
    function displayBookDetails(livre) {
        if (!modalBody) {
            return;
        }

        modalBody.innerHTML = `
            <div class="modal-book">
                <div class="modal-book__image">
                    <img src="${livre.image}" alt="${livre.titre}">
                </div>
                <div class="modal-book__info">
                    <h2>${livre.titre}</h2>
                    <p class="author">${formatAuteurs(livre.auteurs || [])}</p>
                    <p class="category">${livre.categorie}</p>
                    <p class="price">${livre.prix}</p>
                    <div class="description">
                        <h3>Resume</h3>
                        <p>${livre.resume}</p>
                    </div>
                    <div class="purchase-links">
                        <a href="${livre.liens.chariow}" target="_blank" class="btn btn--primary">Acheter sur Chariow</a>
                        <a href="${livre.liens.amazon}" target="_blank" class="btn btn--primary">Acheter sur Amazon</a>
                        <a href="${livre.liens.whatsapp}" target="_blank" class="btn btn--primary">Commander WhatsApp</a>
                    </div>
                </div>
            </div>
        `;
    }

    // Fermer le modal
    function closeModal() {
        if (!modal) {
            return;
        }

        modal.classList.remove('active');
        document.body.style.overflow = '';
    }

    if (modalClose) {
        modalClose.addEventListener('click', closeModal);
    }

    if (modalOverlay) {
        modalOverlay.addEventListener('click', closeModal);
    }

    // Fermer avec Escape
    document.addEventListener('keydown', function(e) {
        if (modal && e.key === 'Escape' && modal.classList.contains('active')) {
            closeModal();
        }
    });

})();
