import React, { useState } from 'react';
import { X, ArrowRight, Sparkles, Lock, Mail } from 'lucide-react';

interface MockAuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  onQuickDemo: () => void;
}

export const MockAuthModal: React.FC<MockAuthModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  onQuickDemo
}) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [mode, setMode] = useState<'signin' | 'signup'>('signin');

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSuccess();
  };

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.65)',
        backdropFilter: 'blur(6px)',
        zIndex: 1000,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1.5rem',
        animation: 'fadeIn 0.2s ease-out'
      }}
    >
      <div
        style={{
          backgroundColor: 'var(--color-bg)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-sm)',
          maxWidth: '460px',
          width: '100%',
          padding: '2.5rem',
          boxShadow: '0 25px 60px -15px rgba(0, 0, 0, 0.3)',
          position: 'relative'
        }}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '1.25rem',
            right: '1.25rem',
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            color: 'var(--color-muted)',
            padding: '0.25rem'
          }}
          aria-label="Close"
        >
          <X size={20} />
        </button>

        {/* Brand Header */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{ display: 'inline-flex', alignItems: 'baseline', gap: '0.3rem', marginBottom: '0.75rem' }}>
            <span style={{ fontFamily: 'var(--font-serif)', fontSize: '1.75rem', fontWeight: 700, color: 'var(--color-black)' }}>CLAUZ</span>
            <span style={{ fontFamily: 'var(--font-serif)', fontSize: '1.75rem', fontWeight: 700, color: 'var(--color-brick)' }}>X</span>
          </div>

          <h3 style={{ fontSize: '1.5rem', color: 'var(--color-black)', letterSpacing: '-0.01em', marginBottom: '0.35rem' }}>
            {mode === 'signin' ? 'Welcome to Clauz X' : 'Create your Clauz X Account'}
          </h3>
          <p style={{ fontSize: '0.875rem', color: 'var(--color-muted)' }}>
            {mode === 'signin' ? 'Sign in to access your compliance cockpit' : 'Start your MSME compliance journey'}
          </p>
        </div>

        {/* Quick Demo CTA */}
        <div
          onClick={onQuickDemo}
          style={{
            padding: '0.85rem 1rem',
            backgroundColor: 'var(--color-beige-light)',
            border: '1px solid var(--color-beige-dark)',
            borderRadius: '4px',
            cursor: 'pointer',
            marginBottom: '1.5rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            transition: 'all 0.2s ease'
          }}
          className="demo-pill"
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <Sparkles size={16} className="text-brick" />
            <div>
              <div style={{ fontSize: '0.8125rem', fontWeight: 700, color: 'var(--color-black)' }}>Instant Sandbox Access</div>
              <div style={{ fontSize: '0.6875rem', color: 'var(--color-muted)' }}>Skip credentials & test live features</div>
            </div>
          </div>
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-brick)' }}>
            Demo →
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', margin: '1.25rem 0' }}>
          <div style={{ flex: 1, height: '1px', backgroundColor: 'var(--color-border)' }} />
          <span style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--color-muted)' }}>OR SIGN IN</span>
          <div style={{ flex: 1, height: '1px', backgroundColor: 'var(--color-border)' }} />
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 600, color: 'var(--color-black)', marginBottom: '0.35rem' }}>
              Work Email
            </label>
            <div style={{ position: 'relative' }}>
              <input
                type="email"
                required
                placeholder="founder@company.in"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem 1rem 0.75rem 2.25rem',
                  backgroundColor: '#FFFFFF',
                  border: '1px solid var(--color-border)',
                  borderRadius: '4px',
                  fontSize: '0.875rem',
                  outline: 'none',
                  color: 'var(--color-black)'
                }}
              />
              <Mail size={16} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-muted)' }} />
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 600, color: 'var(--color-black)', marginBottom: '0.35rem' }}>
              Password
            </label>
            <div style={{ position: 'relative' }}>
              <input
                type="password"
                required
                placeholder="••••••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem 1rem 0.75rem 2.25rem',
                  backgroundColor: '#FFFFFF',
                  border: '1px solid var(--color-border)',
                  borderRadius: '4px',
                  fontSize: '0.875rem',
                  outline: 'none',
                  color: 'var(--color-black)'
                }}
              />
              <Lock size={16} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-muted)' }} />
            </div>
          </div>

          <button
            type="submit"
            className="btn btn-brick"
            style={{ width: '100%', marginTop: '0.5rem', padding: '0.85rem' }}
          >
            {mode === 'signin' ? 'Sign In' : 'Create Account'} <ArrowRight size={16} />
          </button>
        </form>

        {/* Footer Toggle */}
        <div style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: '0.8125rem', color: 'var(--color-muted)' }}>
          {mode === 'signin' ? (
            <>
              New to Clauz X?{' '}
              <button
                type="button"
                onClick={() => setMode('signup')}
                style={{ background: 'none', border: 'none', color: 'var(--color-brick)', fontWeight: 600, cursor: 'pointer', padding: 0 }}
              >
                Create Account
              </button>
            </>
          ) : (
            <>
              Already have an account?{' '}
              <button
                type="button"
                onClick={() => setMode('signin')}
                style={{ background: 'none', border: 'none', color: 'var(--color-brick)', fontWeight: 600, cursor: 'pointer', padding: 0 }}
              >
                Sign In
              </button>
            </>
          )}
        </div>

      </div>

      <style>{`
        .demo-pill:hover {
          border-color: var(--color-brick) !important;
          transform: translateY(-1px);
        }
      `}</style>
    </div>
  );
};
