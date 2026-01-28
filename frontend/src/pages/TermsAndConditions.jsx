import { Link } from 'react-router-dom'

export default function TermsAndConditions() {
  const lastUpdated = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })

  return (
    <div className="min-h-screen relative text-[#E6F1F5]">
      {/* Fixed Background – always covers viewport when scrolling */}
      <div
        className="fixed inset-0 -z-10"
        style={{ backgroundColor: '#050B0D' }}
      />
      {/* Header */}
      <div className="relative border-b border-white/10 bg-[#0E1F24]/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-3xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link to="/login" className="hover:opacity-90 transition-opacity">
            <img src="/logo-with-name..png" alt="AIveilix" className="h-10 w-auto max-w-[200px] object-contain" />
          </Link>
          <Link
            to="/login"
            className="text-sm text-[#E6F1F5]/70 hover:text-[#E6F1F5] transition-colors"
          >
            Back to app
          </Link>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-4 py-10">
        <div className="mb-10">
          <h1 className="text-3xl font-bold text-[#E6F1F5]">Terms and Conditions</h1>
          <p className="text-[#E6F1F5]/60 mt-2">Last updated: {lastUpdated}</p>
        </div>

        <div className="space-y-8 text-[#E6F1F5]/90 leading-relaxed">
          {/* 1 */}
          <section>
            <h2 className="text-xl font-semibold text-[#E6F1F5] mb-4 pb-2 border-b border-[#2DFFB7]/30">
              1. Agreement to Terms
            </h2>
            <p>
              By accessing or using AIveilix (“Service”, “we”, “us”, “our”), you agree to be bound by these Terms and Conditions (“Terms”). If you do not agree, you may not use the Service.
            </p>
            <p className="mt-3">
              AIveilix is a document intelligence platform that lets you upload files, organize them in buckets, and chat with AI over your documents. These Terms apply to all users.
            </p>
          </section>

          {/* 2 */}
          <section>
            <h2 className="text-xl font-semibold text-[#E6F1F5] mb-4 pb-2 border-b border-[#2DFFB7]/30">
              2. Description of the Service
            </h2>
            <p>
              AIveilix provides:
            </p>
            <ul className="list-disc pl-6 mt-2 space-y-1">
              <li>Document buckets to organize your files</li>
              <li>File upload and processing (including PDFs and images)</li>
              <li>Semantic search over your documents</li>
              <li>AI chat over your document content</li>
              <li>API keys and optional OAuth for programmatic access</li>
              <li>Notifications and conversation history</li>
            </ul>
            <p className="mt-3">
              We may change or discontinue parts of the Service with reasonable notice where practical.
            </p>
          </section>

          {/* 3 */}
          <section>
            <h2 className="text-xl font-semibold text-[#E6F1F5] mb-4 pb-2 border-b border-[#2DFFB7]/30">
              3. Accounts and Security
            </h2>
            <p>
              You must register and keep your account information accurate. You are responsible for all activity under your account.
            </p>
            <p className="mt-3 font-medium text-[#E6F1F5]">
              You must not expose, share, or allow others to use:
            </p>
            <ul className="list-disc pl-6 mt-2 space-y-1">
              <li>Your password or login credentials</li>
              <li>Your API keys</li>
              <li>OAuth client secrets or other tokens</li>
              <li>Any means of accessing another user’s data</li>
            </ul>
            <p className="mt-3">
              If you suspect unauthorized access or misuse, you must notify us promptly and change your credentials. We may suspend or terminate accounts that violate these Terms or pose a security risk.
            </p>
          </section>

          {/* 4 */}
          <section>
            <h2 className="text-xl font-semibold text-[#E6F1F5] mb-4 pb-2 border-b border-[#2DFFB7]/30">
              4. Acceptable Use – What You Must Not Do
            </h2>
            <p>
              You may use the Service only for lawful purposes. You must not:
            </p>
            <ul className="list-disc pl-6 mt-2 space-y-1">
              <li>Expose, leak, or share API keys, credentials, or access tokens with anyone else</li>
              <li>Use the Service to distribute malware, spam, or harmful code</li>
              <li>Upload or process content that infringes others’ rights, is illegal, or violates applicable law</li>
              <li>Attempt to gain unauthorized access to our systems, other users’ accounts, or third‑party services</li>
              <li>Reverse engineer, scrape, or abuse the Service in a way that harms us or other users</li>
              <li>Use the Service to build a product that competes with AIveilix by copying its functionality or data</li>
              <li>Resell or sublicense access to the Service in a way we have not explicitly allowed</li>
            </ul>
            <p className="mt-3">
              We may remove content, suspend, or terminate accounts that breach this section, and we may report illegal activity to authorities.
            </p>
          </section>

          {/* 5 */}
          <section>
            <h2 className="text-xl font-semibold text-[#E6F1F5] mb-4 pb-2 border-b border-[#2DFFB7]/30">
              5. Your Data and Privacy
            </h2>
            <p>
              We process your data as described in our Privacy Policy. You keep ownership of your documents and content. By using the Service, you give us the rights we need to store, process, and serve your content (including to power search and chat).
            </p>
            <p className="mt-3">
              You must not upload or process personal data (e.g. about others) unless you have the right to do so and comply with applicable data protection laws.
            </p>
          </section>

          {/* 6 */}
          <section>
            <h2 className="text-xl font-semibold text-[#E6F1F5] mb-4 pb-2 border-b border-[#2DFFB7]/30">
              6. Confidentiality and No Exposure
            </h2>
            <p>
              You must keep confidential and not expose:
            </p>
            <ul className="list-disc pl-6 mt-2 space-y-1">
              <li>Your account credentials and API keys</li>
              <li>OAuth client secrets and tokens</li>
              <li>Any non‑public technical or commercial information we share with you about the Service</li>
            </ul>
            <p className="mt-3">
              You may disclose information only where required by law, and then only to the extent required, and you must try to get confidential treatment for that disclosure.
            </p>
          </section>

          {/* 7 */}
          <section>
            <h2 className="text-xl font-semibold text-[#E6F1F5] mb-4 pb-2 border-b border-[#2DFFB7]/30">
              7. Intellectual Property
            </h2>
            <p>
              AIveilix’s name, logo, software, and documentation are owned by us or our licensors. You do not get any ownership in them. You may use the Service only as allowed by these Terms.
            </p>
            <p className="mt-3">
              You retain rights in the content you upload. You grant us a license to use, store, and process that content to provide and improve the Service.
            </p>
          </section>

          {/* 8 */}
          <section>
            <h2 className="text-xl font-semibold text-[#E6F1F5] mb-4 pb-2 border-b border-[#2DFFB7]/30">
              8. Disclaimers
            </h2>
            <p>
              The Service is provided “as is” and “as available”. We do not guarantee uninterrupted, error‑free, or secure operation. AI outputs (e.g. chat answers) are not legal, medical, or professional advice. You use them at your own risk.
            </p>
          </section>

          {/* 9 */}
          <section>
            <h2 className="text-xl font-semibold text-[#E6F1F5] mb-4 pb-2 border-b border-[#2DFFB7]/30">
              9. Limitation of Liability
            </h2>
            <p>
              To the maximum extent permitted by law, we are not liable for indirect, incidental, special, or consequential damages, or loss of data or profits, arising from your use of the Service. Our total liability to you for any claim shall not exceed the amount you paid us in the twelve (12) months before the claim, or one hundred US dollars, whichever is greater.
            </p>
          </section>

          {/* 10 */}
          <section>
            <h2 className="text-xl font-semibold text-[#E6F1F5] mb-4 pb-2 border-b border-[#2DFFB7]/30">
              10. Termination
            </h2>
            <p>
              We may suspend or terminate your access at any time for breach of these Terms or for operational or legal reasons. You may stop using the Service at any time. On termination, your right to use the Service ends. We may delete your data after a reasonable period.
            </p>
          </section>

          {/* 11 */}
          <section>
            <h2 className="text-xl font-semibold text-[#E6F1F5] mb-4 pb-2 border-b border-[#2DFFB7]/30">
              11. Changes to Terms
            </h2>
            <p>
              We may update these Terms by posting a new version and updating the “Last updated” date. Material changes may be notified by email or in‑app notice. Continued use after changes means you accept the new Terms.
            </p>
          </section>

          {/* 12 */}
          <section>
            <h2 className="text-xl font-semibold text-[#E6F1F5] mb-4 pb-2 border-b border-[#2DFFB7]/30">
              12. Contact
            </h2>
            <p>
              For questions about these Terms, contact us at:
            </p>
            <p className="mt-2">
              <strong className="text-[#2DFFB7]">Email:</strong>{' '}
              <a href="mailto:info@aiveilix.com" className="text-[#2DFFB7] hover:underline">
                info@aiveilix.com
              </a>
            </p>
            <p className="mt-3">
              We will respond to reasonable requests as soon as practicable.
            </p>
          </section>

          {/* Footer */}
          <div className="pt-8 mt-10 border-t border-white/10 text-center text-[#E6F1F5]/60 text-sm">
            <p>By using AIveilix, you confirm that you have read, understood, and agree to these Terms and Conditions.</p>
            <p className="mt-2">
              <Link to="/login" className="text-[#2DFFB7] hover:underline">Return to AIveilix</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
