/**
 * PAGE D'ACCUEIL
 * Gere les interactions specifiques de la page index
 */

(function() {
    "use strict";

    var viewport = document.querySelector("[data-news-ticker]");
    if (!viewport) {
        return;
    }

    var track = viewport.querySelector(".news-ticker__track");
    var items = track ? track.querySelectorAll(".news-ticker__item") : [];
    if (!track || items.length === 0) {
        return;
    }

    var step = items[0].getBoundingClientRect().width + 16;
    var autoTimer = null;

    function scrollNext() {
        var maxScroll = track.scrollWidth - track.clientWidth;
        if (track.scrollLeft + step >= maxScroll - 4) {
            track.scrollTo({ left: 0, behavior: "smooth" });
            return;
        }
        track.scrollBy({ left: step, behavior: "smooth" });
    }

    function scrollPrev() {
        if (track.scrollLeft - step <= 0) {
            track.scrollTo({ left: track.scrollWidth, behavior: "smooth" });
            return;
        }
        track.scrollBy({ left: -step, behavior: "smooth" });
    }

    function startAuto() {
        stopAuto();
        autoTimer = setInterval(scrollNext, 4500);
    }

    function stopAuto() {
        if (autoTimer) {
            clearInterval(autoTimer);
            autoTimer = null;
        }
    }

    var prevBtn = document.querySelector('[data-news-action="prev"]');
    var nextBtn = document.querySelector('[data-news-action="next"]');
    if (prevBtn) {
        prevBtn.addEventListener("click", function() {
            scrollPrev();
            startAuto();
        });
    }
    if (nextBtn) {
        nextBtn.addEventListener("click", function() {
            scrollNext();
            startAuto();
        });
    }

    viewport.addEventListener("mouseenter", stopAuto);
    viewport.addEventListener("mouseleave", startAuto);

    startAuto();
})();
