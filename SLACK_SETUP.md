# Setting up the Slack Integration

The AI Project Management Assistant can integrate with your Slack workspace, allowing it to respond to messages, sync tasks, and provide interactive buttons inside Slack messages.

## Installation Steps (Using the Manifest)

The easiest way to install the Slack app is by using the **App Manifest**. The manifest configures all required scopes, event subscriptions, and webhooks automatically.

### 1. Copy the App Manifest
1. Run your frontend application.
2. Navigate to **Settings > Integrations** in the UI.
3. Under the Slack Setup section, click **Copy JSON** to copy the pre-configured App Manifest.
   *(This manifest is hardcoded to connect to the `pm.fiqros.org` servers).*

### 2. Create the App in Slack
1. Go to [https://api.slack.com/apps](https://api.slack.com/apps).
2. Click **Create New App**.
3. Choose **From an app manifest**.
4. Select the workspace you want to install it to.
5. Paste the copied JSON array into the text box and click **Next**.
6. Review the summary and click **Create**.

### 3. Install the App to your Workspace
1. Inside your newly created app's settings screen, click on **Install to Workspace** (usually found in the left sidebar under Settings > Install App).
2. Authorize the app to access your workspace.

### 4. Provide Credentials to the Assistant
1. Still inside your Slack App settings, go to **Basic Information** (left sidebar).
2. Scroll down to the **App Credentials** section.
3. Copy the **Client ID** and the **Client Secret**.
4. Go back to your Project Assistant frontend (**Settings > Integrations**).
5. Paste the **Client ID** and **Client Secret** into Step 2 of the form and click **Save & Connect to Slack**.

---

## Required Permissions (For Manual Configuration)

If you prefer to set up the app manually without the manifest, you will need to configure the following:

**OAuth & Permissions (Bot Token Scopes):**
- `channels:history`
- `channels:join`
- `channels:read`
- `chat:write`
- `groups:read`
- `im:read`
- `mpim:read`
- `reactions:read`
- `users:read`
- `users:read.email`

**Event Subscriptions:**
- Request URL: `https://pm.fiqros.org/api/integrations/slack/webhook`
- Subscribe to bot events: `reaction_added`

**Interactivity & Shortcuts:**
- Interactivity Request URL: `https://pm.fiqros.org/api/integrations/slack/interactions`

**OAuth Redirect URL:**
- `https://pm.fiqros.org/settings/integrations`
