import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence, useScroll, useTransform } from 'framer-motion';
import {
  FileText, Search, FolderOpen, Link2, Zap, DollarSign,
  Database, Globe, Brain, Lock, Shield, Trash2,
  Code2, BookOpen, GraduationCap, Users, Quote, Mail
} from 'lucide-react';
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
            <img src="/logo-with-name.png" alt="AIveilix" className="nav-logo-img" />
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
              { title: 'Active Storage', desc: 'Files are processed, indexed, and always ready for AI retrieval.', icon: Database },
              { title: 'Universal Access', desc: 'Connect via MCP and instantly access your docs in Claude, Cursor, ChatGPT, and more.', icon: Globe },
              { title: 'Persistent Memory', desc: 'Your context stays alive across sessions and tools with citation‑backed answers.', icon: Brain },
            ].map((card, i) => (
              <ScrollReveal key={card.title} delay={i * 0.12} direction="up">
                <SpotlightCard>
                  <card.icon size={28} color="#2DFFB7" style={{ marginBottom: 14, opacity: 0.9 }} />
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
              { title: '50+ Formats', desc: 'PDF, DOCX, images with OCR, code, CSV, and more.', icon: FileText },
              { title: 'Vector Search', desc: 'Semantic retrieval with hybrid ranking for accuracy.', icon: Search },
              { title: 'Buckets', desc: 'Organize by project, team, or topic with scoped access.', icon: FolderOpen },
              { title: 'Citations', desc: 'Every answer can show the exact source paragraph.', icon: Link2 },
              { title: 'Fast Indexing', desc: 'Most files are ready to query in seconds.', icon: Zap },
              { title: 'Cost Savings', desc: 'Process once, reuse everywhere to reduce tokens.', icon: DollarSign },
            ].map((card, i) => (
              <ScrollReveal key={card.title} delay={i * 0.08} direction="up">
                <SpotlightCard>
                  <card.icon size={26} color="#2DFFB7" style={{ marginBottom: 12, opacity: 0.85 }} />
                  <h3>{card.title}</h3>
                  <p>{card.desc}</p>
                </SpotlightCard>
              </ScrollReveal>
            ))}
          </SpotlightGrid>
        </div>
      </section>

      {/* Works With */}
      <section className="works-with-section">
        <div className="section-inner">
          <ScrollReveal>
            <p className="works-with-label">WORKS WITH YOUR FAVORITE AI TOOLS</p>
          </ScrollReveal>
          <ScrollReveal delay={0.1}>
            <div className="works-with-grid">
              {[
                { name: 'Claude Desktop', abbr: 'C', color: '#FF9500', bg: 'rgba(255,149,0,0.12)' },
                { name: 'Cursor IDE', abbr: '↗', color: '#58A6FF', bg: 'rgba(88,166,255,0.12)' },
                { name: 'ChatGPT', abbr: 'G', color: '#19C37D', bg: 'rgba(25,195,125,0.12)' },
                { name: 'Windsurf', abbr: 'W', color: '#A78BFA', bg: 'rgba(167,139,250,0.12)' },
                { name: 'VS Code', abbr: '◈', color: '#0098FF', bg: 'rgba(0,152,255,0.12)' },
                { name: 'Any MCP Client', abbr: '⚡', color: '#2DFFB7', bg: 'rgba(45,255,183,0.12)' },
              ].map((tool) => (
                <div key={tool.name} className="works-with-item">
                  <div className="works-with-icon" style={{ background: tool.bg, border: `1px solid ${tool.color}55` }}>
                    <span style={{ color: tool.color, fontWeight: 800, fontSize: 20, lineHeight: 1 }}>{tool.abbr}</span>
                  </div>
                  <span className="works-with-name">{tool.name}</span>
                </div>
              ))}
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
              { title: 'TLS 1.3 In‑Transit', desc: 'Bank‑grade encryption for every request.', icon: Lock },
              { title: 'AES‑256 At‑Rest', desc: 'Your vault is encrypted end‑to‑end.', icon: Shield },
              { title: 'Right to be Forgotten', desc: 'Delete means delete: files, vectors, metadata.', icon: Trash2 },
            ].map((card, i) => (
              <ScrollReveal key={card.title} delay={i * 0.12} direction="up">
                <SpotlightCard>
                  <card.icon size={28} color="#2DFFB7" style={{ marginBottom: 14, opacity: 0.9 }} />
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
              { title: 'Developers', desc: 'Ask your IDE about legacy docs and specs instantly.', icon: Code2 },
              { title: 'Researchers', desc: 'Summarize consensus across dozens of papers.', icon: BookOpen },
              { title: 'Students', desc: 'Turn your notes into custom quizzes and study guides.', icon: GraduationCap },
              { title: 'Teams', desc: 'Share buckets with scoped permissions for collaboration.', icon: Users },
            ].map((card, i) => (
              <ScrollReveal key={card.title} delay={i * 0.1} direction={i % 2 === 0 ? 'left' : 'right'}>
                <SpotlightCard>
                  <card.icon size={26} color="#2DFFB7" style={{ marginBottom: 12, opacity: 0.85 }} />
                  <h3>{card.title}</h3>
                  <p>{card.desc}</p>
                </SpotlightCard>
              </ScrollReveal>
            ))}
          </SpotlightGrid>
        </div>
      </section>

      {/* Testimonials */}
      <section className="testimonials-section">
        <div className="section-inner">
          <div className="section-header">
            <ScrollReveal>
              <span className="section-eyebrow">TESTIMONIALS</span>
            </ScrollReveal>
            <TextReveal
              text="What early users are saying"
              className="section-header-h2"
              staggerDelay={0.04}
            />
          </div>
          <div className="testimonials-grid">
            {[
              {
                quote: "AIveilix completely changed how I work with Cursor. My entire codebase docs are always available — no more switching tabs to re-upload specs.",
                name: "Alex K.",
                role: "Full-Stack Developer",
              },
              {
                quote: "I process 50+ research papers a week. The semantic search finds exactly the paragraph I need in milliseconds. It's like having a second brain.",
                name: "Dr. Jordan M.",
                role: "ML Researcher",
              },
              {
                quote: "We shared one bucket across our whole team. Everyone has the same context now. Onboarding new members went from hours to minutes.",
                name: "Sam L.",
                role: "Product Lead",
              },
            ].map((t, i) => (
              <ScrollReveal key={i} delay={i * 0.12} direction="up">
                <div className="testimonial-card">
                  <Quote size={22} color="#2DFFB7" style={{ marginBottom: 16, opacity: 0.6 }} />
                  <p className="testimonial-quote">"{t.quote}"</p>
                  <div className="testimonial-author">
                    <div className="testimonial-avatar">{t.name.charAt(0)}</div>
                    <div>
                      <div className="testimonial-name">{t.name}</div>
                      <div className="testimonial-role">{t.role}</div>
                    </div>
                  </div>
                </div>
              </ScrollReveal>
            ))}
          </div>
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

      {/* Footer */}
      <footer className="site-footer">
        <div className="footer-inner">
          <div className="footer-brand">
            <img src="/logo-with-name.png" alt="AIveilix" className="footer-logo" />
            <p className="footer-tagline">Your AI-powered knowledge vault. Upload once, access everywhere via MCP protocol.</p>
            <a href="mailto:hello@aiveilix.com" className="footer-email">
              <Mail size={14} style={{ display: 'inline', marginRight: 6, verticalAlign: 'middle' }} />
              hello@aiveilix.com
            </a>
          </div>
          <div className="footer-links">
            <div className="footer-col">
              <h4>Product</h4>
              <Link to="/doc">Documentation</Link>
              <a href="#pricing">Pricing</a>
              <Link to="/signup">Get Started Free</Link>
              <Link to="/login">Login</Link>
            </div>
            <div className="footer-col">
              <h4>Legal</h4>
              <Link to="/privacy">Privacy Policy</Link>
              <Link to="/terms">Terms of Service</Link>
              <Link to="/tokusho">Tokusho</Link>
            </div>
          </div>
        </div>
        <div className="footer-bottom">
          <span>© {new Date().getFullYear()} AIveilix · All rights reserved.</span>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
