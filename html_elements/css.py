css = """
body, html, .gradio-container, .gradio-container > .gr-block {
    overflow: visible !important;
    -webkit-touch-callout:none;

    -webkit-user-select:none;

    -webkit-tap-highlight-color:rgba(0, 0, 0, 0);
}
.sticky-image {
    position: sticky;
    top: 10px;
    height: 45dvh;
    z-index: 1000;
}

@media (min-width: 400px) and (max-width: 555px) {
    .sticky-image {
        margin-left: 4dvw;
        margin-right: 4dvw;
    }
}
@media (min-aspect-ratio: 0.8/1) and (max-aspect-ratio: 1.3/1) {
    .sticky-image {
        height: 60dvh;
    }
}
/* When dvh < dvw, set height to 80dvh */
@media (min-aspect-ratio: 1.3/1) {
    .sticky-image {
        height: 85dvh;
    }
}

footer{display:none !important}


#bottom-btn {
    position: fixed;
    bottom: 70px;
    width: 90%;
    left: 5%;
    z-index: 100;
}
"""