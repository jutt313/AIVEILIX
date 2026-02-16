import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence, useScroll, useTransform } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import NeuralGlow from '../components/NeuralGlow';
import DashboardPreview from '../components/DashboardPreview';
import ProblemSection from '../components/ProblemSection';
import ScrollReveal from '../components/landing/ScrollReveal';
import TextReveal from '../components/landing/TextReveal';
import ScrollMarquee from '../components/landing/ScrollMarquee';
import { SpotlightGrid, SpotlightCard } from '../components/landing/SpotlightGrid';
import NumberCounter from '../components/landing/NumberCounter';
import '../styles/landing.css';

const headlines = [
  {
    title: "Your Universal Knowledge Hub",
    subtitle: "Upload your documents once to AIveilix, then access them instantly in Claude, ChatGPT, Cursor, and any MCP-compatible AI tool. No more re-uploading. No more scattered files."
  },
  {
    title: "Stop Re-Uploading. Start Building.",
    subtitle: "Connect all your documents to every AI tool through MCP protocol. One central knowledge base that works everywhere—from coding in Cursor to chatting in Claude."
  },
  {
    title: "One Source of Truth for All Your AI Tools",
    subtitle: "Upload PDFs, docs, images, and code to AIveilix. Connect via MCP and instantly access your knowledge in Claude for research, Cursor for coding, ChatGPT for brainstorming—all synced automatically."
  },
  {
    title: "MCP-Powered Knowledge at Your Fingertips",
    subtitle: "Built on the Model Context Protocol, AIveilix connects your entire knowledge base to any AI platform. Upload once, query anywhere, work smarter across all your favorite tools."
  },
  {
    title: "The Bridge Between Your Docs and AI",
    subtitle: "AIveilix turns your documents into a living knowledge base accessible from Claude, Cursor, ChatGPT, and beyond. Powered by MCP for seamless, instant connectivity everywhere you work."
  }
];

const Landing = () => {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [currentHeadline, setCurrentHeadline] = useState(0);

  const { scrollYProgress } = useScroll();
  const dashboardScale = useTransform(scrollYProgress, [0, 0.3], [0.95, 1]);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentHeadline((prev) => (prev + 1) % headlines.length);
    }, 10000);
    return () => clearInterval(timer);
  }, []);

  const userName = user?.full_name || user?.email?.split('@')[0] || 'User';

  return (
    <div className="landing-container">
      {/* Navigation */}
      <nav className="landing-nav">
        <div className="nav-left">
          <Link to="/">
            <img src="/logo-with-name..png" alt="AIveilix" className="nav-logo-img" />
          </Link>
        </div>

        <div className="nav-right">
          {isAuthenticated ? (
            <div className="nav-user-info">
              <span className="user-name">{userName}</span>
              <Link to="/dashboard" className="nav-btn nav-btn-primary">
                Dashboard
              </Link>
            </div>
          ) : (
            <div className="nav-auth-buttons">
              <Link to="/login" className="nav-btn nav-btn-secondary">
                Login
              </Link>
              <Link to="/signup" className="nav-btn nav-btn-primary">
                Sign In
              </Link>
            </div>
          )}
        </div>
      </nav>

      {/* Hero Content */}
      <section className="hero-section">
        <NeuralGlow />
        <div className="hero-content-wrapper">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentHeadline}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.8, ease: "easeOut" }}
              className="headline-container"
            >
              <h1 className="hero-title">{headlines[currentHeadline].title}</h1>
              <p className="hero-subtitle">{headlines[currentHeadline].subtitle}</p>
            </motion.div>
          </AnimatePresence>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.8 }}
            className="hero-actions"
          >
            <button onClick={() => navigate('/signup')} className="hero-btn hero-btn-primary">
              Get Started
            </button>
            <button onClick={() => navigate('/doc')} className="hero-btn hero-btn-secondary">
              Read Docs
            </button>
          </motion.div>
        </div>

        {/* Dashboard Preview */}
        <div className="dashboard-reveal-outer">
          <motion.div
            style={{ scale: dashboardScale }}
            className="dashboard-reveal-inner"
          >
            <DashboardPreview />
          </motion.div>
        </div>
      </section>

      {/* Problem Section */}
      <ProblemSection />

      {/* Marquee Divider */}
      <section className="marquee-divider">
        <ScrollMarquee baseVelocity={-1.5}>
          {['KNOWLEDGE', 'MCP', 'VECTORS', 'SEMANTIC SEARCH', 'BUCKETS', 'AI MEMORY', 'CITATIONS', 'EMBEDDINGS'].map((word) => (
            <span key={word} className="marquee-text">{word}</span>
          ))}
        </ScrollMarquee>
      </section>

      {/* Solution Section */}
      <section className="solution-section">
        <div className="section-inner">
          <div className="section-header">
            <ScrollReveal>
              <span className="section-eyebrow">SOLUTION</span>
            </ScrollReveal>
            <TextReveal
              text="AIveilix is the Unified Knowledge Layer"
              className="section-header-h2"
              staggerDelay={0.04}
            />
            <ScrollReveal delay={0.2}>
              <p>One vault, one API, one source of truth for every AI tool you use.</p>
            </ScrollReveal>
          </div>
          <SpotlightGrid className="solution-grid">
            {[
              { title: 'Active Storage', desc: 'Files are processed, indexed, and always ready for AI retrieval.' },
              { title: 'Universal Access', desc: 'Connect via MCP and instantly access your docs in Claude, Cursor, ChatGPT, and more.' },
              { title: 'Persistent Memory', desc: 'Your context stays alive across sessions and tools with citation‑backed answers.' },
            ].map((card, i) => (
              <ScrollReveal key={card.title} delay={i * 0.12} direction="up">
                <SpotlightCard>
                  <h3>{card.title}</h3>
                  <p>{card.desc}</p>
                </SpotlightCard>
              </ScrollReveal>
            ))}
          </SpotlightGrid>
        </div>
      </section>

      {/* How It Works */}
      <section className="how-section">
        <div className="section-inner">
          <div className="section-header">
            <ScrollReveal>
              <span className="section-eyebrow">HOW IT WORKS</span>
            </ScrollReveal>
            <TextReveal
              text="Three steps to AI-ready knowledge"
              className="section-header-h2"
              staggerDelay={0.04}
            />
            <ScrollReveal delay={0.2}>
              <p>Upload once, generate a key, and connect everywhere.</p>
            </ScrollReveal>
          </div>
          <div className="timeline-container">
            <div className="timeline-line" />
            {[
              { num: 1, title: 'Upload', desc: 'Drag files or folders into AIveilix. We process PDFs, images, code, docs, and 50+ formats automatically.' },
              { num: 2, title: 'Generate Key', desc: 'Create an MCP API key with scoped permissions for your tools.' },
              { num: 3, title: 'Connect', desc: 'Paste the key into Claude, Cursor, or any MCP client. Your knowledge is instantly available.' },
            ].map((step, i) => (
              <ScrollReveal key={step.num} delay={i * 0.15} direction={i % 2 === 0 ? 'left' : 'right'}>
                <div className="timeline-step">
                  <div className="timeline-dot">
                    <NumberCounter value={step.num} />
                  </div>
                  <div className="timeline-content">
                    <h3>{step.title}</h3>
                    <p>{step.desc}</p>
                  </div>
                </div>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="features-section">
        <div className="section-inner">
          <div className="section-header">
            <ScrollReveal>
              <span className="section-eyebrow">FEATURES</span>
            </ScrollReveal>
            <TextReveal
              text="Everything you need to scale intelligence"
              className="section-header-h2"
              staggerDelay={0.04}
            />
          </div>
          <SpotlightGrid className="features-grid">
            {[
              { title: '50+ Formats', desc: 'PDF, DOCX, images with OCR, code, CSV, and more.' },
              { title: 'Vector Search', desc: 'Semantic retrieval with hybrid ranking for accuracy.' },
              { title: 'Buckets', desc: 'Organize by project, team, or topic with scoped access.' },
              { title: 'Citations', desc: 'Every answer can show the exact source paragraph.' },
              { title: 'Fast Indexing', desc: 'Most files are ready to query in seconds.' },
              { title: 'Cost Savings', desc: 'Process once, reuse everywhere to reduce tokens.' },
            ].map((card, i) => (
              <ScrollReveal key={card.title} delay={i * 0.08} direction="up">
                <SpotlightCard>
                  <h3>{card.title}</h3>
                  <p>{card.desc}</p>
                </SpotlightCard>
              </ScrollReveal>
            ))}
          </SpotlightGrid>
        </div>
      </section>

      {/* Integrations */}
      <section className="integrations-section">
        <div className="section-inner">
          <div className="section-header">
            <ScrollReveal>
              <span className="section-eyebrow">INTEGRATIONS</span>
            </ScrollReveal>
            <TextReveal
              text="MCP connects to everything"
              className="section-header-h2"
              staggerDelay={0.04}
            />
          </div>
          <ScrollReveal>
            <div className="integration-marquee-wrapper">
              <div className="integration-marquee-track">
                {[...Array(2)].map((_, setIdx) => (
                  ['Claude Desktop', 'Cursor', 'ChatGPT (coming soon)', 'Custom MCP Apps', 'REST API', 'Any MCP Client', 'Windsurf', 'VS Code'].map((name) => (
                    <div key={`${setIdx}-${name}`} className="integration-pill">{name}</div>
                  ))
                ))}
              </div>
            </div>
          </ScrollReveal>
        </div>
      </section>

      {/* Security */}
      <section className="security-section">
        <div className="section-inner">
          <div className="section-header">
            <ScrollReveal>
              <span className="section-eyebrow">SECURITY</span>
            </ScrollReveal>
            <TextReveal
              text="Private by design"
              className="section-header-h2"
              staggerDelay={0.05}
            />
          </div>
          <SpotlightGrid className="security-grid">
            {[
              { title: 'TLS 1.3 In‑Transit', desc: 'Bank‑grade encryption for every request.' },
              { title: 'AES‑256 At‑Rest', desc: 'Your vault is encrypted end‑to‑end.' },
              { title: 'Right to be Forgotten', desc: 'Delete means delete: files, vectors, metadata.' },
            ].map((card, i) => (
              <ScrollReveal key={card.title} delay={i * 0.12} direction="up">
                <SpotlightCard>
                  <h3>{card.title}</h3>
                  <p>{card.desc}</p>
                </SpotlightCard>
              </ScrollReveal>
            ))}
          </SpotlightGrid>
        </div>
      </section>

      {/* Use Cases */}
      <section className="usecases-section">
        <div className="section-inner">
          <div className="section-header">
            <ScrollReveal>
              <span className="section-eyebrow">USE CASES</span>
            </ScrollReveal>
            <TextReveal
              text="Built for every workflow"
              className="section-header-h2"
              staggerDelay={0.04}
            />
          </div>
          <SpotlightGrid className="usecases-grid">
            {[
              { title: 'Developers', desc: 'Ask your IDE about legacy docs and specs instantly.' },
              { title: 'Researchers', desc: 'Summarize consensus across dozens of papers.' },
              { title: 'Students', desc: 'Turn your notes into custom quizzes and study guides.' },
              { title: 'Teams', desc: 'Share buckets with scoped permissions for collaboration.' },
            ].map((card, i) => (
              <ScrollReveal key={card.title} delay={i * 0.1} direction={i % 2 === 0 ? 'left' : 'right'}>
                <SpotlightCard>
                  <h3>{card.title}</h3>
                  <p>{card.desc}</p>
                </SpotlightCard>
              </ScrollReveal>
            ))}
          </SpotlightGrid>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="pricing-section" id="pricing">
        <div className="section-inner">
          <div className="section-header">
            <ScrollReveal>
              <span className="section-eyebrow">PRICING</span>
            </ScrollReveal>
            <TextReveal
              text="Simple, transparent pricing"
              className="section-header-h2"
              staggerDelay={0.04}
            />
            <ScrollReveal delay={0.2}>
              <p>Start free for 14 days. Subscribe within 24 hours for 2x limits on your first month.</p>
            </ScrollReveal>
          </div>

          <ScrollReveal delay={0.1}>
            <div className="pricing-grid">
              {[
                {
                  name: 'Free Trial',
                  price: '$0',
                  period: '14 days',
                  features: ['1GB Storage', '50MB max file', '5 Buckets', '0 Team members', '50 Chat/day', '50 MCP queries/day', '50 API calls/day'],
                  cta: 'Get Started',
                  highlight: false,
                },
                {
                  name: 'Starter',
                  price: '$12.78',
                  period: '/month',
                  features: ['5GB Storage', '100MB max file', '25 Buckets', '3 Team members', '200 Chat/day', '300 MCP queries/day', '300 API calls/day'],
                  cta: 'Start Starter',
                  highlight: false,
                },
                {
                  name: 'Pro',
                  price: '$24.13',
                  period: '/month',
                  features: ['12GB Storage', '250MB max file', '100 Buckets', '10 Team members', '1,000 Chat/day', '1,500 MCP queries/day', '1,500 API calls/day'],
                  cta: 'Go Pro',
                  highlight: true,
                  badge: 'Most Popular',
                },
                {
                  name: 'Premium',
                  price: '$49.99',
                  period: '/month',
                  features: ['25GB Storage', '500MB max file', 'Unlimited Buckets', '30 Team members', '5,000 Chat/day', '5,000 MCP queries/day', '5,000 API calls/day'],
                  cta: 'Go Premium',
                  highlight: false,
                },
              ].map((plan) => (
                <div key={plan.name} className={`pricing-card ${plan.highlight ? 'pricing-card-highlight' : ''}`}>
                  {plan.badge && <span className="pricing-badge">{plan.badge}</span>}
                  <h3 className="pricing-plan-name">{plan.name}</h3>
                  <div className="pricing-price">
                    <span className="pricing-amount">{plan.price}</span>
                    <span className="pricing-period">{plan.period}</span>
                  </div>
                  <ul className="pricing-features">
                    {plan.features.map((f) => (
                      <li key={f}>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 13l4 4L19 7"/></svg>
                        {f}
                      </li>
                    ))}
                  </ul>
                  <button onClick={() => navigate('/signup')} className={`pricing-cta ${plan.highlight ? 'pricing-cta-primary' : ''}`}>
                    {plan.cta}
                  </button>
                </div>
              ))}
            </div>
          </ScrollReveal>

          <ScrollReveal delay={0.3}>
            <p className="pricing-bonus-note">
              ⚡ Subscribe within 24 hours of signing up and get <strong>2x all limits</strong> for your first month!
            </p>
          </ScrollReveal>
        </div>
      </section>

      {/* Final CTA */}
      <section className="final-cta final-cta-animated">
        <div className="section-inner cta-inner" style={{ position: 'relative', zIndex: 1 }}>
          <TextReveal
            text="Ready to build your AI memory?"
            as="h2"
            letterAnime
            staggerDelay={0.03}
            className="cta-headline"
          />
          <ScrollReveal delay={0.3}>
            <p>Upload once. Connect everywhere. Stay in flow.</p>
          </ScrollReveal>
          <ScrollReveal delay={0.5}>
            <div className="cta-actions">
              <button onClick={() => navigate('/signup')} className="cta-primary">Get Started Free</button>
              <button onClick={() => navigate('/doc')} className="cta-secondary">Read Docs</button>
            </div>
          </ScrollReveal>
        </div>
      </section>
    </div>
  );
};

export default Landing;
