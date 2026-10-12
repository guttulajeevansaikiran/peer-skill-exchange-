/* =========================================================
   SKILL EXCHANGE - GLOBAL JAVASCRIPT
   ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        /* =================================================
           CARD ANIMATION
           ================================================= */

        const cards =
            document.querySelectorAll(
                ".user-card, .player-card"
            );

        cards.forEach(
            function (card, index) {

                card.style.animationDelay =
                    `${index * 0.08}s`;

            }
        );


        /* =================================================
           BUTTON CLICK EFFECT
           ================================================= */

        const buttons =
            document.querySelectorAll(
                "button"
            );

        buttons.forEach(
            function (button) {

                button.addEventListener(
                    "click",
                    function () {

                        button.style.transform =
                            "scale(0.97)";

                        setTimeout(
                            function () {

                                button.style.transform =
                                    "";

                            },
                            120
                        );

                    }
                );

            }
        );


        /* =================================================
           SEARCH INPUT
           ================================================= */

        const searchInput =
            document.querySelector(
                ".search-box input[name='search']"
            );

        if (searchInput) {

            searchInput.addEventListener(
                "keydown",
                function (event) {

                    if (
                        event.key === "Escape"
                    ) {

                        searchInput.value = "";

                        searchInput.focus();

                    }

                }
            );

        }


        /* =================================================
           AUTO HIDE FLASH MESSAGE
           ================================================= */

        const flashMessages =
            document.querySelectorAll(
                ".flash-message"
            );

        flashMessages.forEach(
            function (message) {

                setTimeout(
                    function () {

                        message.style.transition =
                            "opacity 0.5s ease, transform 0.5s ease";

                        message.style.opacity =
                            "0";

                        message.style.transform =
                            "translateY(-10px)";

                        setTimeout(
                            function () {

                                message.remove();

                            },
                            500
                        );

                    },
                    4500
                );

            }
        );


        /* =================================================
           SMOOTH CARD HOVER
           ================================================= */

        const userCards =
            document.querySelectorAll(
                ".user-card"
            );

        userCards.forEach(
            function (card) {

                card.addEventListener(
                    "mouseenter",
                    function () {

                        card.style.zIndex =
                            "2";

                    }
                );

                card.addEventListener(
                    "mouseleave",
                    function () {

                        card.style.zIndex =
                            "";

                    }
                );

            }
        );


        /* =================================================
           INTERSECTION ANIMATION
           ================================================= */

        if (
            "IntersectionObserver"
            in window
        ) {

            const observer =
                new IntersectionObserver(
                    function (entries) {

                        entries.forEach(
                            function (entry) {

                                if (
                                    entry.isIntersecting
                                ) {

                                    entry.target.classList.add(
                                        "visible"
                                    );

                                    observer.unobserve(
                                        entry.target
                                    );

                                }

                            }
                        );

                    },
                    {
                        threshold: 0.08
                    }
                );


            cards.forEach(
                function (card) {

                    observer.observe(card);

                }
            );

        }

    }
);