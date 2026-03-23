# Startup Splash Regression Check

- time: 2026-03-23 10:41:09 +08:00
- target: `scripts/assets/workflow_startup_splash.html`
- scope: verify splash no longer redirects to a browser error page before the workflow service is actually reachable

## Verification

1. Inline script syntax check

```text
node --check %TEMP%\workflow_startup_splash.inline.js
result: ok
```

2. Edge headless probe against a closed port (`http://127.0.0.1:8766`)

```json
{
  "returncode": 0,
  "stays_on_splash": true
}
```

3. Edge headless probe against a local ready server (`http://127.0.0.1:8765`)

```json
{
  "returncode": 0,
  "requests": [
    "/healthz?_startup_probe=1774233757932",
    "/?_startup_probe=1774233758013",
    "/healthz?_startup_probe=1774233759134",
    "/?_startup_probe=1774233759144",
    "/"
  ],
  "redirected": true
}
```

## Conclusion

- closed port: splash remains on the startup page and does not redirect to a browser-generated connection error page
- open port: splash performs two successful probe cycles and then navigates to the target root path
