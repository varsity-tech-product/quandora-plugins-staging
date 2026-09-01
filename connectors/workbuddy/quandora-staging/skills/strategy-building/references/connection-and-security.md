# Connection and Security

Load this reference only when a required canonical Quandora Staging action is unavailable or the
host reports terminal authorization failure.

OAuth and credentials are host-managed. Never inspect, print, copy, store, or ask for API keys,
bearer/access/refresh tokens, authorization codes, PKCE verifiers, service tokens, or pasted
credentials. Do not reauthorize merely because an access token expired while the host is
refreshing.

Use only WorkBuddy's native Connector recovery path: reconnect the `quandora-staging` Connector,
complete browser authorization when prompted, and start a new chat so the authenticated tools are
loaded. If the Connector remains unavailable, report that state and ask the user to manage it from
WorkBuddy's Connector settings. Do not install, update, or reinstall another plugin as recovery.

Do not use raw HTTP, local helper scripts, internal service paths, or credential paste. The only
direct HTTP exception is immediate consumption of the opaque short-lived URL returned by
`create_strategy_result_bundle_download`; never construct, modify, persist, reuse, or summarize it.
