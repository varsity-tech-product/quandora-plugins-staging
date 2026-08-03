# Install and authorize Quandora Staging in WorkBuddy

## One-sentence Agent request

The user should paste this sentence into a new local WorkBuddy task:

`Read https://raw.githubusercontent.com/varsity-tech-product/quandora-plugins-staging/main/workbuddy.md completely, then install and authorize Quandora Staging for me. I will complete the single browser Authenticate, Authorize, or Allow action when it opens.`

This is an instruction to the WorkBuddy Agent, not a slash command or shell command. If you are the Agent reading this document, read it completely and perform the installation, connection, and verification steps yourself. Do not send the user to Terminal or PowerShell, and do not ask the user to copy or submit a slash command.

The intended interaction is:

1. The Agent confirms that the current WorkBuddy host provides its bundled plugin-management and MCP capabilities.
2. The Agent invokes WorkBuddy's model-driven plugin commands to add or refresh the exact marketplace and install, update, and enable the exact user-scoped plugin.
3. WorkBuddy loads the remote MCP declaration distributed by the plugin and keeps the MCP identity tied to the plugin lifecycle.
4. The Agent requests one native, non-silent connection attempt for that plugin-provided MCP server.
5. WorkBuddy opens the system browser for its native OAuth flow.
6. The user completes any required account sign-in and the single browser **Authenticate**, **Authorize**, or **Allow** action.
7. The Agent calls a protected read-only Quandora tool and verifies the marketplace, plugin, skills, MCP source, endpoint, and authenticated state.

WorkBuddy may display its standard command-permission prompts according to the user's host settings. These are WorkBuddy security controls, not Quandora authorization. Do not bypass them.

## Installation contract

- Supported hosts: WorkBuddy Desktop 5.3.8 or later on macOS and Windows
- Marketplace repository: `https://github.com/varsity-tech-product/quandora-plugins-staging`
- Marketplace name: `quandora-staging`
- Plugin selector: `quandora-staging@quandora-staging`
- Plugin installation scope: `user`
- MCP registration name: `quandora-staging`
- MCP source: the installed `quandora-staging@quandora-staging` plugin
- Expected MCP transport: remote HTTP
- Expected MCP URL: `https://mcp-staging.varsity.lol/quant`
- Expected skills: `factor-mining` and `strategy-building`
- Authorization verification tool: `factor_mining_status`

Use the repository's default `main` branch. Do not pin a plugin version or commit. Do not clone the repository or install from a local checkout.

WorkBuddy Desktop includes the runtime used by its plugin manager. The user does not need a separately installed CodeBuddy CLI, Python, Node.js, npm, package manager, or local MCP process on either macOS or Windows.

## Safety boundaries

- Manage only the exact `quandora-staging` marketplace, plugin, and plugin-provided MCP server.
- Never remove, replace, disable, authenticate, or change a production marketplace, plugin, connector, or MCP server named `quandora`.
- Use WorkBuddy's native, model-driven plugin commands. Do not type those commands into the user's composer and do not ask the user to send them.
- Do not install or update a standalone CodeBuddy CLI. Do not install Python, Node.js, npm, Homebrew, Chocolatey, Scoop, PowerShell 7, WSL, an OAuth helper, or a third-party runtime.
- Do not run a downloaded shell script, PowerShell script, batch file, or executable.
- Do not create a second user, project, local, or custom MCP entry for the same endpoint.
- Do not run `codebuddy mcp add`, edit `~/.workbuddy/mcp.json`, edit WorkBuddy settings, or write plugin state manually.
- Do not create a custom HTTP header, bearer-token entry, API-key entry, local proxy, or local MCP process.
- Never ask for a Quandora API key, bearer token, OAuth token, callback code, cookie, authorization URL, or account credential.
- Never capture, print, save, parse, or relay OAuth secrets or authorization URLs.
- Do not automate browser sign-in, passkeys, MFA, consent, or the **Authenticate**, **Authorize**, or **Allow** action.
- If an existing marketplace, plugin, connector, or MCP entry uses the same staging identity with a different source, transport, command, URL, or headers, stop and report the non-sensitive conflict. Do not delete or overwrite it.

## 1. Confirm the WorkBuddy host capabilities

Determine the WorkBuddy Desktop version through the host's application information. Require version 5.3.8 or later.

Confirm that the current task exposes both of these native capabilities:

- model-driven invocation of WorkBuddy's built-in `/plugin` command;
- native MCP inventory and reconnect operations used by WorkBuddy's MCP management panel.

Use the host capabilities directly. Do not search the system `PATH`, open an external terminal, start a nested interactive CLI, or inspect WorkBuddy's private configuration files.

If the installed application is older or either capability is absent, stop and tell the user to update WorkBuddy from its official in-app updater or official download page, then begin a new local task. Do not substitute a standalone CLI, local script, direct MCP entry, or private WorkBuddy API.

## 2. Add or refresh the exact marketplace

Invoke the following through WorkBuddy's model-driven slash-command capability. These are Agent actions; do not put the text into the user's message composer:

```text
/plugin marketplace list
```

Match the exact marketplace name `quandora-staging` and verify that its source is the public GitHub repository `varsity-tech-product/quandora-plugins-staging`. Treat the HTTPS URL with or without a trailing `.git` as the same repository.

- If the marketplace is absent, invoke:

  ```text
  /plugin marketplace add varsity-tech-product/quandora-plugins-staging --name quandora-staging
  ```

- If exactly one matching marketplace points to the expected repository, invoke:

  ```text
  /plugin marketplace update quandora-staging
  ```

- If the same marketplace name points to another owner, repository, host, branch, local path, or HTTP manifest, stop and report the source conflict.

List marketplaces again and require one `quandora-staging` entry for the expected public GitHub repository. For a timeout, DNS failure, connection reset, or HTTP 5xx response, allow the first operation to finish and retry once. Never run concurrent marketplace operations.

## 3. Install, update, and enable the plugin

Inspect the structured plugin inventory through the native plugin command:

```text
/plugin list --json
```

- If `quandora-staging@quandora-staging` is absent, invoke:

  ```text
  /plugin install quandora-staging@quandora-staging --scope user
  ```

- If it is already installed, invoke:

  ```text
  /plugin update quandora-staging@quandora-staging --scope user
  ```

- If it is disabled, invoke:

  ```text
  /plugin enable quandora-staging@quandora-staging --scope user
  ```

Read the plugin inventory again. Require exactly one enabled, user-scoped `quandora-staging@quandora-staging` item with a non-empty version and no dependency errors.

Require the installed package to contain both `factor-mining` and `strategy-building` skills and its plugin-provided `.mcp.json`. Require that `.mcp.json` resolves the `quandora-staging` server to remote HTTP at exactly `https://mcp-staging.varsity.lol/quant`, with no local command, custom headers, or static credentials.

Do not create replacement skills or alter the installed package. Refresh the marketplace and update the plugin once, then stop and report the incomplete package if a required component remains missing.

## 4. Load the plugin-provided MCP server

Refresh WorkBuddy's native MCP inventory and locate the server named exactly `quandora-staging`.

Require all of the following before starting authorization:

- the MCP source is the installed `quandora-staging@quandora-staging` plugin;
- the transport is remote HTTP;
- the URL is exactly `https://mcp-staging.varsity.lol/quant`;
- no custom headers or static credentials are present;
- no second custom, user, project, or workspace MCP entry with the same name was created.

If the plugin is enabled but the plugin-provided MCP server is not present, request one native plugin and MCP inventory refresh. If it remains absent, stop and report that WorkBuddy did not load the plugin's `.mcp.json`. Do not work around this by creating a direct MCP entry.

## 5. Start native OAuth authorization

Use the current WorkBuddy host's native MCP reconnect operation for the exact plugin-provided server `quandora-staging`. The operation must be non-silent so WorkBuddy can open the authorization URL in the system browser.

Do not simulate a click, invoke a private localhost API, edit a configuration file, start a nested CLI, or use an OAuth helper. The reconnect must remain inside WorkBuddy's native MCP lifecycle.

When the browser opens, tell the user that Quandora Staging is ready for authorization and wait. The user may need to complete account sign-in, passkey, or MFA, followed by one **Authenticate**, **Authorize**, or **Allow** action. Never perform those identity or consent actions for the user.

After the user finishes, let WorkBuddy receive its OAuth callback and reconnect the same plugin-provided MCP server. Do not create concurrent authorization attempts.

If no browser opens, allow the first connection attempt to finish, refresh the exact MCP server once, and request one fresh native reconnect. If the second native attempt also produces no authorization flow, stop and report that the current WorkBuddy host did not expose or execute a non-silent MCP reconnect. Do not fall back to a direct MCP entry, standalone CLI login, browser automation, local script, API key, or static token.

If the first authorization attempt is cancelled, expires, or ends with a transient network error, allow it to finish and offer one fresh native attempt. Otherwise report the exact error and stop.

An MCP status of `Connected` is not sufficient evidence of authorization because the initial MCP handshake can complete before a protected tool call succeeds.

## 6. Final verification gate

Reinspect the marketplace, plugin, skills, and MCP inventory through WorkBuddy's native capabilities. Then call the protected read-only MCP tool `factor_mining_status` through the current WorkBuddy task.

Do not replace this verification with an unauthenticated HTTP request or a connection-status check.

Do not report success until all of these are true:

1. The exact expected public GitHub marketplace is present as `quandora-staging`.
2. `quandora-staging@quandora-staging` is installed, enabled, and user-scoped with a non-empty version and no dependency errors.
3. The installed plugin exposes `factor-mining` and `strategy-building`.
4. The effective `quandora-staging` MCP server comes from that plugin and uses remote HTTP at exactly `https://mcp-staging.varsity.lol/quant`, with no custom headers or static credentials.
5. No duplicate custom, user, project, or workspace MCP entry was created.
6. The protected `factor_mining_status` call succeeds after the user's browser authorization.
7. No production `quandora` marketplace, plugin, connector, MCP server, setting, or credential changed.

If the authenticated tool call has one transient connection timeout, retry it once. Otherwise report the exact incomplete gate and stop; never describe a partial installation as successful.

After all gates pass, tell the user that Quandora Staging is installed, authorized, and ready in WorkBuddy.
