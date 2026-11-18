from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.services.models import ServiceCategory, Service

CATEGORIES_SERVICES_DATA = [
    {
        "category_name": "Business Management & CRM",
        "icon": "📊",
        "description": "Streamline real estate operations, lead tracking, inventory management, and channel partner networks.",
        "services": [
            {
                "name": "Real Estate CRM",
                "icon": "💻",
                "short_description": "Comprehensive Customer Relationship Management tailored specifically for real estate agencies and independent brokers.",
                "detailed_description": "Our Real Estate CRM provides a complete suite of digital tools to manage client interactions, property listings, and pipeline workflows. Built for real estate professionals, it centralizes communications, tracks property inquiries from start to finish, and provides actionable analytics to increase deal closure rates.",
                "benefits": ["Centralized lead repository", "Automated pipeline stage tracking", "Seamless communication logs", "Mobile and desktop synchronization"],
                "whats_included": ["Lead capturing & segmentation", "Property matching engine", "Activity dashboard & reports", "Client interaction timeline"],
                "how_it_works": ["1. Submit requirement & select plan", "2. Onboarding & data migration setup", "3. Team account setup & training", "4. Launch CRM and track operations"],
                "required_documents": ["Business Registration / Agent ID", "Current lead list (CSV/Excel)", "Team member details"],
                "faqs": [
                    {"question": "Can I import existing lead data?", "answer": "Yes, our team supports bulk data import from Excel, CSV, or third-party CRM exports."},
                    {"question": "Is training provided for my sales team?", "answer": "Yes, live onboarding and step-by-step video tutorials are included."}
                ]
            },
            {
                "name": "Lead Management",
                "icon": "🎯",
                "short_description": "Capture, score, assign, and track property buyer and tenant leads across multiple acquiring channels.",
                "detailed_description": "Efficiently organize incoming leads from your website, social media, portals, and field events into a single intelligent lead management system. Prevent lead leakage and ensure rapid response times through automated lead assignment rules.",
                "benefits": ["Zero lead leakage", "Instant lead distribution rules", "Real-time activity tracking", "Channel ROI measurement"],
                "whats_included": ["Multi-channel lead ingestion", "Custom lead scoring matrix", "Agent round-robin assignment", "Lead status audit logs"],
                "how_it_works": ["1. Connect lead capture sources", "2. Configure assignment rules", "3. Monitor team response times", "4. Optimize conversion channels"],
                "required_documents": ["Lead sources & portal credentials", "Team hierarchy & assignment rules"],
                "faqs": [
                    {"question": "How quickly are leads assigned?", "answer": "Leads are routed instantly upon submission via real-time triggers."}
                ]
            },
            {
                "name": "Customer Database Management",
                "icon": "📁",
                "short_description": "Securely organize, structure, and sanitize client contact lists, buyer preferences, and historical transactions.",
                "detailed_description": "Maintain clean, compliant, and indexed customer records. Filter prospects by budget, preferred locality, property type, and investment timeline for hyper-targeted outreach campaigns.",
                "benefits": ["Enhanced data security & compliance", "Instant attribute search", "Duplicate contact cleanup", "Lifetime customer valuation"],
                "whats_included": ["Database cleaning & deduplication", "Tagging & custom attributes", "Role-based access security", "Automated backup schedules"],
                "how_it_works": ["1. Data audit & intake", "2. Cleansing & deduplication", "3. Custom field structuring", "4. Secure database deployment"],
                "required_documents": ["Existing database records", "Security access protocol requirements"],
                "faqs": [
                    {"question": "Is client data kept confidential?", "answer": "Absolute confidentiality is guaranteed with strict encryption and contract NDAs."}
                ]
            },
            {
                "name": "Property Inventory Management",
                "icon": "🏢",
                "short_description": "Real-time tracking of available units, pricing updates, unit features, and listing statuses.",
                "detailed_description": "Manage residential and commercial property inventories seamlessly across your sales force. Track unit availability, floor plans, pricing tiers, and hold statuses in real time.",
                "benefits": ["Prevent double booking", "Instant unit availability checks", "Dynamic price list updates", "Detailed unit feature tags"],
                "whats_included": ["Unit status matrix", "Floor plan attachment storage", "Hold and booking locks", "Inventory export reports"],
                "how_it_works": ["1. Input project/property catalogue", "2. Set pricing & unit attributes", "3. Grant sales team access", "4. Manage live inventory updates"],
                "required_documents": ["Property master list", "Pricing & layout documentation"],
                "faqs": [
                    {"question": "Can multiple agents update inventory simultaneously?", "answer": "Yes, concurrency locks prevent multi-booking conflicts."}
                ]
            },
            {
                "name": "Site Visit Management",
                "icon": "🚗",
                "short_description": "Schedule, confirm, and collect feedback for customer property site visits and project tours.",
                "detailed_description": "Streamline customer site visits with automated SMS/WhatsApp reminders, driver/executive routing, and digital site visit feedback forms to measure buyer interest.",
                "benefits": ["Reduced visit no-show rates", "Automated customer reminders", "Executive check-in tracking", "Instant buyer feedback collection"],
                "whats_included": ["Calendar scheduling portal", "SMS/WhatsApp Visit Pass dispatch", "Site visit feedback form", "Executive location check-in"],
                "how_it_works": ["1. Schedule visit with customer", "2. Automated visit confirmation sent", "3. Executive conducts property tour", "4. Feedback logged in portal"],
                "required_documents": ["Customer contact details", "Project visit location details"],
                "faqs": [
                    {"question": "Does it support WhatsApp visit passes?", "answer": "Yes, automated WhatsApp visit passes with location maps are sent to clients."}
                ]
            },
            {
                "name": "Follow-up & Reminder Automation",
                "icon": "⏰",
                "short_description": "Automated workflow notifications, call reminders, and drip follow-up sequences for prospective buyers.",
                "detailed_description": "Never miss a prospective buyer follow-up. Set up smart automated reminders, scheduled tasks, and multi-channel drip sequences via WhatsApp, email, and SMS.",
                "benefits": ["Higher lead conversion rate", "Automated daily task lists", "Multi-stage drip campaigns", "Consistent client touchpoints"],
                "whats_included": ["Custom reminder rules", "Drip messaging engine", "Daily agent call lists", "Missed task escalations"],
                "how_it_works": ["1. Define client follow-up stages", "2. Set automated trigger rules", "3. Receive daily task alerts", "4. Execute timely client outreach"],
                "required_documents": ["Follow-up strategy guidelines", "Communication templates"],
                "faqs": [
                    {"question": "Can agents set custom follow-up dates?", "answer": "Yes, agents can set custom notes and exact follow-up dates per prospect."}
                ]
            },
            {
                "name": "Deal / Transaction Management",
                "icon": "📑",
                "short_description": "End-to-end tracking of real estate sale and rental transactions from booking to possession.",
                "detailed_description": "Track property deal milestones including booking token payment, agreement execution, bank loan sanction, registration, and final possession handover.",
                "benefits": ["Clear deal milestone visibility", "Document checklist tracking", "Timely payment milestone alerts", "Reduced deal cancellation rate"],
                "whats_included": ["Deal milestone tracker", "Payment schedule manager", "Document vault per transaction", "Closing checklist"],
                "how_it_works": ["1. Create deal entry upon booking", "2. Upload transaction documents", "3. Track stage progress & payments", "4. Complete handover milestone"],
                "required_documents": ["Booking form / Token receipt", "Customer & Seller identification"],
                "faqs": [
                    {"question": "Can buyers view deal status online?", "answer": "Admins can issue client access links for progress tracking."}
                ]
            },
            {
                "name": "Broker & Channel Partner Management",
                "icon": "🤝",
                "short_description": "Organize external channel partners, track CP registrations, property visits, and deal credit.",
                "detailed_description": "Empower your network of real estate brokers and channel partners. Manage CP registrations, tag client introductions, track project site visits, and ensure transparent deal attribution.",
                "benefits": ["Transparent deal attribution", "Stronger channel partner trust", "Streamlined CP onboarding", "Higher partner performance"],
                "whats_included": ["CP registration portal", "Client tagging & protection rules", "CP site visit tracking", "Performance leaderboards"],
                "how_it_works": ["1. Register channel partner firm", "2. CP tags potential buyer", "3. Conduct site visit & deal closing", "4. Attribute deal credit"],
                "required_documents": ["CP RERA Registration", "Firm PAN & GST details"],
                "faqs": [
                    {"question": "How long is a client tag valid for a broker?", "answer": "Default client tagging period is 60-90 days as per agreed policy."}
                ]
            },
            {
                "name": "Commission Tracking",
                "icon": "💵",
                "short_description": "Accurate calculation and tracking of brokerage commissions, payouts, TDS deductions, and slabs.",
                "detailed_description": "Automate commission calculations for internal sales agents and external brokers. Calculate tier-based incentives, tax deductions (TDS), and maintain clear payout ledger history.",
                "benefits": ["Automated commission math", "Zero payout disputes", "Tax deduction compliance", "Transparent agent earnings"],
                "whats_included": ["Commission slab builder", "TDS & GST calculation engine", "Agent payout ledger", "Payout approval workflow"],
                "how_it_works": ["1. Set commission slab structure", "2. Link deal closure record", "3. System calculates net commission", "4. Admin approves payout"],
                "required_documents": ["Commission policy structure", "Agent/Broker bank account details"],
                "faqs": [
                    {"question": "Does it calculate TDS automatically?", "answer": "Yes, applicable TDS under Sec 194H is calculated prior to payout release."}
                ]
            },
            {
                "name": "Team & Employee Management",
                "icon": "👥",
                "short_description": "Manage real estate sales teams, role-based access permissions, targets, and attendance.",
                "detailed_description": "Structure your real estate firm with hierarchical teams, role permissions (Admin, Manager, Agent), target allocation, and attendance/activity monitoring.",
                "benefits": ["Role-based data security", "Performance target tracking", "Activity & location check-ins", "Streamlined team hierarchy"],
                "whats_included": ["User role & permission manager", "Monthly target allocation", "Activity performance logs", "Team attendance dashboard"],
                "how_it_works": ["1. Create organizational roles", "2. Assign team members & targets", "3. Monitor daily agent output", "4. Review monthly performance"],
                "required_documents": ["Employee roster & designation list", "Role hierarchy plan"],
                "faqs": [
                    {"question": "Can agents see leads of other agents?", "answer": "No, permissions can be restricted so agents only see their assigned leads."}
                ]
            }
        ]
    },
    {
        "category_name": "Digital Presence & Marketing",
        "icon": "🌐",
        "description": "Build high-converting real estate websites, run digital campaigns, and elevate brand visibility.",
        "services": [
            {
                "name": "Professional Real Estate Website",
                "icon": "💻",
                "short_description": "Custom high-converting website for real estate developers and agencies with property search and lead capture.",
                "detailed_description": "Establish a top-tier digital presence with a modern, fast, mobile-responsive real estate website. Complete with interactive property search filters, gallery showcases, lead inquiry forms, and search engine optimization.",
                "benefits": ["High lead conversion design", "Mobile-first responsive layout", "SEO optimized structure", "Integrated WhatsApp & Call CTAs"],
                "whats_included": ["Custom homepage & listing engine", "Property filters (Location, Price, Type)", "Lead form integration", "SSL certificate & setup"],
                "how_it_works": ["1. Requirement discovery & design brief", "2. Content & layout draft", "3. Development & listing upload", "4. Testing, domain mapping & launch"],
                "required_documents": ["Company logo & brand guidelines", "Property photos & project details"],
                "faqs": [
                    {"question": "Is the website mobile friendly?", "answer": "Yes, 100% responsive for mobile, tablet, and desktop devices."}
                ]
            },
            {
                "name": "Personal Agent Website",
                "icon": "👤",
                "short_description": "Personalized branding website for individual real estate agents to showcase active listings and client reviews.",
                "detailed_description": "Stand out as a trusted local property expert. Showcase your professional portfolio, featured property listings, client testimonials, achievements, and direct contact buttons on your personal website.",
                "benefits": ["Personal brand elevation", "Direct client connection", "Testimonial showcase", "Social media integration"],
                "whats_included": ["Agent bio & achievement section", "Featured listings gallery", "Client testimonial slider", "Instant contact form"],
                "how_it_works": ["1. Agent profile info collection", "2. Theme selection & branding", "3. Listing & review upload", "4. Live website deployment"],
                "required_documents": ["Agent headshot photo", "Bio & listing details"],
                "faqs": [
                    {"question": "Can I connect my own custom domain?", "answer": "Yes, your personal domain (e.g. yourname.com) can be mapped seamlessly."}
                ]
            },
            {
                "name": "Property Listing Website",
                "icon": "🏡",
                "short_description": "Dedicated portal for displaying residential and commercial properties for buy, sell, and rent.",
                "detailed_description": "Launch a dedicated property portal where users can browse, search, and filter available properties with detailed photo galleries, floor plans, specifications, and owner/agent inquiry forms.",
                "benefits": ["Searchable property catalogue", "High resolution media galleries", "Direct lead generation", "Locality-wise classification"],
                "whats_included": ["Listing submission manager", "Advanced search filters", "Interactive floor plans & maps", "Inquiry notification triggers"],
                "how_it_works": ["1. Define property taxonomy", "2. Configure search & filter parameters", "3. Populate property listings", "4. Go live"],
                "required_documents": ["Property data & photographs", "Pricing & specification sheets"],
                "faqs": [
                    {"question": "Can buyers filter by budget and locality?", "answer": "Yes, multi-attribute filter controls are built in."}
                ]
            },
            {
                "name": "Landing Page Creation",
                "icon": "🚀",
                "short_description": "High-converting single project landing pages engineered for real estate digital marketing campaigns.",
                "detailed_description": "Maximize ad campaign ROI with custom project landing pages. Engineered with captivating project highlights, location maps, floor plans, pricing sheets, and high-conversion inquiry popups.",
                "benefits": ["Higher ad click-to-lead conversion", "Ultra-fast page load speed", "A/B testing optimization", "Direct CRM lead sync"],
                "whats_included": ["Hero banner & brochure download form", "Project amenities & layout section", "Location advantages map", "Mobile-optimized enquiry form"],
                "how_it_works": ["1. Campaign strategy & asset collection", "2. Copywriting & UX wireframing", "3. Landing page build & CRM hook", "4. Launch & tracking setup"],
                "required_documents": ["Project brochure & elevation renders", "RERA registration number"],
                "faqs": [
                    {"question": "Can leads automatically sync to my CRM?", "answer": "Yes, instant webhook integration pushes leads to your CRM."}
                ]
            },
            {
                "name": "Domain & Hosting",
                "icon": "🌐",
                "short_description": "Reliable real estate web hosting, domain registration, SSL certificates, and business emails.",
                "detailed_description": "Secure reliable web infrastructure tailored for real estate websites. Includes domain name registration (.com / .in), high-speed cloud web hosting, SSL security, and professional corporate email accounts.",
                "benefits": ["99.9% web uptime SLA", "Encrypted SSL protection", "Professional business email", "Automated daily backups"],
                "whats_included": ["Domain registration (.com / .in)", "High speed SSD cloud hosting", "Free SSL certificate", "Corporate email mailboxes"],
                "how_it_works": ["1. Domain availability check", "2. Account creation & domain booking", "3. DNS & hosting setup", "4. Email configuration"],
                "required_documents": ["Company / Individual domain owner name", "Contact email"],
                "faqs": [
                    {"question": "Do you handle annual domain renewals?", "answer": "Yes, automated renewal alerts and management are provided."}
                ]
            },
            {
                "name": "Social Media Management",
                "icon": "📱",
                "short_description": "Comprehensive management of Facebook, Instagram, LinkedIn, and YouTube channels for real estate brands.",
                "detailed_description": "Build an active social media community and attract organic buyers. We handle social content strategy, graphic creation, property video reels, posting schedules, and follower engagement.",
                "benefits": ["Consistent social brand presence", "Engaging property video reels", "Higher follower growth", "Active client community"],
                "whats_included": ["Monthly content calendar", "Custom graphic posts & reels", "Hashtag & copy strategy", "Engagement & inbox monitoring"],
                "how_it_works": ["1. Brand identity & target audience audit", "2. Monthly content calendar creation", "3. Design & video production", "4. Scheduled posting & engagement"],
                "required_documents": ["Social media page admin access", "Property photos & project highlights"],
                "faqs": [
                    {"question": "How many posts are created per month?", "answer": "Standard packages include 12 to 20 custom posts/reels per month."}
                ]
            },
            {
                "name": "Digital Marketing Campaigns",
                "icon": "🎯",
                "short_description": "Targeted Google Ads, Facebook Ads, and Instagram lead generation campaigns for property sales.",
                "detailed_description": "Drive qualified property buyer inquiries with performance marketing campaigns on Meta (Facebook/Instagram) and Google Ads. Target buyers by location, income bracket, and real estate purchase intent.",
                "benefits": ["Highly targeted buyer leads", "Optimized Cost-Per-Lead (CPL)", "Real-time campaign analytics", "Direct CRM lead delivery"],
                "whats_included": ["Ad copy & visual creative design", "Audience targeting setup", "Google Search & Meta Ad setup", "Daily CPL optimization"],
                "how_it_works": ["1. Campaign budget & goal planning", "2. Target audience persona setup", "3. Creative design & ad launch", "4. Continuous ROI tracking & tuning"],
                "required_documents": ["Ad account access", "Project details & target locations"],
                "faqs": [
                    {"question": "What is the typical Cost Per Lead?", "answer": "CPL varies by location and segment (e.g. ₹150 - ₹600 per lead)."}
                ]
            },
            {
                "name": "Google Business Profile Setup",
                "icon": "📍",
                "short_description": "Setup, verification, and local SEO optimization for your real estate office on Google Maps.",
                "detailed_description": "Dominate local property searches in your city. We set up, verify, and optimize your Google Business Profile so local buyers and sellers find your office on Google Maps and search results.",
                "benefits": ["Increased local walk-in leads", "Higher Google Search visibility", "Client review collection", "Direct phone call inquiries"],
                "whats_included": ["Google profile creation & verification", "Business category & keyword optimization", "Office photos & listing upload", "Review link generation"],
                "how_it_works": ["1. Business location details submission", "2. Google verification postcard/video", "3. Profile optimization & photo upload", "4. Review campaign launch"],
                "required_documents": ["Office address proof & signboard photo", "Business phone & hours"],
                "faqs": [
                    {"question": "How long does verification take?", "answer": "Google verification typically takes 3 to 7 business days."}
                ]
            },
            {
                "name": "WhatsApp Business Integration",
                "icon": "💬",
                "short_description": "Automated WhatsApp API messaging, catalogue display, and chatbot inquiries for property buyers.",
                "detailed_description": "Engage prospective property buyers where they spend most of their time. Implement Official WhatsApp Business API with automated greetings, interactive property catalogues, and quick inquiry bots.",
                "benefits": ["98% message open rate", "Instant auto-response to leads", "Interactive property catalogue", "Verified WhatsApp green badge assistance"],
                "whats_included": ["Official WhatsApp Business API setup", "Automated greeting & quick replies", "Product catalogue creation", "CRM webhook integration"],
                "how_it_works": ["1. Meta Business Manager verification", "2. WhatsApp API phone number setup", "3. Message template approval", "4. Bot & CRM integration"],
                "required_documents": ["GST / Business registration", "Phone number for WhatsApp API"],
                "faqs": [
                    {"question": "Can I broadcast messages to multiple leads?", "answer": "Yes, compliant broadcast messages can be sent via WhatsApp API."}
                ]
            },
            {
                "name": "Property Brochure & Catalogue Design",
                "icon": "🎨",
                "short_description": "High-quality PDF brochures, project catalogues, and digital marketing collaterals.",
                "detailed_description": "Impress buyers and investors with professionally designed real estate brochures, project e-catalogues, floor plan renders, and promotional flyers created by experienced graphic designers.",
                "benefits": ["Premium brand image", "Clear layout & floor plan presentation", "Print & digital ready PDF formats", "Custom brand color alignment"],
                "whats_included": ["Multi-page project brochure design", "High-res PDF export", "Print-ready CMYK file", "Digital interactive PDF version"],
                "how_it_works": ["1. Project brief & content handover", "2. Concept layout draft", "3. Client review & revisions", "4. Final file delivery"],
                "required_documents": ["Project details, text copy & logo", "High-resolution project images"],
                "faqs": [
                    {"question": "How many design revisions are included?", "answer": "Standard packages include 3 rounds of design revisions."}
                ]
            },
            {
                "name": "Virtual Property Tours",
                "icon": "🕶️",
                "short_description": "360-degree immersive virtual property walkthroughs for remote buyers and NRI clients.",
                "detailed_description": "Allow prospective buyers and NRI clients to tour properties remotely. We capture high-definition 360-degree panoramic virtual tours with interactive hot-spots, floor plans, and embedded video clips.",
                "benefits": ["Attract remote & NRI buyers", "Save site visit travel time", "Interactive 360-degree views", "Embeddable on website & portals"],
                "whats_included": ["360-degree HDR camera shoot", "Virtual tour stitching & hosting", "Interactive floor plan integration", "Embed code for website"],
                "how_it_works": ["1. Site shoot scheduling", "2. 360-degree panoramic capture", "3. Digital processing & hotspot tagging", "4. Tour link & embed delivery"],
                "required_documents": ["Site location & access permission", "Clean, staged property site"],
                "faqs": [
                    {"question": "Can virtual tours be viewed on mobile phones?", "answer": "Yes, tours are fully responsive across smartphones, tablets, and VR headsets."}
                ]
            },
            {
                "name": "Property Photography & Videography",
                "icon": "📸",
                "short_description": "Professional architectural photography, 4K walkthrough videos, and drone aerial footage.",
                "detailed_description": "Showcase real estate properties in their best light. Professional architectural photography, smooth 4K walkthrough video shoots, drone aerial cinematography, and color-graded video editing.",
                "benefits": ["Stunning visual marketing assets", "Higher buyer inquiry rates", "Professional lighting & editing", "Social media video reels included"],
                "whats_included": ["High-res architectural photos", "4K video walkthrough with background score", "Aerial drone video clips (subject to permission)", "Edited video formats for Instagram/YouTube"],
                "how_it_works": ["1. Property shoot booking", "2. On-site photo & video shoot", "3. Color grading & video editing", "4. High-resolution file delivery"],
                "required_documents": ["Site location details", "Shoot date & time confirmation"],
                "faqs": [
                    {"question": "Are drone shoots permitted in all areas?", "answer": "Drone shoots are conducted strictly as per DGCA local zone permissions."}
                ]
            }
        ]
    },
    {
        "category_name": "Calling & Lead Generation Services",
        "icon": "📞",
        "description": "Engage prospective property buyers and tenants with dedicated telecallers, AI voice agents, and lead qualification.",
        "services": [
            {
                "name": "Human Telecaller",
                "icon": "🎧",
                "short_description": "Trained real estate telecallers to handle buyer inquiries, follow-ups, and site visit scheduling.",
                "detailed_description": "Deploy experienced human telecallers trained in real estate sales scripts. They contact prospective buyers, qualify budget and timeline, answer project questions, and schedule site visits.",
                "benefits": ["Professional client communication", "Higher site visit conversion", "Daily call activity reporting", "Custom sales script execution"],
                "whats_included": ["Trained calling executive", "Outbound & inbound call handling", "Daily call report summary", "CRM update after each call"],
                "how_it_works": ["1. Requirement intake & script alignment", "2. Telecaller assignment & briefing", "3. Calling campaign execution", "4. Daily performance reporting"],
                "required_documents": ["Calling database (CSV)", "Project FAQs & script guidelines"],
                "faqs": [
                    {"question": "Are telecallers trained in real estate?", "answer": "Yes, our telecallers undergo specific real estate domain training."}
                ]
            },
            {
                "name": "Dedicated Calling Agent",
                "icon": "👤",
                "short_description": "Full-time dedicated telecalling resource working exclusively for your real estate firm.",
                "detailed_description": "Hire a dedicated telecaller working 100% exclusively for your real estate business. Ideal for high-volume lead handling, cold calling, and continuous client relationship management.",
                "benefits": ["100% exclusive resource dedication", "Deep alignment with your brand", "Direct daily management", "Consistent long-term client touch"],
                "whats_included": ["Full-time telecaller (8 hours/day)", "Dedicated phone line & CRM access", "Weekly performance review", "Backup resource availability"],
                "how_it_works": ["1. Candidate profile review & interview", "2. Onboarding & script training", "3. Dedicated calling operations", "4. Monthly review & management"],
                "required_documents": ["Firm profile & product details", "Work scope & target expectations"],
                "faqs": [
                    {"question": "Can I interview the telecaller before assignment?", "answer": "Yes, you can interview and select your dedicated resource."}
                ]
            },
            {
                "name": "Shared Calling Agent",
                "icon": "🤝",
                "short_description": "Cost-effective shared telecalling team to manage small-scale or periodic lead verification campaigns.",
                "detailed_description": "Cost-effective solution for small agencies or periodic campaigns. Shared telecallers handle lead qualification and site visit reminders on a pay-per-lead or part-time model.",
                "benefits": ["Cost-effective for small databases", "Flexible call volume packages", "Zero long-term payroll commitment", "Quick campaign setup"],
                "whats_included": ["Shared telecaller pool allocation", "Call outcome recording", "Verified lead reporting", "Flexible call volume credits"],
                "how_it_works": ["1. Select call volume package", "2. Share lead list & script", "3. Calling campaign execution", "4. Report delivery"],
                "required_documents": ["Lead contact list", "Key project specifications"],
                "faqs": [
                    {"question": "What is the minimum lead volume for shared callers?", "answer": "Minimum campaign starting size is 100 lead contacts."}
                ]
            },
            {
                "name": "AI Voice Calling Agent",
                "icon": "🤖",
                "short_description": "Automated AI voice agents for instant lead verification, event invitations, and initial qualification.",
                "detailed_description": "Leverage cutting-edge conversational AI voice agents to call thousands of leads concurrently within minutes. Qualify buyer intent, confirm site visit availability, and route interested buyers to live human agents.",
                "benefits": ["Instant call throughput (1000s/min)", "Natural conversational voice", "24/7 lead verification capability", "Significant cost savings"],
                "whats_included": ["AI voice bot setup & script programming", "Natural language speech engine", "Live call transfer to sales reps", "Analytics & recording dashboard"],
                "how_it_works": ["1. AI script & intent tree setup", "2. Voice synthesis configuration", "3. Broadcast call campaign launch", "4. Real-time lead transfer & reporting"],
                "required_documents": ["Call script & intent branches", "Lead contact database"],
                "faqs": [
                    {"question": "Can the AI transfer calls to a human agent?", "answer": "Yes, when a lead expresses high interest, the call is patched live to your sales agent."}
                ]
            },
            {
                "name": "Automated Lead Follow-ups",
                "icon": "🔄",
                "short_description": "Multi-channel automated follow-up calls, SMS, and WhatsApp alerts for uncontacted leads.",
                "detailed_description": "Ensure no lead is left behind. Automated follow-up triggers re-engage cold leads, remind buyers of scheduled site visits, and request feedback post-visit across calling, WhatsApp, and SMS.",
                "benefits": ["Higher lead re-engagement rate", "Zero manual follow-up missed", "Multi-touchpoint coverage", "Automated cadence scheduling"],
                "whats_included": ["Cadence strategy builder", "Multi-channel automated triggers", "Re-engagement message templates", "Lead status updates"],
                "how_it_works": ["1. Map follow-up timelines", "2. Configure automated triggers", "3. System executes follow-up cadence", "4. Review engagement reports"],
                "required_documents": ["Lead database", "Communication templates"],
                "faqs": [
                    {"question": "How many follow-up attempts are made?", "answer": "Default cadences include 3 to 5 automated touchpoints."}
                ]
            },
            {
                "name": "Missed Call Management",
                "icon": "📞",
                "short_description": "Virtual number system to capture missed calls, trigger auto-SMS responses, and alert sales team.",
                "detailed_description": "Never lose a customer call after office hours or during peak traffic. Virtual missed call numbers automatically capture caller IDs, send instant SMS/WhatsApp greetings, and assign follow-up tasks to available agents.",
                "benefits": ["100% call capture rate", "Instant auto-reply to caller", "Centralized virtual number", "Agent alert notifications"],
                "whats_included": ["Virtual phone number provision", "Auto-SMS / WhatsApp instant response", "Caller ID logging portal", "CRM lead auto-creation"],
                "how_it_works": ["1. Virtual number setup & routing", "2. Customer calls virtual number", "3. Call logged & auto-SMS sent", "4. Agent receives follow-up alert"],
                "required_documents": ["Company registration details", "Destination mobile numbers"],
                "faqs": [
                    {"question": "Does it work 24/7?", "answer": "Yes, the virtual number logs calls and triggers instant replies round the clock."}
                ]
            },
            {
                "name": "Lead Qualification",
                "icon": "✅",
                "short_description": "Rigorous filtering and qualification of property inquiries based on budget, timeline, and intent.",
                "detailed_description": "Save your core sales team time by delivering pre-qualified, warm leads. Our qualification process verifies buyer budget, location preference, possession timeline, and home loan requirement before handing off to closing agents.",
                "benefits": ["Saves sales agent time", "Higher closing conversion rate", "Accurate buyer requirement profiling", "Categorized lead quality tiers"],
                "whats_included": ["BANT (Budget, Authority, Need, Timeline) profiling", "Detailed qualification report per lead", "Tagging (Hot / Warm / Cold)", "Hot lead instant escalation"],
                "how_it_works": ["1. Define lead qualification criteria", "2. Team contacts raw inquiries", "3. Detailed profiling & verification", "4. Hand-off qualified leads to sales team"],
                "required_documents": ["Project pricing & minimum criteria", "Lead intake list"],
                "faqs": [
                    {"question": "What parameters are used for qualification?", "answer": "Budget, preferred configuration, purchase timeline, and home loan status."}
                ]
            },
            {
                "name": "Customer Appointment Scheduling",
                "icon": "📅",
                "short_description": "Professional booking of project walk-ins, site visits, and video consultation meetings.",
                "detailed_description": "Convert buyer inquiries into confirmed calendar appointments. We schedule site visits, office consultations, and online video presentations with automated calendar invites and confirmation reminders.",
                "benefits": ["Higher appointment show rate", "Automated calendar sync", "Confirmation SMS & WhatsApp", "Rescheduling assistance"],
                "whats_included": ["Appointment scheduling portal", "Google / Outlook calendar sync", "SMS & WhatsApp confirmation alerts", "Reschedule management"],
                "how_it_works": ["1. Inquiry intake & interest verification", "2. Date & time slot confirmation", "3. Calendar invite & reminder dispatch", "4. Post-appointment status tracking"],
                "required_documents": ["Executive calendar availability", "Project site address & map link"],
                "faqs": [
                    {"question": "Can clients reschedule their appointments?", "answer": "Yes, automated rescheduling links are included in reminder messages."}
                ]
            },
            {
                "name": "Property Enquiry Calling",
                "icon": "📲",
                "short_description": "Prompt response and calling service for inquiries received from magicbricks, housing, and 99acres.",
                "detailed_description": "Instant callback service for property portal inquiries. Speed-to-lead is critical—our callers respond within minutes to portal inquiries from Housing.com, 99acres, Magicbricks, and social media ads.",
                "benefits": ["Sub-15 minute response time", "Higher buyer contact rate", "Portal lead synchronization", "Detailed inquiry feedback"],
                "whats_included": ["Real-time portal inquiry integration", "Immediate outbound call response", "Lead requirement tagging", "CRM status synchronization"],
                "how_it_works": ["1. Connect portal API webhooks", "2. Immediate calling alert trigger", "3. Outbound call executed within minutes", "4. Requirement & outcome logged"],
                "required_documents": ["Portal API / Webhook credentials", "Project details & FAQ cheat sheet"],
                "faqs": [
                    {"question": "Why is fast callback important?", "answer": "Calling leads within 15 minutes increases contact rate by up to 300%."}
                ]
            },
            {
                "name": "Bulk SMS & WhatsApp Campaigns",
                "icon": "📢",
                "short_description": "Targeted promotional broadcast campaigns to property investors and home buyers.",
                "detailed_description": "Reach thousands of target buyers instantly with promotional WhatsApp broadcasts and DLT-approved bulk SMS campaigns. Announce new project launches, festival offers, and site visit events effectively.",
                "benefits": ["Mass market reach", "High open and response rates", "DLT & WhatsApp regulatory compliance", "Click-through analytics"],
                "whats_included": ["DLT template registration help", "WhatsApp API broadcast dispatch", "Target audience segmentation", "Campaign delivery & click reports"],
                "how_it_works": ["1. Message content & DLT template approval", "2. Audience contact list upload", "3. Scheduled campaign broadcast", "4. Delivery & response analytics"],
                "required_documents": ["DLT Entity ID (for SMS)", "WhatsApp API account", "Target database"],
                "faqs": [
                    {"question": "Are SMS campaigns DLT compliant in India?", "answer": "Yes, all SMS broadcasts are executed through registered TRAI DLT pipelines."}
                ]
            }
        ]
    },
    {
        "category_name": "Manpower & Business Support",
        "icon": "👥",
        "description": "Recruit and deploy experienced real estate sales agents, property managers, field executives, and virtual assistants.",
        "services": [
            {
                "name": "Hire Sales Representative",
                "icon": "👔",
                "short_description": "Recruit experienced real estate sales representatives for site sales, closing, and customer counseling.",
                "detailed_description": "Find and hire top-performing real estate sales representatives. We source, screen, and vet candidates experienced in residential and commercial property sales, negotiation, and deal closing.",
                "benefits": ["Pre-vetted real estate talent", "Shorter hiring turnaround", "Domain-experienced candidates", "Replacement guarantee"],
                "whats_included": ["Candidate sourcing & screening", "Domain knowledge assessment", "Interview scheduling", "Background verification assistance"],
                "how_it_works": ["1. Job role & experience requirement intake", "2. Candidate sourcing & vetting", "3. Client interview rounds", "4. Offer rollout & onboarding"],
                "required_documents": ["Job description & CTC structure", "Company profile"],
                "faqs": [
                    {"question": "Is there a candidate replacement guarantee?", "answer": "Yes, a 60-day replacement guarantee is provided for hired candidates."}
                ]
            },
            {
                "name": "Hire Real Estate Agent",
                "icon": "🏘️",
                "short_description": "Onboard licensed or experienced real estate agents and brokers for property transaction sourcing.",
                "detailed_description": "Recruit experienced real estate agents with strong local area networks. Expand your firm's property sourcing, buyer network, and transaction capabilities across key micromarkets.",
                "benefits": ["Local market network access", "Commission-driven performers", "Faster property sourcing", "RERA compliant candidates"],
                "whats_included": ["Agent network sourcing", "Experience & deal track record check", "RERA registration verification", "Contract agreement drafting"],
                "how_it_works": ["1. Territory & specialization requirement setup", "2. Agent outreach & evaluation", "3. Partnership discussion & onboarding", "4. Active listing assignment"],
                "required_documents": ["RERA registration criteria", "Agent commission policy structure"],
                "faqs": [
                    {"question": "Do agents have prior experience in specific cities?", "answer": "Yes, candidates are matched by local micromarket experience."}
                ]
            },
            {
                "name": "Hire Telecaller",
                "icon": "🎧",
                "short_description": "Recruit fluent, persuasive telecallers for real estate lead qualification and appointment setting.",
                "detailed_description": "Recruit dedicated telecallers skilled in outbound phone sales, customer follow-up, and language fluency. Improve your team's lead qualification throughput and site visit booking efficiency.",
                "benefits": ["Fluent multilingual callers", "Pre-screened voice quality", "Quick hiring turnaround", "High productivity candidates"],
                "whats_included": ["Voice quality & language screening", "Real estate script evaluation", "Candidate shortlist delivery", "Onboarding support"],
                "how_it_works": ["1. Language & headcount requirement intake", "2. Voice audition & screening", "3. Client interview selection", "4. Joining & script orientation"],
                "required_documents": ["Job role description", "Language & salary criteria"],
                "faqs": [
                    {"question": "Can I request callers fluent in local languages?", "answer": "Yes, candidates are vetted for regional language fluency as required."}
                ]
            },
            {
                "name": "Hire Relationship Manager",
                "icon": "🤝",
                "short_description": "Hire high-touch Relationship Managers for premium NRI, HNI, and commercial client portfolios.",
                "detailed_description": "Recruit polished Relationship Managers (RMs) experienced in handling High-Net-Worth Individuals (HNIs), NRI investors, and corporate commercial real estate clients.",
                "benefits": ["Polished executive presentation", "HNI & NRI client management", "Strong negotiation skills", "High deal value focus"],
                "whats_included": ["Executive search & sourcing", "Deep domain & soft-skills evaluation", "Comprehensive background check", "Onboarding alignment"],
                "how_it_works": ["1. Profile & HNI experience criteria setup", "2. Executive talent search", "3. Multi-round client evaluation", "4. Offer & joining coordination"],
                "required_documents": ["RM job specification", "CTC & incentive structure"],
                "faqs": [
                    {"question": "Do RMs have experience in luxury real estate?", "answer": "Yes, specialized RMs with luxury project experience can be sourced."}
                ]
            },
            {
                "name": "Hire Field Executive",
                "icon": "🏃",
                "short_description": "Deploy energetic field executives for property site visits, document pickups, and local verifications.",
                "detailed_description": "Hire energetic field executives to manage site visits, transport prospective buyers, collect physical property documents, and conduct local property inspections.",
                "benefits": ["Local geography familiarity", "Prompt site visit assistance", "Document pickup & delivery", "Reliable field presence"],
                "whats_included": ["Field candidate screening", "Driving license & vehicle check", "Local geography test", "Background verification"],
                "how_it_works": ["1. Location & operational requirement intake", "2. Field candidate sourcing", "3. Interview & practical evaluation", "4. Deployment & tracking"],
                "required_documents": ["Field scope details", "Vehicle requirement specifications"],
                "faqs": [
                    {"question": "Do field executives have their own two-wheelers?", "answer": "Yes, candidates with valid driving licenses and personal vehicles are prioritized."}
                ]
            },
            {
                "name": "Hire Property Manager",
                "icon": "🔑",
                "short_description": "Recruit professional Property Managers to handle tenant relations, maintenance, and rental operations.",
                "detailed_description": "Find skilled Property Managers to oversee residential and commercial property portfolios. They manage tenant onboarding, rent collection, routine maintenance, and facility inspections.",
                "benefits": ["Comprehensive property oversight", "Timely rent collection", "Tenant dispute resolution", "Facility maintenance management"],
                "whats_included": ["Property management candidate sourcing", "Facility & legal knowledge check", "Reference verification", "Job contract drafting"],
                "how_it_works": ["1. Portfolio size & role scope definition", "2. Talent search & screening", "3. Client interview & selection", "4. Job offer & deployment"],
                "required_documents": ["Property portfolio details", "Key responsibilities document"],
                "faqs": [
                    {"question": "Can property managers handle commercial properties?", "answer": "Yes, managers with commercial facility experience are available."}
                ]
            },
            {
                "name": "Outsourced Sales Team",
                "icon": "🏢",
                "short_description": "Complete turnkey sales team deployment to manage real estate project launches and site offices.",
                "detailed_description": "Deploy a complete turnkey sales force for your real estate project. Includes Site Sales Head, Closing Managers, Relationship Officers, and Reception Executives dedicated to driving project sales.",
                "benefits": ["Turnkey sales execution", "Zero internal HR overhead", "Target-driven sales velocity", "Full site office management"],
                "whats_included": ["Complete sales team structure", "Sales Manager & Executives", "On-site performance supervision", "Target reporting & analytics"],
                "how_it_works": ["1. Project size & sales target evaluation", "2. Team composition & SLA agreement", "3. Site office team deployment", "4. Live sales operations & management"],
                "required_documents": ["Project RERA & site details", "Sales mandate agreement"],
                "faqs": [
                    {"question": "Is the sales team dedicated to one project?", "answer": "Yes, the outsourced sales team operates exclusively at your project site."}
                ]
            },
            {
                "name": "Virtual Assistant",
                "icon": "💻",
                "short_description": "Remote virtual assistants for real estate data entry, lead management, and administrative support.",
                "detailed_description": "Delegate routine administrative tasks to skilled remote Virtual Assistants (VAs). They handle portal listing updates, lead data entry, email correspondence, and calendar management.",
                "benefits": ["Cost-effective administrative support", "Flexible hourly or monthly plans", "Streamlined office workflow", "Zero physical office space needed"],
                "whats_included": ["Trained real estate Virtual Assistant", "Computer & internet infrastructure", "Daily task activity log", "Supervised quality assurance"],
                "how_it_works": ["1. Task scope & hours requirement setup", "2. VA allocation & briefing", "3. Daily task execution", "4. Weekly activity reporting"],
                "required_documents": ["Task list & system access details"],
                "faqs": [
                    {"question": "What tools can Virtual Assistants use?", "answer": "VAs are trained in Excel, Google Suite, Real Estate CRMs, and listing portals."}
                ]
            },
            {
                "name": "Recruitment & Staffing Support",
                "icon": "📋",
                "short_description": "End-to-end recruitment services for real estate developer firms, agencies, and IPCs.",
                "detailed_description": "Complete recruitment and executive search support for real estate organizations. We source, interview, conduct background checks, and onboard talent across sales, marketing, legal, and operations.",
                "benefits": ["Industry specialized recruiters", "Access to passive talent pool", "Reduced hiring turn-around time", "Rigorous candidate vetting"],
                "whats_included": ["Job mandate profiling", "Resume screening & shortlisting", "Interview coordination", "Offer & joining tracking"],
                "how_it_works": ["1. Staffing mandate agreement", "2. Candidate sourcing & pre-screening", "3. Client interview rounds", "4. Selection & joining support"],
                "required_documents": ["Company profile & hiring requirements", "Agency service agreement"],
                "faqs": [
                    {"question": "What is the typical hiring timeline?", "answer": "First candidate shortlists are delivered within 3 to 5 business days."}
                ]
            },
            {
                "name": "Sales Training",
                "icon": "🎓",
                "short_description": "Professional training programs for real estate sales teams to master pitch closing, objection handling, and negotiation.",
                "detailed_description": "Empower your sales force with high-impact real estate sales training workshops. Modules cover customer psychology, property pitching, handling price objections, negotiation tactics, and closing techniques.",
                "benefits": ["Higher lead-to-booking conversion", "Sharper objection handling", "Professional pitch delivery", "Motivated sales team"],
                "whats_included": ["Customized training curriculum", "Live workshop / Webinar sessions", "Real estate roleplay exercises", "Training certificate & reference manual"],
                "how_it_works": ["1. Team skill gap evaluation", "2. Training module customization", "3. Live interactive training workshop", "4. Post-training evaluation & feedback"],
                "required_documents": ["Team size & current sales workflow"],
                "faqs": [
                    {"question": "Are training sessions conducted online or on-site?", "answer": "Both options are available: on-site at your office or interactive online webinars."}
                ]
            }
        ]
    },
    {
        "category_name": "Banking, Finance & Taxation",
        "icon": "🏦",
        "description": "Comprehensive banking solutions, home loan processing, business loans, GST compliance, and tax filing.",
        "services": [
            {
                "name": "Home Loan for Agents / Firm Owners",
                "icon": "🏠",
                "short_description": "Customized home loan solutions for real estate agents, brokers, and firm owners with income proof flexibility.",
                "detailed_description": "Specialized home loans designed for self-employed real estate professionals and agency owners. Benefit from flexible income evaluation, competitive interest rates, and multi-bank option matching.\n\nDisclaimer: Final eligibility, interest rate, loan amount, and approval depend on the lender bank/NBFC evaluation policies and borrower credit score.",
                "benefits": ["Flexible income proof assessment", "Multi-bank comparison options", "Doorstep documentation assistance", "Pre-approved loan options"],
                "whats_included": ["Eligibility calculation & bank matching", "Document collection & file preparation", "Bank login & sanction tracking", "Disbursal assistance"],
                "how_it_works": ["1. Submit income & loan requirement", "2. Eligibility assessment & bank selection", "3. Document pickup & bank submission", "4. Sanction letter & loan disbursal"],
                "required_documents": ["PAN Card, Aadhaar Card", "2 Years ITR with Computation & Profit & Loss", "6 Months Bank Account Statement", "Property Documents"],
                "faqs": [
                    {"question": "Can self-employed brokers without fixed salary apply?", "answer": "Yes, loans are evaluated based on ITR income, turnover, and bank cash flow."}
                ]
            },
            {
                "name": "Business Loan for Agents / Firms",
                "icon": "💼",
                "short_description": "Collateral-free business expansion loans and working capital lines for real estate agency owners.",
                "detailed_description": "Fuel your real estate business growth. Access collateral-free business loans and working capital facility to expand marketing campaigns, hire sales teams, or open new branch offices.\n\nDisclaimer: Loan sanction, interest rates, and credit limits are subject to bank/NBFC credit policies and GST/ITR turnover verification.",
                "benefits": ["Collateral-free business loan", "Quick sanction & disbursal", "Flexible repayment tenure (12-60 months)", "Competitive interest rates"],
                "whats_included": ["Turnover & eligibility analysis", "Multi-lender loan comparison", "Application filing & tracking", "Disbursal support"],
                "how_it_works": ["1. Submit business details & turnover", "2. Lender eligibility matching", "3. File submission & verification", "4. Loan agreement & disbursal"],
                "required_documents": ["Business Registration / GST Certificate", "2 Years ITR & Audited Financials", "12 Months Bank Statement", "Proprietor / Partner PAN & Aadhaar"],
                "faqs": [
                    {"question": "Is collateral property required for a business loan?", "answer": "Unsecured business loans up to ₹50 Lakhs do not require property collateral."}
                ]
            },
            {
                "name": "Home Loan for Customers",
                "icon": "🔑",
                "short_description": "Seamless home loan processing for property buyers with maximum LTV and low interest rates.",
                "detailed_description": "Help your property buyers secure hassle-free home loans from leading PSU and Private banks. Enjoy doorstep document collection, maximum eligible loan-to-value (LTV), and fast sanction processing.\n\nDisclaimer: Final home loan approval, interest rate, and eligible loan amount depend on the applicant's credit score (CIBIL), income, and bank legal/technical property valuation.",
                "benefits": ["Doorstep service for buyers", "Tie-ups with Top 20+ Banks & NBFCs", "Maximum Loan-to-Value (up to 90%)", "Fast sanction & zero hidden fees"],
                "whats_included": ["FOIR & eligibility computation", "Bank option comparison sheet", "Technical & legal verification tracking", "Sanction letter issuance"],
                "how_it_works": ["1. Buyer application & document collection", "2. Bank selection & file login", "3. Bank technical & legal verification", "4. Sanction letter & agreement signing"],
                "required_documents": ["Buyer PAN, Aadhaar, Photo", "3 Months Salary Slip & 2 Yrs Form 16 (Salaried)", "ITR & Bank Statements (Self-Employed)", "Property Allotment / Agreement Copy"],
                "faqs": [
                    {"question": "How much time does home loan sanction take?", "answer": "Sanction letters are typically issued within 3 to 7 working days."}
                ]
            },
            {
                "name": "Loan Against Property",
                "icon": "🏢",
                "short_description": "Mortgage loan against residential, commercial, or industrial property for business or personal needs.",
                "detailed_description": "Unlock the high monetary value of your owned residential or commercial property. Get high-ticket Loan Against Property (LAP) at lower interest rates than unsecured loans.\n\nDisclaimer: Loan sanction is subject to property title verification, market valuation, and borrower repayment capability as per bank norms.",
                "benefits": ["Lower interest rates than business loans", "High loan amount (up to ₹10 Crores)", "Longer repayment tenure (up to 15 years)", "Multi-purpose fund usage"],
                "whats_included": ["Property valuation guidance", "Bank eligibility matching", "Title search & legal check", "Sanction & disbursal support"],
                "how_it_works": ["1. Submit property & income details", "2. Valuation & title verification", "3. Bank sanction processing", "4. Mortgage execution & loan credit"],
                "required_documents": ["Property Title Deed & Chain Documents", "Approved Plan & Building Permission", "Borrower Income Proofs & KYCs"],
                "faqs": [
                    {"question": "Can commercial property be mortgaged for LAP?", "answer": "Yes, residential, commercial, and industrial properties are eligible."}
                ]
            },
            {
                "name": "Loan Against Property for Customers",
                "icon": "🏬",
                "short_description": "Assist property buyers and owners in securing mortgage loans for business expansion or personal needs.",
                "detailed_description": "Enable your clients to raise funds against their existing real estate assets for personal, medical, or business needs at competitive mortgage interest rates.\n\nDisclaimer: Loan approval depends on property clear market title and bank credit evaluation.",
                "benefits": ["Competitive mortgage interest rates", "High loan-to-value ratio", "Doorstep service", "Flexible tenure options"],
                "whats_included": ["Eligibility assessment", "Legal & technical coordination", "Bank file login & tracking", "Disbursal assistance"],
                "how_it_works": ["1. Customer inquiry intake", "2. Property document & income check", "3. Bank file login", "4. Sanction & mortgage release"],
                "required_documents": ["Customer KYC & Income Proofs", "Complete Property Ownership Papers"],
                "faqs": [
                    {"question": "Is insurance mandatory for LAP?", "answer": "Most banks require property insurance to cover fire and allied hazards."}
                ]
            },
            {
                "name": "Loan Balance Transfer",
                "icon": "🔄",
                "short_description": "Transfer existing high-interest home or property loans to lower interest rate banks with top-up options.",
                "detailed_description": "Reduce monthly EMI burden. Transfer your existing home loan or LAP from high-interest lenders to leading banks offering lower interest rates and additional top-up loan amounts.\n\nDisclaimer: Transfer approval and top-up amount depend on current track record, property valuation, and new bank credit norms.",
                "benefits": ["Lower interest rate & reduced EMI", "Additional top-up loan facility", "Zero hassle foreclosure support", "Longer tenure restructuring"],
                "whats_included": ["EMI savings calculation report", "Foreclosure letter assistance", "New bank balance transfer login", "Top-up loan processing"],
                "how_it_works": ["1. Submit current loan track statement", "2. Savings calculation & bank selection", "3. Foreclosure & new bank sanction", "4. Balance transfer execution"],
                "required_documents": ["Existing Loan Sanction Letter", "12 Months Track Record Statement", "Foreclosure & List of Documents Letter", "Income & Property Papers"],
                "faqs": [
                    {"question": "Can I get extra funds during balance transfer?", "answer": "Yes, a top-up loan can be sanctioned over and above the existing loan balance."}
                ]
            },
            {
                "name": "Loan Eligibility Assessment",
                "icon": "🧮",
                "short_description": "Free mathematical evaluation of maximum eligible home loan amount based on FOIR and credit profile.",
                "detailed_description": "Get an accurate mathematical assessment of maximum eligible home loan amount, EMI capacity, FOIR calculation, and CIBIL score guidance before applying.\n\nDisclaimer: Assessment is indicative based on standard banking formulas. Final sanction is determined by the lender bank.",
                "benefits": ["Accurate loan capacity clarity", "Prevents loan application rejections", "FOIR optimization guidance", "Completely free consultation"],
                "whats_included": ["Income & FOIR calculation", "Existing EMI obligation deduction", "Multi-bank eligibility report", "CIBIL score check guidance"],
                "how_it_works": ["1. Enter monthly income & existing EMIs", "2. Select desired tenure & interest rate", "3. Instant eligibility calculation", "4. Expert advisor call"],
                "required_documents": ["Monthly gross/net income details", "Existing EMI obligation details"],
                "faqs": [
                    {"question": "What is FOIR in home loans?", "answer": "Fixed Obligation to Income Ratio (FOIR) measures maximum monthly EMI capacity (typically 50-65% of net income)."}
                ]
            },
            {
                "name": "GST Registration",
                "icon": "📜",
                "short_description": "New Goods & Services Tax (GST) registration for real estate firms, brokers, and developers.",
                "detailed_description": "Get your real estate agency or firm registered under GST compliance hassle-free. Complete with document verification, application filing, and GSTIN certificate issuance.\n\nDisclaimer: GST Registration is issued by the GST Department, Govt of India, subject to document verification.",
                "benefits": ["Legal tax compliance", "Input Tax Credit (ITC) eligibility", "Seamless invoicing for corporate clients", "Govt portal registration"],
                "whats_included": ["Document review & classification", "GST Portal application filing", "ARN tracking & response handling", "GSTIN Certificate delivery"],
                "how_it_works": ["1. Document submission", "2. Portal filing & ARN generation", "3. Tax officer verification", "4. GSTIN certificate issuance"],
                "required_documents": ["PAN & Aadhaar of Proprietor/Partners", "Business Address Proof (Electricity bill / Rent Agreement)", "Bank Account Cancelled Cheque"],
                "faqs": [
                    {"question": "Is GST registration mandatory for real estate brokers?", "answer": "Mandatory if annual commission turnover exceeds ₹20 Lakhs (₹10 Lakhs for special states)."}
                ]
            },
            {
                "name": "GST Return Filing",
                "icon": "📊",
                "short_description": "Timely monthly and quarterly GST return filing (GSTR-1, GSTR-3B) for real estate businesses.",
                "detailed_description": "Stay 100% GST compliant. Our expert CA team handles your monthly/quarterly GSTR-1 sales reporting, GSTR-3B tax payment returns, ITC reconciliation, and annual GSTR-9 returns.\n\nDisclaimer: Tax filing services are executed by qualified CA/Tax professionals as per GST laws.",
                "benefits": ["Avoid late fees & interest penalties", "Accurate Input Tax Credit (ITC)", "CA-verified tax computations", "Peace of mind compliance"],
                "whats_included": ["GSTR-1 sales invoice filing", "GSTR-3B monthly tax summary", "GSTR-2B ITC reconciliation", "Filing confirmation receipts"],
                "how_it_works": ["1. Monthly sales & purchase data sharing", "2. CA reconciliation & tax computation", "3. Client approval & tax payment", "4. Return filing on GST Portal"],
                "required_documents": ["Monthly Sales Commission Invoices", "Purchase & Expense Bills", "GST Portal credentials"],
                "faqs": [
                    {"question": "What is the penalty for late GST filing?", "answer": "Late fee is ₹50 per day of delay (₹20/day for Nil return) plus 18% interest on unpaid tax."}
                ]
            },
            {
                "name": "Income Tax Return Filing",
                "icon": "📝",
                "short_description": "Annual Income Tax Return (ITR) filing for individuals, agents, partnership firms, and companies.",
                "detailed_description": "File your annual Income Tax Return accurately with expert CA assistance. Optimize tax deductions under Sec 80C, 24(b), and claim commission expense deductions.\n\nDisclaimer: Income tax return processing is executed in compliance with Income Tax Department rules.",
                "benefits": ["Maximized tax savings & refunds", "CA-certified computation sheet", "Avoid IT notice risks", "Essential for home loan approvals"],
                "whats_included": ["Income source compilation", "Tax deduction optimization", "ITR form selection (ITR-1 to ITR-4)", "E-verification support"],
                "how_it_works": ["1. Document & Form 26AS intake", "2. Tax computation draft", "3. Client review & approval", "4. E-filing & e-verification"],
                "required_documents": ["PAN Card & Aadhaar Card", "Form 16 / Form 26AS / AIS", "Bank Statements & Expense details"],
                "faqs": [
                    {"question": "Why is ITR important for real estate agents?", "answer": "3 years of filed ITRs are mandatory for securing personal home loans and business loans."}
                ]
            },
            {
                "name": "TDS Filing & Compliance",
                "icon": "💸",
                "short_description": "Quarterly TDS return filing (Form 26Q, 27Q) and Form 16/16A certificate generation.",
                "detailed_description": "Manage Tax Deducted at Source (TDS) on property transactions (Sec 194-IA), broker commissions (Sec 194H), and rent payments (Sec 194-IB). Includes quarterly returns and Form 16/16A generation.\n\nDisclaimer: TDS compliance services are managed as per Income Tax Act provisions.",
                "benefits": ["Prevents TDS interest & penalty", "Form 16/16A certificate generation", "TRACES portal compliance", "Avoids tax notice risks"],
                "whats_included": ["TDS calculation & challan payment", "Form 26Q / 27Q quarterly filing", "TRACES Form 16A generation", "TDS correction statements"],
                "how_it_works": ["1. Quarterly TDS data collection", "2. Deductor challan verification", "3. Return filing on TRACES", "4. Issue Form 16A certificates"],
                "required_documents": ["Deductor TAN number", "Payment challan details & PAN of deductees"],
                "faqs": [
                    {"question": "Is TDS applicable on property purchase above ₹50 Lakhs?", "answer": "Yes, 1% TDS under Sec 194-IA must be deducted by the buyer on property purchase above ₹50 Lakhs."}
                ]
            },
            {
                "name": "Accounting & Bookkeeping",
                "icon": "📒",
                "short_description": "Complete accounting, bookkeeping, ledger maintenance, and financial reporting for real estate firms.",
                "detailed_description": "Maintain accurate financial accounts for your real estate business. Complete bookkeeping, Profit & Loss statements, Balance Sheet preparation, and bank reconciliation by professional accountants.\n\nDisclaimer: Accounting reports are prepared based on records provided by the client.",
                "benefits": ["Clean financial records", "Audit-ready books of account", "Real-time P&L visibility", "Streamlined tax filing"],
                "whats_included": ["Tally / Zoho Books ledger entry", "Bank statement reconciliation", "Monthly Profit & Loss statement", "Balance sheet preparation"],
                "how_it_works": ["1. Share bills, invoices & bank statements", "2. Accountant inputs entries", "3. Monthly reconciliation", "4. Financial statements delivery"],
                "required_documents": ["Bank statements", "Commission invoices & expense vouchers"],
                "faqs": [
                    {"question": "What accounting software is used?", "answer": "We support Tally Prime, Zoho Books, and QuickBooks."}
                ]
            }
        ]
    },
    {
        "category_name": "Legal & Documentation Services",
        "icon": "⚖️",
        "description": "Expert legal assistance for rental agreements, sale deeds, property title search, due diligence, and e-stamping.",
        "services": [
            {
                "name": "Rental Agreement",
                "icon": "📜",
                "short_description": "Legally compliant 11-month residential and commercial rental agreements with e-stamp paper.",
                "detailed_description": "Draft legally valid 11-month rental agreements formatted to protect both owner and tenant interests. Includes e-stamp paper, custom clause additions, and doorstep execution.",
                "benefits": ["Legally enforceable agreement", "Includes e-stamp paper", "Custom clauses for notice & deposit", "Doorstep delivery option"],
                "whats_included": ["Legal agreement drafting", "E-stamp paper procurement", "Landlord & tenant clause customization", "Digital PDF & print delivery"],
                "how_it_works": ["1. Fill rental details form", "2. Agreement drafting & review", "3. E-stamping & printing", "4. Signature execution & delivery"],
                "required_documents": ["Landlord & Tenant Aadhaar / PAN", "Property Address proof & electricity bill"],
                "faqs": [
                    {"question": "Is an 11-month rental agreement mandatory to register?", "answer": "11-month agreements do not mandate sub-registrar registration under Registration Act Sec 17."}
                ]
            },
            {
                "name": "Leave & License Agreement",
                "icon": "📑",
                "short_description": "Registered Leave and License agreement drafting and government registration assistance.",
                "detailed_description": "Draft and register official Leave and License agreements with the government sub-registrar office. Essential for formal residential tenancies and corporate leases.",
                "benefits": ["Government registered validity", "Stronger legal protection for owners", "Biometric verification option", "Accepted by passport & bank authorities"],
                "whats_included": ["Legal drafting as per Rent Control Act", "Stamp duty & registration fee calculation", "Biometric appointment coordination", "Registered document delivery"],
                "how_it_works": ["1. Submit party details & agreement terms", "2. Draft review & government fee payment", "3. Biometric verification execution", "4. Registered agreement copy delivery"],
                "required_documents": ["Landlord, Tenant & 2 Witness Aadhaar cards", "Property index II / Electricity bill"],
                "faqs": [
                    {"question": "Can biometric verification be done at home?", "answer": "Yes, doorstep biometric verification is available in select cities."}
                ]
            },
            {
                "name": "Sale Deed Preparation",
                "icon": "📄",
                "short_description": "Professional drafting of Property Sale Deeds by experienced real estate advocate.",
                "detailed_description": "Ensure legal title transfer precision with professionally drafted Sale Deeds. Prepared by expert property advocates to cover schedule of property, consideration amount, indemnity clauses, and vacant possession terms.\n\nDisclaimer: Legal drafting is performed by qualified advocates.",
                "benefits": ["Watertight legal drafting", "Protects buyer & seller rights", "Includes clear property boundaries schedule", "Prevents future legal disputes"],
                "whats_included": ["Advocate consultation & drafting", "Custom indemnity & warranty clauses", "Schedule of property specification", "Draft review & revisions"],
                "how_it_works": ["1. Share property chain & agreement terms", "2. Legal draft preparation by advocate", "3. Client & lawyer review", "4. Final execution copy delivery"],
                "required_documents": ["Prior Title Deed & Index II", "Agreement for Sale", "Buyer & Seller Aadhaar & PAN"],
                "faqs": [
                    {"question": "What is the difference between Agreement for Sale and Sale Deed?", "answer": "Agreement for Sale commits future transfer; Sale Deed actually executes immediate title transfer."}
                ]
            },
            {
                "name": "Sale Deed Registration Assistance",
                "icon": "🏛️",
                "short_description": "End-to-end guidance and representation at the Sub-Registrar office for property registration.",
                "detailed_description": "Hassle-free property registration assistance at the Sub-Registrar office. We handle token booking, stamp duty payment calculation, document presentation, and index II collection.",
                "benefits": ["Guided sub-registrar appointment", "Zero queue delays", "Accurate stamp duty payment", "Same-day Index II collection"],
                "whats_included": ["Government fee & stamp duty challan generation", "Sub-registrar token booking", "On-site legal executive assistance", "Registered Sale Deed & Index II collection"],
                "how_it_works": ["1. Document verification & challan payment", "2. Sub-registrar appointment booking", "3. On-site execution & biometric entry", "4. Collect registered deed"],
                "required_documents": ["Drafted Sale Deed", "Stamp Duty Payment Challan", "Buyer, Seller & Witness Original IDs"],
                "faqs": [
                    {"question": "Are witnesses required at the Sub-Registrar office?", "answer": "Yes, 2 witnesses with original Aadhaar cards must be present."}
                ]
            },
            {
                "name": "Power of Attorney (Sale / Rental)",
                "icon": "📜",
                "short_description": "Drafting and registration of General (GPA) or Special Power of Attorney (SPA) for property management.",
                "detailed_description": "Authorize a trusted representative to manage, rent, or sell your property via General Power of Attorney (GPA) or Special Power of Attorney (SPA). Essential for NRIs and outstation property owners.\n\nDisclaimer: POA drafting and registration are subject to Indian Stamp Act and Registration Act rules.",
                "benefits": ["Ideal for NRI & outstation owners", "Specific legal power delegation", "Registered POA validity", "Prevents misuse clauses"],
                "whats_included": ["GPA / SPA legal drafting", "Embassy attestation guidance (for NRIs)", "E-stamping & registration guidance", "Execution support"],
                "how_it_works": ["1. Define power delegation scope", "2. Legal drafting of POA", "3. E-stamping & notary/registration", "4. Delivery of executed POA"],
                "required_documents": ["Principal & Attorney ID & Address Proofs", "Property Ownership Documents"],
                "faqs": [
                    {"question": "Can an NRI execute a Power of Attorney from abroad?", "answer": "Yes, via Indian Embassy/Consulate attestation followed by adjudication in India."}
                ]
            },
            {
                "name": "Agreement for Sale",
                "icon": "📝",
                "short_description": "Legally binding Agreement for Sale drafting detailing advance payment, terms, and closing timeline.",
                "detailed_description": "Draft a comprehensive Agreement for Sale securing the property deal terms between buyer and seller. Outlines advance booking token, payment schedule, possession timeline, default penalties, and RERA disclosures.",
                "benefits": ["Secures advance token payment", "Clear milestone payment schedule", "Default penalty protection clauses", "RERA compliant format"],
                "whats_included": ["Legal agreement drafting", "Payment schedule table", "Default & cancellation terms", "Draft review consultation"],
                "how_it_works": ["1. Submit deal terms & payment stages", "2. Draft preparation by advocate", "3. Both parties review draft", "4. Execution on stamp paper"],
                "required_documents": ["Buyer & Seller ID Details", "Prior Property Chain Papers", "Payment Token Receipt"],
                "faqs": [
                    {"question": "Is Agreement for Sale required for bank home loan?", "answer": "Yes, banks require an executed Agreement for Sale to process home loan sanction."}
                ]
            },
            {
                "name": "MOU Preparation",
                "icon": "🤝",
                "short_description": "Memorandum of Understanding (MOU) drafting for real estate partnerships, joint ventures, and token deals.",
                "detailed_description": "Draft clear Memorandums of Understanding (MOU) for joint venture property developments, investor partnerships, channel partner tie-ups, or initial token advance commitments.",
                "benefits": ["Clarity on partner roles & capital", "Legally sound framework", "Confidentiality & dispute resolution terms", "Quick execution format"],
                "whats_included": ["Custom MOU legal drafting", "Role & profit-share clause inclusion", "Confidentiality NDA terms", "Final execution copy"],
                "how_it_works": ["1. Intake partnership / deal objectives", "2. Draft preparation by legal team", "3. Partner review & feedback", "4. Final signing on stamp paper"],
                "required_documents": ["Partner / Entity ID & Address proofs", "Commercial terms sheet"],
                "faqs": [
                    {"question": "Is an MOU legally binding in court?", "answer": "An MOU is binding if it contains clear intent, consideration, and executed contract elements."}
                ]
            },
            {
                "name": "Possession Letter",
                "icon": "🔑",
                "short_description": "Official Possession Letter drafting for handover of property from builder/seller to buyer.",
                "detailed_description": "Draft a formal Possession Letter documenting the official handover of property keys, physical possession, pending checklist inspection, and utility meter readings.",
                "benefits": ["Official record of key handover", "Documents utility meter readings", "Clarity on maintenance start date", "Avoids possession date disputes"],
                "whats_included": ["Formal possession letter template", "Utility meter & key inventory checklist", "Sign-off documentation", "PDF delivery"],
                "how_it_works": ["1. Input property & party details", "2. Generate formal possession letter", "3. Physical site sign-off", "4. Record retention"],
                "required_documents": ["Sale Deed / Allotment Letter", "Buyer & Seller ID details"],
                "faqs": [
                    {"question": "Who signs the possession letter?", "answer": "Both the builder/seller and the buyer sign upon physical key handover."}
                ]
            },
            {
                "name": "NOC Preparation",
                "icon": "📋",
                "short_description": "No Objection Certificate (NOC) drafting for society transfer, builder transfer, and utility connections.",
                "detailed_description": "Draft valid No Objection Certificates (NOC) required from Housing Societies, Builders, Landlords, or Co-owners for property sale, rental, renovation, or electricity meter transfer.",
                "benefits": ["Standard legal affidavit format", "Accepted by societies & authorities", "Fast turnaround", "Clear non-encumbrance statement"],
                "whats_included": ["NOC legal draft preparation", "Specific purpose customization", "Stamp paper / Affidavit formatting", "Final PDF delivery"],
                "how_it_works": ["1. Select NOC purpose & details", "2. Legal draft generation", "3. Review & print on stamp paper", "4. Execution by issuing party"],
                "required_documents": ["Property details & issuing party ID", "Purpose details (Sale / Rent / Electricity)"],
                "faqs": [
                    {"question": "Is society NOC required for flat sale?", "answer": "Most cooperative housing societies require an NOC before final membership transfer."}
                ]
            },
            {
                "name": "Affidavit & Undertaking",
                "icon": "⚖️",
                "short_description": "Legal affidavits, indemnity bonds, and undertakings drafted and notarized for property transactions.",
                "detailed_description": "Prepare legally valid affidavits, self-declarations, name change affidavits, loss of document affidavits, and indemnity bonds executed on stamp paper and notarized.",
                "benefits": ["Notarized legal validity", "Accepted by govt & municipal bodies", "Fast same-day turnaround", "Covers lost document scenarios"],
                "whats_included": ["Affidavit drafting", "E-stamp paper procurement", "Notary public attestation", "Digital & physical delivery"],
                "how_it_works": ["1. Submit statement details", "2. Draft preparation & stamp printing", "3. Notary attestation", "4. Document dispatch"],
                "required_documents": ["Deponent Aadhaar & PAN", "Factual statement details"],
                "faqs": [
                    {"question": "Is notary attestation included?", "answer": "Yes, notarized affidavits with advocate stamp are provided."}
                ]
            },
            {
                "name": "Legal Notice",
                "icon": "📜",
                "short_description": "Issuance of formal Legal Notice by property advocate for rent default, contract breach, or property dispute.",
                "detailed_description": "Issue an official Legal Notice drafted by a senior property advocate for tenant rent default, illegal occupation, builder delivery delay, or seller contract breach.\n\nDisclaimer: Legal notices are dispatched by enrolled advocates on official legal letterhead.",
                "benefits": ["Drafted by senior property advocate", "Official legal letterhead dispatch", "Registered AD post tracking", "Strong legal leverage for settlement"],
                "whats_included": ["Advocate case consultation", "Formal legal notice drafting", "Dispatch via Registered Post AD", "Proof of delivery & tracking"],
                "how_it_works": ["1. Case facts & document review", "2. Advocate drafts legal notice", "3. Client approval", "4. Dispatch via Registered Post"],
                "required_documents": ["Breached Agreement copy", "Communication logs & default proof", "Opposing party full name & address"],
                "faqs": [
                    {"question": "How much response time is given in a legal notice?", "answer": "Standard legal notices provide 15 to 30 days for compliance."}
                ]
            },
            {
                "name": "Property Title Search",
                "icon": "🔍",
                "short_description": "Comprehensive 30-year property title search and Search Report by advocate.",
                "detailed_description": "Ensure the seller has clear, marketable title. Our property legal team conducts a 13 to 30-year search at the Sub-Registrar office to verify ownership chain, encumbrances, and mortgages.\n\nDisclaimer: Search report is based on public records available at the Sub-Registrar office.",
                "benefits": ["Uncovers hidden mortgages & disputes", "30-year title chain verification", "Advocate Title Search Report", "Essential for home loan approval"],
                "whats_included": ["Sub-Registrar office record search", "Index II & Revenue record verification", "Search Report by legal advocate", "Encumbrance check certificate"],
                "how_it_works": ["1. Property survey & document submission", "2. Sub-registrar office record inspection", "3. Advocate title evaluation", "4. Search Report delivery"],
                "required_documents": ["Copy of latest Sale Deed / Index II", "Property survey number & city survey details"],
                "faqs": [
                    {"question": "Why is a 30-year title search necessary?", "answer": "It verifies uninterrupted legal ownership chain and rules out undisclosed family or bank claims."}
                ]
            },
            {
                "name": "Property Due Diligence",
                "icon": "🛡️",
                "short_description": "Full legal due diligence checking project approvals, RERA status, land use, and litigation risk.",
                "detailed_description": "Protect your capital investment. Complete legal due diligence auditing property land conversion (NA), municipal building approvals, RERA compliance, litigation history, and environmental NOCs.\n\nDisclaimer: Legal opinion is based on documents provided and public registry records.",
                "benefits": ["Risk-free property purchase", "RERA & municipal approval audit", "Litigation check in local courts", "Comprehensive legal risk score"],
                "whats_included": ["Land title & NA status audit", "RERA registration & complaint verification", "Building plan approval check", "Formal Written Legal Opinion Report"],
                "how_it_works": ["1. Property document bundle collection", "2. Comprehensive legal audit", "3. Court & RERA record search", "4. Detailed Due Diligence Report delivery"],
                "required_documents": ["Master Title Deeds & NA Order", "Building Plan Approval & RERA Certificate", "7/12 Extract / Khata Certificate"],
                "faqs": [
                    {"question": "What is verified in due diligence?", "answer": "Land ownership, NA order, commencement certificate, approved plans, RERA status, and pending court cases."}
                ]
            },
            {
                "name": "Document Verification",
                "icon": "✅",
                "short_description": "Fast-track legal verification of property documents before paying booking advances.",
                "detailed_description": "Get property papers verified by a legal expert within 48 hours before paying booking tokens or advance payments to sellers or builders.",
                "benefits": ["Quick 48-hour turn-around", "Prevents advance token loss", "Expert advocate opinion", "Affordable safety check"],
                "whats_included": ["Title deed & ownership check", "Seller identity verification", "Encumbrance overview", "Advocate consultation call"],
                "how_it_works": ["1. Upload property document scans", "2. Legal review by advocate", "3. Written verification summary", "4. Consultation call"],
                "required_documents": ["Sale Deed / Allotment Letter scan", "7/12 Extract / Property Card scan"],
                "faqs": [
                    {"question": "How fast is document verification done?", "answer": "Fast-track verification is completed within 24 to 48 hours."}
                ]
            },
            {
                "name": "E-Stamping & Stamp Duty Assistance",
                "icon": "💳",
                "short_description": "Calculation and online procurement of official e-stamp papers for agreements.",
                "detailed_description": "Accurate calculation and instant online procurement of official SHCIL E-Stamp papers for agreements, sale deeds, MOUs, and affidavits as per state stamp duty rates.",
                "benefits": ["Official Stock Holding (SHCIL) e-stamps", "Accurate stamp duty calculation", "Zero overcharging", "Same-day e-stamp generation"],
                "whats_included": ["State-wise stamp duty calculation", "Official SHCIL e-stamp paper generation", "Document printing service", "Doorstep / Digital delivery"],
                "how_it_works": ["1. Select state & document type", "2. System calculates exact stamp duty", "3. Online payment & e-stamp generation", "4. E-stamp paper delivery"],
                "required_documents": ["First Party & Second Party Names", "Consideration Amount & Document Type"],
                "faqs": [
                    {"question": "Are e-stamp papers valid across India?", "answer": "Yes, e-stamp papers generated through authorized SHCIL centers are legally valid."}
                ]
            }
        ]
    },
    {
        "category_name": "Verification & Compliance Services",
        "icon": "🔍",
        "description": "Thorough tenant police verification, KYC checks, employment verification, and credit report assistance.",
        "services": [
            {
                "name": "Tenant Police Verification",
                "icon": "👮",
                "short_description": "End-to-end assistance for mandatory tenant police verification filing.",
                "detailed_description": "Comply with legal mandates for tenant verification. We assist property owners in completing online or offline tenant police verification filing with local police departments.\n\nDisclaimer: Verification acknowledgment is issued by the respective State Police Department.",
                "benefits": ["Avoid police penalty notices", "Enhances property safety", "Official police acknowledgment", "Hassle-free process"],
                "whats_included": ["Police verification form filing", "Tenant ID & background check", "Submission at police portal / station", "Police acknowledgment receipt"],
                "how_it_works": ["1. Upload tenant & owner details", "2. Application drafting & portal filing", "3. Police verification submission", "4. Acknowledgment receipt delivery"],
                "required_documents": ["Tenant Photo, Aadhaar & PAN", "Owner Aadhaar & Property Address Proof", "Registered / Executed Rent Agreement"],
                "faqs": [
                    {"question": "Is tenant police verification compulsory by law?", "answer": "Yes, under Sec 188 IPC, failing to verify tenants is a punishable offense in most cities."}
                ]
            },
            {
                "name": "Offline Police Verification Assistance",
                "icon": "📋",
                "short_description": "Physical application filing and police station visit assistance for tenant verification.",
                "detailed_description": "For areas requiring physical station submission, our field executive assists in completing the physical police verification form, submitting documents, and obtaining the stamped station acknowledgment.",
                "benefits": ["Local field executive assistance", "Physical station submission done for you", "Stamped station receipt", "Ideal for non-online police jurisdictions"],
                "whats_included": ["Physical form filling & photo attestation", "Executive visit to local police station", "Submission tracking", "Physical stamped acknowledgment delivery"],
                "how_it_works": ["1. Collect physical documents & photos", "2. Field executive visits local police station", "3. Submission & officer acknowledgment", "4. Delivery of stamped copy"],
                "required_documents": ["Tenant physical passport photos", "Tenant & Owner signed verification form", "Aadhaar & Rent Agreement copies"],
                "faqs": [
                    {"question": "Which cities require physical police verification?", "answer": "Jurisdictions without online citizen portals require physical station submission."}
                ]
            },
            {
                "name": "Online Police Verification Assistance",
                "icon": "💻",
                "short_description": "Fast-track online portal submission for state tenant police verification.",
                "detailed_description": "Submit tenant police verification electronically through official state citizen portals (e.g. Maharashtra Digital Police, Delhi Police, Karnataka Police portal) without visiting the police station.",
                "benefits": ["100% online process", "No police station visit required", "Fast electronic acknowledgment", "Trackable online status"],
                "whats_included": ["State police portal account creation", "Data & photo upload", "Government fee payment", "Downloadable official PDF receipt"],
                "how_it_works": ["1. Upload digital photos & ID scans", "2. Executive files application on police portal", "3. System generates application reference", "4. Download official police acknowledgment"],
                "required_documents": ["Passport size photos (JPEG)", "Aadhaar / Passport scans of Tenant & Owner", "Rent agreement copy"],
                "faqs": [
                    {"question": "How long does online verification acknowledgment take?", "answer": "Electronic submission receipts are generated instantly or within 24 to 48 hours."}
                ]
            },
            {
                "name": "Tenant KYC Verification",
                "icon": "👤",
                "short_description": "Comprehensive identity, address, and criminal record verification for prospective tenants.",
                "detailed_description": "Verify prospective tenants before signing rental agreements. Includes real-time Aadhaar/PAN authentication, court record checks, and permanent address verification.",
                "benefits": ["Screen out fraudulent tenants", "Instant identity authentication", "Court case & criminal record check", "Detailed tenant risk report"],
                "whats_included": ["Aadhaar & PAN instant verification", "Civil & criminal court database check", "Defaulter database screening", "Comprehensive KYC Summary Report"],
                "how_it_works": ["1. Tenant consent & document intake", "2. Automated API & court record check", "3. Verification analysis", "4. Share Tenant KYC Report with owner"],
                "required_documents": ["Tenant consent form", "Tenant Aadhaar & PAN details"],
                "faqs": [
                    {"question": "Is tenant consent required for KYC checks?", "answer": "Yes, explicit tenant consent is mandatory under DPDP data privacy regulations."}
                ]
            },
            {
                "name": "Owner KYC Verification",
                "icon": "🏠",
                "short_description": "Verify property ownership, identity, and title documents for prospective tenants and buyers.",
                "detailed_description": "Protect tenants and buyers from fake landlord scams. We verify the property owner's government ID, electricity bill, and property ownership tax receipts before signing or transferring deposits.",
                "benefits": ["Protects tenants from fake owner scams", "Verifies true property ownership", "Prevents deposit fraud", "Instant peace of mind"],
                "whats_included": ["Owner identity verification", "Property tax / Electricity bill cross-check", "Index II / Ownership matching", "Owner KYC Certificate"],
                "how_it_works": ["1. Submit owner ID & property bill", "2. Cross-verify with municipal records", "3. Ownership match check", "4. Issue Owner KYC Report"],
                "required_documents": ["Owner Aadhaar & PAN", "Property Tax Receipt / Electricity Bill"],
                "faqs": [
                    {"question": "Why should tenants verify owner KYC?", "answer": "It ensures the person collecting rent/deposit is the legitimate property owner or authorized attorney."}
                ]
            },
            {
                "name": "Government ID Verification",
                "icon": "🆔",
                "short_description": "Real-time verification of Aadhaar, PAN, Passport, Voter ID, and Driving License.",
                "detailed_description": "Instant API-based verification of government-issued IDs for real estate transactions. Validates Aadhaar (via OTP/QR), PAN status, Passport authenticity, and Driving License records.",
                "benefits": ["Instant ID authentication", "Eliminates forged documents", "API-driven accuracy", "Supports remote onboarding"],
                "whats_included": ["PAN status & name match check", "Aadhaar offline XML / QR verification", "Passport / Driving License verification", "ID Match Report"],
                "how_it_works": ["1. Submit document numbers with consent", "2. Instant API check with NSDL/UIDAI databases", "3. Receive match score", "4. Generate verification report"],
                "required_documents": ["User ID numbers (PAN/Aadhaar/Passport)", "Subject consent"],
                "faqs": [
                    {"question": "Is Aadhaar verification secure?", "answer": "Yes, performed via masked UIDAI API methods compliant with privacy norms."}
                ]
            },
            {
                "name": "Address Verification",
                "icon": "📍",
                "short_description": "Physical doorstep or digital GPS address verification of tenants, buyers, and brokers.",
                "detailed_description": "Confirm the physical residency of prospective tenants, buyers, or employees. Includes physical doorstep visit by field agents or geo-tagged digital selfie verification.",
                "benefits": ["Confirms physical existence at address", "Prevents false address declarations", "Field agent photo proof", "Detailed address verification report"],
                "whats_included": ["Physical doorstep visit by field officer", "Neighbor reference check", "Geo-tagged photo of residence", "Verification report"],
                "how_it_works": ["1. Address details intake", "2. Field executive assigned", "3. Physical visit & neighbor check", "4. Report delivery"],
                "required_documents": ["Full address with landmark", "Subject contact number"],
                "faqs": [
                    {"question": "How long does physical address verification take?", "answer": "Physical visits are completed within 2 to 4 business days."}
                ]
            },
            {
                "name": "Employment Verification",
                "icon": "💼",
                "short_description": "Verify corporate employment status, job title, and monthly income proof of tenant applicants.",
                "detailed_description": "Verify tenant employment credentials to ensure rental payment capability. We contact corporate HR departments, verify official email domain, and validate salary slip authenticity.",
                "benefits": ["Confirms stable income source", "Verifies official company employment", "Prevents fake salary slip scams", "Reduces rent default risk"],
                "whats_included": ["Official corporate email verification", "HR employment confirmation call", "Salary slip authenticity check", "Employment Verification Report"],
                "how_it_works": ["1. Submit employer & HR contact info", "2. Verification team contacts HR", "3. Official domain email check", "4. Report delivery"],
                "required_documents": ["Tenant Employee ID Card", "Offer Letter / Salary Slips", "HR contact details"],
                "faqs": [
                    {"question": "Will HR disclose employee salary details?", "answer": "HR departments confirm employment status, designation, and active employment tenure with consent."}
                ]
            },
            {
                "name": "Property Document Verification",
                "icon": "📄",
                "short_description": "Authenticity check of sale deeds, Index II, approved plans, and title documents.",
                "detailed_description": "Verify the authenticity of property papers before buying or renting. Our team cross-checks Sale Deeds, Index II copies, Property Cards, and 7/12 extracts against government registrar databases.",
                "benefits": ["Detects forged property papers", "Cross-checks sub-registrar records", "Validates Index II entry", "Ensures genuine transaction"],
                "whats_included": ["Index II online verification", "Property card & 7/12 cross-check", "Document completeness check", "Verification Summary Report"],
                "how_it_works": ["1. Upload property document scans", "2. Cross-verification with public land records", "3. Analysis of document seals & numbers", "4. Report issuance"],
                "required_documents": ["Property Sale Deed scan", "Index II & Property Tax receipt scan"],
                "faqs": [
                    {"question": "Can fake Index II documents be identified?", "answer": "Yes, by cross-checking the registration number and volume page against official sub-registrar data."}
                ]
            },
            {
                "name": "Company / Firm Verification",
                "icon": "🏢",
                "short_description": "Corporate registration, MCA status, GSTIN, and director background checks for business tenants.",
                "detailed_description": "Conduct thorough corporate background checks for commercial leases or B2B partnerships. Includes MCA portal check, Director Identification Number (DIN) check, active GSTIN verification, and litigation check.",
                "benefits": ["Ensures legitimate corporate tenant", "Verifies company active MCA status", "Checks director background", "Prevents commercial lease defaults"],
                "whats_included": ["MCA Company Master Data check", "DIN & Director verification", "Active GSTIN status check", "Corporate Credit Profile Summary"],
                "how_it_works": ["1. Submit Company CIN / GSTIN", "2. Database pull from MCA & GST portals", "3. Director litigation screening", "4. Deliver Corporate Verification Report"],
                "required_documents": ["Company Name / CIN / GSTIN", "Authorized Signatory details"],
                "faqs": [
                    {"question": "What is verified for a Private Limited company?", "answer": "Active MCA registration, paid-up capital, active directors, registered address, and GST filing status."}
                ]
            },
            {
                "name": "CIBIL / Credit Report Assistance (with consent)",
                "icon": "📊",
                "short_description": "Assist home loan applicants and tenants in obtaining CIBIL credit score reports with explicit consent.",
                "detailed_description": "Help home loan buyers and prospective tenants check their CIBIL credit score and credit history. Includes credit report interpretation, score improvement guidance, and dispute resolution.\n\nDisclaimer: Credit reports are pulled strictly upon receiving explicit data consent from the individual as per RBI and CIBIL guidelines.",
                "benefits": ["Know your credit score before applying", "Identifies credit report errors", "Score improvement roadmap", "Prevents loan rejections"],
                "whats_included": ["Official CIBIL credit report pull", "Detailed score & payment history breakdown", "Credit score improvement consultation", "Dispute resolution guidance"],
                "how_it_works": ["1. User submits PAN & mobile with OTP consent", "2. Official CIBIL score pull", "3. Credit report analysis", "4. Consultation & action plan"],
                "required_documents": ["PAN Card & Aadhaar", "Mobile number linked with Aadhaar"],
                "faqs": [
                    {"question": "What CIBIL score is required for home loans?", "answer": "A CIBIL score of 750 or higher is considered excellent for low interest rate home loans."}
                ]
            }
        ]
    },
    {
        "category_name": "Property & Post-Sales Services",
        "icon": "🛠️",
        "description": "End-to-end property maintenance, home cleaning, pest control, interior design, renovation, and rental collection.",
        "services": [
            {
                "name": "Property Management",
                "icon": "🔑",
                "short_description": "End-to-end property oversight including tenant management, maintenance, inspection, and rent collection.",
                "detailed_description": "Complete peace of mind for property owners and NRI landlords. We manage your property end-to-end: finding verified tenants, collecting rent, managing repairs, and conducting periodic inspections.",
                "benefits": ["Hands-free property ownership", "Ideal for NRI & outstation owners", "Timely rent collection", "Regular property inspections"],
                "whats_included": ["Tenant onboarding & agreement", "Monthly rent collection & payout", "Routine maintenance supervision", "Periodic video inspection reports"],
                "how_it_works": ["1. Property onboarding & key handover", "2. Tenant matching & agreement", "3. Monthly rent collection & management", "4. Regular reports to owner"],
                "required_documents": ["Property Ownership papers", "Owner ID & Bank account details"],
                "faqs": [
                    {"question": "How do NRI owners receive rental updates?", "answer": "Monthly rental payouts are transferred electronically with inspection photo/video reports via email/WhatsApp."}
                ]
            },
            {
                "name": "Rental Collection Management",
                "icon": "💰",
                "short_description": "Automated monthly rent collection, payment reminders, and direct bank transfers to owners.",
                "detailed_description": "Never chase tenants for monthly rent again. Our system sends automated WhatsApp/SMS rent invoices, collects payments electronically, and remits rent directly to your bank account with receipt generation.",
                "benefits": ["Zero rent payment delays", "Automated rent invoices & receipts", "Direct bank transfers", "Late fee management"],
                "whats_included": ["Monthly digital rent invoice dispatch", "Multiple online payment options for tenants", "Direct bank transfer to owner", "Rent payment history ledger"],
                "how_it_works": ["1. Set monthly rent due date & amount", "2. Automated invoice sent to tenant", "3. Tenant pays online", "4. Instant credit to owner account"],
                "required_documents": ["Rent Agreement copy", "Owner bank account details"],
                "faqs": [
                    {"question": "What payment methods can tenants use?", "answer": "Tenants can pay via UPI, Net Banking, Credit Card, or Debit Card."}
                ]
            },
            {
                "name": "Property Inspection",
                "icon": "🔍",
                "short_description": "Comprehensive pre-purchase, pre-lease, and move-out property inspection with photo/video report.",
                "detailed_description": "Identify hidden property defects before buying or renting. Our technical team conducts detailed property inspections covering structural dampness, plumbing leaks, electrical wiring, doors/windows, and paint condition.",
                "benefits": ["Uncovers hidden property defects", "Detailed 100+ point checklist report", "High-res photo & video evidence", "Empowers price negotiation"],
                "whats_included": ["Full property walkthrough inspection", "Plumbing, electrical & dampness audit", "Itemized defect checklist report", "HD photo & video documentation"],
                "how_it_works": ["1. Schedule inspection appointment", "2. Engineer inspects property site", "3. Report compilation", "4. Detailed Inspection Report delivery"],
                "required_documents": ["Property location & key access", "Floor plan layout"],
                "faqs": [
                    {"question": "How long does a property inspection take?", "answer": "A thorough 2BHK/3BHK inspection takes approximately 2 to 3 hours on site."}
                ]
            },
            {
                "name": "Home Cleaning",
                "icon": "🧹",
                "short_description": "Deep home cleaning, move-in/move-out cleaning, and kitchen/bathroom sanitization.",
                "detailed_description": "Transform your apartment or villa into a sparkling clean home. Professional deep cleaning services including floor scrubbing, window cleaning, kitchen degreasing, bathroom sanitization, and sofa shampooing.",
                "benefits": ["Hassle-free move-in cleanliness", "Professional industrial equipment", "Eco-friendly cleaning chemicals", "Trained cleaning staff"],
                "whats_included": ["Deep cleaning of all rooms", "Kitchen cabinets & appliance degreasing", "Bathroom descaling & sanitization", "Balcony & window track cleaning"],
                "how_it_works": ["1. Select home size & slot", "2. Cleaning team arrives with equipment", "3. Thorough deep cleaning execution", "4. Customer inspection & handoff"],
                "required_documents": ["Property address & water/electricity access"],
                "faqs": [
                    {"question": "Are cleaning supplies brought by the team?", "answer": "Yes, our team brings all professional machinery, vacuums, and eco-friendly chemicals."}
                ]
            },
            {
                "name": "Painting & Renovation",
                "icon": "🎨",
                "short_description": "Interior and exterior house painting, waterproofing, and full home renovation services.",
                "detailed_description": "Refresh or overhaul your property with expert painting and renovation services. From single-room repainting and dampness waterproofing to complete home remodeling, kitchen modular upgrades, and flooring replacement.",
                "benefits": ["Asian Paints / Berger certified painters", "Laser measurement & clear pricing", "Waterproofing warranty", "On-time completion commitment"],
                "whats_included": ["Wall inspection & laser measurement", "Sanding, putty, primer & 2 coats paint", "Furniture masking & floor protection", "Post-painting cleanup"],
                "how_it_works": ["1. Book free site measurement visit", "2. Color consultation & quotation", "3. Masking & painting execution", "4. Final inspection & handover"],
                "required_documents": ["Property site access", "Color preferences"],
                "faqs": [
                    {"question": "Is furniture masking provided?", "answer": "Yes, all furniture and flooring are completely masked and protected before painting begins."}
                ]
            },
            {
                "name": "Plumbing & Electrical Services",
                "icon": "🔧",
                "short_description": "Licensed plumbers and electricians for property repairs, wiring, fixture installation, and leaks.",
                "detailed_description": "On-demand expert plumbers and electricians for all property maintenance needs. Fix water leaks, install geysers, repair electrical MCB DB boxes, replace light fixtures, and resolve drainage blockages.",
                "benefits": ["Background verified technicians", "Transparent standardized rates", "30-day service warranty", "Quick response time"],
                "whats_included": ["Diagnostic inspection", "Repair & fixture replacement", "Quality testing", "Service invoice with warranty"],
                "how_it_works": ["1. Book plumbing/electrical service slot", "2. Technician arrives with tools", "3. Problem diagnosis & price approval", "4. Repair execution & testing"],
                "required_documents": ["Property address & issue description"],
                "faqs": [
                    {"question": "Is there a warranty on repairs?", "answer": "Yes, all repair work comes with a 30-day service warranty."}
                ]
            },
            {
                "name": "Pest Control",
                "icon": "🐜",
                "short_description": "Eco-friendly pest control treatments for termites, cockroaches, bedbugs, and rodents.",
                "detailed_description": "Protect your property from damaging pests. Odorless, eco-friendly pest control treatments for cockroaches, termites, bedbugs, mosquitoes, and rodents with long-term service warranty.",
                "benefits": ["Odorless & herbal chemicals", "Safe for kids & pets", "Government approved pesticides", "Long-term protection warranty"],
                "whats_included": ["Full property inspection & spraying", "Gel baiting for cockroaches", "Anti-termite drilling & treatment (if selected)", "Follow-up visit"],
                "how_it_works": ["1. Select pest control package", "2. Certified technician site visit", "3. Treatment application", "4. Post-treatment guidelines"],
                "required_documents": ["Property address"],
                "faqs": [
                    {"question": "Do we need to vacate the house during pest control?", "answer": "Our advanced herbal gel treatments do not require you to vacate the premises."}
                ]
            },
            {
                "name": "Interior Design",
                "icon": "🛋️",
                "short_description": "Full home interior design, 3D visualization, modular kitchens, and custom wardrobe woodworking.",
                "detailed_description": "Turn your vacant flat into a dream home. Complete end-to-end interior design services: 3D design renders, modular kitchens, custom wardrobes, false ceilings, ambient lighting, and loose furniture.",
                "benefits": ["3D design visualization before execution", "10-year warranty on modular woodwork", "Factory-finish precision", "Dedicated project manager"],
                "whats_included": ["Space planning & 3D layout renders", "Modular kitchen & wardrobe manufacturing", "False ceiling & electrical lighting", "Site installation & handover"],
                "how_it_works": ["1. Designer consultation & site measurement", "2. 3D layout design & material selection", "3. Factory manufacturing of modules", "4. On-site installation & final handover"],
                "required_documents": ["Property floor plan & budget preference"],
                "faqs": [
                    {"question": "How long does a complete 2BHK interior project take?", "answer": "Complete interior execution takes approximately 45 to 60 days from design approval."}
                ]
            },
            {
                "name": "Furniture & Appliance Rental",
                "icon": "🛏️",
                "short_description": "Rent premium furniture, refrigerators, washing machines, TVs, and ACs for short/long term.",
                "detailed_description": "Furnish your home effortlessly without heavy capital expenditure. Rent stylish sofas, double beds, wardrobes, refrigerators, washing machines, and split ACs with free delivery and installation.",
                "benefits": ["Zero heavy upfront buying cost", "Free delivery & installation", "Free maintenance & relocation", "Flexible monthly tenure"],
                "whats_included": ["Selected furniture/appliance items", "Doorstep delivery & assembly", "Maintenance support", "Return pick-up on contract end"],
                "how_it_works": ["1. Select items & rental tenure", "2. KYC verification & contract signing", "3. Free delivery & installation", "4. Monthly rental payments"],
                "required_documents": ["KYC Aadhaar & PAN", "Current Rent Agreement / Address Proof"],
                "faqs": [
                    {"question": "What if an appliance breaks down during rental?", "answer": "Free repair or replacement is provided for normal operational faults."}
                ]
            },
            {
                "name": "Tenant Move-in / Move-out Support",
                "icon": "📦",
                "short_description": "Hassle-free packing and moving, key handover, inspection, and security deposit settlement support.",
                "detailed_description": "Smooth tenant transitions for landlords and renters. Complete support covering packing and moving, initial move-in property condition report, key handover, and final move-out inspection for deposit settlement.",
                "benefits": ["Stress-free tenant transitions", "Documented move-in/out condition report", "Prevents deposit deduction disputes", "Packers & Movers coordination"],
                "whats_included": ["Move-in / Move-out checklist inspection", "Photo documentation of property state", "Utility meter reading sign-off", "Deposit settlement summary sheet"],
                "how_it_works": ["1. Book transition date", "2. Inspector conducts walkthrough with tenant", "3. Document property condition & meter readings", "4. Issue formal handover report"],
                "required_documents": ["Rent Agreement copy", "Tenant & Owner contact details"],
                "faqs": [
                    {"question": "How does it help in deposit refund disputes?", "answer": "The initial move-in photo report acts as clear baseline proof of original property condition."}
                ]
            },
            {
                "name": "Property Maintenance",
                "icon": "🛠️",
                "short_description": "Annual property maintenance packages covering plumbing, electrical, carpentry, and painting upkeep.",
                "detailed_description": "Annual Maintenance Contracts (AMC) to keep your property in top condition year-round. Regular plumbing tune-ups, electrical safety checks, carpentry repairs, and touch-up painting.",
                "benefits": ["Year-round property upkeep", "Preventive maintenance visits", "Priority technician dispatch", "Significant cost savings over single jobs"],
                "whats_included": ["Quarterly preventive inspection visits", "Unlimited emergency repair calls", "Plumbing, electrical & carpentry coverage", "Discounted spare parts"],
                "how_it_works": ["1. Select property AMC plan", "2. Initial property health audit visit", "3. Scheduled quarterly preventive checkups", "4. On-demand repair calls"],
                "required_documents": ["Property address & owner details"],
                "faqs": [
                    {"question": "Does AMC cover spare part costs?", "answer": "Labor is 100% free under AMC; physical spare parts are charged at actual discounted rates."}
                ]
            },
            {
                "name": "Resale & Rental Assistance",
                "icon": "📈",
                "short_description": "Professional marketing and agent representation to resell or rent out your property at top market value.",
                "detailed_description": "Maximize rental yield or resale price for your property. We list your property across top portals, capture professional photography, screen prospective buyers/tenants, and negotiate the best deal value.",
                "benefits": ["Maximum rental yield & resale price", "Professional property marketing", "Pre-screened genuine buyers/tenants", "Complete paperwork assistance"],
                "whats_included": ["Professional property photo shoot", "Multi-portal premium listing placement", "Buyer/Tenant lead screening & site visits", "Deal closing & agreement support"],
                "how_it_works": ["1. Submit property details & price expectation", "2. Site visit & professional photography", "3. Marketing & buyer inquiry handling", "4. Deal negotiation & closing"],
                "required_documents": ["Ownership Title Copy / Index II", "Property photos & floor plan"],
                "faqs": [
                    {"question": "What is the brokerage fee for rental assistance?", "answer": "Standard brokerage is 1 month rent for rental lease, or 1-2% for property resale deals."}
                ]
            }
        ]
    }
]


class Command(BaseCommand):
    help = "Idempotently seeds all 8 categories and all 92 individual services within Partner Marketplace."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Starting Partner Marketplace Catalogue Seeding (8 Categories, 92 Individual Services)..."))

        total_categories = 0
        total_services = 0

        for cat_order, cat_data in enumerate(CATEGORIES_SERVICES_DATA, start=1):
            cat_name = cat_data["category_name"]
            cat_slug = slugify(cat_name)

            category, cat_created = ServiceCategory.objects.get_or_create(
                name=cat_name,
                defaults={
                    "slug": cat_slug,
                    "description": cat_data["description"],
                    "icon": cat_data["icon"],
                    "display_order": cat_order,
                    "approval_status": "APPROVED",
                    "is_published": True,
                    "is_active": True,
                    "seo_title": f"{cat_name} — Partner Marketplace | The Home First",
                    "meta_description": cat_data["description"]
                }
            )

            # Keep category attributes updated idempotently
            category.slug = cat_slug
            category.description = cat_data["description"]
            category.icon = cat_data["icon"]
            category.display_order = cat_order
            category.approval_status = "APPROVED"
            category.is_published = True
            category.is_active = True
            category.save()

            total_categories += 1

            for svc_order, svc_data in enumerate(cat_data["services"], start=1):
                svc_name = svc_data["name"]
                svc_slug = slugify(svc_name)

                # Ensure slug uniqueness across system
                existing_svc = Service.objects.filter(slug=svc_slug).exclude(name=svc_name).first()
                if existing_svc:
                    svc_slug = f"{svc_slug}-{cat_slug}"

                service, svc_created = Service.objects.get_or_create(
                    name=svc_name,
                    category=category,
                    defaults={
                        "slug": svc_slug,
                        "short_description": svc_data["short_description"],
                        "detailed_description": svc_data["detailed_description"],
                        "benefits": svc_data["benefits"],
                        "whats_included": svc_data["whats_included"],
                        "how_it_works": svc_data["how_it_works"],
                        "required_documents": svc_data["required_documents"],
                        "faqs": svc_data["faqs"],
                        "icon": svc_data["icon"],
                        "display_order": svc_order,
                        "approval_status": "APPROVED",
                        "is_active": True,
                        "is_published": True,
                        "is_featured": (svc_order <= 3) # Feature first 3 services per category
                    }
                )

                # Update attributes idempotently without creating duplicates
                service.category = category
                service.slug = svc_slug
                service.short_description = svc_data["short_description"]
                service.detailed_description = svc_data["detailed_description"]
                service.benefits = svc_data["benefits"]
                service.whats_included = svc_data["whats_included"]
                service.how_it_works = svc_data["how_it_works"]
                service.required_documents = svc_data["required_documents"]
                service.faqs = svc_data["faqs"]
                service.icon = svc_data["icon"]
                service.display_order = svc_order
                service.approval_status = "APPROVED"
                service.is_active = True
                service.is_published = True
                service.save()

                total_services += 1

        self.stdout.write(self.style.SUCCESS(
            f"Successfully seeded {total_categories} Categories and {total_services} Individual Services!"
        ))
