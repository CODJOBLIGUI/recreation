/*
 * Data.js - Version Django
 * Les données viennent maintenant de l'API Django.
 * Ce fichier charge les données et les met à disposition globalement.
 */

let livres = [];
let auteurs = [];

// Fonction pour charger toutes les données nécessaires depuis l'API Django
async function loadData() {
    try {
        // S'assurer que DJANGO_URLS est disponible
        if (!window.DJANGO_URLS || !window.DJANGO_URLS.livresJson || !window.DJANGO_URLS.auteursJson) {
            console.error("❌ Les URLs Django ne sont pas définies. Assurez-vous que le script est dans base.html.");
            return;
        }

        // Charger les livres et les auteurs en parallèle pour plus de performance
        const [livresResponse, auteursResponse] = await Promise.all([
            fetch(window.DJANGO_URLS.livresJson),
            fetch(window.DJANGO_URLS.auteursJson)
        ]);

        if (!livresResponse.ok || !auteursResponse.ok) {
            throw new Error('La réponse du réseau était incorrecte.');
        }

        const livresData = await livresResponse.json();
        const auteursData = await auteursResponse.json();

        livres = livresData.livres || [];
        auteurs = auteursData.auteurs || [];

        console.log('✅ Données chargées depuis Django API:', livres.length, 'livres,', auteurs.length, 'auteurs.');
        
        // Déclencher un événement personnalisé pour notifier les autres scripts que les données sont prêtes
        document.dispatchEvent(new CustomEvent('dataLoaded', { detail: { livres, auteurs } }));
        
    } catch (error) {
        console.error('❌ Erreur lors du chargement des données depuis l'API Django:', error);
    }
}

// Lancer le chargement des données au démarrage de l'application
document.addEventListener('DOMContentLoaded', loadData);

// Fonctions utilitaires pour accéder aux données chargées (peuvent être appelées par d'autres scripts)
window.getLivreById = function(id) {
    return livres.find(livre => livre.id === id);
}

window.getAuteurById = function(id) {
    return auteurs.find(auteur => auteur.id === id);
}
