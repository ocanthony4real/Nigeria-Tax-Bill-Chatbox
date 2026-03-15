// Extra JavaScript for Nigeria Tax Bill Chatbot Documentation

// Initialize table sorting
document.addEventListener("DOMContentLoaded", function() {
    // Sort tables
    const tables = document.querySelectorAll("article table:not([class])");
    tables.forEach(function(table) {
        new Tablesort(table);
    });

    // Add copy button to code blocks (if not already present)
    addCodeCopyButtons();

    // Smooth scroll for anchor links
    initSmoothScroll();

    // Track outbound links
    trackOutboundLinks();
});

// Add copy buttons to code blocks
function addCodeCopyButtons() {
    const codeBlocks = document.querySelectorAll("pre > code");
    codeBlocks.forEach(function(codeBlock) {
        // Check if copy button already exists (MkDocs Material adds them)
        if (!codeBlock.parentElement.querySelector(".md-clipboard")) {
            const button = document.createElement("button");
            button.className = "code-copy-btn";
            button.textContent = "Copy";
            button.addEventListener("click", function() {
                navigator.clipboard.writeText(codeBlock.textContent).then(function() {
                    button.textContent = "Copied!";
                    setTimeout(function() {
                        button.textContent = "Copy";
                    }, 2000);
                });
            });
            codeBlock.parentElement.appendChild(button);
        }
    });
}

// Smooth scroll for anchor links
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener("click", function(e) {
            const href = this.getAttribute("href");
            if (href !== "#") {
                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: "smooth",
                        block: "start"
                    });
                }
            }
        });
    });
}

// Track outbound links (for analytics)
function trackOutboundLinks() {
    document.querySelectorAll('a[href^="http"]').forEach(link => {
        if (!link.href.includes(window.location.hostname)) {
            link.addEventListener("click", function() {
                // If Google Analytics is configured
                if (typeof gtag !== "undefined") {
                    gtag("event", "click", {
                        event_category: "outbound",
                        event_label: this.href
                    });
                }
            });
        }
    });
}

// Keyboard shortcuts
document.addEventListener("keydown", function(e) {
    // Press '/' to focus search
    if (e.key === "/" && !isInputFocused()) {
        e.preventDefault();
        const searchInput = document.querySelector(".md-search__input");
        if (searchInput) {
            searchInput.focus();
        }
    }

    // Press 'Escape' to close search
    if (e.key === "Escape") {
        const searchInput = document.querySelector(".md-search__input");
        if (searchInput && document.activeElement === searchInput) {
            searchInput.blur();
        }
    }
});

function isInputFocused() {
    const activeElement = document.activeElement;
    return activeElement.tagName === "INPUT" ||
           activeElement.tagName === "TEXTAREA" ||
           activeElement.isContentEditable;
}

// Console welcome message
console.log("%c🇳🇬 Nigeria Tax Bill Chatbot Documentation", "font-size: 20px; font-weight: bold; color: #16a34a;");
console.log("%cBuilt with MkDocs Material", "font-size: 12px; color: #666;");
console.log("%cSource: https://github.com/ocanthony4real/Nigeria-Tax-Bill-Chatbox", "font-size: 12px; color: #666;");
