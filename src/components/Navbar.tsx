import React, { useState, useEffect } from 'react';
import { Menu, X, ArrowRight } from 'lucide-react';

interface NavbarProps {
  onOpenAuth: () => void;
  onGetStarted: () => void;
  activeView: 'landing' | 'demo';
  onNavigateLanding: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  onOpenAuth,
  onGetStarted,
  activeView,
  onNavigateLanding
}) => {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToSection = (id: string) => {
    setMobileMenuOpen(false);
    if (activeView !== 'landing') {
      onNavigateLanding();
      setTimeout(() => {
        const el = document.getElementById(id);
        if (el) el.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    } else {
      const el = document.getElementById(id);
      if (el) el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <header
      style={{
        position: 'sticky',
        top: 0,
        zIndex: 100,
        transition: 'all 0.3s ease',
        backgroundColor: scrolled ? 'rgba(247, 239, 227, 0.94)' : 'transparent',
        backdropFilter: scrolled ? 'blur(12px)' : 'none',
        borderBottom: scrolled ? '1px solid rgba(0, 0, 0, 0.08)' : '1px solid transparent',
      }}
    >
      <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '80px' }}>
        {/* Brand Logo */}
        <button
          onClick={onNavigateLanding}
          style={{
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            textAlign: 'left',
            display: 'flex',
            alignItems: 'baseline',
            gap: '0.4rem',
            padding: 0
          }}
        >
          <span style={{
            fontFamily: 'var(--font-serif)',
            fontSize: '1.75rem',
            fontWeight: 700,
            letterSpacing: '-0.03em',
            color: 'var(--color-black)',
            lineHeight: 1
          }}>
            CLAUZ
          </span>
          <span style={{
            fontFamily: 'var(--font-serif)',
            fontSize: '1.75rem',
            fontWeight: 700,
            color: 'var(--color-brick)',
            lineHeight: 1
          }}>
            X
          </span>
        </button>

        {/* Center Nav Links - Desktop */}
        <nav style={{ display: 'none', alignItems: 'center', gap: '2.5rem' }} className="desktop-nav">
          <button
            onClick={() => scrollToSection('product-preview')}
            style={navLinkStyle}
          >
            Product
          </button>
          <button
            onClick={() => scrollToSection('features')}
            style={navLinkStyle}
          >
            Features
          </button>
          <button
            onClick={() => scrollToSection('how-it-works')}
            style={navLinkStyle}
          >
            How It Works
          </button>
          <button
            onClick={() => scrollToSection('why-clauz-x')}
            style={navLinkStyle}
          >
            Why Clauz X
          </button>
        </nav>

        {/* Right CTA / Auth */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
          {activeView === 'demo' ? (
            <button
              onClick={onNavigateLanding}
              className="btn btn-secondary"
              style={{ fontSize: '0.875rem', padding: '0.6rem 1.25rem' }}
            >
              ← Back to Overview
            </button>
          ) : (
            <>
              <button
                onClick={onOpenAuth}
                style={{
                  background: 'none',
                  border: 'none',
                  fontFamily: 'var(--font-sans)',
                  fontSize: '0.9375rem',
                  fontWeight: 600,
                  color: 'var(--color-black)',
                  cursor: 'pointer',
                  padding: '0.5rem 0.75rem'
                }}
              >
                Sign In
              </button>
              <button
                onClick={onGetStarted}
                className="btn btn-brick"
                style={{ fontSize: '0.9375rem', padding: '0.7rem 1.5rem' }}
              >
                Get Started <ArrowRight size={16} />
              </button>
            </>
          )}

          {/* Mobile Menu Toggle */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="mobile-menu-btn"
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              color: 'var(--color-black)',
              padding: '0.5rem',
              display: 'none'
            }}
            aria-label="Toggle Navigation Menu"
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div
          style={{
            backgroundColor: 'var(--color-bg)',
            borderBottom: '1px solid var(--color-border)',
            padding: '1.5rem 2rem 2rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '1.25rem',
            animation: 'fadeIn 0.2s ease-out'
          }}
        >
          <button onClick={() => scrollToSection('product-preview')} style={mobileNavLinkStyle}>Product</button>
          <button onClick={() => scrollToSection('features')} style={mobileNavLinkStyle}>Features</button>
          <button onClick={() => scrollToSection('how-it-works')} style={mobileNavLinkStyle}>How It Works</button>
          <button onClick={() => scrollToSection('why-clauz-x')} style={mobileNavLinkStyle}>Why Clauz X</button>
          <div style={{ height: '1px', backgroundColor: 'var(--color-border)', margin: '0.5rem 0' }} />
          <button onClick={() => { setMobileMenuOpen(false); onOpenAuth(); }} style={mobileNavLinkStyle}>Sign In</button>
          <button onClick={() => { setMobileMenuOpen(false); onGetStarted(); }} className="btn btn-brick" style={{ width: '100%' }}>
            Get Started <ArrowRight size={16} />
          </button>
        </div>
      )}

      <style>{`
        @media (min-width: 860px) {
          .desktop-nav {
            display: flex !important;
          }
          .mobile-menu-btn {
            display: none !important;
          }
        }
        @media (max-width: 859px) {
          .mobile-menu-btn {
            display: block !important;
          }
        }
      `}</style>
    </header>
  );
};

const navLinkStyle: React.CSSProperties = {
  background: 'none',
  border: 'none',
  fontFamily: 'var(--font-sans)',
  fontSize: '0.9375rem',
  fontWeight: 500,
  color: 'var(--color-black)',
  cursor: 'pointer',
  padding: '0.4rem 0',
  transition: 'color var(--transition-fast)',
  position: 'relative'
};

const mobileNavLinkStyle: React.CSSProperties = {
  background: 'none',
  border: 'none',
  fontFamily: 'var(--font-sans)',
  fontSize: '1.125rem',
  fontWeight: 600,
  color: 'var(--color-black)',
  textAlign: 'left',
  cursor: 'pointer',
  padding: '0.5rem 0'
};
