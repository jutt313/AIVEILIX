import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence, useScroll, useTransform } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import NeuralGlow from '../components/NeuralGlow';
import DashboardPreview from '../components/DashboardPreview';
import ProblemSection from '../components/ProblemSection';
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

      {/* Solution Section */}
      <section className="solution-section">
        <div className="section-inner">
          <div className="section-header">
            <span className="section-eyebrow">SOLUTION</span>
            <h2>AIveilix is the <span>Unified Knowledge Layer</span></h2>
            <p>One vault, one API, one source of truth for every AI tool you use.</p>
          </div>
          <div className="solution-grid">
            <div className="solution-card">
              <h3>Active Storage</h3>
              <p>Files are processed, indexed, and always ready for AI retrieval.</p>
            </div>
            <div className="solution-card">
              <h3>Universal Access</h3>
              <p>Connect via MCP and instantly access your docs in Claude, Cursor, ChatGPT, and more.</p>
            </div>
            <div className="solution-card">
              <h3>Persistent Memory</h3>
              <p>Your context stays alive across sessions and tools with citation‑backed answers.</p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="how-section">
        <div className="section-inner">
          <div className="section-header">
            <span className="section-eyebrow">HOW IT WORKS</span>
            <h2>Three steps to <span>AI‑ready</span> knowledge</h2>
            <p>Upload once, generate a key, and connect everywhere.</p>
          </div>
          <div className="how-steps">
            <div className="how-step">
              <div className="step-index">01</div>
              <h3>Upload</h3>
              <p>Drag files or folders into AIveilix.</p>
            </div>
            <div className="how-step">
              <div className="step-index">02</div>
              <h3>Generate Key</h3>
              <p>Create an MCP API key for your tools.</p>
            </div>
            <div className="how-step">
              <div className="step-index">03</div>
              <h3>Connect</h3>
              <p>Paste the key into Claude, Cursor, or any MCP client.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="features-section">
        <div className="section-inner">
          <div className="section-header">
            <span className="section-eyebrow">FEATURES</span>
            <h2>Everything you need to <span>scale intelligence</span></h2>
          </div>
          <div className="features-grid">
            <div className="feature-card">
              <h3>50+ Formats</h3>
              <p>PDF, DOCX, images with OCR, code, CSV, and more.</p>
            </div>
            <div className="feature-card">
              <h3>Vector Search</h3>
              <p>Semantic retrieval with hybrid ranking for accuracy.</p>
            </div>
            <div className="feature-card">
              <h3>Buckets</h3>
              <p>Organize by project, team, or topic with scoped access.</p>
            </div>
            <div className="feature-card">
              <h3>Citations</h3>
              <p>Every answer can show the exact source paragraph.</p>
            </div>
            <div className="feature-card">
              <h3>Fast Indexing</h3>
              <p>Most files are ready to query in seconds.</p>
            </div>
            <div className="feature-card">
              <h3>Cost Savings</h3>
              <p>Process once, reuse everywhere to reduce tokens.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Integrations */}
      <section className="integrations-section">
        <div className="section-inner">
          <div className="section-header">
            <span className="section-eyebrow">INTEGRATIONS</span>
            <h2>MCP connects to <span>everything</span></h2>
          </div>
          <div className="integrations-grid">
            <div className="integration-pill">Claude Desktop</div>
            <div className="integration-pill">Cursor</div>
            <div className="integration-pill">ChatGPT (coming soon)</div>
            <div className="integration-pill">Custom MCP Apps</div>
            <div className="integration-pill">REST API</div>
            <div className="integration-pill">Any MCP Client</div>
          </div>
        </div>
      </section>

      {/* Security */}
      <section className="security-section">
        <div className="section-inner">
          <div className="section-header">
            <span className="section-eyebrow">SECURITY</span>
            <h2>Private by design</h2>
          </div>
          <div className="security-grid">
            <div className="security-card">
              <h3>TLS 1.3 In‑Transit</h3>
              <p>Bank‑grade encryption for every request.</p>
            </div>
            <div className="security-card">
              <h3>AES‑256 At‑Rest</h3>
              <p>Your vault is encrypted end‑to‑end.</p>
            </div>
            <div className="security-card">
              <h3>Right to be Forgotten</h3>
              <p>Delete means delete: files, vectors, metadata.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section className="usecases-section">
        <div className="section-inner">
          <div className="section-header">
            <span className="section-eyebrow">USE CASES</span>
            <h2>Built for <span>every workflow</span></h2>
          </div>
          <div className="usecases-grid">
            <div className="usecase-card">
              <h3>Developers</h3>
              <p>Ask your IDE about legacy docs and specs instantly.</p>
            </div>
            <div className="usecase-card">
              <h3>Researchers</h3>
              <p>Summarize consensus across dozens of papers.</p>
            </div>
            <div className="usecase-card">
              <h3>Students</h3>
              <p>Turn your notes into custom quizzes and study guides.</p>
            </div>
            <div className="usecase-card">
              <h3>Teams</h3>
              <p>Share buckets with scoped permissions for collaboration.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="final-cta">
        <div className="section-inner cta-inner">
          <h2>Ready to build your AI memory?</h2>
          <p>Upload once. Connect everywhere. Stay in flow.</p>
          <div className="cta-actions">
            <button onClick={() => navigate('/signup')} className="cta-primary">Get Started Free</button>
            <button onClick={() => navigate('/doc')} className="cta-secondary">Read Docs</button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Landing;
