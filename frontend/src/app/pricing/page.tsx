'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { billingApi, BillingStatus, PaymentProvider } from '@/lib/api/billing';
import { useProjectStore } from '@/lib/stores';

interface Feature {
  text: string;
  limited?: boolean; // shown with a muted "limited" badge
}

const FEATURES_FREE: Feature[] = [
  { text: '1 Project' },
  { text: '50 AI Messages / month' },
  { text: 'Basic Task Management' },
  { text: 'Document Upload (5 MB)' },
  { text: 'Slack Integration (1 channel)', limited: true },
  { text: 'AI Model Selection (1 provider)', limited: true },
  { text: 'Community Support' },
];

const FEATURES_PRO: Feature[] = [
  { text: 'Unlimited Projects' },
  { text: 'Unlimited AI Messages' },
  { text: 'Advanced Planning & Workflows' },
  { text: 'Document Upload (100 MB)' },
  { text: 'Full Slack Integration' },
  { text: 'All AI Model Providers' },
  { text: 'Priority Support' },
  { text: 'Team Collaboration' },
];

export default function PricingPage() {
  const { currentProject } = useProjectStore();
  const backHref = currentProject ? `/projects/${currentProject.id}/chat` : '/';

  const [billingStatus, setBillingStatus] = useState<BillingStatus | null>(null);
  const [providers, setProviders] = useState<PaymentProvider[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const load = async () => {
      try {
        const [statusRes, providersRes] = await Promise.all([
          billingApi.status().catch(() => null),
          billingApi.providers(),
        ]);
        if (statusRes) setBillingStatus(statusRes);
        setProviders(providersRes.providers);
        if (providersRes.providers.length > 0) {
          setSelectedProvider(providersRes.providers[0].id);
        }
      } catch {
        setError('Failed to load billing information.');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  // Load Paddle.js for overlay checkout
  useEffect(() => {
    if (providers.some(p => p.id === 'paddle')) {
      const existing = document.querySelector('script[src*="paddle.com"]');
      if (!existing) {
        const script = document.createElement('script');
        script.src = 'https://cdn.paddle.com/paddle/v2/paddle.js';
        script.async = true;
        script.onload = () => {
          const env = 'sandbox'; // Match PADDLE_ENVIRONMENT
          (window as any).Paddle?.Environment?.set?.(env);
          (window as any).Paddle?.Setup?.({
            seller: undefined, // Not needed for transaction-based checkout
          });
        };
        document.head.appendChild(script);
      }
    }
  }, [providers]);

  const handleCheckout = async () => {
    if (!selectedProvider) return;
    setCheckoutLoading(true);
    setError('');
    try {
      const result = await billingApi.checkout(
        selectedProvider,
        'pro',
        `${window.location.origin}/settings?billing=success`,
        `${window.location.origin}/pricing?billing=canceled`,
      );

      if (selectedProvider === 'paddle' && result.session_id) {
        // Open Paddle.js overlay with the transaction ID
        (window as any).Paddle?.Checkout?.open({
          transactionId: result.session_id,
          settings: {
            successUrl: `${window.location.origin}/settings?billing=success`,
          },
        });
      } else if (result.checkout_url) {
        // Stripe: redirect to hosted checkout page
        window.location.href = result.checkout_url;
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create checkout session.');
    } finally {
      setCheckoutLoading(false);
    }
  };

  const isActive = billingStatus?.is_active ?? false;
  const isTrialing = billingStatus?.is_trialing ?? false;
  const isPro = billingStatus?.plan_type === 'pro';

  const trialDaysLeft = billingStatus?.trial_ends_at
    ? Math.max(0, Math.ceil((new Date(billingStatus.trial_ends_at).getTime() - Date.now()) / (1000 * 60 * 60 * 24)))
    : 0;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      {/* Navigation */}
      <nav className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link href={backHref} className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                Project Management Assistant
              </h1>
            </Link>
            <div className="flex items-center space-x-4">
              <Link
                href={backHref}
                className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md transition-colors"
              >
                ← Back
              </Link>
              <Link
                href="/settings"
                className="px-4 py-2 text-sm font-medium text-gray-600 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 rounded-md"
              >
                Settings
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="text-center mb-12 animate-fade-in">
          <h2 className="text-4xl font-extrabold text-gray-900 dark:text-white mb-3">
            Choose Your Plan
          </h2>
          <p className="text-lg text-gray-500 dark:text-gray-400 max-w-2xl mx-auto">
            Start with a 7-day free trial of Pro. No credit card required to begin.
            Upgrade anytime to unlock the full power of AI-driven project management.
          </p>
          {isTrialing && trialDaysLeft > 0 && (
            <div className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-full">
              <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
              <span className="text-sm font-medium text-blue-700 dark:text-blue-300">
                Trial active — {trialDaysLeft} day{trialDaysLeft !== 1 ? 's' : ''} remaining
              </span>
            </div>
          )}
        </div>

        {error && (
          <div className="mb-8 p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg text-sm text-red-700 dark:text-red-300">
            {error}
          </div>
        )}

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {/* Free Plan */}
          <div className="animate-fade-in-delay bg-white dark:bg-gray-900 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 p-8 flex flex-col">
            <div className="mb-6">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-1">Free</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                For individuals getting started
              </p>
            </div>
            <div className="mb-8">
              <span className="text-5xl font-extrabold text-gray-900 dark:text-white">$0</span>
              <span className="text-gray-500 dark:text-gray-400 ml-1">/month</span>
            </div>
            <ul className="space-y-3 mb-8 flex-1">
              {FEATURES_FREE.map((f) => (
                <li key={f.text} className="flex items-start gap-3 text-sm text-gray-600 dark:text-gray-300">
                  <svg className={`w-5 h-5 flex-shrink-0 mt-0.5 ${f.limited ? 'text-amber-400 dark:text-amber-500' : 'text-gray-400 dark:text-gray-500'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="flex items-center gap-2">
                    {f.text}
                    {f.limited && (
                      <span className="text-[10px] font-semibold uppercase tracking-wide px-1.5 py-0.5 rounded bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400">
                        Limited
                      </span>
                    )}
                  </span>
                </li>
              ))}
            </ul>
            <button
              disabled
              className="w-full py-3 px-4 rounded-xl font-semibold text-sm bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400 border border-gray-200 dark:border-gray-700 cursor-default"
            >
              {!isPro ? 'Current Plan' : 'Downgrade'}
            </button>
          </div>

          {/* Pro Plan */}
          <div className="animate-fade-in-delay-2 relative bg-white dark:bg-gray-900 rounded-2xl shadow-xl border-2 border-blue-500 dark:border-blue-400 p-8 flex flex-col ring-1 ring-blue-500/20">
            {/* Badge */}
            <div className="absolute -top-4 left-1/2 -translate-x-1/2">
              <span className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full text-xs font-bold bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-500/25">
                <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
                MOST POPULAR
              </span>
            </div>

            <div className="mb-6 mt-2">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-1">Pro</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                For teams who want to move faster
              </p>
            </div>
            <div className="mb-8">
              <span className="text-5xl font-extrabold text-gray-900 dark:text-white">$19</span>
              <span className="text-gray-500 dark:text-gray-400 ml-1">/month</span>
            </div>
            <ul className="space-y-3 mb-8 flex-1">
              {FEATURES_PRO.map((f) => (
                <li key={f.text} className="flex items-start gap-3 text-sm text-gray-700 dark:text-gray-200">
                  <svg className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                  {f.text}
                </li>
              ))}
            </ul>

            {/* Provider selection + CTA */}
            {!loading && (
              <div className="space-y-3">
                {providers.length > 1 && (
                  <div className="flex gap-2">
                    {providers.map((p) => (
                      <button
                        key={p.id}
                        onClick={() => setSelectedProvider(p.id)}
                        className={`flex-1 py-2 px-3 rounded-lg text-xs font-medium border transition-all ${
                          selectedProvider === p.id
                            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                            : 'border-gray-200 dark:border-gray-700 text-gray-500 dark:text-gray-400 hover:border-gray-300 dark:hover:border-gray-600'
                        }`}
                      >
                        {p.label}
                      </button>
                    ))}
                  </div>
                )}
                <button
                  onClick={handleCheckout}
                  disabled={checkoutLoading || (isPro && isActive && !isTrialing)}
                  className="w-full py-3.5 px-4 rounded-xl font-bold text-sm bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40 transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed disabled:shadow-none"
                >
                  {checkoutLoading
                    ? 'Redirecting...'
                    : isPro && isActive && !isTrialing
                      ? '✓ Current Plan'
                      : isTrialing
                        ? 'Upgrade Now — Skip Trial'
                        : 'Start 7-Day Free Trial'}
                </button>
                <p className="text-center text-xs text-gray-400 dark:text-gray-500">
                  Secure payment via Visa, Mastercard & more
                </p>
              </div>
            )}
          </div>
        </div>

        {/* FAQ / Trust */}
        <div className="mt-16 text-center animate-fade-in-delay-2">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Cancel anytime — no questions asked. Payments processed securely by{' '}
            {providers.map((p) => p.name).join(' & ') || 'Stripe & Paddle'}.
          </p>
        </div>
      </main>
    </div>
  );
}
