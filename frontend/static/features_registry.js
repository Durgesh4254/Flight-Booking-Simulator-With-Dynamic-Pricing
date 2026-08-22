/**
 * FLYEASE CENTRAL FEATURE REGISTRY
 * Centralized configuration of all product capabilities, services, tools & workflows.
 * Adding or updating a feature here automatically propagates to the Homepage Feature Discovery Hub,
 * category filters, search index, interactive highlights, and navigation links.
 */

window.FLYEASE_FEATURE_REGISTRY = [
  {
    id: "ai-assistant",
    title: "FlyEase AI Travel Assistant",
    category: "AI & Smart Travel",
    categoryKey: "ai",
    badge: "✨ NEW",
    badgeType: "new",
    icon: "fa-solid fa-wand-magic-sparkles",
    iconBg: "linear-gradient(135deg, #0284c7, #6366f1)",
    description: "Natural-language aviation intelligence powered by live database grounding for route finding, fare trends & visa rules.",
    benefits: [
      "Real-time database flight & deal grounding",
      "Answers baggage & document questions",
      "One-click direct flight booking"
    ],
    actionType: "js",
    actionTarget: "app.toggleAIChat()",
    ctaText: "Ask FlyEase AI",
    highlightTitle: "Conversational Travel Intelligence",
    highlightDesc: "Ask complex natural language questions like 'Find me the cheapest weekend flight to Dubai under ₹25,000' and get instant factual recommendations.",
    stats: "Llama 3.3 70B Grounded"
  },
  {
    id: "dynamic-pricing",
    title: "Real-Time Dynamic Pricing",
    category: "Deals & Pricing",
    categoryKey: "pricing",
    badge: "⚡ LIVE ALGO",
    badgeType: "hot",
    icon: "fa-solid fa-chart-line",
    iconBg: "linear-gradient(135deg, #4f46e5, #818cf8)",
    description: "Sophisticated pricing engine adjusting fares based on seat load factor, departure countdown, and booking trends.",
    benefits: [
      "Transparent base fare & tax breakdowns",
      "Dynamic load factor multipliers",
      "Live fare trajectory predictions"
    ],
    actionType: "scroll",
    actionTarget: "pricing-chart",
    ctaText: "Explore Fare Engine",
    highlightTitle: "Airline-Grade Pricing Algorithm",
    highlightDesc: "Experience how seat availability, lead time, and booking surges dynamically calculate live fares with complete transparency.",
    stats: "100% Deterministic"
  },
  {
    id: "seat-selection-3d",
    title: "Interactive 3D Seat Selection",
    category: "Booking",
    categoryKey: "booking",
    badge: "💺 3D CABIN",
    badgeType: "hot",
    icon: "fa-solid fa-couch",
    iconBg: "linear-gradient(135deg, #0ea5e9, #38bdf8)",
    description: "Full 3D aircraft cabin visualizer with interactive seat map, emergency exit upgrades, and live seat fee computation.",
    benefits: [
      "Window, aisle & extra-legroom tagging",
      "Interactive 3D orbit and zoom controls",
      "Real-time seat reservation locking"
    ],
    actionType: "link",
    actionTarget: "/#step-search",
    ctaText: "Select Your Seat",
    highlightTitle: "Immersive 3D Aircraft Cabin",
    highlightDesc: "Choose your favorite seat with full 3D spatial visualization. Rotate, zoom in, and inspect premium rows before confirming.",
    stats: "3D WebGL Canvas"
  },
  {
    id: "flight-comparison",
    title: "Smart Flight Comparison",
    category: "AI & Smart Travel",
    categoryKey: "ai",
    badge: "🚀 JUST ADDED",
    badgeType: "new",
    icon: "fa-solid fa-code-compare",
    iconBg: "linear-gradient(135deg, #06b6d4, #3b82f6)",
    description: "Side-by-side comparison matrix for up to 4 flights comparing prices, duration, baggage, amenities & carbon footprint.",
    benefits: [
      "Automated Best Value & Cheapest badges",
      "Side-by-side amenities & CO2 comparison",
      "Direct 1-click booking from comparison matrix"
    ],
    actionType: "link",
    actionTarget: "/#step-search",
    ctaText: "Compare Flights",
    highlightTitle: "Multi-Factor Side-by-Side Matrix",
    highlightDesc: "Never guess between flights again. Select up to 4 options and compare exact legroom, baggage allowance, WiFi, and dynamic fares in one table.",
    stats: "Up to 4 Flights"
  },
  {
    id: "route-visualizer-3d",
    title: "3D Flight Route & Globe",
    category: "Explore",
    categoryKey: "explore",
    badge: "🌍 THREE.JS",
    badgeType: "hot",
    icon: "fa-solid fa-earth-americas",
    iconBg: "linear-gradient(135deg, #10b981, #0ea5e9)",
    description: "Interactive Three.js 3D Earth globe rendering Great Circle orbital airways and animated cruising aircraft in real time.",
    benefits: [
      "Great Circle curved flight trajectories",
      "Live altitude, airspeed & distance telemetry",
      "WebGL animated airplane flight path"
    ],
    actionType: "js",
    actionTarget: "app.openRoute3DModal('BOM', 'DXB', '3.5')",
    ctaText: "Preview 3D Globe",
    highlightTitle: "Orbital Great Circle Visualizer",
    highlightDesc: "Experience your flight path in full 3D space with an orbital globe, atmospheric glow, and live airplane progress animation.",
    stats: "3D Orbital Canvas"
  },
  {
    id: "price-drop-alerts",
    title: "Price Drop Tracking & Alerts",
    category: "Deals & Pricing",
    categoryKey: "pricing",
    badge: "🔔 AUTOMATED",
    badgeType: "new",
    icon: "fa-solid fa-bell",
    iconBg: "linear-gradient(135deg, #f59e0b, #d97706)",
    description: "Automated fare monitoring with target price thresholds and instant transactional email notifications on price drops.",
    benefits: [
      "Custom target budget notification alerts",
      "Automated seat inventory price tracking",
      "One-click alert activation for any route"
    ],
    actionType: "js",
    actionTarget: "app.openPriceAlertModal()",
    ctaText: "Track Fares",
    highlightTitle: "Never Miss a Fare Drop",
    highlightDesc: "Set your target price for any route. As soon as seat inventory shifts or promotions trigger a price drop, you receive an instant email alert.",
    stats: "24/7 Monitoring"
  },
  {
    id: "destination-weather",
    title: "Live Destination Weather",
    category: "Explore",
    categoryKey: "explore",
    badge: "⛅ 5-DAY FORECAST",
    badgeType: "hot",
    icon: "fa-solid fa-cloud-sun",
    iconBg: "linear-gradient(135deg, #f97316, #fbbf24)",
    description: "Real-time meteorological conditions, temperature, humidity, wind velocity, and 5-day forecasts for all destinations.",
    benefits: [
      "Live temperature & feels-like calculations",
      "5-day meteorological weather forecast",
      "Best season to visit travel recommendations"
    ],
    actionType: "js",
    actionTarget: "app.openDestinationWeatherModal()",
    ctaText: "Check Weather",
    highlightTitle: "Destination Meteorological Intelligence",
    highlightDesc: "Inspect live weather, wind speeds, humidity, and upcoming 5-day forecasts before you pack your bags.",
    stats: "Global Weather Data"
  },
  {
    id: "visa-requirements",
    title: "Visa & Travel Requirements",
    category: "Safety & Support",
    categoryKey: "safety",
    badge: "🛂 OFFICIAL DOCS",
    badgeType: "hot",
    icon: "fa-solid fa-passport",
    iconBg: "linear-gradient(135deg, #0284c7, #38bdf8)",
    description: "Official visa policies, passport validity criteria, mandatory document checklists, and transit guidelines.",
    benefits: [
      "Domestic vs International policy resolution",
      "Required documents checklist with official links",
      "Clear transit & immigration guidelines"
    ],
    actionType: "js",
    actionTarget: "app.openTravelRequirementsModal()",
    ctaText: "Check Visa Rules",
    highlightTitle: "Instant Visa & Entry Clearance Info",
    highlightDesc: "Get clear guidelines on visa requirements, mandatory identification documents, and passport validity for any international route.",
    stats: "Official Regulations"
  },
  {
    id: "live-flight-radar",
    title: "Live Flight Radar & Telemetry",
    category: "Trips & Tickets",
    categoryKey: "trips",
    badge: "📡 TELEMETRY",
    badgeType: "new",
    icon: "fa-solid fa-satellite-dish",
    iconBg: "linear-gradient(135deg, #3b82f6, #1d4ed8)",
    description: "Live aircraft tracker providing real-time altitude, airspeed, distance remaining, gate, and flight progress indicators.",
    benefits: [
      "Cruising altitude & groundspeed telemetry",
      "Distance remaining & ETA progress bar",
      "Terminal & gate assignment updates"
    ],
    actionType: "js",
    actionTarget: "app.openLiveFlightTracker('FE-1024')",
    ctaText: "View Live Radar",
    highlightTitle: "Real-Time Aircraft Radar Tracking",
    highlightDesc: "Track your simulated flight in the air with real-time altitude, speed, remaining distance, and gate info on My Trips.",
    stats: "Live Telemetry"
  },
  {
    id: "deals-and-coupons",
    title: "Smart Deals & Promo Coupons",
    category: "Deals & Pricing",
    categoryKey: "pricing",
    badge: "🔥 UP TO 40% OFF",
    badgeType: "hot",
    icon: "fa-solid fa-tags",
    iconBg: "linear-gradient(135deg, #ef4444, #f59e0b)",
    description: "Special seasonal discounts, student/family packages, weekend flash offers, and instant coupon validation.",
    benefits: [
      "Verified promo codes with 1-click copy",
      "Category filters for Weekend, Family & Student",
      "Real-time checkout price recalculation"
    ],
    actionType: "link",
    actionTarget: "/deals/",
    ctaText: "Browse Special Deals",
    highlightTitle: "Curated Travel Discounts",
    highlightDesc: "Enjoy exclusive promo codes and flash sales. Copy codes directly and apply them during booking for instant fare savings.",
    stats: "200+ Active Deals"
  },
  {
    id: "explore-destinations",
    title: "Interactive Destination Finder",
    category: "Explore",
    categoryKey: "explore",
    badge: "🌴 EXPLORE",
    badgeType: "hot",
    icon: "fa-solid fa-compass",
    iconBg: "linear-gradient(135deg, #10b981, #059669)",
    description: "Explore without a fixed destination! Filter getaways by budget sliders, travel categories, and weekend windows.",
    benefits: [
      "Interactive budget slider (₹2,000 – ₹50,000)",
      "Beaches, Mountains, Cities & Heritage filters",
      "Instant 1-click flight search population"
    ],
    actionType: "scroll",
    actionTarget: "explore-no-dest",
    ctaText: "Explore Destinations",
    highlightTitle: "Where Can I Go? Finder",
    highlightDesc: "Don't know where to fly? Adjust your budget slider, pick your vibe (Beaches, Nature, Cities), and let FlyEase suggest top destinations.",
    stats: "50+ Global Hubs"
  },
  {
    id: "multiple-payments",
    title: "Multi-Gateway Secure Payment",
    category: "Payments",
    categoryKey: "payments",
    badge: "🔒 SECURE",
    badgeType: "hot",
    icon: "fa-solid fa-credit-card",
    iconBg: "linear-gradient(135deg, #6366f1, #4338ca)",
    description: "Simulated multi-channel checkout supporting Credit/Debit Cards, Instant UPI ID collect, Net Banking, and Wallets.",
    benefits: [
      "UPI ID live format validation",
      "Major Indian & Global Net Banking options",
      "Instant mock payment confirmation"
    ],
    actionType: "link",
    actionTarget: "/#step-search",
    ctaText: "Book & Pay",
    highlightTitle: "Seamless Multi-Method Checkout",
    highlightDesc: "Choose your preferred payment method from Cards, UPI, Net Banking, and Wallets with real-time field validation.",
    stats: "Zero-Latency Mock Gateway"
  },
  {
    id: "travel-insurance",
    title: "Comprehensive Travel Protection",
    category: "Safety & Support",
    categoryKey: "safety",
    badge: "🛡️ ₹499 COVER",
    badgeType: "hot",
    icon: "fa-solid fa-shield-halved",
    iconBg: "linear-gradient(135deg, #10b981, #047857)",
    description: "Integrated travel protection covering medical emergencies, trip delays, baggage loss, and seamless refund processing.",
    benefits: [
      "Trip delay & cancellation reimbursement",
      "Lost baggage protection & medical cover",
      "Integrated line item in official PDF E-Tickets"
    ],
    actionType: "link",
    actionTarget: "/#step-search",
    ctaText: "Learn About Protection",
    highlightTitle: "Worry-Free Travel Insurance",
    highlightDesc: "Add peace of mind to any trip for just ₹499 per passenger with comprehensive baggage, delay, and emergency medical coverage.",
    stats: "Full Policy Coverage"
  },
  {
    id: "cancellation-refunds",
    title: "Cancellation & Refund Engine",
    category: "Safety & Support",
    categoryKey: "safety",
    badge: "💰 INSTANT REFUNDS",
    badgeType: "hot",
    icon: "fa-solid fa-rotate-left",
    iconBg: "linear-gradient(135deg, #f43f5e, #be123c)",
    description: "Tiered cancellation fees based on departure countdown with automatic refund calculation and status tracking.",
    benefits: [
      "Automated refund computation (>48h: 90%, 24-48h: 70%)",
      "Instant booking status updates on My Trips",
      "Transactional cancellation & refund email dispatch"
    ],
    actionType: "link",
    actionTarget: "/dashboard/",
    ctaText: "Manage Bookings",
    highlightTitle: "Transparent Cancellation Policy",
    highlightDesc: "Cancel bookings easily from My Trips. Review exact refund eligibility based on departure time and receive refund confirmations.",
    stats: "Tiered Policy Algorithm"
  },
  {
    id: "pdf-eticket-email",
    title: "PDF E-Tickets & Notifications",
    category: "Trips & Tickets",
    categoryKey: "trips",
    badge: "📄 ATTACHED PDF",
    badgeType: "hot",
    icon: "fa-solid fa-file-pdf",
    iconBg: "linear-gradient(135deg, #e11d48, #9f1239)",
    description: "ReportLab-generated PDF E-Tickets with QR verification, seat tags, and automatic transactional email dispatch.",
    benefits: [
      "Printable official PDF E-Ticket generation",
      "Unique PNR barcode & QR verification URLs",
      "Responsive HTML emails with attached PDF tickets"
    ],
    actionType: "link",
    actionTarget: "/dashboard/",
    ctaText: "View E-Tickets",
    highlightTitle: "Official Aviation E-Ticket Generation",
    highlightDesc: "Download high-resolution PDF tickets anytime with official airline logos, QR codes, seat assignments, and itemized fare receipts.",
    stats: "ReportLab PDF Engine"
  },
  {
    id: "flyease-passport",
    title: "FlyEase Travel Passport",
    category: "Rewards",
    categoryKey: "rewards",
    badge: "🏆 GAMIFICATION",
    badgeType: "hot",
    icon: "fa-solid fa-award",
    iconBg: "linear-gradient(135deg, #f59e0b, #b45309)",
    description: "Gamified traveler profile tracking total kilometers flown, destination stamps collected, and achievement milestones.",
    benefits: [
      "Collectible country & city passport stamps",
      "Total distance & flight milestones tracking",
      "Unlockable traveler badges (Frequent Flyer, Voyager)"
    ],
    actionType: "link",
    actionTarget: "/dashboard/",
    ctaText: "View My Passport",
    highlightTitle: "Traveler Gamification & Stamps",
    highlightDesc: "Track every flight you book, collect stamps for each airport you visit, and unlock milestones as your total distance grows.",
    stats: "Stamps & Achievements"
  },
  {
    id: "airport-mode",
    title: "Day-of-Travel Airport Mode",
    category: "Trips & Tickets",
    categoryKey: "trips",
    badge: "🛫 TRAVEL DAY",
    badgeType: "hot",
    icon: "fa-solid fa-plane-departure",
    iconBg: "linear-gradient(135deg, #0ea5e9, #6366f1)",
    description: "Dedicated airport mode providing live countdowns to boarding, baggage drop counters, security checkpoint reminders, and digital boarding passes.",
    benefits: [
      "Real-time countdown timer to departure",
      "Digital mobile boarding pass with QR code",
      "Gate & terminal wayfinding assistance"
    ],
    actionType: "link",
    actionTarget: "/dashboard/",
    ctaText: "Explore Airport Mode",
    highlightTitle: "Streamlined Airport Experience",
    highlightDesc: "Switch any active booking into Airport Mode on travel day for streamlined check-in, boarding countdowns, and quick boarding passes.",
    stats: "Mobile Friendly"
  },
  {
    id: "admin-operations-monitor",
    title: "Operations & Health Monitoring",
    category: "Safety & Support",
    categoryKey: "safety",
    badge: "⚙️ ADMIN ONLY",
    badgeType: "hot",
    icon: "fa-solid fa-server",
    iconBg: "linear-gradient(135deg, #475569, #1e293b)",
    description: "Enterprise system health dashboard monitoring Database, AI Service, Pricing Engine, Payment Gateway, and Weather API latency.",
    benefits: [
      "Live latency probes (ms) and uptime percentages",
      "Automated incident alert detection & action items",
      "Visa & Travel Requirement database CRUD manager"
    ],
    actionType: "link",
    actionTarget: "/admin-portal/system-monitor/",
    ctaText: "Open System Monitor",
    highlightTitle: "Live Infrastructure Health Probes",
    highlightDesc: "Monitor database query speeds, AI latency, payment gateway health, and automated operational alerts in real time.",
    stats: "Sub-millisecond Probes"
  }
];

/**
 * Helper to get all categories present in the registry
 */
window.FLYEASE_FEATURE_CATEGORIES = [
  { key: "all", label: "✨ All Capabilities", icon: "fa-solid fa-shapes" },
  { key: "booking", label: "✈️ Booking & 3D Seats", icon: "fa-solid fa-plane" },
  { key: "ai", label: "🤖 AI & Smart Travel", icon: "fa-solid fa-wand-magic-sparkles" },
  { key: "pricing", label: "💰 Deals & Pricing", icon: "fa-solid fa-tags" },
  { key: "explore", label: "🌍 Explore & Weather", icon: "fa-solid fa-compass" },
  { key: "payments", label: "💳 Payments", icon: "fa-solid fa-credit-card" },
  { key: "trips", label: "🎫 Trips & Radar", icon: "fa-solid fa-ticket" },
  { key: "safety", label: "🛡️ Safety & Support", icon: "fa-solid fa-shield-halved" },
  { key: "rewards", label: "🏆 Rewards & Passport", icon: "fa-solid fa-award" }
];
