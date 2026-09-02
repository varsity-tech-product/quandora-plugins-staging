# Connection and Security

Load this reference only when Quandora Staging tools are unavailable or authentication has
terminally failed.

OAuth and credentials are host-managed. Never inspect, print, copy, store, or ask for API keys,
bearer/access/refresh tokens, authorization codes, PKCE verifiers, service tokens, or pasted
credentials. Token expiry alone is not a reason to start another authorization flow while the host
is refreshing.

Use only WorkBuddy's native Connector recovery path: reconnect the `quandora-staging` Connector,
complete browser authorization when prompted, and start a new chat so the authenticated tools are
loaded. If the Connector remains unavailable, report that state and ask the user to manage it from
WorkBuddy's Connector settings. Do not install, update, or reinstall another plugin as recovery.

Do not use raw HTTP, local helper scripts, internal service endpoints, local execution keys, or a
credential-paste flow. The only direct HTTP exception is immediate consumption of an unmodified,
short-lived Result Bundle URL returned by the canonical bundle-ticket action. Never construct,
persist, log, reuse, or summarize that URL.
