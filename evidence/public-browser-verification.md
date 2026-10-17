# Public browser verification

- Checked: 2026-10-17
- Production URL: https://echo-turnstile.pages.dev/
- Browser-visible contract read: `get_ticket("REQ-B-1792202938")`
- Observed state: `REDIRECTED`
- Observed earlier match: `REQ-A-1792202938`
- Observed lane: `LANE-1792202938`
- Observed digest: `d959a3988dcced281e421405dc3710d6609118be20b5f2a63e5d04dcf0b00544`

The public receipt showed the finalized lane, sender, digest, and exact duplicate ID without connecting a wallet. The lane editor opened with the semantic rule and cooldown editable.
