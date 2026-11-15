# Automated Multi-Platform Posting API

A Python 3 and FastAPI service that validates a short message and attempts to publish it to five platforms: **Bluesky, Mastodon, Telegram, Discord, and DEV.to**.

Each platform is handled by an independent adapter. A failure on one platform should not prevent the application from attempting publication on the others. Platform selection is configured internally by the application; API clients submit a message only.

## Features

- REST API endpoint: `POST /posting`
- Message validation: 1–200 characters and exactly one valid HTTP(S) URL
- Internal fan-out to five platform integrations
- Independent result reporting for each platform
- Per-platform error handling so one failure does not cancel the other attempts
- Result fields for platform, status, post URL, public-access indication, date, time, and error
- Credentials loaded from environment variables rather than hard-coded in source files
- Automated tests using `pytest`

## Tech stack

- Python 3.11 or newer
- FastAPI
- Pydantic
- HTTPX
- Uvicorn
- Pytest

## Project structure

```text
automated-posting/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   ├── platforms/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── bluesky.py
│   │   ├── mastodon.py
│   │   ├── telegram.py
│   │   ├── discord.py
│   │   └── devto.py
│   └── services/
│       ├── __init__.py
│       └── posting_service.py
├── tests/
│   └── test_posting.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## Requirements

- Python 3.11 or newer
- Git (optional, for version control)
- Accounts and API credentials for the platforms you want to publish to

## Setup on Windows (PowerShell)

Open PowerShell in the project directory.

### 1. Create and activate a virtual environment

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use the Python executable inside the environment directly or adjust the execution policy for your user according to your organization's policy.

### 2. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3. Create your environment file

Create `.env` from the example only when it does not already exist. This avoids overwriting credentials you have already configured.

```powershell
if (!(Test-Path .env)) {
    Copy-Item .env.example .env
}
```

Open `.env` and replace the placeholders with your own credentials. Keep `.env` private and do not commit it to Git.

## Environment variables

The application reads the following variables from `.env`:

| Variable | Purpose |
|---|---|
| `BLUESKY_HANDLE` | Bluesky account handle, for example `yourname.bsky.social` |
| `BLUESKY_APP_PASSWORD` | App Password generated in Bluesky account settings |
| `MASTODON_BASE_URL` | Base URL of the Mastodon instance where your account is registered |
| `MASTODON_ACCESS_TOKEN` | Mastodon access token with status-writing permission (`write:statuses`) |
| `TELEGRAM_BOT_TOKEN` | Token generated for your bot by `@BotFather` |
| `TELEGRAM_CHAT_ID` | Destination channel username or chat ID; for a public channel, use a value such as `@your_channel` |
| `DISCORD_WEBHOOK_URL` | Webhook URL created for the destination Discord channel |
| `DEVTO_API_KEY` | API key generated in DEV Community account settings |
| `REQUEST_TIMEOUT_SECONDS` | HTTP request timeout in seconds (the example uses `20`) |

The `.env.example` file documents the expected variable names. It should contain placeholders only, never real credentials.

## Platform configuration

### 1. Bluesky

1. Create or use a Bluesky account.
2. Generate an App Password in the account's **Settings → Advanced → App Passwords** area.
3. Set `BLUESKY_HANDLE` and `BLUESKY_APP_PASSWORD` in `.env`.

The adapter authenticates with the Bluesky API and creates a post. It constructs the post permalink using the account and record information returned by the API.

Documentation: <https://docs.bsky.app/docs/tutorials/creating-a-post>

### 2. Mastodon

1. Create or use an account on a Mastodon instance.
2. Register an application in the instance's **Preferences → Development** area.
3. Grant the application status-writing permission (`write:statuses`) and obtain an access token.
4. Set `MASTODON_BASE_URL` to your account's instance URL and set `MASTODON_ACCESS_TOKEN` in `.env`.

The adapter publishes a status to the configured Mastodon instance. The base URL must match the instance on which the token was created.

Documentation: <https://docs.joinmastodon.org/methods/statuses/>

### 3. Telegram

1. Create a bot using the official `@BotFather` account and obtain its bot token.
2. Create or choose a destination channel.
3. Add the bot as a channel administrator and grant permission to post messages.
4. Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `.env`.

For a public channel, `TELEGRAM_CHAT_ID` can be the channel username, such as `@your_channel`. A private channel may require its numeric chat ID. A successful delivery to a private channel does not mean the message is publicly accessible.

Documentation: <https://core.telegram.org/bots/api#sendmessage>

### 4. Discord

1. Create or choose a Discord server and text channel.
2. Open the server's **Settings → Integrations → Webhooks** area.
3. Create a webhook for the destination channel and copy its URL.
4. Set `DISCORD_WEBHOOK_URL` in `.env`.

The adapter executes the webhook and requests the created message object so it can build a Discord message permalink when the webhook metadata and message response provide the required IDs. A permalink does not establish that the channel is publicly accessible; therefore, the adapter reports `public_access` as `false`.

Keep the webhook URL secret. Anyone who obtains it may be able to post to its configured channel.

Documentation: <https://discord.com/developers/docs/resources/webhook#execute-webhook>

### 5. DEV.to

1. Create or use a DEV Community account.
2. Generate an API key in the account's **Settings → Extensions** area.
3. Set `DEVTO_API_KEY` in `.env`.

DEV.to is an article-publishing platform rather than a short-status social feed. The current adapter creates an article using the message as its Markdown body and the title `Automated update`. This means a short message is published as an article, not as a conventional micro-post.

Documentation: <https://developers.forem.com/api/v1#tag/articles/operation/createArticle>

## Run the application

Activate the virtual environment, then run:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 4000
```

The API will be available at:

- Health check: <http://127.0.0.1:4000/>
- Interactive API documentation: <http://127.0.0.1:4000/docs>
- OpenAPI schema: <http://127.0.0.1:4000/openapi.json>

Keep the server process running while sending requests. Stop it with `Ctrl+C`.

## API usage

### Endpoint

```http
POST /posting
Content-Type: application/json
```

### Request body

The client sends only a `message`. The target platforms are configured internally and are not selected by the request.

```json
{
  "message": "Check out our latest update: https://example.com"
}
```

### Validation rules

- `message` must contain between 1 and 200 characters.
- The message must contain exactly one HTTP or HTTPS URL.
- The URL must be valid.
- Additional request fields, including a client-supplied platform list, are not accepted.

A request that fails validation is rejected by FastAPI/Pydantic before publishing begins.

### Response format

The response contains an overall outcome and one result for each configured platform. A result includes:

| Field | Meaning |
|---|---|
| `platform` | Platform name |
| `status` | `success` or `failed` |
| `posted_url` | Platform post/article permalink, when available |
| `public_access` | Whether the adapter has a basis to report the content as publicly accessible |
| `date` | Local server date when the adapter creates its result |
| `time` | Local server time when the adapter creates its result |
| `error` | Error description when publishing fails; otherwise `null` |

The top-level fields are:

- `success`: `true` when at least one platform reports successful publication; otherwise `false`.
- `overall_status`: `success` when every configured platform succeeds, `partial_success` when at least one but not all succeed, or `failed` when all fail.
- `results`: per-platform outcomes.

The date and time values are generated using the local server timezone. They are not timestamps supplied by the third-party platforms. A `public_access` value of `true` is the adapter's determination; verify important posts independently where public visibility matters. Discord reports `false` because a message permalink does not prove anonymous public access.

## Run tests

From the project directory, with the virtual environment activated, run:

```powershell
python -m pytest -q
```

The automated tests cover request validation and response/partial-success behavior. They do not publish to the real third-party platforms. End-to-end publishing requires valid credentials and should be verified by checking the resulting content on each platform.

## Security notes

- Never commit `.env` or share its contents publicly.
- Keep `.env.example` limited to placeholder values.
- Keep Bluesky App Passwords, Mastodon tokens, Telegram bot tokens, Discord webhook URLs, and DEV.to API keys private.
- The `.gitignore` file excludes `.env` and local virtual-environment/cache directories. Verify the staged files before pushing to a public repository.
- If a credential is accidentally exposed, revoke or rotate it with the relevant platform.
- Use test accounts or channels when validating real publishing, because API tests can create visible posts or articles.

## Known limitations and possible improvements

- Third-party APIs may enforce rate limits, content restrictions, and account-specific permissions.
- DEV.to publishes an article rather than a short social status.
- Discord message permalinks may require server membership or channel permissions, even when a permalink is available.
- The date/time fields represent the local server time at result creation, not the platform's authoritative publication timestamp.
- A production deployment should consider structured logging, retry/backoff for transient errors, endpoint authentication, rate limiting, persistent audit records, and monitoring.

## License

Add a license file if you intend to distribute this project under a specific open-source license. Until then, no license is granted by this README.
