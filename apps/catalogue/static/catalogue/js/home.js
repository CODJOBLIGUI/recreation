/**
 * PAGE D'ACCUEIL
 * Gere les interactions specifiques de la page index
 */

(function() {
    "use strict";

    function setupBookCarousels() {
        var carousels = document.querySelectorAll("[data-book-carousel]");
        if (!carousels.length) {
            return;
        }

        carousels.forEach(function(wrapper) {
            var track = wrapper.querySelector(".book-carousel__track");
            if (!track) {
                return;
            }

            var items = track.querySelectorAll(".book-card");
            if (!items.length) {
                return;
            }

            function getGap() {
                var styles = window.getComputedStyle(track);
                var gap = parseFloat(styles.gap || styles.columnGap || "0");
                return isNaN(gap) ? 0 : gap;
            }

            function getStep() {
                var width = items[0].getBoundingClientRect().width;
                return width + getGap();
            }

            var step = getStep();

            function scrollNext() {
                var maxScroll = track.scrollWidth - track.clientWidth;
                if (track.scrollLeft + step >= maxScroll - 4) {
                    track.scrollTo({ left: 0, behavior: "smooth" });
                    setTimeout(updateActive, 450);
                    return;
                }
                track.scrollBy({ left: step, behavior: "smooth" });
                setTimeout(updateActive, 450);
            }

            function scrollPrev() {
                if (track.scrollLeft - step <= 0) {
                    track.scrollTo({ left: track.scrollWidth, behavior: "smooth" });
                    setTimeout(updateActive, 450);
                    return;
                }
                track.scrollBy({ left: -step, behavior: "smooth" });
                setTimeout(updateActive, 450);
            }

            var target = wrapper.getAttribute("data-book-carousel");
            var prevBtn = document.querySelector('[data-book-action="prev"][data-book-target="' + target + '"]');
            var nextBtn = document.querySelector('[data-book-action="next"][data-book-target="' + target + '"]');

            if (prevBtn) {
                prevBtn.addEventListener("click", function() {
                    scrollPrev();
                });
            }
            if (nextBtn) {
                nextBtn.addEventListener("click", function() {
                    scrollNext();
                });
            }

            var autoTimer = null;
            function startAuto() {
                stopAuto();
                autoTimer = setInterval(scrollNext, 5000);
            }
            function stopAuto() {
                if (autoTimer) {
                    clearInterval(autoTimer);
                    autoTimer = null;
                }
            }

            wrapper.addEventListener("mouseenter", stopAuto);
            wrapper.addEventListener("mouseleave", startAuto);
            wrapper.addEventListener("touchstart", stopAuto, { passive: true });
            wrapper.addEventListener("touchend", startAuto);

            window.addEventListener("resize", function() {
                step = getStep();
            });

            updateActive();
            startAuto();
        });
    }

    var viewport = document.querySelector("[data-news-ticker]");
    if (!viewport) {
        setupBookCarousels();
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
        autoTimer = setInterval(scrollNext, 5000);
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

    setupBookCarousels();
})();
