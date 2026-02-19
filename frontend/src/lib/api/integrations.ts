import apiClient from './client';

export const integrationsApi = {
  setup: async (clientId: string, clientSecret: string) => {
    const response = await apiClient.post('/integrations/slack/setup', { client_id: clientId, client_secret: clientSecret });
    return response.data;
  },

  callback: async (code: string, redirectUri: string) => {
    // POST the code and redirect_uri in the request body as the backend expects
    const response = await apiClient.post('/integrations/slack/callback', { code, redirect_uri: redirectUri });
    return response.data;
  },

  status: async () => {
    const response = await apiClient.get('/integrations/slack/status');
    return response.data;
  },

  channels: async () => {
    const response = await apiClient.get('/integrations/slack/channels');
    return response.data;
  },

  setDefaultChannel: async (channelId: string, channelName?: string) => {
    const response = await apiClient.put('/integrations/slack/channel', { channel_id: channelId, channel_name: channelName });
    return response.data;
  },

  sendMessage: async (message: string, channel?: string) => {
    const response = await apiClient.post('/integrations/slack/send', { message, channel });
    return response.data;
  },

  disconnect: async () => {
    const response = await apiClient.delete('/integrations/slack');
    return response.data;
  },
};

export default integrationsApi;

