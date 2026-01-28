import { Link } from 'react-router-dom'

export default function Tokusho() {
  const lastUpdated = new Date().toLocaleDateString('ja-JP', { year: 'numeric', month: 'long', day: 'numeric' })

  return (
    <div className="min-h-screen relative text-[#E6F1F5]">
      {/* Fixed Background */}
      <div className="fixed inset-0 -z-10" style={{ backgroundColor: '#050B0D' }} />
      {/* Minimal top bar */}
      <div className="relative border-b border-white/10 bg-[#0E1F24]/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link to="/login" className="hover:opacity-90 transition-opacity">
            <img src="/logo-with-name..png" alt="AIveilix" className="h-10 w-auto max-w-[200px] object-contain" />
          </Link>
          <Link to="/login" className="text-xs text-[#E6F1F5]/70 hover:text-[#E6F1F5] transition-colors">
            Back to app
          </Link>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-10">
        <div className="mb-10">
          <h1 className="text-3xl font-bold text-[#E6F1F5]">特定商取引法に基づく表記</h1>
          <p className="text-[#E6F1F5]/60 mt-1">Specified Commercial Transactions Act Disclosure</p>
          <p className="text-[#E6F1F5]/60 mt-1">最終更新日: {lastUpdated}</p>
        </div>

        <div className="space-y-8 text-[#E6F1F5]/90 leading-relaxed">
          <section>
            <p>本サービスは、特定商取引法に基づき、以下の通り表記いたします。</p>
          </section>

          <section>
            <table className="w-full border-collapse rounded-xl overflow-hidden border border-[#2DFFB7]/20 bg-[#0E1F24]/50">
              <tbody>
                <tr className="border-b border-white/5">
                  <th className="w-48 sm:w-56 py-4 px-4 text-left font-semibold text-[#E6F1F5] text-sm bg-[#2DFFB7]/10 border-r border-white/5">
                    事業者名
                  </th>
                  <td className="py-4 px-4 text-[#E6F1F5]/90 text-sm">株式会社 SAAD INTERNATIONAL</td>
                </tr>
                <tr className="border-b border-white/5">
                  <th className="py-4 px-4 text-left font-semibold text-[#E6F1F5] text-sm bg-[#2DFFB7]/10 border-r border-white/5">
                    代表者
                  </th>
                  <td className="py-4 px-4 text-[#E6F1F5]/90 text-sm">CHAUDHARY ABDUL JABBAR JUTT</td>
                </tr>
                <tr className="border-b border-white/5">
                  <th className="py-4 px-4 text-left font-semibold text-[#E6F1F5] text-sm bg-[#2DFFB7]/10 border-r border-white/5">
                    所在地
                  </th>
                  <td className="py-4 px-4 text-[#E6F1F5]/90 text-sm">
                    〒455-0834<br />愛知県名古屋市港区神宮寺1丁目1303-1<br />レンダイスクォッター401
                  </td>
                </tr>
                <tr className="border-b border-white/5">
                  <th className="py-4 px-4 text-left font-semibold text-[#E6F1F5] text-sm bg-[#2DFFB7]/10 border-r border-white/5">
                    電話番号
                  </th>
                  <td className="py-4 px-4 text-[#E6F1F5]/90 text-sm">070-9114-6677</td>
                </tr>
                <tr className="border-b border-white/5">
                  <th className="py-4 px-4 text-left font-semibold text-[#E6F1F5] text-sm bg-[#2DFFB7]/10 border-r border-white/5">
                    メールアドレス
                  </th>
                  <td className="py-4 px-4 text-[#E6F1F5]/90 text-sm">
                    <a href="mailto:info@aiveilix.com" className="text-[#2DFFB7] hover:underline">info@aiveilix.com</a>
                  </td>
                </tr>
                <tr className="border-b border-white/5">
                  <th className="py-4 px-4 text-left font-semibold text-[#E6F1F5] text-sm bg-[#2DFFB7]/10 border-r border-white/5 align-top pt-4">
                    販売価格
                  </th>
                  <td className="py-4 px-4 text-[#E6F1F5]/90 text-sm">
                    <p>料金はサービス内の表示に従います。無料でご利用いただける場合があります。</p>
                    <p className="mt-2 text-[#E6F1F5]/60 text-xs">※ 価格は予告なく変更される場合があります。</p>
                  </td>
                </tr>
                <tr className="border-b border-white/5">
                  <th className="py-4 px-4 text-left font-semibold text-[#E6F1F5] text-sm bg-[#2DFFB7]/10 border-r border-white/5 align-top pt-4">
                    商品代金以外の必要料金
                  </th>
                  <td className="py-4 px-4 text-[#E6F1F5]/90 text-sm">
                    <ul className="list-disc pl-5 space-y-1">
                      <li>決済手数料：無料（当社負担）</li>
                      <li>送料：該当なし（デジタルサービス）</li>
                      <li>その他：なし</li>
                    </ul>
                    <p className="mt-2 text-[#E6F1F5]/60 text-xs">※ お客様が利用するAI・埋め込み等の第三者サービスの利用料は、各提供者にお問い合わせください。</p>
                  </td>
                </tr>
                <tr className="border-b border-white/5">
                  <th className="py-4 px-4 text-left font-semibold text-[#E6F1F5] text-sm bg-[#2DFFB7]/10 border-r border-white/5 align-top pt-4">
                    代金の支払方法
                  </th>
                  <td className="py-4 px-4 text-[#E6F1F5]/90 text-sm">
                    <p>有料プランがある場合、サービス内で案内する方法（クレジットカード等）に従います。決済方法の詳細はお問い合わせください。</p>
                  </td>
                </tr>
                <tr className="border-b border-white/5">
                  <th className="py-4 px-4 text-left font-semibold text-[#E6F1F5] text-sm bg-[#2DFFB7]/10 border-r border-white/5 align-top pt-4">
                    代金の支払時期
                  </th>
                  <td className="py-4 px-4 text-[#E6F1F5]/90 text-sm">
                    <p>有料プランがある場合、サービス内で案内する時期（例：月額の契約開始日等）に従います。</p>
                  </td>
                </tr>
                <tr className="border-b border-white/5">
                  <th className="py-4 px-4 text-left font-semibold text-[#E6F1F5] text-sm bg-[#2DFFB7]/10 border-r border-white/5 align-top pt-4">
                    サービス提供時期
                  </th>
                  <td className="py-4 px-4 text-[#E6F1F5]/90 text-sm">
                    <p>アカウント登録後、即時にご利用いただけます。インターネット接続が必要です。</p>
                  </td>
                </tr>
                <tr className="border-b border-white/5">
                  <th className="py-4 px-4 text-left font-semibold text-[#E6F1F5] text-sm bg-[#2DFFB7]/10 border-r border-white/5 align-top pt-4">
                    返品・交換・キャンセルについて
                  </th>
                  <td className="py-4 px-4 text-[#E6F1F5]/90 text-sm">
                    <h3 className="font-semibold text-[#E6F1F5] mt-0 mb-2">返金ポリシー</h3>
                    <p>本サービスはデジタルサービス（SaaS）のため、以下のとおりとします。</p>
                    <ul className="list-disc pl-5 mt-2 space-y-1">
                      <li><strong>返金：</strong>返金は行いません。デジタルサービスの性質上、ご利用開始後・お支払い後の返金はお受けしておりません。</li>
                      <li><strong>キャンセル：</strong>有料プランをご利用の場合は、サービス内の手順または info@aiveilix.com へのご連絡でキャンセルできます。</li>
                    </ul>
                    <p className="mt-2 text-[#E6F1F5]/60 text-xs">※ 返金に関する例外は法令で認められる場合を除き、ご対応しておりません。</p>
                  </td>
                </tr>
                <tr className="border-b border-white/5">
                  <th className="py-4 px-4 text-left font-semibold text-[#E6F1F5] text-sm bg-[#2DFFB7]/10 border-r border-white/5 align-top pt-4">
                    動作環境
                  </th>
                  <td className="py-4 px-4 text-[#E6F1F5]/90 text-sm">
                    <ul className="list-disc pl-5 space-y-1">
                      <li>インターネット接続</li>
                      <li>モダンなウェブブラウザ（Chrome、Firefox、Safari、Edgeの最新版）</li>
                      <li>JavaScript有効</li>
                    </ul>
                  </td>
                </tr>
                <tr className="border-b border-white/5">
                  <th className="py-4 px-4 text-left font-semibold text-[#E6F1F5] text-sm bg-[#2DFFB7]/10 border-r border-white/5 align-top pt-4">
                    サービス内容
                  </th>
                  <td className="py-4 px-4 text-[#E6F1F5]/90 text-sm">
                    <p>AIveilixは、お客様のドキュメントをアップロード・整理し、AIとチャットで対話できるドキュメント活用プラットフォームです。</p>
                    <ul className="list-disc pl-5 mt-2 space-y-1">
                      <li>ドキュメントをバケット単位で整理・管理</li>
                      <li>ファイルのアップロードと処理（PDF、画像等）</li>
                      <li>文書の意味検索（セマンティック検索）</li>
                      <li>ドキュメント内容に基づくAIチャット</li>
                      <li>APIキー・OAuthによるプログラムからの利用（オプション）</li>
                      <li>通知機能・会話履歴</li>
                    </ul>
                  </td>
                </tr>
                <tr className="border-b border-white/5">
                  <th className="py-4 px-4 text-left font-semibold text-[#E6F1F5] text-sm bg-[#2DFFB7]/10 border-r border-white/5">
                    個人情報の取り扱い
                  </th>
                  <td className="py-4 px-4 text-[#E6F1F5]/90 text-sm">
                    <p>
                      個人情報の取り扱いについては、<Link to="/privacy-policy" className="text-[#2DFFB7] hover:underline">プライバシーポリシー</Link>をご確認ください。
                    </p>
                  </td>
                </tr>
                <tr>
                  <th className="py-4 px-4 text-left font-semibold text-[#E6F1F5] text-sm bg-[#2DFFB7]/10 border-r border-white/5">
                    お問い合わせ
                  </th>
                  <td className="py-4 px-4 text-[#E6F1F5]/90 text-sm">
                    <p>ご不明な点やご質問がございましたら、以下の連絡先までお気軽にお問い合わせください。</p>
                    <p className="mt-2">
                      <strong>メール:</strong> <a href="mailto:info@aiveilix.com" className="text-[#2DFFB7] hover:underline">info@aiveilix.com</a><br />
                      <strong>電話:</strong> 070-9114-6677<br />
                      <strong>受付時間:</strong> 平日 9:00 - 18:00（日本時間）
                    </p>
                    <p className="mt-2 text-[#E6F1F5]/60 text-xs">※ お問い合わせへの返信には、通常1-2営業日かかります。</p>
                  </td>
                </tr>
              </tbody>
            </table>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[#E6F1F5] mb-4 pb-2 border-b border-[#2DFFB7]/30">免責事項</h2>
            <p>当社は、本サービスの提供に関して、以下の事項について責任を負いません。</p>
            <ul className="list-disc pl-6 mt-2 space-y-1">
              <li>第三者のAI・埋め込み等サービスの可用性・性能・正確性</li>
              <li>お客様がアップロードするデータの内容・正確性</li>
              <li>APIキー・認証情報の管理</li>
              <li>ネットワーク・端末・ソフトウェアの不具合</li>
              <li>本サービスの一時的な停止・メンテナンス</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[#E6F1F5] mb-4 pb-2 border-b border-[#2DFFB7]/30">その他の重要事項</h2>
            <ul className="list-disc pl-6 space-y-1">
              <li>本サービスの利用は、<Link to="/terms" className="text-[#2DFFB7] hover:underline">利用規約</Link>に従うものとします。</li>
              <li>本表記は日本の特定商取引法に基づくものです。海外からのご利用には当該国の法律が適用される場合があります。</li>
            </ul>
          </section>

          <div className="pt-8 mt-10 border-t border-white/10 text-center text-[#E6F1F5]/60 text-sm">
            <p>本表記は特定商取引法に基づき作成しています。最新情報は本ページでご確認ください。</p>
            <p className="mt-2">
              <Link to="/login" className="text-[#2DFFB7] hover:underline">Return to AIveilix</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
