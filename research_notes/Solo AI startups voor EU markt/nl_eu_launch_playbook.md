# NL/EU Launch Playbook for a Solo, Non-Programmer, Vibe-Coded AI Business (state as of late November 2026)

Research note scope: legal/admin (NL), consumer law, regulation (GDPR, EU AI Act, DSA), vibe-coding tool stack and security, payments, AI API costs, go-to-market in NL/EU, and success-rate data for indie/micro-SaaS. Research date: 24 November 2026.

Method caveats (read first):
- Several primary sources could not be fetched directly from this research environment (kvk.nl, dev.to and bigideasdb.com failed to resolve from the sandbox), so many figures come from search-result extracts of those pages or from secondary sources (banks, accountancy trade press, vendor blogs). Where a figure comes from a secondary/vendor/affiliate source, that is flagged.
- Many 2026 figures (AI model prices, tool prices, Wero migration timing, 2027 tax changes) are fast-moving. Treat all prices as "verify on vendor page on launch day".

---

## 1. Legal/admin setup in the Netherlands (eenmanszaak, KvK, BTW, KOR, OSS, tax deductions, BV)

### Takeaway
A solo founder should start as an eenmanszaak: KvK registration costs a one-off €85.15 (2026), the KOR exempts you from charging BTW up to €20,000 turnover/year, and the 2026 entrepreneur deductions are much smaller than before (zelfstandigenaftrek €1,200, startersaftrek €2,123, falling further in 2027). A BV only becomes tax-attractive at roughly €80k–€150k profit depending on whether profit is distributed, so it is not a day-one decision; selling digital services cross-border to EU consumers above €10,000/year triggers destination-country VAT (handled via OSS or a merchant of record).

### Cited Findings
**KvK registration**
- KvK one-off registration fee (inschrijfvergoeding) is €85.15 in 2026; KvK page updated 11 June 2026; adjusted annually for inflation — [KvK inschrijfvergoeding](https://www.kvk.nl/inschrijven/inschrijfvergoeding/); same amount on [Ondernemersplein (overheid)](https://ondernemersplein.overheid.nl/inschrijven-bij-kvk/); KvK tariff change announcement: [KvK pers: tarieven per 1 januari 2026](https://www.kvk.nl/pers/kvk-past-tarieven-aan-per-1-januari-2026/)
- Process: an online registration form for the eenmanszaak is filled in first, then an appointment at a KvK office to finalise (KvK pages "Inschrijven en afspraak maken eenmanszaak" and "zo vul je het online inschrijfformulier in") — [KvK: inschrijven en afspraak maken eenmanszaak](https://kvk.nl/inschrijven/inschrijven-en-afspraak-maken-eenmanszaak); [KvK: online inschrijfformulier eenmanszaak](https://www.kvk.nl/starten/eenmanszaak-zo-vul-je-het-online-inschrijfformulier-in/). (Detail of documents required/BTW-number issuance not retrieved — see Gaps.)

**Income tax deductions (inkomstenbelasting, eenmanszaak)**
- Zelfstandigenaftrek 2026: €1,200 (was €2,470 in 2025; falls to €900 in 2027; half for people past AOW age) — [MKB Servicedesk](https://www.mkbservicedesk.nl/nieuws/ondernemersnieuws/zelfstandigenaftrek-2024-verlaagd); [Rabobank](https://www.rabobank.nl/bedrijven/eigen-bedrijf-starten/belasting/zelfstandigenaftrek-en-startersaftrek-zo-zit-dat); [KvK belastingtarieven 2026](https://www.kvk.nl/geldzaken/belastingtarieven-2026/)
- Startersaftrek 2026: €2,123 (same as 2025), max 3 times in the first 5 years; combined max with zelfstandigenaftrek €3,323 in 2026 — [Rabobank](https://www.rabobank.nl/bedrijven/eigen-bedrijf-starten/belasting/zelfstandigenaftrek-en-startersaftrek-zo-zit-dat); [Knab](https://bieb.knab.nl/ondernemen/aftrekposten-voor-zzp-ers-bij-aangifte-inkomstenbelasting)
- UNCERTAIN for 2027: the cabinet announced (April 2026) that the startersaftrek should disappear from 2027; Prinsjesdag 2026 reporting suggests it may not disappear entirely — status in flux — [Rabobank: wetswijzigingen 2027 startende ondernemers](https://www.rabobank.nl/bedrijven/eigen-bedrijf-starten/wetswijzigingen-2027-startende-ondernemers); [KvK: belastingplannen 2027 eenmanszaak](https://www.kvk.nl/wetten-en-regels/plannen-voor-je-eenmanszaak-vof-maatschap-of-cv/)
- Note: these deductions generally depend on meeting the urencriterium (1,225 hours/year) — this is standard NL tax law but was not re-verified in this session (see Gaps).
- MKB-winstvrijstelling 2026: 12.7% — [Holdwise (secondary)](https://holdwise.nl/kennisbank/omslagpunt-bv-eenmanszaak-2026)

**BTW / KOR**
- KOR: available if the business is established in NL and turnover is ≤ €20,000 per calendar year; you then don't charge BTW (and can't reclaim input BTW) — [Belastingdienst KOR](https://belastingdienst.nl/kor); [KvK KOR](https://kvk.nl/geldzaken/kleineondernemersregeling-gebruiken/)
- The mandatory 3-year participation period has been dropped (you can deregister at any time) per MKB Servicedesk; older sources still mention the 3-year rule (likely outdated) — [MKB Servicedesk: KOR flexibeler](https://www.mkbservicedesk.nl/nieuws/ondernemersnieuws/kleineondernemersregeling-kor-flexibeler); conflicting older: [Shopify NL blog](https://www.shopify.com/nl/blog/kleineondernemersregeling)
- KOR registration has deadlines (must apply in advance) — [MKB Servicedesk: deadline KOR 2026](https://www.mkbservicedesk.nl/nieuws/ondernemersnieuws/deadline-kleineondernemersregeling-kor-2026-nadert)
- EU threshold €10,000: the combined total of intra-EU distance sales of goods + digital services (telecom/broadcast/electronic services) to consumers in other EU countries; above it you must charge the customer's country VAT rate from the first invoice crossing the threshold; OSS (One Stop Shop) is the optional single-return system at the Belastingdienst; a KOR-entrepreneur exceeding the EU threshold must apply normal VAT rules for those sales — [KvK: btw-regels e-commerce EU](https://kvk.nl/internationaal/btw-regels-voor-e-commerce-in-de-eu/)
- NEW in 2026: a simplified VAT regime for small entrepreneurs in e-commerce (implementation bill) was reportedly adopted by the Eerste Kamer on 6 October 2026; entry-into-force details not verified — [SRA-Nieuwsbank, Oct 2026](https://www.sra.nl/nieuws/121502/2026/10/vereenvoudigde-btw-regeling-voor-kleine-ondernemers-bij-e-commerce)
- EU-KOR concept (from 2025 internet consultation): national threshold stays at €20,000 — [internetconsultatie.nl](https://internetconsultatie.nl/kleineondernemersregeling2025/document/7572)

**Eenmanszaak vs BV (2026 parameters)**
- BV parameters 2026: gebruikelijk loon minimum €58,000; vennootschapsbelasting 19% on first €200,000 profit, 25.8% above; box 2: 24.5% up to €68,843, 31% above — [Holdwise (secondary)](https://holdwise.nl/kennisbank/omslagpunt-bv-eenmanszaak-2026); [KvK belastingtarieven 2026](https://www.kvk.nl/geldzaken/belastingtarieven-2026/)
- Break-even (omslagpunt) estimates conflict: ~€113k–€149k profit if all profit is distributed (one source), €128k–€147k (another); ~€95k if all distributed / ~€72k if retained in BV (another); "roughly €80k–€100k" (another). Spread is driven by distribution assumptions, salary level and BV running costs — [Holdwise](https://holdwise.nl/kennisbank/eenmanszaak-naar-bv-wanneer); [Norman Finance](https://norman.finance/nl/blog/eenmanszaak-of-bv); [Belasting-overzicht](https://belasting-overzicht.nl/bv-oprichten-belastingvoordeel); [DeZaak tool](https://www.dezaak.nl/tools/bv-of-eenmanszaak/); [Accountancy van Morgen: 10 redenen om naar BV](https://www.accountancyvanmorgen.nl/2026/03/27/10-redenen-om-een-ib-onderneming-om-te-zetten-naar-een-bv/)

### Inferences
- For a pre-revenue solo founder, an eenmanszaak + KOR is the cheapest, simplest structure. But: if the plan targets B2B SaaS buyers, the KOR's "no BTW on invoices" is neutral for consumers but B2B buyers can't reclaim BTW anyway on a KOR invoice (no BTW charged), so KOR is mostly a simplification, not a price advantage, in B2B. Consider not opting into KOR if you have large deductible startup costs (input BTW on laptop, software subscriptions) — since KOR forfeits input-VAT reclaim.
- The €10,000 EU-wide threshold is low: a B2C AI app selling to consumers across the EU will likely cross it quickly (e.g., ~42 subscribers at €20/month for a year). Plan from day one for either OSS registration or a merchant-of-record (Paddle etc., see §4).
- B2B sales to VAT-registered businesses in other EU countries are generally reverse-charged (customer accounts for VAT) — standard EU VAT rule, not re-verified in this session.
- A BV mainly makes sense for (a) profit consistently above ~€80k–€130k, or (b) liability ring-fencing (an eenmanszaak means personal liability for business debts). For AI products with potential liability (e.g., advice-like outputs), liability is the stronger early argument than tax; good T&Cs + professional liability insurance are the cheaper first step.
- Tax incentives are shrinking (zelfstandigenaftrek €2,470 → €1,200 → €900), so business plans should not lean on them.

### Gaps
- Could not fetch kvk.nl directly: exact list of documents for the KvK appointment, whether fully-online registration (without appointment) is available in 2026, home-address shielding rules, and how/when the BTW-identificatienummer is issued (normally automatically by Belastingdienst after KvK registration) — not verified.
- Urencriterium (1,225 hours) and its applicability for side-business starters not re-verified for 2026.
- Whether the October 2026 simplified small-business e-commerce VAT law has entered into force and what it changes for OSS/KOR not verified.
- Final 2027 status of startersaftrek unresolved.

---

## 2. Required legal documents and NL consumer law (T&Cs, privacy policy, herroepingsrecht, subscriptions, withdrawal button)

### Takeaway
Selling B2C online in NL means: give 14-day withdrawal info; for services (SaaS) you may start immediately only with the consumer's express consent, and they owe a pro-rata amount if they withdraw; since 19 June 2026 every online shop/app must offer an online "withdrawal function" (herroepingsknop); subscriptions concluded online must be cancellable online without obstacles, and tacit renewal is only allowed into an indefinite-term contract cancellable monthly. B2B contracts are largely outside these consumer rules.

### Cited Findings
- Withdrawal period for a service: up to and including 14 days after the contract is concluded/confirmed — [ACM: bedenktijd](https://www.acm.nl/nl/onderwerpen/verkoop-aan-consumenten/verkopen-aan-consumenten/bedenktijd/)
- Service contracts: no withdrawal right after full performance, but only if performance began with the consumer's express prior consent AND the consumer declared they lose their withdrawal right; if the consumer withdraws during the period, they owe an amount pro rata to what was already performed — [Ondernemersplein: consumentenrecht rechten en plichten als verkoper](https://ondernemersplein.overheid.nl/bedrijfsvoering/juridische-zaken/consumentenrecht-uw-rechten-en-plichten-als-verkoper/); [ACM bedenktijd](https://www.acm.nl/nl/verkoop-aan-consumenten/klantenservice/bedenktijd)
- Digital content (downloads/streaming): the withdrawal right can be waived if, before delivery starts, the consumer is asked to give up the cooling-off period (separate regime from services; qualification of a SaaS as "service" vs "digital content" matters) — [ACM bedenktijd](https://www.acm.nl/nl/onderwerpen/verkoop-aan-consumenten/verkopen-aan-consumenten/bedenktijd/)
- If the trader fails to inform the consumer about the withdrawal right, the cooling-off period is extended (up to 12 months) — [Rocket Lawyer NL](https://www.rocketlawyer.com/nl/nl/zakelijk/webshop-beheren/rechtwijzer/waar-moet-je-als-verkoper-op-letten-bij-het-herroepingsrecht)
- NEW: From 19 June 2026, online traders (webshops and apps) must offer a clear, accessible withdrawal/"ontbindings" function online (EU Directive 2023/2673); ACM called on traders to prepare — [ACM: herroepingsknop](https://www.acm.nl/nl/publicaties/acm-roept-online-retailers-op-zich-voor-te-bereiden-op-herroepingsknop); [Dutch IT Channel, 12 June 2026](https://www.dutchitchannel.nl/news/753332/webshops-vanaf-19-juni-wettelijk-verplicht-tot-herroepingsknop); [Taylor Wessing, April 2026](https://www.taylorwessing.com/en/insights-and-events/insights/2026/04/the-withdrawal-button)
- For subscriptions, an account area with a cancel button may suffice only if the label makes the statutory withdrawal right clear (not just "cancel subscription"), there's a genuine two-step confirmation, and the function remains available throughout the withdrawal period (iubenda interpretation, not an official source) — [iubenda NL](https://www.iubenda.com/nl/blog/de-nieuwe-online-herroepingsfunctie-wat-eu-richtlijn-2023-2673-betekent-voor-jouw-bedrijf/)
- Online-concluded subscriptions must be cancellable online; no barriers such as redirecting to phone cancellation or multiple click-throughs; applies to all subscriptions that can be concluded online — [ACM: online afgesloten abonnement moet je online kunnen opzeggen](https://www.acm.nl/nl/publicaties/acm-online-afgesloten-abonnement-moet-je-online-kunnen-opzeggen)
- ACM enforcement example: in 2026 nine telecom providers removed online-cancellation barriers after ACM action — [ACM](https://www.acm.nl/nl/publicaties/telecomaanbieders-maken-opzeggen-abonnementen-makkelijker-na-actie-acm)
- Tacit renewal: allowed only into an indefinite-term contract that can be cancelled with max one month's notice (exception: newspapers/magazines max 3 months); trial subscriptions to magazines may not be tacitly renewed — [Rijksoverheid: mogen abonnementen stilzwijgend verlengd worden](https://www.rijksoverheid.nl/vraag-en-antwoord/bescherming-van-consumenten/mogen-abonnementen-stilzwijgend-verlengd-worden); [Ondernemersplein: abonnement stilzwijgend verlengen](https://ondernemersplein.overheid.nl/wetten-en-regels/abonnement-stilzwijgend-verlengen/); [Consumentenbond](https://www.consumentenbond.nl/juridisch-advies/rechten-bij-aankoop/verlengen-en-opzeggen-van-abonnementen)
- Consumer withdrawal rules apply only B2C; B2B SaaS contracts are in principle not covered — [Ondernemersplein](https://ondernemersplein.overheid.nl/consumentenrecht-uw-rechten-en-plichten-als-verkoper/)

### Inferences
- Practical checkout pattern for a B2C AI subscription: (1) checkbox "I request immediate start and understand I lose my withdrawal right once the service is fully performed / I owe a pro-rata amount if I withdraw within 14 days"; (2) confirmation email with T&Cs + model withdrawal form; (3) visible "Contract herroepen / Withdraw from contract" function in the account area (since 19 June 2026) plus a separate "Abonnement opzeggen" button; (4) monthly plans, or annual plans that roll into monthly-cancellable after year one.
- Minimum document set: Algemene voorwaarden (T&Cs), privacy statement (GDPR Art. 13), cookie notice/consent (if non-essential cookies/analytics), withdrawal info + model form, and a DPA (verwerkersovereenkomst) to offer B2B customers. Generators (iubenda etc.) or a jurist; Thuiswinkel/branche-voorwaarden are a reference.
- B2B-only positioning (selling to ZZP'ers/MKB with KvK number) avoids most consumer-law obligations — a significant simplification for a solo founder.

### Gaps
- Exact Dutch statutory text/ACM guidance on how the withdrawal button applies to SaaS subscriptions specifically was not found from an official source (only iubenda's interpretation).
- Whether "fully performed" can ever apply to an ongoing monthly SaaS subscription (likely not, so pro-rata refund risk remains) — not confirmed from an official source.
- Legal requirements for T&Cs "ter hand stellen" (providing T&Cs before contract) not re-verified.

---

## 3. Regulation: GDPR, EU AI Act, DSA

### Takeaway
GDPR: a SaaS that processes customer data must sign DPAs with sub-processors (OpenAI/Anthropic/Supabase/etc.) and offer one to B2B customers; US transfers currently rely on the EU-US Data Privacy Framework, which survived the General Court in Sept 2025 but is under appeal at the CJEU (C-703/25 P) — so have SCCs/EU-hosted fallbacks. AI Act: the Digital Omnibus (Reg. (EU) 2026/1744, in force ~27 July 2026) postponed high-risk obligations to 2 Dec 2027 (Annex III) / 2 Aug 2028 (Annex I), but Article 50 transparency duties (chatbot disclosure, labelling AI-generated content) apply since 2 August 2026, with a grace period to 2 December 2026 for machine-readable marking of systems already on the market.

### Cited Findings
**AI Act / Digital Omnibus**
- Omnibus moved Annex III high-risk obligations to 2 December 2027 and Annex I (embedded products) to 2 August 2028; Regulation (EU) 2026/1744 — [Fontvera](https://fontvera.eu/intelligence/ai-act-omnibus-delay-failed); [Gibson Dunn](https://www.gibsondunn.com/eu-ai-act-omnibus-agreement-postponed-high-risk-deadlines-and-other-key-changes/); [AIActo](https://www.aiacto.eu/en/blog/digital-omnibus-ai-act-report-2027)
- Article 50 general transparency obligations were NOT postponed and apply since 2 August 2026 — [aiactblog.nl](https://www.aiactblog.nl/en/posts/article-50-transparency-deadline-2-august-2026); [Jones Walker](https://www.joneswalker.com/en/insights/blogs/ai-law-blog/yes-august-2-still-matters-the-eu-approved-a-high-risk-ai-delay-but-most-trans.html)
- Transitional relief only for Article 50(2) machine-readable marking: systems placed on the market before 2 August 2026 have until 2 December 2026 — [Fontvera](https://fontvera.eu/intelligence/ai-act-omnibus-delay-failed); [Dastra](https://www.dastra.eu/en/blog/simpler-safer-stricter-where-it-counts-inside-the-eu-ai-omnibus-deal/60025)
- Minor date conflicts across sources: political agreement 6 or 7 May 2026; OJ publication 24 July 2026, entry into force 27 July 2026 — [Fontvera](https://fontvera.eu/intelligence/ai-act-omnibus-delay-failed); [Dastra](https://www.dastra.eu/en/blog/simpler-safer-stricter-where-it-counts-inside-the-eu-ai-omnibus-deal/60025). All are law-firm/commentary sources; Official Journal text not fetched.
- Labelling AI content under the Omnibus (commentary) — [Hello Growth](https://hellogrowth.ai/en/blog/eu-ai-act-2026-omnibus-labelling-ai-content)

**GDPR / data transfers**
- EU General Court dismissed Latombe's annulment action against the EU-US DPF adequacy decision on 3 Sept 2025 (T-553/23); Latombe appealed on 31 Oct 2025 (C-703/25 P) with four pleas; DPF remains in force pending appeal — [EUR-Lex C/2025/6610](https://eur-lex.europa.eu/eli/C/2025/6610/oj/eng); [Digital Policy Alert](https://digitalpolicyalert.org/event/35459-latombe-filed-appeal-against-general-court-dismissal-of-challenge-to-european-unionunited-states-data-protection-framework-adequacy-decision-in-latombe-v-commission); [WilmerHale](https://www.wilmerhale.com/en/insights/blogs/wilmerhale-privacy-and-cybersecurity-law/20251201-european-court-of-justice-to-review-challenge-to-eu-us-data-privacy-framework); [Baker McKenzie, Jan 2026](https://connectontech.bakermckenzie.com/eu-us-data-privacy-framework-still-business-as-usual/); [Lawfare](https://www.lawfaremedia.org/article/the-european-commission-s-rejection-of-latombe)
- CJEU previously invalidated Safe Harbor and Privacy Shield, so the appeal is viewed as a real risk — [WilmerHale](https://www.wilmerhale.com/en/insights/blogs/wilmerhale-privacy-and-cybersecurity-law/20251201-european-court-of-justice-to-review-challenge-to-eu-us-data-privacy-framework)

### Inferences
- Article 50 duties most relevant to a solo AI wrapper (from the AI Act text as generally understood; not re-fetched in this session): (a) tell users they are interacting with an AI system unless obvious (chatbots); (b) providers of systems generating synthetic audio/image/video/text must mark outputs in a machine-readable way; (c) deployers of deepfakes and of AI-generated text published to inform the public on matters of public interest must disclose. Practical implementation: "AI-assistent" label in chat UI, footer/FAQ disclosure, metadata/watermark (C2PA etc.) on generated images, and rely on upstream model providers' watermarking where available.
- Most wrapper apps (writing assistants, summarisers, customer-support bots, marketing content tools) are NOT high-risk. Avoid Annex III areas for a solo launch: hiring/HR screening, credit scoring, education/exam assessment, access to essential services, biometric ID — these carry heavy obligations from Dec 2027.
- GDPR to-do list for a small SaaS: privacy statement; record of processing (verwerkingsregister); DPAs with every sub-processor (OpenAI, Anthropic, Mistral, Supabase, Vercel, Resend, Stripe/Mollie, analytics); a sub-processor list published on the site; offer a verwerkersovereenkomst to B2B customers; choose EU regions (Supabase EU region, Vercel EU functions, Mistral as EU provider or EU-hosted Azure/Bedrock/Vertex endpoints) to minimise transfer exposure; disable training on customer data via API terms; DPIA if processing sensitive data (health, HR). Because the DPF is under CJEU appeal, having SCCs in vendor DPAs is a prudent fallback.
- DSA: a pure SaaS tool with no user-to-user content sharing is generally not a hosting "online platform"; obligations become relevant only if users can publish content visible to others (then notice-and-action, contact point, T&C transparency). Micro/small enterprises are exempt from many platform-level duties. (Not verified in this session — see Gaps.)

### Gaps
- No primary Autoriteit Persoonsgegevens guidance retrieved on AI/chatbot use or verwerkersovereenkomst templates.
- DSA applicability to small SaaS not researched in this session (tool-call budget).
- No 2026 update found on the CJEU Latombe appeal (no AG opinion/hearing date located).
- Article 50 Code of Practice / Commission guidelines on labelling status in late 2026 not verified.

---

## 4. Vibe-coding tool stack in 2026: prices, fit for non-coders, security limitations

### Takeaway
Entry plans cluster around $20–25/month (Lovable Pro ~$25, Bolt Pro ~$25, Replit Core ~$20), but usage-based credits/tokens make real costs variable, with reports of $1,000+ spend on complex projects. Lovable is most often recommended for non-technical founders. The defining risk is security: the Lovable/Supabase RLS flaw (CVE-2025-48757, CVSS 9.3) exposed ~10% of scanned apps' databases; the anon key is meant to be public — missing Row Level Security policies and leaked service-role keys are the real problems.

### Cited Findings
**Pricing (secondary/affiliate sources; verify on vendor pages)**
- Lovable Pro and Bolt Pro ~$25/month; Replit Core ~$20/month; Bolt yearly billing saves up to 28%, Replit up to 10% — [Taskade comparison](https://www.taskade.com/blog/lovable-bolt-replit-base44); [AI for Mortals](https://www.aiformortals.co/blog/lovable-vs-replit-vs-bolt); [Productos.dev](https://productos.dev/blog/ai-app-builder-pricing-compared)
- Free tiers: Lovable 5 credits/day capped at 30/month; Bolt 1M tokens/month (300K daily limit, Bolt branding, hosting up to 333K requests); Replit Starter free with daily Agent credits, one published app, "Lite" builds — [Mythex](https://mythex.ai/guides/lovable-vs-bolt-vs-replit); [Creatr](https://getcreatr.com/ai-app-builder-pricing-comparison-2026)
- Billing models: Lovable credits per message (Build mode priced by task size); Bolt by tokens (tokens roll over on Pro); Replit effort-based credits — [AI for Mortals](https://www.aiformortals.co/blog/lovable-vs-replit-vs-bolt); [Superapp](https://superapp.dev/blog/lovable-vs-bolt-vs-replit-vs-v0-2026)
- Cost risk: "heavy users report spending $1,000+ on complex projects" on Bolt token pricing; Replit compute-based hosting costs can exceed development costs; bill spikes a common Replit complaint — [Taskade](https://www.taskade.com/blog/lovable-bolt-replit-base44); [AI Tools Directory](https://www.aitools-directory.com/bolt-new-vs-lovable-vs-replit-non-coders/)
- Fit: Lovable aimed at non-technical founders shipping MVPs; Bolt flagged as "high lock-in risk" by one guide — [AI Tools Directory](https://www.aitools-directory.com/bolt-new-vs-lovable-vs-replit-non-coders/); [Mythex](https://mythex.ai/guides/lovable-vs-bolt-vs-replit)
- A November 2026 cost breakdown for Lovable, Bolt, Replit, v0, Base44 and Cursor exists but could not be fetched — [DEV: what they actually cost in November 2026](https://dev.to/vibecost/what-lovable-bolt-replit-v0-base44-and-cursor-actually-cost-in-november-2026-45ch)

**Security of vibe-coded apps**
- CVE-2025-48757: insufficient Supabase Row-Level Security policies in Lovable-generated sites (through 2025-04-15) allowed unauthenticated attackers to read/write arbitrary tables; CVSS 9.3 (some vendors list 9.8) — [Tenable CVE entry](https://www.tenable.com/cve/CVE-2025-48757); [PT dbugs](https://dbugs.ptsecurity.com/vulnerability/PT-2025-23236); [SentinelOne](https://www.sentinelone.com/vulnerability-database/cve-2025-48757/)
- Scan: 170 of 1,645 Lovable apps (10.3%) had exposed databases (303 vulnerable endpoints) — [Superblocks](https://www.superblocks.com/blog/lovable-vulnerabilities) (figure widely repeated; original researcher post not fetched)
- Supabase anon keys are designed to be public; security is enforced by RLS; service-role keys bypass RLS and must never be in client code — [Superblocks](https://www.superblocks.com/blog/lovable-rls-breach); [DEV: scanning production Lovable apps](https://dev.to/jacefromhi/ive-been-scanning-production-lovable-apps-for-security-issues-the-same-5-problems-show-up-every-50gp)
- 2026 reporting: Lovable left thousands of projects exposed for 48 days (TNW); Lovable user-data exposure (Sept 2026 reporting) — [The Next Web](https://thenextweb.com/news/lovable-vibe-coding-security-crisis-exposed); [Cybersecurity News](https://cybersecuritynews.com/lovable-security-vulnerability/)
- "Moltbook" vibe-coded social network breached within 3 days of launch: 1.5M API tokens and 35,000 emails exposed via Supabase database without RLS — [The Next Web](https://thenextweb.com/news/lovable-vibe-coding-security-crisis-exposed) (as summarised in search results)
- Wiz guidance on common risks in vibe-coded apps (vendor research, co-curated with Lovable) — [Wiz](https://wiz.io/blog/common-security-risks-in-vibe-coded-apps)
- Unverified claim: Q1 2026 assessment of 200+ vibe-coded apps found 91.5% with at least one AI-hallucination-traceable vulnerability (methodology unknown) — [Superblocks/search extract](https://www.superblocks.com/blog/lovable-vulnerabilities)

### Inferences
- Recommended non-coder stack: Lovable (or Bolt) for the first MVP (UI + Supabase backend) → export to GitHub → continue in Cursor or Claude Code once the product needs custom logic. Supabase (EU region) for auth/DB, Vercel or Netlify for hosting, Resend for transactional email, Stripe or Mollie/Paddle for payments.
- Budget assumption for month 1–3: ~€25–€75/month for builder credits + €0–€25 Supabase + €0–€20 hosting + domain; reserve a buffer for credit overruns (keep prompts small, iterate in plan/chat mode before build mode).
- Security mitigation checklist for non-coders: (1) enable RLS on every Supabase table and write policies per user_id; run Supabase's security advisor; (2) never put service-role keys or AI API keys in front-end code — call AI APIs via server/edge functions; (3) rate-limit and cap spend on AI endpoints (prevent "denial of wallet"); (4) run an automated scanner and ask the AI tool to do a security review before launch; (5) consider a paid one-off pentest/code review (freelancer) before taking payments or personal data; (6) GDPR: a breach of personal data must be reported to the AP within 72 hours (standard GDPR rule).

### Gaps
- Official current prices for v0, Cursor, Claude Code, Windsurf, Supabase Pro, Vercel Pro, Resend were not verified this session (search returned nothing reliable for Supabase/Vercel/Resend). Commonly cited historical values (Supabase Pro $25/mo, Vercel Pro $20/user/mo, Cursor Pro $20/mo) are from training knowledge only and must be re-checked.
- No independent peer-reviewed study on vibe-coded app vulnerability rates found.

---

## 5. Payments: Stripe vs Mollie vs Paddle/Lemon Squeezy (MoR), iDEAL/Wero

### Takeaway
For NL consumers iDEAL (now co-branded "iDEAL | Wero") is essential and cheap (≈€0.29–€0.32 per transaction at Stripe/Mollie); the iDEAL→Wero migration runs from late 2026 to end-2027 with EPI promising current price levels until 31 Dec 2028. Merchants of record (Paddle, Lemon Squeezy ~5% + $0.50; Stripe Managed Payments ~3.5% on top of processing) cost 3–4x more but take over EU VAT/OSS compliance — often worth it for a solo B2C seller across the EU.

### Cited Findings
- Mollie: €0.32 per successful iDEAL | Wero transaction, no monthly fees; Wero within Belgium €0.39 — [Overonlinebetalen](https://overonlinebetalen.nl/mollie/); [Betaalprovidervergelijken](https://betaalprovidervergelijken.nl/betaalproviders/mollie/); [Bedrijfssoftwaregids](https://bedrijfssoftwaregids.nl/blog/mollie-kosten-2026/)
- Stripe iDEAL: €0.29 per transaction (comparison sites) — [Webwinkelsucces](https://www.webwinkelsucces.nl/payment-providers-vergelijken/)
- iDEAL→Wero migration: starts late 2026, completion end 2027; EPI pledge to keep prices at current iDEAL level until 31 December 2028, though Mollie says prices/contracts may be adjusted in the second phase; one source expects a future shift to percentage pricing (conflicting) — [Mijnevent](https://mijnevent.nl/nl/blog/van-ideal-naar-wero-wat-verandert-er-voor-je-ticketverkoop); [Memo ICT](https://memo-ict.nl/en/blog/ideal-becomes-wero-webshop); [Reservatie.app](https://reservatie.app/blog/ideal-wero-bancontact-wat-verandert-er)
- Stripe EEA card pricing has two tiers (standard vs premium EEA cards); exact 2026 % not verified — [Stripe support: EEA pricing updates](https://support.stripe.com/questions/pricing-updates-for-businesses-based-in-the-european-economic-area-(eea)); [Stripe NL pricing](https://stripe.com/de-nl/pricing)
- Paddle and Lemon Squeezy headline fee ≈ 5% + $0.50 per transaction; Lemon Squeezy reportedly +1.5% on international sales — [Dodo Payments](https://dodopayments.com/blogs/paddle-vs-lemon-squeezy/); [Rework](https://resources.rework.com/tools/billing-revenue/best-paddle-alternatives)
- Stripe Managed Payments (MoR built on Lemon Squeezy tech, acquired 2024): +3.5% per successful transaction on top of processing (>6% all-in by one estimate), indirect tax in 80+ countries; Lemon Squeezy moving customers to Managed Payments (Jan 2026), in Stripe API by April 2026; reports of Lemon Squeezy sign-up restrictions — [Rework](https://resources.rework.com/tools/billing-revenue/paddle-vs-lemon-squeezy); [Dodo Payments](https://dodopayments.com/blogs/paddle-vs-lemon-squeezy/)
- Stripe + Stripe Tax alternative: ~0.5% for Stripe Tax on top of processing, but you remain responsible for filings — [alexcloudstar](https://alexcloudstar.com/md/blog/merchant-of-record-indie-saas-2026/)

### Inferences
- Worked example, €20/month subscription: Mollie/Stripe iDEAL ≈ €0.29–€0.32 (≈1.5%); MoR ≈ 5% + $0.50 ≈ €1.45 (≈7%). At 100 subscribers that's ~€30/month vs ~€145/month — the ~€115/month difference buys VAT compliance across 27 countries, invoicing, and chargeback handling.
- Decision rule: NL-only or B2B (reverse charge) → Mollie or Stripe directly (Mollie strong on iDEAL/Bancontact/SEPA direct debit for recurring). EU-wide B2C → Paddle (most independent MoR) or Stripe Managed Payments. Avoid starting new on Lemon Squeezy given its transition into Stripe.
- Recurring payments via iDEAL require a first iDEAL payment followed by SEPA direct-debit mandates (standard mechanism at Mollie/Stripe; not re-verified).

### Gaps
- Exact Stripe 2026 EEA card rates and Mollie card rates not verified from vendor pages.
- Paddle's official 2026 fee page not fetched; Wero adoption/user numbers in NL not found.

---

## 6. AI API costs and EU-hosted options; cost per user for a wrapper app

### Takeaway
Small/fast models are now very cheap: GPT-5 mini ~$0.25/$2.00 per million input/output tokens, Claude Haiku 5.5 ~$0.10/$0.50, Claude Sonnet 5.5 ~$2/$10, Mistral Medium 3.5 ~$1.50/$7.50 (third-party aggregators, Oct–Nov 2026). A typical chat-wrapper user costs well under €1/month on small models and ~€2–€3/month on mid-tier models, so pricing at €10–€30/month leaves ample margin if usage caps exist.

### Cited Findings
- GPT-5 mini: $0.25/M input, $2.00/M output (cached input $0.025, batch $0.125/$1.00), stated as current Nov 2026 — [OpenRouter](https://openrouter.ai/openai/gpt-5-mini); [PricePerToken](https://pricepertoken.com/pricing-page/model/openai-gpt-5-mini); [Artificial Analysis](https://artificialanalysis.ai/models/gpt-5-mini)
- Claude Haiku 5.5: $0.10/M input, $0.50/M output for prompts ≤100K tokens (higher for longer); Claude Sonnet 5.5: $2/M input, $10/M output — [Reflekt Lab](https://reflektlab.ai/blog/claude-api-pricing/); [aipricing.guru](https://www.aipricing.guru/anthropic-pricing/); [aifreeapi (Oct 2026)](https://www.aifreeapi.com/en/posts/claude-api-pricing-per-million-tokens)
- Anthropic top-tier pricing conflicts between sources (Fable listed at $8/$40 vs $10/$50) — [infro.io](https://infro.io/blog/claude-api-pricing-2026); [growthcab](https://www.growthcab.com/claude-opus-api-pricing)
- Mistral Medium 3.5: $1.50/M input, $7.50/M output; older Mistral Medium 3: $0.40/$2.00; Mistral Large 4 figures conflict ($0.68/$2.09 launch promo vs $1.36/$4.18 list vs $0.70/$2.10) — [OpenRouter Mistral Medium 3.5](https://openrouter.ai/mistralai/mistral-medium-3-5); [BenchLM (Nov 2026)](https://benchlm.ai/mistral/api-pricing); [Puter (Oct 2026)](https://developer.puter.com/tutorials/mistral-api-pricing/)
- Unconfirmed: a "GPT-6 Luna" at $0.10/$0.50 reported by one aggregator — not verified against OpenAI — (search extract; treat as unverified)

### Inferences
- Cost-per-user model (assumption: 300 messages/month, ~2,000 input + 500 output tokens each = 0.6M in / 0.15M out per month): Claude Haiku 5.5 ≈ $0.14; GPT-5 mini ≈ $0.45; Mistral Medium 3.5 ≈ $2.03; Claude Sonnet 5.5 ≈ $2.70 per user per month. Heavy users (RAG over documents, long contexts, agents) can be 5–20x higher → implement usage caps/fair-use, prompt caching, and route easy tasks to small models.
- EU data-residency options: Mistral (French company, EU hosting) is the simplest "EU-first" story for Dutch B2B buyers; alternatives are EU-region endpoints of hyperscalers (Azure OpenAI EU, AWS Bedrock Frankfurt/Paris, Google Vertex EU) — availability and pricing per region not verified this session.
- Prices are from aggregators; vendor pricing pages must be checked on launch day.

### Gaps
- Official vendor pricing pages (openai.com, anthropic.com, mistral.ai) not fetched.
- EU-region availability/pricing for OpenAI/Anthropic models via Azure/Bedrock/Vertex not verified; no data on real-world average tokens per user for wrapper apps.

---

## 7. Go-to-market in NL/EU: market size, channels, ad costs, language strategy

### Takeaway
NL is a dense, digitally mature market: 2.64M registered establishments at KvK (end Q3 2026), ~1.8M ZZP'ers (69% of establishments), and starters up 15% y/y in Q3 2026. Meta CPMs in NL appear roughly half of US levels (directional data). Dutch-language niches are smaller but less competitive than English; expansion to Flanders (same language) and DACH is the natural next step.

### Cited Findings
- 2,637,902 establishments registered in the KvK Handelsregister at end Q3 2026; 62,395 starting establishments in Q3 2026 (+15% y/y); 82% of starters are ZZP'ers; ZZP'ers = 69% of all establishments; 36,610 stoppers in Q3 (−4.3%) — [KvK cijfers en trends](https://www.kvk.nl/cijfers-en-trends/actuele-trends-en-inzichten-zo-verandert-het-bedrijfsleven/); [KvK pers: 82% starters zzp](https://www.kvk.nl/pers/82-procent-van-de-starters-is-zzper-ondanks-aanpak-schijnzelfstandigheid/)
- ZZP count: 1,793,380 on 31 March 2026 (KvK Zzp-monitor); ~1.8M end June 2026 (Rabobank) — [KvK Zzp-monitor](https://www.kvk.nl/cijfers-en-trends/kvk-zzp-monitor-zo-ontwikkelt-het-aantal-zzpers-in-nederland/); [Rabobank: meer starters 2026](https://www.rabobank.nl/bedrijven/eigen-bedrijf-starten/meer-starters-2026)
- 2025 context: business population grew <1% (historically low), ZZP starters −13%, stoppers +19% — [KvK pers](https://kvk.nl/pers/historisch-lage-groei-in-nederlandse-bedrijvenpopulatie-1-erbij-in-2025); [Accountant.nl](https://www.accountant.nl/nieuws/2026/1/kvk-groei-aantal-bedrijven-in-tien-jaar-niet-zo-laag-veel-zzpers-gestopt/)
- Social media: 14.6M Dutch people use ≥1 social platform (avg 4.5 platforms); LinkedIn ranked 5th most used in NL — [Metricool](https://metricool.com/nl/meest-gebruikte-social-media-nederland/); DataReportal-based figure 14.8M — [Searchlab](https://searchlab.nl/statistieken/social-media-statistieken-nederland-2026)
- TikTok NL: 4.2M active users (+18% vs 2025), ~24% of Dutch internet users (page has inconsistencies) — [Searchlab TikTok 2026](https://searchlab.nl/statistieken/tiktok-statistieken-2026)
- KvK guidance on which audiences are reachable on which social channels — [KvK EN](https://kvk.nl/en/marketing/which-audiences-can-i-reach-on-which-social-media)
- Meta CPM: NL Facebook CPM est. $7.00–$9.50, Instagram $9–$12 (Adligator 2026); NL ~31% below global benchmark (14.2 vs 20.6) on one dashboard; US the highest at $16.08 in an e-commerce dataset; general FB benchmark $8–$11 — [Adligator](https://adligator.com/blog/meta-ads-cpm-by-country-benchmarks); [Superads NL](https://www.superads.ai/facebook-ads-costs/cpm-cost-per-mille/netherlands); [Lebesgue](https://lebesgue.io/?p=305); [Influee](https://influee.co/nl/blog/good-cpm-facebook-ads). All vendor datasets with undisclosed methods → directional only.

### Inferences
- Primary NL target segments for a solo AI tool: ZZP'ers (≈1.8M) and micro-MKB — B2B (avoids consumer-law complexity; reverse charge in EU). Typical NL-specific wedges: Dutch-language compliance/admin tasks (offertes, facturen, BTW-aangifte prep, Wet DBA/zzp documentation, Dutch-language customer service, tenders), where US tools are weak in Dutch language and local rules.
- Channels: LinkedIn (founder-led content in Dutch) for B2B; Dutch SEO on long-tail "how to" queries (smaller volumes, less competition than English — not quantified, see Gaps); TikTok/Instagram for B2C; communities (ZZP-Nederland, branche-verenigingen), and marketplaces/directories (Product Hunt, AI tool directories, app stores).
- Paid ads: with NL CPMs ≈ half US, test budgets of a few hundred euros give meaningful signal; but small total audience means faster saturation.
- Expansion order: Flanders (Dutch, same language; Bancontact payments) → DACH (largest EU market, German localisation; strong privacy expectations favour EU hosting) → France/others. AI translation makes multi-language landing pages cheap, but support/legal docs need proper localisation.

### Gaps
- No reliable 2026 LinkedIn NL user count found (Statista/DataReportal paywalled/not retrieved).
- No quantitative data found on Dutch vs English SEO keyword difficulty.
- No data on DACH/Belgium market sizes or EU multi-language conversion benchmarks retrieved.

---

## 8. Success-rate data for indie/micro-SaaS

### Takeaway
Realistic expectations are sobering: in the most-cited 2026 dataset (3,787 revenue-generating indie SaaS on TrustMRR), median MRR is ~$145 and only ~6.1% reach ≥$10K MRR; for AI products the median is ~$203 MRR and ~25% cross $1K MRR. These are survivorship-biased toward products that already have revenue, so true odds from idea stage are lower.

### Cited Findings
- 3,787 revenue-generating indie SaaS businesses: median ~$145 MRR; ~6.1% at ≥$10K MRR — [BigIdeasDB: State of Indie SaaS Revenue 2026](https://bigideasdb.com/state-of-indie-saas-revenue-2026); repeated by [mean.ceo](https://blog.mean.ceo/micro-saas-revenue-statistics/)
- AI subset: median AI company $203 MRR; 25.3% crossed $1K MRR — [mean.ceo](https://blog.mean.ceo/micro-saas-revenue-statistics/) (secondary, citing TrustMRR-based analysis)
- Conflicting $1K estimates: ~18% reach $1K–$5K MRR (one source); ~30% of solo SaaS never cross $1K (another); "70% never clear $1K" (2025 analysis of 1,000 products, different sample) — [Boring Riches](https://boringriches.com/guides/saas-business-revenue-benchmarks/); [BuildMVPFast](https://www.buildmvpfast.com/blog/saas-only-way-out-indie-hacker-dream-desperation-2026); [SoftwareSeni](https://www.softwareseni.com/solo-founder-saas-metrics-from-0-to-10k-mrr-in-6-months-with-realistic-timelines/) — unreconciled
- Unreliable: "54% of Stripe-verified indie products make zero revenue" appears only in a blog's schema markup without methodology — do not rely on it — (search extract)
- MicroConf State of Independent SaaS: latest edition found is 2024 (surveys hundreds of bootstrapped founders on revenue, team, churn; sample reported as 700 or 469 — conflicting); 2020 edition: 88.27% of respondents had not raised funding — [MicroConf SOIS 2024](https://microconf.com/saas-this-year); [Startups For the Rest of Us ep. 721](https://www.startupsfortherestofus.com/episodes/episode-721-7-key-takeaways-from-the-2024-state-of-independent-saas-report); [MicroConf 2020 report (issuu)](https://issuu.com/microconf/docs/2020_state_of_indie_saas_report)
- Bootstrapped B2B SaaS median growth ~15–25%/year; ~85% at/near breakeven or profitable (SaaS Capital via secondary source) — [BigIdeasDB](https://bigideasdb.com/state-of-indie-saas-revenue-2026)
- Freemius 2025 State of Micro-SaaS (AI, pricing, community) — [Freemius](https://freemius.com/blog/state-of-micro-saas-2025/)

### Inferences
- Planning baseline for each idea: assume the median outcome (<$250 MRR) is the most likely result; treat $1K MRR as a realistic 6–12-month goal for a well-executed niche B2B tool, and $10K MRR as a top-~5–10% outcome among products that get any revenue.
- Because low costs (vibe coding + cheap APIs) make experiments cheap, the rational strategy is a portfolio of fast, cheap validation tests (landing page + waitlist + pre-sales) and killing ideas that don't reach early paid signal within ~4–8 weeks.
- Survivorship bias: TrustMRR lists only products that connect revenue — idea-stage failure rates are not captured.

### Gaps
- Could not access TrustMRR raw data or the full BigIdeasDB report (host blocked); distribution buckets beyond median/6.1%/25.3% not verified.
- No primary data from Stripe (e.g., Stripe Atlas/indie reports) or Indie Hackers on % reaching $1K/$10K.
- No reliable data on typical time-to-profitability or time-to-$1K/$10K MRR (only blog anecdotes like "6 months" claims, which are not credible as benchmarks).
- MicroConf SOIS 2025/2026 editions (if any) not found; revenue distribution from the 2024 report not extracted.
