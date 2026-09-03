# Security policy

## Supported version

Security fixes are applied to the latest commit on `main`. There are no supported release branches yet.

## Reporting a vulnerability

Use GitHub's **Report a vulnerability** option in this repository's Security tab. Do not open a public issue containing exploit details, credentials, deployment identifiers, private URLs, transcripts, or personal data.

Include the affected component, reproduction steps, impact, and any suggested mitigation. You should receive an initial response within seven days.

## Sensitive local data

Keep `.env.local`, `livekit.toml`, console recordings, credentials, private endpoints, and real conversation data out of commits. Use dedicated least-privilege development credentials and rotate them immediately if they are exposed.
