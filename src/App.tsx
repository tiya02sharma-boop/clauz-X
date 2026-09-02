import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { HeroSection } from './components/HeroSection';
import { TrustProblemSection } from './components/TrustProblemSection';
import { ProblemSection } from './components/ProblemSection';
import { SolutionSection } from './components/SolutionSection';
import { HowItWorksSection } from './components/HowItWorksSection';
import { FeaturesSection } from './components/FeaturesSection';
import { WhyClauzXSection } from './components/WhyClauzXSection';
import { WhoIsItForSection } from './components/WhoIsItForSection';
import { ProductPreviewSection } from './components/ProductPreviewSection';
import { FinalCTASection } from './components/FinalCTASection';
import { Footer } from './components/Footer';
import { MockAuthModal } from './components/demo/MockAuthModal';
import { MSMEProfileOnboarding } from './components/demo/MSMEProfileOnboarding';
import { ProfileAnalysisLoading } from './components/demo/ProfileAnalysisLoading';
import { DemoDashboard } from './components/demo/DemoDashboard';
import type { BusinessProfile } from './types';
import { defaultProfile } from './data/mockComplianceData';

export const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<'landing' | 'onboarding' | 'analysis' | 'dashboard'>('landing');
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [userProfile, setUserProfile] = useState<BusinessProfile>(() => {
    const saved = localStorage.getItem('clauz_x_profile');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        return {
          ...defaultProfile,
          ...parsed,
          whatsappNumber: parsed.whatsappNumber || defaultProfile.whatsappNumber || '+919896603656'
        };
      } catch {
        return defaultProfile;
      }
    }
    return defaultProfile;
  });

  useEffect(() => {
    localStorage.setItem('clauz_x_profile', JSON.stringify(userProfile));
  }, [userProfile]);

  // Scroll to top on view changes
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [currentView]);

  const handleStartOnboarding = () => {
    setIsAuthModalOpen(false);
    setCurrentView('onboarding');
  };

  const handleQuickDemo = () => {
    setIsAuthModalOpen(false);
    setUserProfile(defaultProfile);
    setCurrentView('analysis');
  };

  const handleProfileSubmit = (newProfile: BusinessProfile) => {
    setUserProfile(newProfile);
    setCurrentView('analysis');
  };

  const handleAnalysisComplete = () => {
    setCurrentView('dashboard');
  };

  const scrollToSection = (id: string) => {
    if (currentView !== 'landing') {
      setCurrentView('landing');
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
    <div className="min-h-screen bg-offwhite text-black" style={{ display: 'flex', flexDirection: 'column' }}>
      
      {/* Global Sticky Navbar */}
      <Navbar
        onOpenAuth={() => setIsAuthModalOpen(true)}
        onGetStarted={() => setIsAuthModalOpen(true)}
        activeView={currentView === 'landing' ? 'landing' : 'demo'}
        onNavigateLanding={() => setCurrentView('landing')}
      />

      {/* Main View Router */}
      <main style={{ flex: 1 }}>
        {currentView === 'landing' && (
          <>
            {/* Section 01: Hero */}
            <HeroSection
              onGetStarted={() => setIsAuthModalOpen(true)}
              onExplore={() => scrollToSection('trust-problem')}
            />

            {/* Section 02: Trust / Landscape */}
            <div id="trust-problem">
              <TrustProblemSection />
            </div>

            {/* Section 03: The Problem (Warm Beige) */}
            <ProblemSection />

            {/* Section 04: Solution (Meet Clauz X Visual Flow) */}
            <SolutionSection />

            {/* Section 05: How It Works */}
            <HowItWorksSection />

            {/* Section 06: Features (6 Dedicated Showcases) */}
            <FeaturesSection />

            {/* Section 07: Why Clauz X (Full-width Deep Brick Red) */}
            <WhyClauzXSection />

            {/* Section 08: Who Is It For? */}
            <WhoIsItForSection />

            {/* Section 09: Product Preview */}
            <ProductPreviewSection
              onGetStarted={() => setIsAuthModalOpen(true)}
            />

            {/* Section 10: Final CTA */}
            <FinalCTASection
              onGetStarted={() => setIsAuthModalOpen(true)}
            />
          </>
        )}

        {/* Interactive Demo Flow Screens */}
        {currentView === 'onboarding' && (
          <MSMEProfileOnboarding
            initialProfile={userProfile}
            onSubmit={handleProfileSubmit}
            onCancel={() => setCurrentView('landing')}
          />
        )}

        {currentView === 'analysis' && (
          <ProfileAnalysisLoading
            profile={userProfile}
            onComplete={handleAnalysisComplete}
          />
        )}

        {currentView === 'dashboard' && (
          <DemoDashboard
            profile={userProfile}
            onEditProfile={() => setCurrentView('onboarding')}
            onBackToLanding={() => setCurrentView('landing')}
          />
        )}
      </main>

      {/* Global Footer (shown on landing page & onboarding) */}
      {currentView === 'landing' && (
        <Footer
          onNavigateSection={scrollToSection}
          onGetStarted={() => setIsAuthModalOpen(true)}
        />
      )}

      {/* Mock Authentication Modal */}
      <MockAuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        onSuccess={handleStartOnboarding}
        onQuickDemo={handleQuickDemo}
      />

    </div>
  );
};

export default App;
