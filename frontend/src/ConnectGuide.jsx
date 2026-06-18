import { useEffect } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { BlurFade } from './landing-components';
import { TOOLS, ClaudeLogo, ChatGPTLogo, ClaudeDesktopLogo, GenericMcpLogo } from './brand-logos';

function Arrow({ className = 'h-4 w-4' }) {
  return <svg viewBox="0 0 24 24" fill="none" strokeWidth="1.8" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" className={className}><path d="M5 12h14M13 6l6 6-6 6"/></svg>;
}

const palettes = {
  dark:  { page: 'bg-[#020617] text-slate-200', title: 'text-white', text: 'text-slate-300', muted: 'text-slate-400', accent: 'text-blue-400', card: 'border border-white/10 bg-white/[0.03]', soft: 'bg-white/[0.025] border border-white/10', divider: 'border-white/10', code: 'bg-slate-900/80 border-white/10 text-slate-200', secondary: 'border border-white/20 bg-white/5 text-white hover:bg-white/10' },
  light: { page: 'bg-white text-slate-800',     title: 'text-slate-900', text: 'text-slate-700', muted: 'text-slate-500', accent: 'text-blue-600', card: 'border border-slate-200 bg-white',         soft: 'bg-slate-50 border border-slate-200',     divider: 'border-slate-200', code: 'bg-slate-50 border-slate-200 text-slate-800', secondary: 'border border-slate-300 bg-white text-slate-900 hover:bg-slate-50' },
};

const GUIDES = {
  'claude': {
    tool: 'Claude (web)',
    Logo: ClaudeLogo,
    intro: 'Add your AIveilix bucket to Claude.ai using its Custom Connectors feature. Once connected, Claude reads your docs whenever you ask a question — no re-uploading.',
    prereq: 'A Claude Pro, Team, or Enterprise account (Custom Connectors are a paid-tier feature).',
    steps: [
      { t: 'Get your MCP link from AIveilix',           b: 'Open the bucket you want to connect → click the "MCP" button in the top bar → copy the URL. It looks like: ', code: 'https://mcp.aiveilix.com/bucket/mcp_xxxxx' },
      { t: 'Open Claude Settings',                       b: 'Go to claude.ai → click your profile in the bottom-left → Settings.' },
      { t: 'Navigate to Connectors',                     b: 'Find Connectors in the left sidebar (or under "Integrations" depending on plan).' },
      { t: 'Add a custom connector',                     b: 'Click "Add custom connector" → paste your AIveilix MCP URL → give it a name like "My research bucket".' },
      { t: 'Authorize it',                               b: 'Claude will verify the connection. You\'ll see your bucket\'s tools (search, query, list_files, etc.) appear.' },
      { t: 'Ask away',                                   b: 'Open any chat. Claude can now pull from your bucket whenever the question calls for it. Try: "What does the Q3 strategy doc say about EMEA?"' },
    ],
    tip: 'Treat the MCP URL like a password — anyone with it can read that bucket. Revoke + regenerate it any time from the bucket\'s MCP panel.',
  },
  'claude-desktop': {
    tool: 'Claude Desktop',
    Logo: ClaudeDesktopLogo,
    intro: 'Claude Desktop has first-class MCP support built into its config file. This is the most reliable way to use AIveilix with Claude.',
    prereq: 'Claude Desktop installed on macOS or Windows. Any Claude account (free works).',
    steps: [
      { t: 'Get your MCP link from AIveilix',     b: 'Open your bucket → click "MCP" → copy the URL.' },
      { t: 'Open Claude Desktop settings',        b: 'Click the Claude menu → Settings → Developer tab → "Edit Config".' },
      { t: 'Add the AIveilix server',             b: 'Paste this into the `mcpServers` block (replace YOUR_TOKEN with your actual token):',
        code: `{
  "mcpServers": {
    "aiveilix": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.aiveilix.com/bucket/YOUR_TOKEN"]
    }
  }
}` },
      { t: 'Save + restart Claude Desktop',       b: 'Quit Claude Desktop completely (Cmd+Q on Mac) and reopen it. You\'ll see a small 🔌 icon in the chat — that\'s your AIveilix bucket.' },
      { t: 'Test it',                             b: 'Start a new chat. Ask: "What files are in my AIveilix bucket?" Claude will list them. Then ask anything about their contents.' },
    ],
    tip: 'If the 🔌 icon doesn\'t show, check Settings → Developer → MCP logs. Most issues are typos in the config file (missing comma, wrong bracket).',
  },
  'chatgpt': {
    tool: 'ChatGPT',
    Logo: ChatGPTLogo,
    intro: 'ChatGPT supports MCP via the Custom GPTs / Connectors interface (rolling out across plans). Add your AIveilix bucket as a knowledge connector.',
    prereq: 'A ChatGPT Plus, Team, or Enterprise account.',
    steps: [
      { t: 'Get your MCP link from AIveilix',           b: 'Open your bucket → click "MCP" → copy the URL.' },
      { t: 'Open ChatGPT',                              b: 'Go to chatgpt.com → click your profile (top-right) → Settings.' },
      { t: 'Go to Connectors',                          b: 'Find "Connectors" or "Connected apps" in the Settings menu.' },
      { t: 'Add a custom MCP server',                   b: 'Click "Add a connector" → choose "Custom MCP server" → paste your AIveilix URL → name it.' },
      { t: 'Enable for chats',                          b: 'Toggle the connector "on" for the chats where you want it active. You can mention @aiveilix in a message to scope a question to your bucket.' },
      { t: 'Test it',                                   b: 'Ask: "Using my AIveilix bucket, summarize the main risks in Q3-strategy.pdf."' },
    ],
    tip: 'ChatGPT\'s MCP support is rolling out gradually. If you don\'t see "Connectors", try Claude Desktop instead — same data, same link.',
  },
  'mcp': {
    tool: 'Any MCP-compatible AI',
    Logo: GenericMcpLogo,
    intro: 'MCP is an open standard. Any AI client that speaks MCP can connect to your AIveilix bucket — Continue, Cline, Goose, Zed, custom builds, internal tools, you name it.',
    prereq: 'A client that supports MCP (most major AI editors and agents now do).',
    steps: [
      { t: 'Get your MCP link from AIveilix',           b: 'Open your bucket → "MCP" → copy the URL. This URL implements the MCP specification.' },
      { t: 'Find your client\'s MCP config',            b: 'Every MCP client has a place to register servers — usually a JSON config file or a UI form. Common locations: VS Code/Cursor settings → MCP; Continue → Models config; Cline → MCP servers.' },
      { t: 'Add AIveilix as a remote server',           b: 'Most clients accept a URL directly. If yours needs a stdio-style command, use:', code: 'npx -y mcp-remote https://mcp.aiveilix.com/bucket/YOUR_TOKEN' },
      { t: 'Restart your client',                       b: 'Reload the client or restart it so it picks up the new server.' },
      { t: 'Use the tools',                             b: 'AIveilix exposes: search, query, list_files, get_file, get_file_summary, get_bucket_info, list_categories, list_chunks, get_chunk, get_file_layout. Most clients show these in their tool inspector.' },
    ],
    tip: 'Building your own integration? AIveilix follows the MCP JSON-RPC spec — POST your initialize/tools/list/tools/call to the bucket URL.',
  },
};

export default function ConnectGuide({ theme, onToggleTheme }) {
  const { tool } = useParams();
  const navigate = useNavigate();
  const p = palettes[theme] || palettes.dark;
  const guide = GUIDES[tool];

  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'dark') root.classList.add('dark'); else root.classList.remove('dark');
  }, [theme]);

  if (!guide) {
    return (
      <main className={`${p.page} min-h-screen`}>
        <div className="mx-auto max-w-3xl px-6 py-32 text-center">
          <h1 className={`text-3xl font-semibold ${p.title}`}>Unknown tool</h1>
          <p className={`mt-4 ${p.text}`}>We don't have a connect guide for "{tool}".</p>
          <Link to="/" className={`mt-6 inline-block rounded-full px-5 py-2 ${p.secondary}`}>Back home</Link>
        </div>
      </main>
    );
  }

  const Logo = guide.Logo;

  return (
    <main className={`${p.page} min-h-screen`}>
      {/* Top nav */}
      <header className="sticky top-0 z-40 bg-transparent backdrop-blur-md">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <Link to="/" className="flex items-center gap-2.5">
            <img src="/logo-tight.png" alt="AIveilix" className="h-8 w-8 rounded-md" />
            <span className={`text-base font-semibold tracking-tight ${p.title}`}>AIveilix</span>
            <span className={`text-xs ${p.muted}`}>· Connect</span>
          </Link>
          <div className="flex items-center gap-2">
            <button onClick={onToggleTheme} className={`hidden sm:inline-flex rounded-full px-3 py-1.5 text-xs font-medium transition ${p.secondary}`}>
              {theme === 'dark' ? '☀' : '☾'}
            </button>
            <Link to="/" className={`rounded-full px-3 py-1.5 text-sm font-medium transition ${p.secondary}`}>← Back home</Link>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-3xl px-6 py-16 sm:py-24">
        <BlurFade>
          <div className="flex items-center gap-4">
            <Logo className="h-14 w-14" />
            <div>
              <p className={`text-xs font-semibold uppercase tracking-[0.18em] ${p.accent}`}>Setup guide</p>
              <h1 className={`text-3xl font-semibold tracking-tight sm:text-4xl ${p.title}`}>
                Connect AIveilix to {guide.tool}
              </h1>
            </div>
          </div>
        </BlurFade>

        <BlurFade delay={0.05}>
          <p className={`mt-6 text-base leading-relaxed ${p.text}`}>{guide.intro}</p>
        </BlurFade>

        <BlurFade delay={0.08}>
          <div className={`mt-6 rounded-xl px-4 py-3 text-sm ${p.soft}`}>
            <strong className={p.title}>Prerequisite:</strong> <span className={p.text}>{guide.prereq}</span>
          </div>
        </BlurFade>

        <ol className="mt-10 space-y-5">
          {guide.steps.map((s, i) => (
            <BlurFade key={i} delay={i * 0.05}>
              <li className={`flex gap-4 rounded-2xl p-5 ${p.card}`}>
                <span className="inline-flex h-9 w-9 flex-none items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-sm font-semibold text-white">{i + 1}</span>
                <div className="flex-1">
                  <p className={`text-base font-semibold ${p.title}`}>{s.t}</p>
                  <p className={`mt-1.5 text-sm leading-relaxed ${p.text}`}>{s.b}</p>
                  {s.code && (
                    <pre className={`mt-3 overflow-x-auto rounded-lg border px-3 py-2.5 text-[12.5px] leading-relaxed ${p.code}`}>
                      <code className="font-mono">{s.code}</code>
                    </pre>
                  )}
                </div>
              </li>
            </BlurFade>
          ))}
        </ol>

        <BlurFade delay={0.4}>
          <div className={`mt-10 rounded-2xl border-l-4 border-blue-500 p-5 ${p.soft}`}>
            <p className={`text-xs font-semibold uppercase tracking-wider ${p.accent}`}>Pro tip</p>
            <p className={`mt-1.5 text-sm leading-relaxed ${p.text}`}>{guide.tip}</p>
          </div>
        </BlurFade>

        <BlurFade delay={0.5}>
          <div className={`mt-10 flex flex-wrap items-center justify-between gap-4 rounded-2xl p-6 ${p.card}`}>
            <div>
              <p className={`text-base font-semibold ${p.title}`}>Don't have an AIveilix account?</p>
              <p className={`mt-1 text-sm ${p.text}`}>Free forever for your first bucket.</p>
            </div>
            <button onClick={() => navigate('/signup')} className="inline-flex items-center gap-2 rounded-full bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-500">
              Start free <Arrow />
            </button>
          </div>
        </BlurFade>

        <BlurFade delay={0.55}>
          <div className="mt-10 flex items-center justify-between text-sm">
            <Link to="/" className={`${p.text} transition hover:${p.title}`}>← Back to home</Link>
            <Link to="/docs" className={`${p.text} transition hover:${p.title}`}>More docs →</Link>
          </div>
        </BlurFade>
      </div>
    </main>
  );
}
