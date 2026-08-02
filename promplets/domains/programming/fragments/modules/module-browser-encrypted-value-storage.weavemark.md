@promplet version: 0.7

@module weavemark.domains.programming.modules.browser_encrypted_value_storage

@note
  Reusable browser-secret persistence contract. Consumers configure:
  - secret_crypto_requirement: "mandatory" | "optional"
  - secret_storage_backend: "cookie" | "local-storage" | "indexeddb" | "none"
  - secret_unlock_mode: "passphrase" | "external-key"
  - secret_cookie_name, secret_cookie_days, secret_cookie_path
  - secret_kdf_iterations, secret_min_passphrase_length, secret_context
  - secret_allow_replacement: "on" | "off"

# Module: Browser Encrypted Secret Storage

Use this module only when a browser application has a legitimate user-controlled
reason to restore a secret across page sessions. Session memory remains safer.
Client-side encryption reduces accidental disclosure and plaintext-at-rest risk;
it does not protect against malicious same-origin script, XSS, a compromised
browser profile, or an attacker who knows the unlock secret.

## Requirement mode

@match secret_crypto_requirement
  "mandatory" ==>
    The product MUST implement the configured encrypted persistence path. If Web
    Crypto, secure randomness, storage, or unlock material is unavailable, fail
    closed and keep the secret disconnected. Never persist plaintext or silently
    downgrade.
  "optional" ==>
    Encrypted persistence is explicitly opt-in and session-only use is the
    default. Declining, cancelling, or failing persistence MUST leave the
    session-only path fully usable. "Optional" never permits plaintext storage.
  _ ==>
    Reject unsupported secret_crypto_requirement values during validation.

## Persistence backend

@match secret_storage_backend
  "cookie" ==>
    Store only one compact versioned ciphertext envelope in a host-only cookie
    named `@{secret_cookie_name}`. Scope it to `@{secret_cookie_path}`, use
    `SameSite=Strict`, set `Secure` on HTTPS, omit `Domain`, enforce a maximum
    lifetime of @{secret_cookie_days} days, and delete with identical attributes.
    JavaScript-created cookies cannot be HttpOnly; disclose that limitation.
    Keep the encoded value safely below browser cookie limits and reject overflow.
  "local-storage" ==>
    Store only the versioned ciphertext envelope under a namespaced key. Never
    store plaintext, unlock material, provider responses, or request history.
  "indexeddb" ==>
    Store only the versioned ciphertext envelope in a dedicated versioned object
    store. Treat transaction or quota failure as persistence failure.
  "none" ==>
    Do not persist the secret. Keep it in page/session memory only and make all
    persistence controls unavailable.
  _ ==>
    Reject unsupported secret_storage_backend values during validation.

## Unlock mode

@match secret_unlock_mode
  "passphrase" ==>
    Derive a non-extractable AES-256-GCM key with PBKDF2-HMAC-SHA-256 using a
    unique random salt, at least @{secret_kdf_iterations} iterations, and a
    passphrase of at least @{secret_min_passphrase_length} characters. Never
    persist or log the passphrase. Keep the derived key only in page memory.
  "external-key" ==>
    Accept a non-extractable key from an explicitly configured platform
    credential or key broker. Never synthesize, persist, or recover raw key
    material through browser storage.
  _ ==>
    Reject unsupported secret_unlock_mode values during validation.

## Cryptographic envelope

- Use `crypto.getRandomValues` for a fresh 128-bit salt and 96-bit IV on initial
  save; every subsequent encryption MUST use a fresh IV.
- Use AES-256-GCM and authenticate a stable context containing origin,
  `@{secret_context}`, envelope version, and storage key/cookie name.
- Store only a closed envelope containing version, algorithm, KDF parameters,
  salt, IV, ciphertext/tag, creation time, and expiry time, encoded base64url.
- Validate every field and bound before derivation or decryption. Reject expired,
  malformed, oversized, unknown-version, unknown-algorithm, or authentication-
  failed envelopes with one clear recovery action; never return partial plaintext.
- Decrypt only after an explicit user unlock gesture. Finding stored ciphertext
  MUST NOT connect a provider, imply consent, or transmit anything.
- After unlock, explain that encrypted storage was unlocked for this page
  session. Keep plaintext and derived keys only in memory and clear references on
  forget, replacement, page exit, and authentication failure. Do not claim
  guaranteed JavaScript memory erasure.

## Replacement and deletion

@match secret_allow_replacement
  "on" ==>
    Let the user keep the unlocked secret or replace it. Replacement is one
    authenticated write with a fresh IV and updated expiry; failure preserves the
    prior valid envelope and reports that the replacement was not saved.
  "off" ==>
    Do not replace in place. Require explicit deletion followed by a fresh save.
  _ ==>
    Reject unsupported secret_allow_replacement values during validation.

Forget MUST disconnect the in-memory secret, abort dependent work, and delete the
encrypted envelope. Provide a separate session-end path when the product needs to
disconnect without deleting an intentionally saved envelope.

## Verification

Test round-trip encryption, wrong passphrase, tampering, malformed base64url,
unknown versions, expiry, cookie/storage limits, attribute/path deletion parity,
replacement rollback, opt-in cancellation, unavailable Web Crypto, no plaintext
in storage, no automatic provider call after discovery, and reload/unlock/forget.
Use test-only secrets and inspect storage, logs, URLs, exports, and telemetry for
leakage.
