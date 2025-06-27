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
/* When dvh < dvw, set height to 80dvh */
@media (min-aspect-ratio: 1.3/1) {
    .sticky-image {
        height: 80dvh;
    }
}

footer{display:none !important}
"""