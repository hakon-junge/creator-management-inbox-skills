# Connect Gmail (about 15 minutes, once)

You create a small private "app" in Google Cloud that only you use. It lets the
`inbox` tool read your mail and create drafts in your own mailbox. Nobody else
(including the people who made this repo) ever sees your mail or your login.

**Why not a simpler login?** A shared app would mean one company holding
access to everyone's inbox. Your own app means the only copy of the key is on
your laptop.

Google renames these menus from time to time. If a button isn't where this says,
search the page for the word in **bold**, or ask Claude to open the page with you.

---

## Before you start: which kind of Gmail do you have?

- **Work Gmail (Google Workspace)** - your address is `you@yourcompany.com`.
  You'll choose **Internal** in step 3. Easiest path: no warnings, no weekly logout.
  Some companies block staff from creating these apps; if a step is greyed out,
  ask your IT admin (send them the "For IT admins" section below).
- **Personal Gmail** - your address ends in `@gmail.com`. You'll choose
  **External** in step 3 and add yourself as a test user. Read "Stop the weekly
  logout" at the end.

---

## Step 1 - Create a project

1. Open <https://console.cloud.google.com> and sign in with the Gmail account you
   want drafts in.
2. First time here? Accept the terms. (No credit card is needed for this.)
3. Top bar: click the project picker -> **New project**. Name it
   `Creator Management Inbox` -> **Create**. Make sure it's selected in the top bar afterwards.

## Step 2 - Turn on the Gmail API

1. Search bar at the top: type **Gmail API** and open it.
2. Click **Enable**.

## Step 3 - Set up the consent screen

1. Left menu (☰) -> **Google Auth Platform** -> **Branding**. If asked, click
   **Get started**.
2. App name: `Creator Management Inbox`. User support email: your address. **Next**.
3. **Audience**: **Internal** for work Gmail, **External** for personal Gmail. **Next**.
4. Contact email: your address. Agree to the policy -> **Create**.
5. Personal Gmail only: left menu -> **Audience** -> **Test users** -> **Add users**
   -> your Gmail address -> **Save**.

## Step 4 - Create the desktop client

1. Left menu -> **Clients** -> **Create client**.
2. Application type: **Desktop app**. Name: `Creator Management Inbox`. **Create**.
3. In the box that appears, click **Download JSON**. The file lands in your
   Downloads folder with a long name starting `client_secret_`.

   It must be a **Desktop app** client. A "Web application" client won't work.

## Step 5 - Hand the file to the inbox tool

In Claude, say: **"import my Gmail client file"**. Or run it yourself:

```bash
inbox import-client ~/Downloads/client_secret_*.json
```

It checks the file, stores a private copy at `~/.claude/inbox/`, and tells you
to delete the one in Downloads (do - it's a secret).

## Step 6 - Connect

```bash
inbox auth
```

Your browser opens:

1. Pick your Gmail account.
2. You'll see **"Google hasn't verified this app"**. That's expected: it's your
   own app, and Google only verifies apps offered to the public. Click
   **Continue** (on some screens: **Advanced** -> **Go to Creator Management Inbox**).
3. Tick both boxes: **read your email** and **manage drafts and send emails**.
   (Google has no "drafts only" permission. The tool has no send command, and its
   guard blocks sending during runs - see SECURITY.md.)
4. "The authentication flow has completed." Close the tab.

Back in Claude: `inbox whoami` should show your address. Then set
`provider: gmail` in `settings.md` (Claude does this for you).

---

## Stop the weekly logout (personal Gmail)

Google expires the connection **every 7 days** for External apps still in
"Testing". Two fixes:

- **Publish it (recommended).** Google Auth Platform -> **Audience** -> **Publish
  app** -> **Confirm**. You'll keep seeing the "unverified" screen when you connect,
  and Google caps unverified apps at 100 users - irrelevant for a one-person app.
  The weekly expiry stops. You do not need to submit for verification.
- **Or stay in Testing** and run `inbox auth` whenever a run says the connection
  expired. 30 seconds a week.

Work Gmail (Internal) never has this problem.

## For IT admins (Google Workspace)

The app requests `gmail.readonly` and `gmail.compose` for a single user's own
mailbox, via a Desktop OAuth client the user owns. Nothing leaves the user's
machine except calls to Google and to the Claude model that drafts replies.
To allow it: Admin console -> Security -> Access and data control -> API controls
-> manage third-party app access -> trust the user's OAuth client ID.
Your organisation's AI policy should also cover email content being processed by
Claude.

## Troubleshooting

| You see | Do this |
|---|---|
| `Access blocked: ... has not completed the Google verification process` | Personal Gmail: you're not a test user. Step 3.5. |
| `Error 400: redirect_uri_mismatch` | The client isn't a Desktop app. Redo step 4. |
| `admin_policy_enforced` | Workspace admin blocks it. Send them "For IT admins". |
| Browser didn't open | Copy the link `inbox auth` prints into your browser. |
| `invalid_grant` / "expired or revoked" after a week | See "Stop the weekly logout", then `inbox auth`. |
| Worked yesterday, not after a password change | Google revokes Gmail tokens on password change. `inbox auth`. |

## Disconnect at any time

<https://myaccount.google.com/permissions> -> Creator Management Inbox -> **Remove access**.
Then delete `~/.claude/inbox/token.json` (ask Claude: "disconnect my Gmail").
