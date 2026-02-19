export interface SlackSetupRequest {
  client_id: string;
  client_secret: string;
}

export interface SlackOAuthURLResponse {
  oauth_url: string;
  message: string;
}

export interface SlackChannel {
  id: string;
  name: string;
}

export interface SlackStatus {
  connected: boolean;
  has_credentials: boolean;
  team_name?: string;
  channel_id?: string;
  channel_name?: string;
}
