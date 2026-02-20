import { Link } from 'react-router-dom'

export default function PrivacyPolicy() {
  const lastUpdated = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })

  return (
    <div className="min-h-screen relative text-[#E6F1F5]">
      {/* Fixed Background – always covers viewport when scrolling */}
      <div
        className="fixed inset-0 -z-10"
        style={{ backgroundColor: '#050B0D' }}
      />
      {/* Minimal top bar – no heavy header */}
      <div className="relative border-b border-white/10 bg-[#0E1F24]/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link to="/login" className="hover:opacity-90 transition-opacity">
            <img src="/logo-with-name..png" alt="AIveilix" className="h-10 w-auto max-w-[200px] object-contain" />
          </Link>
          <Link
            to="/login"
            className="text-xs text-[#E6F1F5]/70 hover:text-[#E6F1F5] transition-colors"
          >
            Back to app
          </Link>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-10">
        <div className="mb-10">
          <h1 className="text-3xl font-bold text-[#E6F1F5]">Privacy Policy</h1>
          <p className="text-[#E6F1F5]/60 mt-2">Last updated: {lastUpdated}</p>
        </div>

        <div className="space-y-8 text-[#E6F1F5]/90 leading-relaxed">
          {/* 1 */}
          <section>
            <h2 className="text-xl font-semibold text-[#E6F1F5] mb-4 pb-2 border-b border-[#2DFFB7]/30">
              1. Introduction
            </h2>
            <p>
              AIveilix (“we”, “us”, “our”) is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our document intelligence service, including our website and application (the “Service”).
            </p>
            <p className="mt-3">
              By using AIveilix, you agree to this Privacy Policy. If you do not agree, please do not use the Service.
            </p>
          </section>

          {/* 2 */}
          <section>
            <h2 className="text-xl font-semibold text-[#E6F1F5] mb-4 pb-2 border-b border-[#2DFFB7]/30">
              2. Information We Collect
            </h2>
            <p>
              We collect information you give us, and some that is created when you use the Service.
            </p>
            <h3 className="text-lg font-medium text-[#E6F1F5] mt-6 mb-2">2.1 Information you provide</h3>
            <ul className="list-disc pl-6 space-y-1">
              <li><strong>Account:</strong> Email, password, and name when you sign up</li>
              <li><strong>Documents and content:</strong> Files and text you upload into buckets (PDFs, images, etc.)</li>
              <li><strong>Usage in product:</strong> Bucket names, chat messages, and conversation history</li>
              <li><strong>API keys and OAuth:</strong> If you use API access, we store and use API keys and OAuth client details you provide</li>
              <li><strong>Support:</strong> Anything you send when you contact us</li>
            </ul>
            <h3 className="text-lg font-medium text-[#E6F1F5] mt-6 mb-2">2.2 Information we collect automatically</h3>
            <ul className="list-disc pl-6 space-y-1">
              <li><strong>Usage:</strong> How you use the Service (e.g. buckets, file counts, activity)</li>
              <li><strong>Technical:</strong> IP address, browser type, device type, and similar technical data</li>
              <li><strong>Logs:</strong> Access times and errors for security and operations</li>
            </ul>
          </section>

          {/* 3 */}
          <section>
            <h2 className="text-xl font-semibold text-[#E6F1F5] mb-4 pb-2 border-b border-[#2DFFB7]/30">
              3. How We Use Your Information
            </h2>
            <p>We use your information to:</p>
            <ul className="list-disc pl-6 mt-2 space-y-1">
              <li>Provide and operate the Service (storage, search, chat, embeddings)</li>
              <li>Create and manage your account and buckets</li>
              <li>Process and index your documents for search and AI chat</li>
              <li>Send notifications you have requested (e.g. file processed, login)</li>
              <li>Improve the Service and fix issues</li>
              <li>Comply with law and protect our rights and security</li>
              <li>Respond to your requests (e.g. support, privacy requests)</li>
            </ul>
          </section>

          {/* 4 */}
          <section>
            <h2 className="text-xl font-semibold text-[#E6F1F5] mb-4 pb-2 border-b border-[#2DFFB7]/30">
              4. Sharing and Disclosure
            </h2>
            <p>
              We do not sell your personal information. We may share it only:
            </p>
            <ul className="list-disc pl-6 mt-2 space-y-1">
              <li><strong>Service providers:</strong> With vendors that help us run the Service (e.g. hosting, auth). They are required to protect your data and use it only for our instructions.</li>
              <li><strong>AI / embeddings:</strong> Your document content may be sent to third‑party AI/embedding services we use to power search and chat. Use of the Service means you accept that.</li>
              <li><strong>Legal:</strong> When required by law, court order, or to protect rights and safety.</li>
              <li><strong>With your consent:</strong> Where you have agreed to a specific sharing.</li>
            </ul>
          </section>

          {/* 5 */}
          <section>
            <h2 className="text-xl font-semibold text-[#E6F1F5] mb-4 pb-2 border-b border-[#2DFFB7]/30">
              5. Data Security
            </h2>
            <p>
              We use safeguards (e.g. encryption in transit, access controls, secure storage) to protect your data. No system is completely secure; you use the Service at your own risk. You are responsible for keeping your password and API keys secret and for activity under your account.
            </p>
          </section>

          {/* 6 */}
          <section>
            <h2 className="text-xl font-semibold text-[#E6F1F5] mb-4 pb-2 border-b border-[#2DFFB7]/30">
              6. Data Retention
            </h2>
            <p>
              We keep your data for as long as your account is active and as needed to provide the Service, comply with law, and resolve disputes. If you delete your account or data, we will delete or anonymize it within a reasonable time, except where we must keep it by law.
            </p>
          </section>

          {/* 7 */}
          <section>
            <h2 className="text-xl font-semibold text-[#E6F1F5] mb-4 pb-2 border-b border-[#2DFFB7]/30">
              7. Your Rights
            </h2>
            <p>
              Depending on where you live, you may have the right to access, correct, delete, or export your personal data, or to object to or restrict certain processing. To request this, contact us at <a href="mailto:info@aiveilix.com" className="text-[#2DFFB7] hover:underline">info@aiveilix.com</a>. We will respond as required by law.
            </p>
            <p className="mt-3">
              You can also update account details and preferences in the app where we provide those options.
            </p>
          </section>

          {/* 8 */}
          <section>
            <h2 className="text-xl font-semibold text-[#E6F1F5] mb-4 pb-2 border-b border-[#2DFFB7]/30">
              8. Cookies and Similar Technologies
            </h2>
            <p>
              We use cookies and similar technologies for sign‑in, preferences, and security. You can adjust your browser settings, but some features may not work if you disable them.
            </p>
          </section>

          {/* 9 */}
          <section>
            <h2 className="text-xl font-semibold text-[#E6F1F5] mb-4 pb-2 border-b border-[#2DFFB7]/30">
              9. International Transfers
            </h2>
            <p>
              Your data may be stored and processed in countries other than your own. We take steps so that it receives adequate protection where required by law.
            </p>
          </section>

          {/* 10 */}
          <section>
            <h2 className="text-xl font-semibold text-[#E6F1F5] mb-4 pb-2 border-b border-[#2DFFB7]/30">
              10. Children
            </h2>
            <p>
              The Service is not intended for children under 16. We do not knowingly collect data from them. If you learn a child has given us data, contact us and we will delete it.
            </p>
          </section>

          {/* 11 */}
          <section>
            <h2 className="text-xl font-semibold text-[#E6F1F5] mb-4 pb-2 border-b border-[#2DFFB7]/30">
              11. Changes to This Policy
            </h2>
            <p>
              We may update this Privacy Policy from time to time. We will post the new version here and update the “Last updated” date. For big changes we may notify you by email or in the app. Continued use after changes means you accept the updated policy.
            </p>
          </section>

          {/* 12 */}
          <section>
            <h2 className="text-xl font-semibold text-[#E6F1F5] mb-4 pb-2 border-b border-[#2DFFB7]/30">
              12. Data Breach Notification (GDPR)
            </h2>
            <p>
              In the event of a personal data breach, AIveilix will act promptly in accordance with applicable law, including the EU General Data Protection Regulation (GDPR).
            </p>
            <h3 className="text-lg font-medium text-[#E6F1F5] mt-4 mb-2">What we will do:</h3>
            <ul className="list-disc pl-6 space-y-1">
              <li><strong>Detect and contain:</strong> Upon becoming aware of a breach, we will immediately assess the scope, contain it, and begin investigation.</li>
              <li><strong>Notify authorities:</strong> If the breach is likely to result in a risk to individuals' rights and freedoms, we will notify the relevant supervisory authority within <strong>72 hours</strong> of becoming aware.</li>
              <li><strong>Notify affected users:</strong> If the breach is likely to result in a high risk to individuals, we will notify affected users without undue delay, clearly explaining what happened, what data was affected, and what steps we are taking.</li>
              <li><strong>Document:</strong> All breaches, regardless of severity, will be documented internally including the facts, effects, and remedial actions taken.</li>
            </ul>
            <h3 className="text-lg font-medium text-[#E6F1F5] mt-4 mb-2">What a breach notification will include:</h3>
            <ul className="list-disc pl-6 space-y-1">
              <li>A description of the nature of the breach</li>
              <li>The categories and approximate number of individuals and records affected</li>
              <li>The likely consequences of the breach</li>
              <li>Measures taken or proposed to address the breach</li>
              <li>Contact details for our data protection inquiries</li>
            </ul>
            <p className="mt-3">
              To report a suspected security issue, contact us immediately at{' '}
              <a href="mailto:info@aiveilix.com" className="text-[#2DFFB7] hover:underline">info@aiveilix.com</a>.
            </p>
          </section>

          {/* 13 */}
          <section>
            <h2 className="text-xl font-semibold text-[#E6F1F5] mb-4 pb-2 border-b border-[#2DFFB7]/30">
              13. Contact
            </h2>
            <p>
              For privacy questions, requests, or complaints, contact us at:
            </p>
            <p className="mt-2">
              <strong className="text-[#2DFFB7]">Email:</strong>{' '}
              <a href="mailto:info@aiveilix.com" className="text-[#2DFFB7] hover:underline">
                info@aiveilix.com
              </a>
            </p>
          </section>

          {/* Footer */}
          <div className="pt-8 mt-10 border-t border-white/10 text-center text-[#E6F1F5]/60 text-sm">
            <p>By using AIveilix, you acknowledge that you have read and agree to this Privacy Policy.</p>
            <p className="mt-2">
              <Link to="/login" className="text-[#2DFFB7] hover:underline">Return to AIveilix</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
