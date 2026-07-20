(() => {
  "use strict";

  const MEASUREMENT_ID = "G-LS8DP9R5KX";
  const CONSENT_KEY = "weavemark-analytics-consent";
  const PUBLISHED_HOSTS = new Set(["paulosalem.github.io"]);
  const GOOGLE_TAG_URL =
    `https://www.googletagmanager.com/gtag/js?id=${MEASUREMENT_ID}`;
  const isPublishedSite =
    window.location.protocol === "https:" &&
    PUBLISHED_HOSTS.has(window.location.hostname);
  const isPreview = new URLSearchParams(window.location.search).has(
    "analytics-preview",
  );

  if (!isPublishedSite && !isPreview) {
    return;
  }

  function readConsent() {
    try {
      return window.localStorage.getItem(CONSENT_KEY);
    } catch (error) {
      if (error instanceof DOMException) {
        console.warn("Analytics preference storage is unavailable.", error);
        return null;
      }
      throw error;
    }
  }

  function writeConsent(value) {
    try {
      window.localStorage.setItem(CONSENT_KEY, value);
    } catch (error) {
      if (error instanceof DOMException) {
        console.warn("Analytics preference could not be saved.", error);
        return;
      }
      throw error;
    }
  }

  function loadAnalytics() {
    if (!isPublishedSite) {
      return;
    }
    if (document.querySelector(`script[src="${GOOGLE_TAG_URL}"]`)) {
      return;
    }

    window.dataLayer = window.dataLayer || [];
    window.gtag = function gtag() {
      window.dataLayer.push(arguments);
    };
    window.gtag("js", new Date());
    window.gtag("config", MEASUREMENT_ID, {
      allow_google_signals: false,
      allow_ad_personalization_signals: false,
    });

    const script = document.createElement("script");
    script.async = true;
    script.src = GOOGLE_TAG_URL;
    document.head.append(script);
  }

  function addStyles() {
    if (document.getElementById("analytics-consent-styles")) {
      return;
    }

    const styles = document.createElement("style");
    styles.id = "analytics-consent-styles";
    styles.textContent = `
      .analytics-consent {
        position: fixed;
        z-index: 1000;
        right: 1rem;
        bottom: 1rem;
        width: min(32rem, calc(100vw - 2rem));
        padding: 1rem;
        color: #102033;
        background: #ffffff;
        border: 1px solid rgba(24, 48, 96, 0.18);
        border-radius: 0.9rem;
        box-shadow: 0 1.25rem 4rem rgba(16, 32, 51, 0.2);
        font: 400 0.93rem/1.5 system-ui, -apple-system, BlinkMacSystemFont,
          "Segoe UI", sans-serif;
      }
      .analytics-consent h2 {
        margin: 0 0 0.35rem;
        color: #102033;
        font: 700 1rem/1.3 system-ui, -apple-system, BlinkMacSystemFont,
          "Segoe UI", sans-serif;
      }
      .analytics-consent p { margin: 0; }
      .analytics-consent-actions {
        display: flex;
        flex-wrap: wrap;
        justify-content: flex-end;
        gap: 0.55rem;
        margin-top: 0.9rem;
      }
      .analytics-consent button,
      .analytics-preferences {
        min-height: 2.4rem;
        padding: 0.5rem 0.8rem;
        border: 1px solid #315f68;
        border-radius: 0.55rem;
        font: 650 0.86rem/1 system-ui, -apple-system, BlinkMacSystemFont,
          "Segoe UI", sans-serif;
        cursor: pointer;
      }
      .analytics-consent-allow {
        color: #ffffff;
        background: #245c63;
      }
      .analytics-consent-decline {
        color: #183060;
        background: #ffffff;
      }
      .analytics-consent button:focus-visible,
      .analytics-preferences:focus-visible {
        outline: 3px solid #e26f51;
        outline-offset: 2px;
      }
      .analytics-preferences {
        min-height: auto;
        padding: 0;
        color: inherit;
        background: transparent;
        border: 0;
        border-radius: 0;
        text-decoration: underline;
        text-underline-offset: 0.16em;
      }
      @media (max-width: 36rem) {
        .analytics-consent { left: 1rem; right: 1rem; width: auto; }
        .analytics-consent-actions { justify-content: stretch; }
        .analytics-consent-actions button { flex: 1 1 9rem; }
      }
    `;
    document.head.append(styles);
  }

  function removeConsentPanel() {
    document.getElementById("analytics-consent")?.remove();
  }

  function showConsentPanel(preferencesButton) {
    removeConsentPanel();
    preferencesButton.hidden = true;

    const panel = document.createElement("aside");
    panel.id = "analytics-consent";
    panel.className = "analytics-consent";
    panel.setAttribute("role", "dialog");
    panel.setAttribute("aria-labelledby", "analytics-consent-title");
    panel.innerHTML = `
      <h2 id="analytics-consent-title">Help improve the WeaveMark site</h2>
      <p>
        Allow privacy-conscious Google Analytics to measure visits and improve
        the documentation. Advertising signals are disabled.
      </p>
      <div class="analytics-consent-actions">
        <button class="analytics-consent-decline" type="button">
          Decline
        </button>
        <button class="analytics-consent-allow" type="button">
          Allow analytics
        </button>
      </div>
    `;

    panel
      .querySelector(".analytics-consent-decline")
      .addEventListener("click", () => {
        writeConsent("denied");
        removeConsentPanel();
        preferencesButton.hidden = false;
        preferencesButton.focus();
      });
    panel
      .querySelector(".analytics-consent-allow")
      .addEventListener("click", () => {
        writeConsent("granted");
        loadAnalytics();
        removeConsentPanel();
        preferencesButton.hidden = false;
        preferencesButton.focus();
      });

    document.body.append(panel);
    panel.querySelector(".analytics-consent-allow").focus();
  }

  function addPreferencesButton() {
    const button = document.createElement("button");
    button.className = "analytics-preferences";
    button.type = "button";
    button.textContent = "Analytics preferences";
    button.addEventListener("click", () => showConsentPanel(button));

    const footer = document.querySelector(".footer-meta") || document.body;
    footer.append(button);
    return button;
  }

  addStyles();
  const preferencesButton = addPreferencesButton();
  const consent = readConsent();
  if (consent === "granted") {
    loadAnalytics();
  } else if (consent !== "denied") {
    showConsentPanel(preferencesButton);
  }
})();
