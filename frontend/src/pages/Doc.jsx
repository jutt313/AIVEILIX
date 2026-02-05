import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { Sun, Moon, Search, Book, Shield, Server, Box, MessageSquare, Terminal, Zap, Key, Link as LinkIcon, Lock, Cpu, Users, Globe, Copy, Check } from 'lucide-react';
import introductionMarkdown from '../../../Introduction.md?raw';
import userGuidesMarkdown from '../../../UserGuides.md?raw';
import integrationsMarkdown from '../../../Integrations_MCP.md?raw';
import apiReferenceMarkdown from '../../../APIReference.md?raw';
import SignupPageGif from './SignupPageGif';
import LoginPageGif from './LoginPageGif';
import ForgotPasswordGif from './ForgotPasswordGif';
import DashboardGif from './DashboardGif';
import CreateBucketGif from './CreateBucketGif';
import BucketFullWorkflowGif from './BucketFullWorkflowGif';
import ProfileSettingsGif from './ProfileSettingsGif';

const Doc = () => {
    const { isDark, toggleTheme } = useTheme();
    const { user } = useAuth();
    const navigate = useNavigate();
    const scrollContainerRef = useRef(null);

    const [activeItem, setActiveItem] = useState('What is AIveilix?');

    const navItems = [
        {
            title: 'Introduction',
            items: [
                { id: 'section-1-what-is-aiveilix', name: 'What is AIveilix?', icon: <Book size={18} /> },
                { id: 'section-2-how-it-works', name: 'How It Works', icon: <Cpu size={18} /> },
                { id: 'section-3-who-is-this-for', name: 'Who Is This For?', icon: <Users size={18} /> },
                { id: 'section-4-security-privacy', name: 'Security & Privacy', icon: <Shield size={18} /> },
            ]
        },
        {
            title: 'User Guides',
            items: [
                { id: 'quick-start', name: 'Quick Start', icon: <Zap size={18} /> },
                { id: 'step-1-create-your-account', name: 'Create Account', icon: <Users size={18} /> },
                { id: 'step-2-login-to-your-account', name: 'Login', icon: <MessageSquare size={18} /> },
                { id: 'step-3-password-recovery-optional', name: 'Password Recovery', icon: <Search size={18} /> },
                { id: 'step-4-dashboard-overview', name: 'Dashboard Overview', icon: <Box size={18} /> },
                { id: 'step-5-create-your-first-bucket', name: 'Create Bucket', icon: <Box size={18} /> },
                { id: 'step-6-open-a-bucket', name: 'Bucket Workflow', icon: <Box size={18} /> },
                { id: 'step-7-profile--settings', name: 'Profile & Settings', icon: <Users size={18} /> },
            ]
        },
        {
            title: 'Integrations (MCP)',
            items: [
                { id: 'overview', name: 'Overview', icon: <LinkIcon size={18} /> },
                { id: 'cursor-setup', name: 'Cursor Setup', icon: <Terminal size={18} /> },
                { id: 'claude-desktop-setup', name: 'Claude Setup', icon: <Terminal size={18} /> },
                { id: 'chatgpt-setup', name: 'ChatGPT Setup', icon: <Terminal size={18} /> },
            ]
        },
        {
            title: 'API Reference',
            items: [
                { id: 'authentication', name: 'Authentication', icon: <Lock size={18} /> },
                { id: 'endpoints', name: 'Endpoints', icon: <Server size={18} /> },
                { id: 'rate-limits', name: 'Rate Limits', icon: <Key size={18} /> },
            ]
        }
    ];

    const scrollToSection = (id, name) => {
        setActiveItem(name);
        const element = document.getElementById(id);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    };

    const slugify = (value) =>
        value
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, '-')
            .replace(/(^-|-$)/g, '');

    const getNodeText = (node) => {
        if (typeof node === 'string' || typeof node === 'number') return String(node);
        if (Array.isArray(node)) return node.map(getNodeText).join('');
        if (node && node.props && node.props.children) return getNodeText(node.props.children);
        return '';
    };

    const markdownComponents = {
        h1: ({ children, ...props }) => {
            const text = getNodeText(children);
            return (
                <h1 id={slugify(text)} className={`text-6xl font-black mb-8 tracking-tight leading-[1.1] ${isDark ? 'text-white' : 'text-gray-900'}`} {...props}>
                    {children}
                </h1>
            );
        },
        h2: ({ children, ...props }) => {
            const text = getNodeText(children);
            return (
                <h2 id={slugify(text)} className={`text-4xl font-bold mt-16 mb-6 ${isDark ? 'text-gray-200' : 'text-gray-800'}`} {...props}>
                    {children}
                </h2>
            );
        },
        h3: ({ children, ...props }) => {
            const text = getNodeText(children);
            const isSignupStep = text.trim() === 'Step 1: Create Your Account';
            const isLoginStep = text.trim() === 'Step 2: Login to Your Account';
            const isForgotStep = text.trim() === 'Step 3: Password Recovery (Optional)';
            const isDashboardStep = text.trim() === 'Step 4: Dashboard Overview';
            const isCreateBucketStep = text.trim() === 'Step 5: Create Your First Bucket';
            const isOpenBucketStep = text.trim() === 'Step 6: Bucket Workflow';
            const isProfileSettingsStep = text.trim() === 'Step 7: Profile & Settings';
            return (
                <>
                    <h3 id={slugify(text)} className={`text-3xl font-bold mt-10 mb-4 ${isDark ? 'text-dark-accent' : 'text-light-accent'}`} {...props}>
                        {children}
                    </h3>
                    {isSignupStep && (
                        <div className={`mt-6 rounded-3xl overflow-hidden border ${isDark ? 'border-white/10 bg-black/40' : 'border-black/10 bg-white/70'} shadow-2xl`}>
                            <SignupPageGif />
                        </div>
                    )}
                    {isLoginStep && (
                        <div className={`mt-6 rounded-3xl overflow-hidden border ${isDark ? 'border-white/10 bg-black/40' : 'border-black/10 bg-white/70'} shadow-2xl`}>
                            <LoginPageGif embedded />
                        </div>
                    )}
                    {isForgotStep && (
                        <div className={`mt-6 rounded-3xl overflow-hidden border ${isDark ? 'border-white/10 bg-black/40' : 'border-black/10 bg-white/70'} shadow-2xl`}>
                            <ForgotPasswordGif />
                        </div>
                    )}
                    {isDashboardStep && (
                        <div className={`mt-6 rounded-3xl overflow-hidden border ${isDark ? 'border-white/10 bg-black/40' : 'border-black/10 bg-white/70'} shadow-2xl`}>
                            <DashboardGif />
                        </div>
                    )}
                    {isCreateBucketStep && (
                        <div className={`mt-6 rounded-3xl overflow-hidden border ${isDark ? 'border-white/10 bg-black/40' : 'border-black/10 bg-white/70'} shadow-2xl`}>
                            <CreateBucketGif />
                        </div>
                    )}
                    {isOpenBucketStep && (
                        <div className={`mt-6 rounded-3xl overflow-hidden border ${isDark ? 'border-white/10 bg-black/40' : 'border-black/10 bg-white/70'} shadow-2xl`}>
                            <BucketFullWorkflowGif />
                        </div>
                    )}
                    {isProfileSettingsStep && (
                        <div className={`mt-6 rounded-3xl overflow-hidden border ${isDark ? 'border-white/10 bg-black/40' : 'border-black/10 bg-white/70'} shadow-2xl`}>
                            <ProfileSettingsGif />
                        </div>
                    )}
                </>
            );
        },
        h4: ({ children, ...props }) => (
            <h4 className={`text-xl font-bold mt-6 mb-3 ${isDark ? 'text-gray-300' : 'text-gray-700'}`} {...props}>
                {children}
            </h4>
        ),
        p: ({ children, ...props }) => (
            <p className={`${isDark ? 'text-gray-300' : 'text-gray-700'} text-xl leading-relaxed`} {...props}>
                {children}
            </p>
        ),
        ul: ({ children, ...props }) => (
            <ul className={`list-disc pl-6 space-y-3 text-lg ${isDark ? 'text-gray-300' : 'text-gray-700'}`} {...props}>
                {children}
            </ul>
        ),
        ol: ({ children, ...props }) => (
            <ol className={`list-decimal pl-6 space-y-3 text-lg ${isDark ? 'text-gray-300' : 'text-gray-700'}`} {...props}>
                {children}
            </ol>
        ),
        li: ({ children, ...props }) => (
            <li className="leading-relaxed" {...props}>
                {children}
            </li>
        ),
        table: ({ children, ...props }) => (
            <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse" {...props}>
                    {children}
                </table>
            </div>
        ),
        th: ({ children, ...props }) => (
            <th className={`py-3 font-bold ${isDark ? 'text-teal-300' : 'text-teal-600'}`} {...props}>
                {children}
            </th>
        ),
        td: ({ children, ...props }) => (
            <td className="py-3 align-top text-lg opacity-80" {...props}>
                {children}
            </td>
        ),
        blockquote: ({ children, ...props }) => (
            <blockquote className={`border-l-4 pl-4 italic ${isDark ? 'border-teal-500/40 text-gray-300' : 'border-teal-300 text-gray-700'}`} {...props}>
                {children}
            </blockquote>
        ),
        hr: (props) => <hr className={`${isDark ? 'border-white/10' : 'border-black/10'} my-10`} {...props} />,
        code: ({ node, inline, className, children, ...props }) => {
            const [copied, setCopied] = useState(false);
            const match = /language-(\w+)/.exec(className || '');
            const language = match ? match[1] : '';
            const codeString = String(children).replace(/\n$/, '');

            const handleCopy = () => {
                navigator.clipboard.writeText(codeString);
                setCopied(true);
                setTimeout(() => setCopied(false), 2000);
            };

            // Inline code
            if (inline) {
                return (
                    <code className={`px-2 py-1 rounded text-sm font-mono ${isDark ? 'bg-white/10 text-teal-300' : 'bg-black/10 text-teal-600'}`} {...props}>
                        {children}
                    </code>
                );
            }

            // Code block
            return (
                <div className="relative group my-6">
                    <div className={`absolute top-3 right-3 flex items-center gap-2 z-10`}>
                        {language && (
                            <span className={`text-xs px-2 py-1 rounded font-mono ${isDark ? 'bg-white/10 text-gray-400' : 'bg-black/10 text-gray-600'}`}>
                                {language}
                            </span>
                        )}
                        <button
                            onClick={handleCopy}
                            className={`p-2 rounded transition-all ${isDark ? 'bg-white/10 hover:bg-white/20 text-gray-300' : 'bg-black/10 hover:bg-black/20 text-gray-700'}`}
                            title="Copy code"
                        >
                            {copied ? <Check size={16} /> : <Copy size={16} />}
                        </button>
                    </div>
                    <pre className={`rounded-xl p-6 overflow-x-auto border ${isDark ? 'bg-black/60 border-white/10' : 'bg-gray-50 border-black/10'}`}>
                        <code className={`font-mono text-sm ${isDark ? 'text-gray-300' : 'text-gray-800'}`} {...props}>
                            {children}
                        </code>
                    </pre>
                </div>
            );
        },
    };

    // Scroll-spy: update active nav item when user scrolls into a section
    useEffect(() => {
        const scrollEl = scrollContainerRef.current;
        if (!scrollEl) return;
        const sectionIds = navItems.flatMap((s) => s.items.map((i) => i.id));
        const idToName = {};
        navItems.forEach((s) => s.items.forEach((i) => { idToName[i.id] = i.name; }));

        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (!entry.isIntersecting) return;
                    const id = entry.target.id;
                    if (idToName[id]) setActiveItem(idToName[id]);
                });
            },
            { root: scrollEl, rootMargin: '-20% 0px -60% 0px', threshold: 0 }
        );

        sectionIds.forEach((id) => {
            const el = document.getElementById(id);
            if (el) observer.observe(el);
        });
        return () => observer.disconnect();
    }, []);

    return (
        <div className={`min-h-screen flex font-sans relative ${isDark ? 'text-dark-text' : 'text-light-text'}`}>
            <div
                className="fixed inset-0 -z-10 transition-colors duration-300"
                style={{ backgroundColor: isDark ? '#050B0D' : '#E5F2ED' }}
            />

            {/* Sidebar Navigation - sticky, does not scroll with main content */}
            <div
                className="w-[280px] flex-shrink-0 flex flex-col h-screen sticky top-0 self-start overflow-hidden transition-colors duration-300"
                style={{ backgroundColor: isDark ? '#050B0D' : '#E5F2ED' }}
            >
                <div className="p-6 border-b border-transparent">
                    <Link to="/" className="flex items-center gap-3 group">
                        <img src="/logo-with-name..png" alt="AIveilix" className="h-12 w-auto object-contain" />
                    </Link>
                </div>
                <div className="flex-1 overflow-y-auto px-4 py-8 space-y-8 scrollbar-hide">
                    {navItems.map((section, idx) => (
                        <div key={idx}>
                            <h3 className={`text-xs font-bold uppercase tracking-widest mb-4 px-3 ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
                                {section.title}
                            </h3>
                            <ul className="space-y-1">
                                {section.items.map((item, itemIdx) => (
                                    <li key={itemIdx}>
                                        <button
                                            onClick={() => scrollToSection(item.id, item.name)}
                                            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-base font-medium transition-all duration-200 group
                                            ${activeItem === item.name
                                                    ? (isDark ? 'bg-white/10 text-dark-accent' : 'bg-black/10 text-light-accent')
                                                    : (isDark ? 'text-dark-text/70 hover:text-dark-text hover:bg-white/10' : 'text-light-text/70 hover:text-light-text hover:bg-black/10')
                                                }
                                        `}>
                                            <span className={`transition-opacity ${activeItem === item.name
                                                ? (isDark ? 'opacity-100 text-dark-accent' : 'opacity-100 text-light-accent')
                                                : (isDark ? 'opacity-70 group-hover:opacity-100 text-dark-accent' : 'opacity-70 group-hover:opacity-100 text-light-accent')
                                                }`}>
                                                {item.icon}
                                            </span>
                                            <span>{item.name}</span>
                                        </button>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ))}
                </div>
                <div className={`p-4 border-t ${isDark ? 'border-gray-800' : 'border-gray-200'}`}>
                    <div className={`text-xs text-center ${isDark ? 'text-gray-600' : 'text-gray-400'}`}>
                        v1.0.0 • AIveilix Inc.
                    </div>
                </div>
            </div>

            {/* Main Content Area */}
            <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden relative">

                {/* Header */}
                <div className="w-full h-[60px] flex items-center justify-end px-8 z-20 flex-shrink-0">
                    <div className="flex items-center gap-4">
                        {user ? (
                            <button onClick={() => navigate('/dashboard')} className={`px-4 py-2 rounded-full text-sm font-semibold transition-colors ${isDark ? 'bg-dark-accent text-dark-bg hover:opacity-90' : 'bg-light-accent text-light-bg hover:opacity-90'}`}>
                                Dashboard
                            </button>
                        ) : (
                            <div className="flex items-center gap-3">
                                <Link to="/login" className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${isDark ? 'text-dark-text/70 hover:text-dark-text' : 'text-light-text/70 hover:text-light-text'}`}>Log in</Link>
                                <Link to="/signup" className={`px-4 py-2 rounded-full text-sm font-semibold transition-colors ${isDark ? 'bg-dark-accent text-dark-bg hover:opacity-90' : 'bg-light-accent text-light-bg hover:opacity-90'}`}>Sign up</Link>
                            </div>
                        )}
                        <button onClick={toggleTheme} className={`p-2 rounded-full transition-colors ${isDark ? 'hover:bg-white/10' : 'hover:bg-black/10'}`}>
                            {isDark ? <Moon size={20} /> : <Sun size={20} />}
                        </button>
                    </div>
                </div>

                {/* Content Card Wrapper */}
                <div className="flex-1 flex flex-col overflow-hidden pb-[5px] pr-[5px] pl-[5px]">
                    <div className={`w-full h-full rounded-3xl overflow-hidden relative shadow-2xl transition-all duration-300 backdrop-blur-3xl flex border
                        ${isDark ? 'bg-[#0A0A0A]/80 border-white/5' : 'bg-white/80 border-black/5'}
                    `}>

                        {/* Center Scrollable Content */}
                        <div ref={scrollContainerRef} className="flex-1 h-full overflow-y-auto p-8 md:p-16 scrollbar-thin">
                            <div className="max-w-4xl mx-auto space-y-24 pb-64">

                                {/* --- Section 1 & 2: Introduction Content (Markdown) --- */}
                                <section className="scroll-mt-16">
                                    <div className="space-y-10">
                                        <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
                                            {introductionMarkdown}
                                        </ReactMarkdown>
                                    </div>
                                </section>

                                {/* --- User Guides (Markdown) --- */}
                                <section className="scroll-mt-16">
                                    <div className="space-y-10">
                                        <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
                                            {userGuidesMarkdown}
                                        </ReactMarkdown>
                                    </div>
                                </section>

                                {/* --- Integrations (MCP) (Markdown) --- */}
                                <section className="scroll-mt-16">
                                    <div className="space-y-10">
                                        <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
                                            {integrationsMarkdown}
                                        </ReactMarkdown>
                                    </div>
                                </section>

                                {/* --- API Reference (Markdown) --- */}
                                <section className="scroll-mt-16">
                                    <div className="space-y-10">
                                        <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
                                            {apiReferenceMarkdown}
                                        </ReactMarkdown>
                                    </div>
                                </section>

                                {/* --- Section 3: Who Is This For? --- */}
                                <section id="section-3-who-is-this-for" className="scroll-mt-16">
                                    <div className="mb-12">
                                        <h2 className={`text-5xl font-extrabold mb-8 tracking-tight ${isDark ? 'text-white' : 'text-gray-900'}`}>
                                            Section 3: Who Is This For?
                                        </h2>
                                        <div className={`h-2 w-32 rounded-full mb-12 ${isDark ? 'bg-dark-accent' : 'bg-light-accent'}`} />
                                    </div>

                                    <div className="space-y-20">
                                        {/* Row 1 */}
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                                            <div className="space-y-6">
                                                <div className="flex items-center gap-4">
                                                    <Terminal className="text-teal-400 w-10 h-10" />
                                                    <h3 className="text-3xl font-bold">For Developers</h3>
                                                </div>
                                                <p className="opacity-70 text-xl leading-relaxed">"How was the legacy auth token formatted in 2018 according to the specs?" Ask your IDE directly. Onboard in 3 days instead of 2 weeks.</p>
                                            </div>
                                            <div className="space-y-6">
                                                <div className="flex items-center gap-4">
                                                    <Globe className="text-teal-400 w-10 h-10" />
                                                    <h3 className="text-3xl font-bold">For Researchers</h3>
                                                </div>
                                                <p className="opacity-70 text-xl leading-relaxed">Summarize consensus across 50 papers at once. Literature reviews compressed from 3 weeks to 3 days.</p>
                                            </div>
                                        </div>

                                        {/* Row 2 */}
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                                            <div className="space-y-6">
                                                <div className="flex items-center gap-4">
                                                    <Zap className="text-teal-400 w-10 h-10" />
                                                    <h3 className="text-3xl font-bold">For Students</h3>
                                                </div>
                                                <p className="opacity-70 text-xl leading-relaxed">Turn 20 slide decks into a tailored 20-question quiz. $0/month for a tutor that knows YOUR syllabus.</p>
                                            </div>
                                            <div className="space-y-6">
                                                <div className="flex items-center gap-4">
                                                    <Box className="text-teal-400 w-10 h-10" />
                                                    <h3 className="text-3xl font-bold">Information Hoarders</h3>
                                                </div>
                                                <p className="opacity-70 text-xl leading-relaxed">Stop searching for "Grandma's recipe." Find memories and receipts across 10,000 files in 10 seconds.</p>
                                            </div>
                                        </div>
                                    </div>
                                </section>

                                {/* --- Section 4: Security & Privacy --- */}
                                <section id="section-4-security-privacy" className="scroll-mt-16">
                                    <div className="mb-12">
                                        <h2 className={`text-5xl font-extrabold mb-8 tracking-tight ${isDark ? 'text-white' : 'text-gray-900'}`}>
                                            Section 4: Security & Privacy
                                        </h2>
                                        <div className={`h-2 w-32 rounded-full mb-12 ${isDark ? 'bg-dark-accent' : 'bg-light-accent'}`} />
                                    </div>

                                    <div className="space-y-12">
                                        <div className={`p-10 rounded-[3rem] border ${isDark ? 'bg-white/5 border-white/10' : 'bg-gray-50 border-black/5'}`}>
                                            <div className="flex items-center gap-6 mb-8">
                                                <Shield className="w-12 h-12 text-teal-400" />
                                                <h3 className="text-3xl font-black">Defense-In-Depth</h3>
                                            </div>
                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                                                <div className="space-y-4">
                                                    <h4 className="text-xl font-bold">In Transit (TLS 1.3)</h4>
                                                    <p className="opacity-70 text-base">Bank-grade encryption preventing packet sniffing and man-in-the-middle attacks.</p>
                                                </div>
                                                <div className="space-y-4">
                                                    <h4 className="text-xl font-bold">At Rest (AES-256)</h4>
                                                    <p className="opacity-70 text-base">Encryption on physical disks. Physical theft results in nothing but mathematical gibberish.</p>
                                                </div>
                                            </div>
                                        </div>

                                        <div className={`p-8 rounded-3xl ${isDark ? 'bg-red-900/10 border border-red-500/20' : 'bg-red-50 border border-red-100'}`}>
                                            <h4 className="text-xl font-bold mb-2">Right To Be Forgotten (Article 17)</h4>
                                            <p className="opacity-80 italic italic">"No 'soft delete' retention purgatory. When you hit delete, your files, vectors, logs, and metadata are scrubbed permanently. GONE FOREVER."</p>
                                        </div>
                                    </div>
                                </section>

                            </div>
                        </div>

                    </div>
                </div>
            </div>
        </div>
    );
};

export default Doc;
