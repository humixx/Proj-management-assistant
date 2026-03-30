import apiClient from './client';

export interface BillingStatus {
  is_active: boolean;
  is_trialing: boolean;
  plan_type: string;
  provider: string | null;
  trial_ends_at: string | null;
  current_period_end: string | null;
  subscription: {
    id: string;
    provider: string | null;
    plan_type: string;
    status: string;
    trial_ends_at: string | null;
    current_period_start: string | null;
    current_period_end: string | null;
    canceled_at: string | null;
    created_at: string;
    updated_at: string;
  } | null;
}

export interface PaymentProvider {
  id: string;
  name: string;
  label: string;
}

export interface CheckoutResponse {
  checkout_url: string;
  session_id: string | null;
  provider: string;
}

export const billingApi = {
  /** Get available payment providers configured on the backend. */
  providers: async (): Promise<{ providers: PaymentProvider[] }> => {
    const response = await apiClient.get('/billing/providers');
    return response.data;
  },

  /** Get the current user's billing/subscription status. */
  status: async (): Promise<BillingStatus> => {
    const response = await apiClient.get('/billing/status');
    return response.data;
  },

  /** Create a checkout session to subscribe via the given provider. */
  checkout: async (
    provider: string,
    plan: string = 'pro',
    successUrl?: string,
    cancelUrl?: string,
  ): Promise<CheckoutResponse> => {
    const response = await apiClient.post('/billing/checkout', {
      provider,
      plan,
      success_url: successUrl,
      cancel_url: cancelUrl,
    });
    return response.data;
  },

  /** Create a customer portal session for billing management. */
  portal: async (): Promise<{ portal_url: string; provider: string }> => {
    const response = await apiClient.post('/billing/portal');
    return response.data;
  },
};

export default billingApi;
