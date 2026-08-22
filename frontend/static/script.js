/**
 * FlyEase SPA Controller — v3.0
 * Fixes: Select button, round-trip seat selection, confirmBooking itinerary payload,
 *        confirmation screen, and adds premium animated page transitions.
 */

/* =============================================
   NOTIFICATION SERVICE
   ============================================= */
class NotificationService {
  static show(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let icon = 'fa-info-circle';
    if (type === 'success') icon = 'fa-check-circle';
    if (type === 'error')   icon = 'fa-exclamation-circle';
    if (type === 'warning') icon = 'fa-exclamation-triangle';
    
    toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => { toast.classList.remove('show'); setTimeout(() => toast.remove(), 300); }, 3500);
  }
}

/* =============================================
   COMPLETE CINEMATIC AVIATION TRANSITION SYSTEM (V6.0)
   ============================================= */
class FlightTransitionManager {
  static getOverlay() {
    let overlay = document.getElementById('flight-transition-overlay');
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.id = 'flight-transition-overlay';
      document.body.appendChild(overlay);
    }
    return overlay;
  }

  static getAviationJetSvg(angle = 0) {
    return `
      <svg class="trans-jet-svg" style="transform: rotate(${angle}deg);" viewBox="0 0 512 512" fill="none" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="fuselageGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#ffffff"/>
            <stop offset="35%" stop-color="#f1f5f9"/>
            <stop offset="75%" stop-color="#94a3b8"/>
            <stop offset="100%" stop-color="#475569"/>
          </linearGradient>
          <linearGradient id="primaryWingGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#0284c7"/>
            <stop offset="50%" stop-color="#0369a1"/>
            <stop offset="100%" stop-color="#0c4a6e"/>
          </linearGradient>
          <radialGradient id="jetBurner" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#38bdf8"/>
            <stop offset="50%" stop-color="#818cf8"/>
            <stop offset="100%" stop-color="transparent"/>
          </radialGradient>
        </defs>
        <!-- Main Wings -->
        <path d="M256 160 L50 335 L80 355 L256 265 L432 355 L462 335 Z" fill="url(#primaryWingGrad)" opacity="0.98"/>
        <!-- Jet Engines & Afterburners -->
        <ellipse cx="175" cy="305" rx="14" ry="32" fill="url(#jetBurner)"/>
        <ellipse cx="337" cy="305" rx="14" ry="32" fill="url(#jetBurner)"/>
        <rect x="165" y="270" width="20" height="42" rx="10" fill="#334155"/>
        <rect x="327" y="270" width="20" height="42" rx="10" fill="#334155"/>
        <!-- Aerodynamic Fuselage -->
        <path d="M256 25 C240 85 234 175 234 345 L240 455 L256 475 L272 455 L278 345 C278 175 272 85 256 25 Z" fill="url(#fuselageGrad)"/>
        <!-- Cockpit Windshield -->
        <path d="M249 78 Q256 62 263 78 L266 104 Q256 108 246 104 Z" fill="#0f172a"/>
        <!-- Stabilizers -->
        <path d="M256 425 L165 475 L175 490 L256 462 L337 490 L347 475 Z" fill="url(#primaryWingGrad)"/>
        <path d="M253 375 L259 375 L258 460 L254 460 Z" fill="#38bdf8"/>
        <!-- Navigation Lights -->
        <circle cx="52" cy="336" r="4" fill="#ef4444"/>
        <circle cx="460" cy="336" r="4" fill="#10b981"/>
      </svg>
    `;
  }

  static isReducedMotion() {
    return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }
  
  static async playTransition(type, meta = {}) {
    return;
  }
}

class TransitionEngine {
  static async fadeOut(el) {
    if (!el) return;
    el.style.transition = 'opacity 0.25s cubic-bezier(0.4,0,0.2,1), transform 0.25s cubic-bezier(0.4,0,0.2,1)';
    el.style.opacity = '0';
    el.style.transform = 'translateY(8px)';
    await new Promise(r => setTimeout(r, 200));
  }

  static async fadeIn(el) {
    if (!el) return;
    el.style.opacity = '0';
    el.style.transform = 'translateY(12px) scale(0.98)';
    el.style.transition = 'opacity 0.35s cubic-bezier(0.2,0.8,0.2,1), transform 0.35s cubic-bezier(0.2,0.8,0.2,1)';
    void el.offsetWidth;
    el.style.opacity = '1';
    el.style.transform = 'translateY(0) scale(1)';
  }
}

/* =============================================
   MAIN APP
   ============================================= */
class FlightApp {
  constructor() {
    this.state = {
      // Departure flight & seats
      flight: null,
      seats: [],
      extraSeatFees: 0,
      selectedSeatTypes: [],

      // Return flight & seats (round-trip)
      returnFlight: null,
      returnSeats: [],
      returnExtraSeatFees: 0,

      // Search params
      depOffers: [],
      retOffers: [],
      origin: '',
      dest: '',
      date: '',
      returnDate: '',

      // Shared
      passengersCount: 1,
      cabinClass: 'ECONOMY',
      tripType: 'oneway',
      currentLeg: 'departure', // 'departure' | 'return'
      seatLeg: 'departure',    // which leg we're picking seats for

      // Booking
      pax: [],
      coupon: null,
      couponDiscount: 0,
      appliedDeal: null,
      dealCode: null,
      dealTitle: null,
      dealDiscountAmount: 0,
      selectedServices: [],
      serviceFees: 0,
      servicePrices: { baggage: 1200, priority: 500, meal: 350, insurance: 700 },
      termsConsented: false,
    };

    this.airports = [];
    try {
      const dataNode = document.getElementById('airports-data');
      if (dataNode) this.airports = JSON.parse(dataNode.textContent);
    } catch (e) { console.warn('Could not load airports JSON'); }

    this.initDOM();
    this.bindEvents();
    this.setupAutocomplete();
    this.handleUrlParams();
    this.initDestinationsPage();
    this.initDealsPage();

    // Advanced Aviation Suite state
    this.comparisonList = [];
    this.seatViewMode = '3d';
    this.cabinRotation = 0;
    this.cabinZoom = 1.0;
    this.globeAngle = 0;
    this.globeAutoSpin = true;
    this.globeAnimFrame = null;
    this.activeGlobeHub = 'BOM';
    this.notifications = this.loadStoredNotifications();

    this.initNotifications();
    this.initExploreSection();
    this.initInteractiveGlobe();
    this.updateNotificationBadge();
    this.initFeatureDiscoveryHub();
  }

  /* ---- DOM init ---- */
  initDOM() {
    this.sections = {
      search:       document.getElementById('step-search'),
      results:      document.getElementById('step-results'),
      seats:        document.getElementById('step-seats'),
      passengers:   document.getElementById('step-passengers'),
      payment:      document.getElementById('step-payment'),
      confirmation: document.getElementById('step-confirmation'),
    };
  }

  /* ---- Step navigation with animated transitions ---- */
  async goToStep(stepName, transitionType = null, meta = {}) {
    if (transitionType) {
      await FlightTransitionManager.playTransition(transitionType, meta);
    }

    const currentActive = Object.values(this.sections).find(s => s && s.classList.contains('active'));
    if (currentActive) await TransitionEngine.fadeOut(currentActive);

    Object.values(this.sections).forEach(sec => {
      if (sec) { sec.classList.remove('active'); sec.classList.add('hidden'); sec.style.opacity = ''; sec.style.transform = ''; }
    });

    const target = this.sections[stepName];
    if (target) {
      target.classList.remove('hidden');
      await TransitionEngine.fadeIn(target);
      target.classList.add('active');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    // Step-specific post-processing
    if (stepName === 'payment') {
      this.populatePaymentSummary();
    }
  }

  /* ---- Populate payment summary sidebar ---- */
  populatePaymentSummary() {
    const setEl = (id, v) => { const el = document.getElementById(id); if (el != null) el.innerText = v; };
    const count = this.state.passengersCount;

    // Route / flight / date
    setEl('pay-sum-route', `${this.state.origin} → ${this.state.dest}${this.state.returnFlight ? ` · ${this.state.dest} → ${this.state.origin}` : ''}`);
    setEl('pay-sum-flight', (() => {
      const leg1 = `${this.state.flight?.airline?.code || 'FE'}-${this.state.flight?.flight_number || '----'}`;
      if (!this.state.returnFlight) return leg1;
      const leg2 = `${this.state.returnFlight?.airline?.code || 'FE'}-${this.state.returnFlight?.flight_number || '----'}`;
      return `${leg1}  ·  ${leg2}`;
    })());
    setEl('pay-sum-date', (() => {
      const d1 = this.state.date ? new Date(this.state.date).toLocaleDateString(undefined, { day: '2-digit', month: 'short' }) : '--';
      if (!this.state.returnDate) return d1;
      const d2 = new Date(this.state.returnDate).toLocaleDateString(undefined, { day: '2-digit', month: 'short' });
      return `${d1} → ${d2}`;
    })());
    setEl('pay-sum-pax', `${count} Adult${count !== 1 ? 's' : ''}`);
    setEl('pay-sum-seats', [...this.state.seats, ...this.state.returnSeats].join(', ') || 'Unassigned');

    // Fare breakdown
    const p1 = this.state.flight?.pricing;
    const p2 = this.state.returnFlight?.pricing;
    const base      = ((p1?.base_fare    || 0) + (p2?.base_fare    || 0)) * count;
    const dynamic   = ((p1?.dynamic_fare || 0) + (p2?.dynamic_fare || 0)) * count;
    const seatFees  = (this.state.extraSeatFees || 0) + (this.state.returnExtraSeatFees || 0);
    const srvFees   = this.state.serviceFees || 0;
    const taxes     = ((p1?.taxes || 0) + (p2?.taxes || 0)) * count;
    const discount  = this.state.couponDiscount || 0;
    const total     = this.calcGrandTotal();

    setEl('pay-sum-base',     `₹${base.toFixed(0)}`);
    setEl('pay-sum-dynamic',  `₹${dynamic.toFixed(0)}`);
    setEl('pay-sum-seatfees', `₹${seatFees.toFixed(0)}`);
    setEl('pay-sum-services', `₹${srvFees.toFixed(0)}`);
    setEl('pay-sum-taxes',    `₹${taxes.toFixed(0)}`);
    if (discount > 0) {
      const r = document.getElementById('pay-sum-discount-row');
      if (r) r.classList.remove('hidden');
      setEl('pay-sum-discount', `-₹${discount.toFixed(0)}`);
    } else {
      const r = document.getElementById('pay-sum-discount-row');
      if (r) r.classList.add('hidden');
    }

    // Large total and button text
    const pretty = `₹${total.toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
    setEl('pay-sum-total', pretty);
    setEl('pay-btn-amount', pretty);
  }

  /* ---- Event Bindings ---- */
  bindEvents() {
    this.bindSearchForm();

    // Seat map continue button
    const continueToPax = document.getElementById('continue-to-pax');
    if (continueToPax) {
      continueToPax.addEventListener('click', () => {
        const neededSeats = this.state.passengersCount;
        const currentSeats = this.state.seatLeg === 'departure' ? this.state.seats : this.state.returnSeats;

        if (currentSeats.length !== neededSeats) {
          NotificationService.show(`Please select exactly ${neededSeats} seat(s).`, 'error');
          return;
        }

        // If round-trip and we just did departure seats, now do return seats
        if (this.state.tripType === 'roundtrip' && this.state.seatLeg === 'departure') {
          this.state.seatLeg = 'return';
          this.loadSeatMapFor(this.state.returnFlight);
          return;
        }

        // Otherwise proceed to passengers
        this.generatePassengerForms();
        this.updateFareSummary();
        this.goToStep('passengers', 'CABIN');
      });
    }

    // Coupon
    const applyCouponBtn = document.getElementById('apply-coupon-btn');
    if (applyCouponBtn) applyCouponBtn.addEventListener('click', () => this.applyCoupon());

    // Proceed to Payment
    const proceedToPayment = document.getElementById('continue-to-payment');
    if (proceedToPayment) {
      proceedToPayment.addEventListener('click', async () => {
        if (!this.state.termsConsented) {
          NotificationService.show('Please accept FlyEase Terms & Conditions to continue.', 'warning');
          return;
        }
        if (!this.validatePassengerForms()) return;

        const btnText = document.getElementById('btn-pax-text');
        const btnLoading = document.getElementById('btn-pax-loading');
        if (btnText) btnText.classList.add('hidden');
        if (btnLoading) btnLoading.classList.remove('hidden');
        proceedToPayment.disabled = true;

        this.collectPassengerData();
        const total = this.calcGrandTotal();
        const paymentDisplay = document.getElementById('payment-amount-display');
        if (paymentDisplay) paymentDisplay.innerText = `₹${total.toFixed(2)}`;

        // Smooth transition delay showing "Saving passenger details..."
        await new Promise(r => setTimeout(r, 400));

        if (btnText) btnText.classList.remove('hidden');
        if (btnLoading) btnLoading.classList.add('hidden');
        proceedToPayment.disabled = !this.state.termsConsented;

        this.goToStep('payment', 'VERIFICATION');
      });
    }

    // Confirm Booking
    const confirmBtn = document.getElementById('confirm-booking-btn');
    if (confirmBtn) confirmBtn.addEventListener('click', () => this.confirmBooking());

    // Confirmation Screen Action Buttons
    const downloadPdfBtn = document.getElementById('conf-download-pdf-btn');
    if (downloadPdfBtn) downloadPdfBtn.addEventListener('click', () => this.downloadETicket());

    const viewBookingBtn = document.getElementById('conf-view-booking-btn');
    if (viewBookingBtn) viewBookingBtn.addEventListener('click', () => this.viewBookingDetail());

    // Auth Forms
    this.bindAuthForms();

    // Payment method tabs, live card formatting, wallet radios
    this.bindPaymentUI();
  }

  /* ---- Payment UI bindings (tabs + live card preview + verify UPI) ---- */
  bindPaymentUI() {
    // --- Tabs ---
    const tabs = document.querySelectorAll('.pay-method-tab');
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const method = tab.dataset.method;
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        document.querySelectorAll('.payment-form-pane').forEach(p => {
          if (p.dataset.pane === method) {
            p.classList.remove('hidden');
            p.classList.add('active');
          } else {
            p.classList.add('hidden');
            p.classList.remove('active');
          }
        });
      });
    });

    // --- Live Card Preview formatting ---
    const cardNumInput  = document.getElementById('pay-card-number');
    const cardExpInput  = document.getElementById('pay-card-expiry');
    const cardNameInput = document.getElementById('pay-card-name');
    const numDisplay    = document.getElementById('card-num-display');
    const expDisplay    = document.getElementById('card-exp-display');
    const nameDisplay   = document.querySelector('.card-name-display');

    if (cardNumInput && numDisplay) {
      // Init
      numDisplay.innerText = this._formatCardNum(cardNumInput.value || '');
      cardNumInput.addEventListener('input', (e) => {
        const digits = (e.target.value || '').replace(/\D/g, '').slice(0, 19);
        const groups = digits.match(/.{1,4}/g) || [];
        e.target.value = groups.join(' ');
        numDisplay.innerText = this._formatCardNum(e.target.value);
      });
    }
    if (cardExpInput && expDisplay) {
      expDisplay.innerText = cardExpInput.value || 'MM/YY';
      cardExpInput.addEventListener('input', (e) => {
        let v = (e.target.value || '').replace(/\D/g, '').slice(0, 4);
        if (v.length >= 3) v = v.slice(0, 2) + '/' + v.slice(2);
        e.target.value = v;
        expDisplay.innerText = v || 'MM/YY';
      });
    }
    if (cardNameInput && nameDisplay) {
      cardNameInput.addEventListener('input', (e) => {
        const v = (e.target.value || '').trim().toUpperCase();
        nameDisplay.innerText = v || 'FLYEASE USER';
      });
    }

    // --- CVV: allow digits only, 4 max ---
    const cvv = document.getElementById('pay-card-cvv');
    if (cvv) {
      cvv.addEventListener('input', (e) => {
        e.target.value = (e.target.value || '').replace(/\D/g, '').slice(0, 4);
      });
    }

    // --- Wallet radios: only one checked, highlight card ---
    document.querySelectorAll('.wallet-radio').forEach(r => {
      r.addEventListener('change', () => {
        document.querySelectorAll('#err-wallet-select').forEach(err => err.classList.add('hidden'));
      });
    });

    // --- Confirmation action buttons ---
    const dlBtn = document.getElementById('conf-download-pdf-btn');
    const vbBtn = document.getElementById('conf-view-booking-btn');
    if (dlBtn) dlBtn.addEventListener('click', () => this.downloadETicket());
    if (vbBtn) vbBtn.addEventListener('click', () => this.viewBookingDetail());
  }

  _formatCardNum(raw) {
    const digits = (raw || '').replace(/\D/g, '').padEnd(16, '•').slice(0, 16);
    return digits.match(/.{4}/g).join(' ');
  }

  /* ---- UPI Verify button handler ---- */
  verifyUpiId() {
    const input = document.getElementById('pay-upi-id');
    const statusEl = document.getElementById('upi-status-msg');
    if (!input || !statusEl) return;
    const val = input.value.trim();
    statusEl.classList.remove('hidden', 'ok', 'bad');
    if (!val || !/@/.test(val) || val.split('@').length !== 2) {
      statusEl.classList.add('bad');
      statusEl.innerText = '✗ Invalid UPI ID. Format: name@bank (e.g. user@okicici).';
      document.getElementById('err-upi-id')?.classList.remove('hidden');
      return;
    }
    statusEl.classList.add('ok');
    statusEl.innerText = '✓ UPI ID verified. Collect request will be sent to your app on payment.';
    document.getElementById('err-upi-id')?.classList.add('hidden');
  }

  /* ---- Return the currently selected payment method key ---- */
  getSelectedPaymentMethod() {
    const active = document.querySelector('.pay-method-tab.active');
    return active ? active.dataset.method : 'CARD';
  }

  /* ---- Validate payment fields for the active method; returns {valid, firstInvalidEl, paymentDetails} ---- */
  validatePaymentDetails() {
    // Reset all payment inline errors (those NOT inside passenger forms)
    document.querySelectorAll('#step-payment .inline-error-msg').forEach(el => el.classList.add('hidden'));

    const method = this.getSelectedPaymentMethod();
    const details = { method };
    let valid = true;
    let firstInvalid = null;
    const markBad = (errId, inputEl) => {
      valid = false;
      document.getElementById(errId)?.classList.remove('hidden');
      if (!firstInvalid && inputEl) firstInvalid = inputEl;
    };

    switch (method) {
      case 'CARD': {
        const nameEl = document.getElementById('pay-card-name');
        const numEl  = document.getElementById('pay-card-number');
        const expEl  = document.getElementById('pay-card-expiry');
        const cvvEl  = document.getElementById('pay-card-cvv');

        const name = nameEl?.value.trim() || '';
        if (name.length < 2) markBad('err-card-name', nameEl);

        const digits = (numEl?.value || '').replace(/\s/g, '');
        if (digits.length < 13 || digits.length > 19 || !/^\d+$/.test(digits)) markBad('err-card-number', numEl);
        else details.card_last4 = digits.slice(-4);

        const exp = (expEl?.value || '').trim();
        if (!/^\d{2}\/\d{2}$/.test(exp)) markBad('err-card-expiry', expEl);

        const cvv = (cvvEl?.value || '').trim();
        if (!/^\d{3,4}$/.test(cvv)) markBad('err-card-cvv', cvvEl);
        break;
      }
      case 'UPI': {
        const upiEl = document.getElementById('pay-upi-id');
        const v = upiEl?.value.trim() || '';
        if (!/@/.test(v) || v.split('@').length !== 2 || v.length < 5) markBad('err-upi-id', upiEl);
        else details.upi_id = v;
        break;
      }
      case 'NET_BANKING': {
        const bankEl = document.getElementById('pay-bank-select');
        const v = bankEl?.value || '';
        if (!v) markBad('err-bank-select', bankEl);
        else details.bank_name = v;
        break;
      }
      case 'WALLET': {
        const checked = document.querySelector('input[name="wallet-provider"]:checked');
        if (!checked) markBad('err-wallet-select', document.querySelector('.wallet-options-grid'));
        else details.wallet_provider = checked.value;
        break;
      }
      case 'COUNTER': {
        const idEl = document.getElementById('pay-counter-id');
        const v = idEl?.value.trim() || '';
        if (v.length < 4) markBad('err-counter-id', idEl);
        break;
      }
    }

    if (!valid && firstInvalid) {
      firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
      if (typeof firstInvalid.focus === 'function') firstInvalid.focus();
      NotificationService.show('Please correct the highlighted payment fields before proceeding.', 'error');
    }
    return { valid, firstInvalidEl: firstInvalid, paymentDetails: details };
  }

  /* ---- Search form & trip-type toggle ---- */
  bindSearchForm() {
    const form = document.getElementById('search-form');
    if (!form) return;

    form.addEventListener('submit', (e) => { e.preventDefault(); this.handleSearch(); });

    const swapBtn = document.getElementById('swap-routes');
    if (swapBtn) {
      swapBtn.addEventListener('click', () => {
        const orig = document.getElementById('origin');
        const dest = document.getElementById('destination');
        const temp = orig.value; orig.value = dest.value; dest.value = temp;
        swapBtn.style.transform = 'rotate(180deg)';
        setTimeout(() => { swapBtn.style.transform = ''; }, 400);
      });
    }

    const tripRadios = document.querySelectorAll('input[name="tripType"]');
    const returnDateInput = document.getElementById('return-date');
    if (tripRadios && returnDateInput) {
      tripRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
          const isRT = e.target.value === 'roundtrip';
          returnDateInput.disabled = !isRT;
          returnDateInput.required = isRT;
          if (!isRT) returnDateInput.value = '';
          // Animate the return date
          returnDateInput.style.transition = 'opacity 0.3s, transform 0.3s';
          returnDateInput.style.opacity = isRT ? '1' : '0.4';
        });
      });
    }
  }

  /* ---- Autocomplete ---- */
  setupAutocomplete() {
    const setup = (inputId, listId) => {
      const input = document.getElementById(inputId);
      const list  = document.getElementById(listId);
      if (!input || !list) return;

      input.addEventListener('input', () => {
        const val = input.value.toLowerCase();
        list.innerHTML = '';
        if (!val) { list.classList.add('hidden'); return; }

        const matches = this.airports.filter(a =>
          a.city.toLowerCase().includes(val) ||
          a.code.toLowerCase().includes(val) ||
          a.name.toLowerCase().includes(val)
        );

        if (matches.length > 0) {
          list.classList.remove('hidden');
          matches.slice(0, 6).forEach(m => {
            const div = document.createElement('div');
            div.className = 'suggestion-item';
            div.innerHTML = `<strong>${m.city} (${m.code})</strong> <small>— ${m.name}</small>`;
            div.addEventListener('click', () => { input.value = m.code; list.classList.add('hidden'); });
            list.appendChild(div);
          });
        } else {
          list.classList.add('hidden');
        }
      });

      document.addEventListener('click', (e) => {
        if (e.target !== input && !list.contains(e.target)) list.classList.add('hidden');
      });
    };

    setup('origin', 'origin-suggestions');
    setup('destination', 'destination-suggestions');
  }

  /* ---- CSRF ---- */
  getCsrfToken() {
    const cookies = document.cookie.split(';');
    for (const c of cookies) {
      const t = c.trim();
      if (t.startsWith('csrftoken=')) return t.substring('csrftoken='.length);
    }
    return '';
  }

  /* ---- SEARCH ---- */
  async handleSearch() {
    const origin     = document.getElementById('origin').value.trim().toUpperCase();
    const dest       = document.getElementById('destination').value.trim().toUpperCase();
    const date       = document.getElementById('depart-date').value;
    const returnDate = document.getElementById('return-date').value;
    const passengers = parseInt(document.getElementById('passengers').value) || 1;
    const cabinClass = document.getElementById('cabin-class').value;
    const tripType   = document.querySelector('input[name="tripType"]:checked')?.value || 'oneway';

    if (!origin || !dest) { NotificationService.show('Please enter origin and destination.', 'error'); return; }
    if (origin === dest)  { NotificationService.show('Origin and Destination cannot be the same airport.', 'error'); return; }
    if (!date)            { NotificationService.show('Please select a departure date.', 'error'); return; }

    const todayStr = new Date().toISOString().split('T')[0];
    if (date < todayStr) {
      NotificationService.show('Departure date cannot be in the past. Please select a future date.', 'error');
      return;
    }

    if (tripType === 'roundtrip') {
      if (!returnDate) {
        NotificationService.show('Please select a return date for your round-trip.', 'error');
        return;
      }
      if (returnDate <= date) {
        NotificationService.show('Return date must be after the departure date.', 'error');
        return;
      }
    }

    this.state.passengersCount = passengers;
    this.state.cabinClass      = cabinClass;
    this.state.tripType        = tripType;
    this.state.origin          = origin;
    this.state.dest            = dest;
    this.state.date            = date;
    this.state.returnDate      = returnDate;

    const btn = document.getElementById('search-btn');
    const searchBtnText    = document.getElementById('search-btn-text');
    const searchBtnLoading = document.getElementById('search-loading');

    if (btn) btn.disabled = true;
    if (searchBtnText)    searchBtnText.classList.add('hidden');
    if (searchBtnLoading) searchBtnLoading.classList.remove('hidden');

    try {
      const depParams = new URLSearchParams({ origin, destination: dest, departure_date: date, passengers, class: cabinClass });
      const depRes  = await fetch(`/flights/search/?${depParams}`);
      if (!depRes.ok) throw new Error('Search failed for departure flights');
      const depData = await depRes.json();

      let retData = { offers: [] };
      if (tripType === 'roundtrip') {
        const retParams = new URLSearchParams({ origin: dest, destination: origin, departure_date: returnDate, passengers, class: cabinClass });
        const retRes  = await fetch(`/flights/search/?${retParams}`);
        if (!retRes.ok) throw new Error('Search failed for return flights');
        retData = await retRes.json();
      }

      this.state.depOffers = depData.offers || [];
      this.state.retOffers = retData.offers || [];
      this.state.currentLeg = 'departure';
      this.state.flight = null;
      this.state.returnFlight = null;

      // Bind results sort dropdown
      const sortSelect = document.getElementById('sort-results');
      if (sortSelect) {
        sortSelect.onchange = () => {
          const val = sortSelect.value;
          const offers = this.state.currentLeg === 'return' ? this.state.retOffers : this.state.depOffers;
          if (val === 'cheapest') {
            offers.sort((a,b) => a.pricing.total - b.pricing.total);
          } else if (val === 'fastest') {
            offers.sort((a,b) => a.duration_hours - b.duration_hours);
          }
          this.renderFlightList();
        };
      }

      this.renderFlightList();
      const origAirport = this.airports.find(a => a.code === origin);
      const destAirport = this.airports.find(a => a.code === dest);
      await this.goToStep('results', 'WORLD_ROUTE', {
        origin,
        dest,
        originCity: origAirport ? origAirport.city : origin,
        destCity: destAirport ? destAirport.city : dest,
        isReturn: false
      });
    } catch (err) {
      NotificationService.show(err.message, 'error');
    } finally {
      if (btn) btn.disabled = false;
      if (searchBtnText)    searchBtnText.classList.remove('hidden');
      if (searchBtnLoading) searchBtnLoading.classList.add('hidden');
    }
  }

  /* ---- Search alternative date directly ---- */
  searchWithDate(newDateStr) {
    const depInput = document.getElementById('depart-date');
    if (depInput) depInput.value = newDateStr;
    this.handleSearch();
  }

  /* ---- Render current flight list (dep or return) ---- */
  renderFlightList() {
    const container = document.getElementById('flight-results-container');
    const isReturn  = this.state.currentLeg === 'return';
    const offers    = isReturn ? this.state.retOffers : this.state.depOffers;
    const fromCode  = isReturn ? this.state.dest   : this.state.origin;
    const toCode    = isReturn ? this.state.origin : this.state.dest;
    const dateStr   = isReturn ? this.state.returnDate : this.state.date;

    document.getElementById('results-route-title').innerText = `${fromCode} → ${toCode}`;

    let meta = `${dateStr} • ${this.state.passengersCount} Passenger(s) • ${this.state.cabinClass}`;
    if (this.state.tripType === 'roundtrip') {
      const legLabel = isReturn ? '✈ Select Return Flight' : '✈ Select Departure Flight';
      meta += `  |  ${legLabel}`;
    }
    document.getElementById('results-meta-subtitle').innerText = meta;

    container.innerHTML = '';

    if (!offers || offers.length === 0) {
      const curDate = new Date(dateStr);
      const nextDate1 = new Date(curDate); nextDate1.setDate(curDate.getDate() + 1);
      const nextDate2 = new Date(curDate); nextDate2.setDate(curDate.getDate() + 2);
      const d1Str = nextDate1.toISOString().split('T')[0];
      const d2Str = nextDate2.toISOString().split('T')[0];

      container.innerHTML = `
        <div class="glass p-5 text-center mt-4 fade-in">
          <i class="fa-solid fa-plane-slash fa-3x text-muted mb-3" style="display:block;margin-bottom:1rem;"></i>
          <h3>No flights available on ${dateStr}</h3>
          <p class="muted">Try checking flights on adjacent travel dates below:</p>
          <div class="flex justify-center gap-3 mt-3 flex-wrap">
            <button class="btn btn-outline" onclick="app.searchWithDate('${d1Str}')">
              <i class="fa-regular fa-calendar-days me-1"></i> Try ${nextDate1.toLocaleDateString(undefined, {day:'numeric', month:'short'})}
            </button>
            <button class="btn btn-outline" onclick="app.searchWithDate('${d2Str}')">
              <i class="fa-regular fa-calendar-days me-1"></i> Try ${nextDate2.toLocaleDateString(undefined, {day:'numeric', month:'short'})}
            </button>
            <button class="btn btn-primary" onclick="app.goToStep('search')">
              <i class="fa-solid fa-arrow-left me-1"></i> Modify Search
            </button>
          </div>
        </div>`;
      return;
    }

    offers.forEach((flight, i) => {
      const depTime = new Date(flight.departure_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      const arrTime = new Date(flight.arrival_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      const code = flight.airline.code || 'FE';

      // Airline background colors & fallback initials
      const airlineColors = {
        '6E': '#001b94', 'AI': '#b91c1c', 'UK': '#49163b', 'EK': '#991b1b',
        'SG': '#c2410c', 'QP': '#ea580c', 'SQ': '#00205b', 'BA': '#1d4ed8',
        'LH': '#1e3a8a', 'QR': '#5c0632', 'EY': '#854d0e', 'TG': '#581c87',
        'FE': '#4f46e5'
      };
      const bgCol = airlineColors[code] || '#4f46e5';

      // Recommendation badge pills
      let badgesHtml = '';
      if (flight.tags && flight.tags.length > 0) {
        if (flight.tags.includes('BEST_VALUE')) badgesHtml += `<span class="badge-tag-best-value me-1">🏆 BEST VALUE</span>`;
        if (flight.tags.includes('CHEAPEST')) badgesHtml += `<span class="badge-tag-cheapest me-1">💰 CHEAPEST</span>`;
        if (flight.tags.includes('FASTEST')) badgesHtml += `<span class="badge-tag-fastest me-1">⚡ FASTEST</span>`;
      }

      // Prediction trend pill
      let predHtml = '';
      if (flight.price_prediction) {
        const p = flight.price_prediction;
        predHtml = `
          <div class="price-prediction-pill ${p.color}" title="${p.message}">
            <span>${p.trend_label} (${p.confidence}% conf.)</span>
          </div>
        `;
      }

      // Transparent score bullet notes
      let reasonsHtml = '';
      if (flight.reasons && flight.reasons.length > 0) {
        reasonsHtml = `
          <div class="flight-reasons-box small mt-2 pt-2 border-top border-secondary text-muted">
            ${flight.reasons.slice(0, 2).map(r => `<div class="d-flex align-center gap-1">${r}</div>`).join('')}
          </div>
        `;
      }

      const card = document.createElement('div');
      card.className = 'flight-card glass';
      card.style.animationDelay = `${i * 0.07}s`;
      card.classList.add('fade-in');
      card.innerHTML = `
        <div class="flight-card-main">
          <div class="airline-info">
            <div class="airline-logo-box" style="background:${bgCol};">
              ${flight.airline.logo
                ? `<img src="${flight.airline.logo}" alt="${code}" class="airline-img-logo" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                   <span class="airline-fallback-code" style="display:none;">${code}</span>`
                : `<span class="airline-fallback-code">${code}</span>`}
            </div>
            <div>
              <div class="flex align-center gap-1 flex-wrap">
                <strong>${flight.airline.name}</strong>
                ${badgesHtml}
              </div>
              <div class="small muted">${flight.flight_number} • ${flight.aircraft}</div>
              ${predHtml}
            </div>
          </div>

          <div class="time-info text-center">
            <h4>${depTime}</h4>
            <div class="muted small">${flight.origin}</div>
          </div>

          <div class="duration-visual text-center px-3" style="flex:1;">
            <div class="small muted mb-1">${flight.duration_hours}h</div>
            <div class="flight-flightpath">
              <div class="flight-flightpath-line"></div>
              <div class="flight-plane-runner">
                <i class="fa-solid fa-plane"></i>
              </div>
            </div>
            <div class="small text-success mt-1">Non-stop</div>
            <button type="button" class="btn btn-link btn-xs text-cyan p-0 mt-1" onclick="event.stopPropagation(); app.openRoute3DModal('${flight.origin}', '${flight.destination}', '${flight.duration_hours}')">
              <i class="fa-solid fa-earth-americas me-1"></i> 3D Route
            </button>
          </div>

          <div class="time-info text-center">
            <h4>${arrTime}</h4>
            <div class="muted small">${flight.destination}</div>
          </div>

          <div class="price-action text-right" style="border-left:1px solid var(--border-color);padding-left:1.2rem;">
            <div class="text-gradient" style="font-size:1.5rem;font-weight:700;">₹${flight.pricing.total.toFixed(2)}</div>
            <div class="small muted mb-2">per adult</div>
            <div class="flex gap-1 justify-end flex-wrap">
              <button type="button" class="btn btn-outline btn-xs compare-check-btn" data-id="${flight.id}" onclick="event.stopPropagation(); app.toggleFlightForComparison(${flight.id})">
                <i class="fa-solid fa-code-compare me-1"></i> Compare
              </button>
              <button class="btn btn-primary btn-sm btn-select-flight" data-id="${flight.id}" style="min-width:90px;">
                Select <i class="fa-solid fa-arrow-right ms-1"></i>
              </button>
            </div>
          </div>
        </div>
        ${reasonsHtml}
      `;

      container.appendChild(card);

      card.querySelector('.btn-select-flight').addEventListener('click', (e) => {
        // Animate selected state on the card
        document.querySelectorAll('.flight-card').forEach(c => c.classList.remove('card-selected'));
        card.classList.add('card-selected');
        e.currentTarget.innerHTML = '<i class="fa-solid fa-check"></i> Selected';
        setTimeout(() => this.selectFlight(flight), 350);
      });
    });
    this.updateCompareCheckboxes();
  }

  /* ---- Select a flight (handles dep → return → seat map) ---- */
  async selectFlight(flight) {
    if (this.state.currentLeg === 'departure') {
      this.state.flight = flight;
      if (this.state.tripType === 'roundtrip') {
        // Move to return leg selection
        this.state.currentLeg = 'return';
        NotificationService.show(`Departure flight selected! Now pick your return flight.`, 'success');
        setTimeout(() => this.renderFlightList(), 400);
        return;
      }
    } else {
      this.state.returnFlight = flight;
    }

    // Reset seat state
    this.state.seats             = [];
    this.state.returnSeats       = [];
    this.state.extraSeatFees     = 0;
    this.state.returnExtraSeatFees = 0;
    this.state.selectedSeatTypes = [];
    this.state.coupon            = null;
    this.state.couponDiscount    = 0;
    const fNum = `${flight.airline?.code || 'FE'}-${flight.flight_number || '102'}`;
    const rCode = `${flight.origin} → ${flight.destination}`;
    await this.goToStep('seats', 'GATE_BOARDING', {
      flightNum: fNum,
      gate: `Gate ${Math.floor(Math.random() * 18) + 1}${['A','B','C'][Math.floor(Math.random()*3)]}`,
      route: rCode
    });
    this.loadSeatMapFor(this.state.flight);
  }

  /* ---- Load seat map for a given flight ---- */
  async loadSeatMapFor(flight) {
    const isReturn = this.state.seatLeg === 'return';
    const label    = isReturn ? 'Return Flight' : 'Departure Flight';

    // Update seat map header
    const depDate = new Date(flight.departure_time);
    const arrDate = new Date(flight.arrival_time);
    document.getElementById('seat-map-orig').innerText     = flight.origin;
    document.getElementById('seat-map-dest').innerText     = flight.destination;
    document.getElementById('seat-map-dep-time').innerText = depDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    document.getElementById('seat-map-arr-time').innerText = arrDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    document.getElementById('seat-map-flight-num').innerText = `${flight.airline.code}-${flight.flight_number}`;
    document.getElementById('seat-map-duration').innerText   = `${flight.duration_hours}h`;

    const origAirport = this.airports.find(a => a.code === flight.origin);
    const destAirport = this.airports.find(a => a.code === flight.destination);
    document.getElementById('seat-map-orig-city').innerText = origAirport ? origAirport.city : flight.origin;
    document.getElementById('seat-map-dest-city').innerText = destAirport ? destAirport.city : flight.destination;

    // Reset counters for this leg
    const currentSeats = isReturn ? this.state.returnSeats : this.state.seats;
    document.getElementById('seats-total-needed').innerText   = this.state.passengersCount;
    document.getElementById('seats-selected-count').innerText = currentSeats.length;
    document.getElementById('sidebar-pax-count').innerText    = `${this.state.passengersCount} Adult(s)`;
    document.getElementById('sidebar-seats-selected').innerText = 'None';
    document.getElementById('sidebar-base-fare').innerText    = '₹0';
    document.getElementById('sidebar-dynamic-fare').innerText = '₹0';
    document.getElementById('sidebar-seat-fees').innerText    = '₹0';
    document.getElementById('sidebar-taxes').innerText        = '₹0';
    document.getElementById('sidebar-total-fare').innerText   = '₹0';

    const continueBtn = document.getElementById('continue-to-pax');
    continueBtn.disabled  = true;
    const legLabel = (this.state.tripType === 'roundtrip' && !isReturn)
      ? `Continue to Return Seats <i class="fa-solid fa-arrow-right ms-2"></i>`
      : `Continue to Passengers <i class="fa-solid fa-arrow-right ms-2"></i>`;
    continueBtn.innerHTML = `Select ${this.state.passengersCount} seat(s) · ${label}`;

    const grid = document.getElementById('seat-grid');
    if (grid) grid.innerHTML = '<div class="loading-spinner"><i class="fa-solid fa-plane fa-bounce text-primary me-2"></i> Loading aircraft...</div>';

    this.bindSeatFilters();

    try {
      const res  = await fetch(`/flights/seats/${flight.id}/`);
      const data = await res.json();
      this.renderSeatMap(data.seats, flight);
      this.updateSidebarSummary(flight);
    } catch (e) {
      if (grid) grid.innerHTML = '<p class="text-danger text-center">Failed to load seat map. Please try again.</p>';
    }
  }

  /* ---- Render seat map grid ---- */
  renderSeatMap(seats, flight) {
    const grid = document.getElementById('seat-grid');
    if (!grid) return;
    grid.innerHTML = '';

    const currentCabin = (this.state.cabinClass || 'ECONOMY').toUpperCase();
    
    // Check if the flight has seats specifically generated for the user's selected cabin class
    const cabinSeatCount = seats.filter(s => s.seat_class === currentCabin).length;
    const isRestrictedToExactClass = cabinSeatCount > 0;

    const rowsMap = {};
    seats.forEach(s => {
      // Handle standard "12A", Business "B2A", First "F1A"
      const numMatch = s.seat_number.match(/\d+/);
      const rowNum = numMatch ? parseInt(numMatch[0]) : 1;
      const prefix = s.seat_number.startsWith('B') ? 'B' : s.seat_number.startsWith('F') ? 'F' : 'E';
      const key = `${prefix}-${rowNum}`;
      if (!rowsMap[key]) rowsMap[key] = { prefix, rowNum, seats: [] };
      rowsMap[key].seats.push(s);
    });

    // Sort: First Class -> Business -> Economy
    const sortedKeys = Object.keys(rowsMap).sort((a, b) => {
      const order = { 'F': 1, 'B': 2, 'E': 3 };
      const [pA, rA] = [rowsMap[a].prefix, rowsMap[a].rowNum];
      const [pB, rB] = [rowsMap[b].prefix, rowsMap[b].rowNum];
      if (order[pA] !== order[pB]) return order[pA] - order[pB];
      return rA - rB;
    });

    sortedKeys.forEach(key => {
      const rowObj = rowsMap[key];
      const rn = rowObj.rowNum;
      const rowSeats = rowObj.seats.sort((a, b) => a.seat_number.localeCompare(b.seat_number));

      // Add emergency exit dividers for economy middle rows
      if (rowObj.prefix === 'E' && (rn === 12 || rn === 14)) {
        const exitDiv = document.createElement('div');
        exitDiv.className = 'exit-row-divider';
        exitDiv.innerHTML = '<div class="exit-path"><i class="fa-solid fa-person-running"></i> Emergency Exit</div>';
        grid.appendChild(exitDiv);
      }

      const rowDiv = document.createElement('div');
      rowDiv.className = `seat-row ${rowObj.prefix === 'B' ? 'business-row' : rowObj.prefix === 'F' ? 'first-row' : ''}`;

      rowSeats.forEach((seat, idx) => {
        // Add aisle spacer at middle
        if (idx === Math.floor(rowSeats.length / 2)) {
          const aisle = document.createElement('div');
          aisle.className = 'aisle';
          aisle.innerText = rowObj.prefix === 'B' ? `B${rn}` : rowObj.prefix === 'F' ? `F${rn}` : rn;
          rowDiv.appendChild(aisle);
        }

        let seatTypeClass = '';
        let seatPriceInfo = 'Standard';
        let extraFee = 0;

        if (seat.seat_class === 'FIRST' || currentCabin === 'FIRST') {
          seatTypeClass = 'first';
          seatPriceInfo = 'First Class Private Suite';
        } else if (seat.seat_class === 'BUSINESS' || currentCabin === 'BUSINESS') {
          seatTypeClass = 'business';
          seatPriceInfo = 'Business Class Lie-Flat';
        } else if (rn <= 3) {
          seatTypeClass = 'premium';
          seatPriceInfo = 'Premium (+₹1,500)';
          extraFee = 1500;
        } else if (rn === 12 || rn === 14 || rn === 1) {
          seatTypeClass = 'legroom';
          seatPriceInfo = 'Extra Legroom (+₹800)';
          extraFee = 800;
        }

        // Available if seat matches cabin (or fallback if all economy layout)
        const isMyClass = isRestrictedToExactClass ? (seat.seat_class === currentCabin) : true;
        const isAvailable = (seat.status === 'AVAILABLE') && isMyClass;

        const seatBtn = document.createElement('div');
        seatBtn.className = `seat-item ${isAvailable ? 'available' : 'occupied'} ${isMyClass ? seatTypeClass : ''}`;
        seatBtn.dataset.seatType = seatTypeClass;
        seatBtn.dataset.seatFee  = extraFee;
        seatBtn.dataset.window   = seat.is_window;
        seatBtn.dataset.aisle    = seat.is_aisle;
        seatBtn.dataset.seatNumber = seat.seat_number;
        seatBtn.title = `${seat.seat_number} | ${seat.seat_class || currentCabin} | ${seat.is_window ? 'Window' : seat.is_aisle ? 'Aisle' : 'Middle'} | ${seatPriceInfo}`;
        seatBtn.innerText = seat.seat_number.replace(/^\D+/, '').replace(/\d+/g, '') || seat.seat_number.slice(-1);

        if (isAvailable) {
          seatBtn.addEventListener('click', () => this.toggleSeat(seat, seatBtn, extraFee, flight));
        }

        rowDiv.appendChild(seatBtn);
      });

      grid.appendChild(rowDiv);
    });
  }

  /* ---- Seat filter buttons ---- */
  bindSeatFilters() {
    document.querySelectorAll('.filter-btn').forEach(btn => {
      const newBtn = btn.cloneNode(true);
      btn.parentNode.replaceChild(newBtn, btn);
      newBtn.addEventListener('click', () => {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        newBtn.classList.add('active');
        const filter = newBtn.dataset.filter;
        document.querySelectorAll('.seat-item').forEach(s => {
          s.classList.remove('dimmed');
          if (filter === 'all') return;
          if (filter === 'window'  && s.dataset.window !== 'true')         s.classList.add('dimmed');
          else if (filter === 'aisle'   && s.dataset.aisle !== 'true')     s.classList.add('dimmed');
          else if (filter === 'legroom' && s.dataset.seatType !== 'legroom') s.classList.add('dimmed');
          else if (filter === 'premium' && s.dataset.seatType !== 'premium') s.classList.add('dimmed');
        });
      });
    });
  }

  /* ---- Toggle seat selection ---- */
  toggleSeat(seat, element, extraFee, flight) {
    const isReturn   = this.state.seatLeg === 'return';
    const seatsArr   = isReturn ? this.state.returnSeats : this.state.seats;
    const feeKey     = isReturn ? 'returnExtraSeatFees' : 'extraSeatFees';

    const idx = seatsArr.indexOf(seat.seat_number);
    if (idx > -1) {
      seatsArr.splice(idx, 1);
      this.state[feeKey] -= extraFee;
      element.classList.remove('selected');
      element.classList.add('available');
    } else {
      if (seatsArr.length >= this.state.passengersCount) {
        NotificationService.show(`You only need ${this.state.passengersCount} seat(s).`, 'warning');
        return;
      }
      seatsArr.push(seat.seat_number);
      this.state[feeKey] += extraFee;
      element.classList.remove('available');
      element.classList.add('selected');
      // Micro bounce animation
      element.style.transform = 'scale(1.3)';
      setTimeout(() => { element.style.transform = ''; }, 220);
    }

    if (isReturn) this.state.returnSeats = seatsArr;
    else          this.state.seats       = seatsArr;

    document.getElementById('seats-selected-count').innerText = seatsArr.length;

    const continueBtn = document.getElementById('continue-to-pax');
    const allSelected = seatsArr.length === this.state.passengersCount;
    continueBtn.disabled = !allSelected;

    if (allSelected) {
      const isLastLeg = !(this.state.tripType === 'roundtrip' && !isReturn);
      continueBtn.innerHTML = isLastLeg
        ? `Continue to Passengers <i class="fa-solid fa-arrow-right ms-2"></i>`
        : `Continue to Return Seats <i class="fa-solid fa-arrow-right ms-2"></i>`;
    } else {
      continueBtn.innerText = `Select ${this.state.passengersCount - seatsArr.length} more seat(s)`;
    }

    this.updateSidebarSummary(flight);
  }

  /* ---- Undo Last Selected Seat ---- */
  undoLastSeat() {
    const isReturn = this.state.seatLeg === 'return';
    const seatsArr = isReturn ? this.state.returnSeats : this.state.seats;
    if (!seatsArr.length) {
      NotificationService.show('No seat selected to undo.', 'info');
      return;
    }
    const lastSeatNum = seatsArr[seatsArr.length - 1];
    const seatEl = document.querySelector(`.seat-item[data-seat-number="${lastSeatNum}"]`);
    if (seatEl) {
      seatEl.click();
      NotificationService.show(`Removed seat ${lastSeatNum}. Pick your new choice.`, 'info');
    } else {
      seatsArr.pop();
      if (isReturn) this.state.returnSeats = seatsArr;
      else          this.state.seats = seatsArr;
      document.getElementById('seats-selected-count').innerText = seatsArr.length;
      this.updateSidebarSummary(isReturn ? this.state.returnFlight : this.state.flight);
      NotificationService.show(`Undid seat ${lastSeatNum}.`, 'info');
    }
  }

  /* ---- Reset all selected seats on current leg ---- */
  resetSeatSelection() {
    const isReturn = this.state.seatLeg === 'return';
    const seatsArr = isReturn ? [...this.state.returnSeats] : [...this.state.seats];
    if (!seatsArr.length) {
      NotificationService.show('No seats are currently selected.', 'info');
      return;
    }
    seatsArr.forEach(seatNum => {
      const seatEl = document.querySelector(`.seat-item[data-seat-number="${seatNum}"]`);
      if (seatEl) seatEl.click();
    });
    NotificationService.show('Seat selection reset. Choose your preferred seats.', 'info');
  }

  /* ---- Update sidebar fare summary on seat map ---- */
  updateSidebarSummary(flight) {
    const count    = this.state.passengersCount;
    const pricing  = flight ? flight.pricing : (this.state.seatLeg === 'return' ? this.state.returnFlight?.pricing : this.state.flight?.pricing);
    if (!pricing) return;

    const depFees  = this.state.extraSeatFees;
    const retFees  = this.state.returnExtraSeatFees;
    const allFees  = depFees + retFees;
    const base     = pricing.base_fare    * count;
    const dyn      = pricing.dynamic_fare * count;
    const tax      = pricing.taxes        * count;
    const total    = (pricing.total * count) + allFees;

    const seatsArr = this.state.seatLeg === 'return' ? this.state.returnSeats : this.state.seats;
    document.getElementById('sidebar-seats-selected').innerText = seatsArr.length ? seatsArr.join(', ') : 'None';
    document.getElementById('sidebar-base-fare').innerText      = `₹${base.toFixed(2)}`;
    document.getElementById('sidebar-dynamic-fare').innerText   = `₹${dyn.toFixed(2)}`;
    document.getElementById('sidebar-seat-fees').innerText      = `₹${allFees.toFixed(2)}`;
    document.getElementById('sidebar-taxes').innerText          = `₹${tax.toFixed(2)}`;
    document.getElementById('sidebar-total-fare').innerText     = `₹${total.toFixed(2)}`;
  }

  /* ---- Generate passenger forms ---- */
  generatePassengerForms() {
    const flight = this.state.flight;
    if (!flight) return;

    // 1. Update Compact Flight Summary Banner
    const depDate = new Date(flight.departure_time);
    const arrDate = new Date(flight.arrival_time);
    const dateFormatted = depDate.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
    const depTimeStr = depDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const arrTimeStr = arrDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    const origAirport = this.airports.find(a => a.code === flight.origin);
    const destAirport = this.airports.find(a => a.code === flight.destination);
    const origCity = origAirport ? origAirport.city : flight.origin;
    const destCity = destAirport ? destAirport.city : flight.destination;

    const setEl = (id, val) => { const el = document.getElementById(id); if (el) el.innerText = val; };
    setEl('pax-sum-route', `${origCity} (${flight.origin}) → ${destCity} (${flight.destination})`);
    setEl('pax-sum-dep-date', `${dateFormatted} • ${depTimeStr}`);
    setEl('pax-sum-arr-date', `${dateFormatted} • ${arrTimeStr}`);
    setEl('pax-sum-duration', `${flight.duration_hours}h`);
    setEl('pax-sum-flight-num', `${flight.airline ? flight.airline.code : 'FE'}-${flight.flight_number}`);
    
    const allSeats = [...this.state.seats, ...this.state.returnSeats].join(', ') || 'Unassigned';
    setEl('pax-sum-seats', allSeats);

    // Check if route is international
    const intlAirports = ['DXB', 'LHR', 'SIN', 'HND', 'JFK', 'CDG', 'FRA'];
    const isIntl = intlAirports.includes(flight.origin) || intlAirports.includes(flight.destination);
    const docsBadge = document.getElementById('docs-requirement-badge');
    const docsSub   = document.getElementById('docs-subtitle-text');
    if (docsBadge) {
      docsBadge.innerText = isIntl ? 'Mandatory for International Flight' : 'Optional for Domestic Route';
      docsBadge.className = isIntl ? 'badge badge-pill badge-primary' : 'badge badge-outline';
    }
    if (docsSub) {
      docsSub.innerText = isIntl 
        ? 'Passport details are required by customs and immigration authorities for international travel.'
        : 'For domestic flights, passport details are optional. You may also provide a Government ID.';
    }

    // 2. Generate Passenger Cards
    const container = document.getElementById('passenger-forms-container');
    container.innerHTML = '';

    for (let i = 0; i < this.state.passengersCount; i++) {
      const depSeat = this.state.seats[i]       || '—';
      const retSeat = this.state.returnSeats[i] || '';
      const seatBadgeText = this.state.tripType === 'roundtrip'
        ? `Dep: ${depSeat} | Ret: ${retSeat}`
        : `Seat: ${depSeat}`;

      const paxCategory = (i === 0) ? 'Adult' : (i % 2 === 1 ? 'Adult' : 'Child');

      const card = document.createElement('div');
      card.className = 'glass pax-card p-4 mb-4';
      card.style.cssText = 'border-radius:16px; animation:fadeSlideIn 0.4s ease both;';
      card.style.animationDelay = `${i * 0.08}s`;

      card.innerHTML = `
        <div class="flex justify-between align-center mb-3">
          <div class="flex align-center gap-2">
            <div class="user-avatar" style="width:36px;height:36px;font-size:0.9rem;background:var(--primary);">${i + 1}</div>
            <h4 class="m-0">Passenger ${i + 1}</h4>
            <span class="badge badge-pill badge-outline ms-2">${paxCategory}</span>
          </div>
          <span class="badge badge-pill text-secondary" style="background:rgba(14,165,233,0.12);"><i class="fa-solid fa-chair me-1"></i> ${seatBadgeText}</span>
        </div>
        <hr class="glass-divider my-3">
        
        <div class="form-row-2col">
          <div class="form-floating-custom">
            <input type="text" class="form-control-custom pax-fname" placeholder=" " required>
            <label>First Name *</label>
            <div class="input-glow-line"></div>
            <div class="inline-error-msg hidden">Please enter first name as per ID.</div>
          </div>

          <div class="form-floating-custom">
            <input type="text" class="form-control-custom pax-lname" placeholder=" " required>
            <label>Last Name *</label>
            <div class="input-glow-line"></div>
            <div class="inline-error-msg hidden">Please enter last name as per ID.</div>
          </div>
        </div>

        <div class="form-row-3col mt-2">
          <div class="form-floating-custom">
            <input type="date" class="form-control-custom pax-dob" placeholder=" " required>
            <label>Date of Birth *</label>
            <div class="input-glow-line"></div>
            <div class="inline-error-msg hidden">Please select a valid date of birth.</div>
          </div>

          <div class="form-floating-custom">
            <select class="form-control-custom pax-gender" required>
              <option value="MALE" selected>Male</option>
              <option value="FEMALE">Female</option>
              <option value="OTHER">Other</option>
            </select>
            <label>Gender *</label>
            <div class="input-glow-line"></div>
          </div>

          <div class="form-floating-custom">
            <input type="text" class="form-control-custom pax-nationality" value="Indian" placeholder=" " required>
            <label>Nationality *</label>
            <div class="input-glow-line"></div>
            <div class="inline-error-msg hidden">Please specify nationality.</div>
          </div>
        </div>`;

      container.appendChild(card);
    }
  }

  /* ---- Additional Service Toggle ---- */
  toggleService(serviceId, price) {
    const idx = this.state.selectedServices.indexOf(serviceId);
    if (idx > -1) {
      this.state.selectedServices.splice(idx, 1);
    } else {
      this.state.selectedServices.push(serviceId);
    }

    const paxCount = this.state.passengersCount;
    this.state.serviceFees = this.state.selectedServices.reduce((acc, s) => {
      return acc + (this.state.servicePrices[s] || 0) * paxCount;
    }, 0);

    this.updateFareSummary();
  }

  /* ---- Terms Consent Toggle ---- */
  toggleTermsConsent(checked) {
    this.state.termsConsented = checked;
    const btn = document.getElementById('continue-to-payment');
    if (btn) btn.disabled = !checked;
  }

  /* ---- Info & Policy Modal Handler for Footer & Links ---- */
  openInfoModal(type) {
    const modal = document.getElementById('flyease-info-modal');
    const titleEl = document.getElementById('info-modal-title');
    const iconEl = document.getElementById('info-modal-icon');
    const bodyEl = document.getElementById('info-modal-body');
    if (!modal || !titleEl || !bodyEl) return;

    const data = {
      careers: {
        title: 'Careers at FlyEase',
        icon: '<i class="fa-solid fa-briefcase text-primary"></i>',
        content: `
          <p>Join our pioneering aviation tech team building state-of-the-art dynamic pricing algorithms, machine learning revenue management, and immersive booking platforms.</p>
          <div class="glass-inner p-3 rounded mb-3">
            <b>🔥 Open Roles:</b>
            <ul class="mb-0 mt-1 small">
              <li>Senior Algorithm Engineer (Revenue Optimization)</li>
              <li>Aviation UX / Frontend Architect</li>
              <li>Full-Stack Django & High-Concurrency Systems Engineer</li>
            </ul>
          </div>
          <p class="small muted mb-0"><i class="fa-solid fa-envelope me-1 text-primary"></i> Send your portfolio to <b>careers@flyease.aero</b></p>
        `
      },
      press: {
        title: 'Press & Media Center',
        icon: '<i class="fa-solid fa-newspaper text-secondary"></i>',
        content: `
          <p>Official media resources, press kits, and announcements about FlyEase's real-time AI dynamic fare engine and simulated aviation systems.</p>
          <div class="glass-inner p-3 rounded small mb-2">
            <b>Latest Press Releases:</b>
            <div class="mt-1 text-muted">· FlyEase launches next-gen predictive seat pricing across 12 domestic & international hubs.</div>
            <div class="mt-1 text-muted">· Zero-latency E-ticket issuing pipeline integrated with instant digital QR verification.</div>
          </div>
          <p class="small muted mb-0">Media queries: <b>press@flyease.aero</b></p>
        `
      },
      contact: {
        title: 'Contact FlyEase',
        icon: '<i class="fa-solid fa-headset text-success"></i>',
        content: `
          <p>We are here 24×7 to assist you with flight inquiries, cancellations, group bookings, and platform feedback.</p>
          <div class="grid-2 gap-2 glass-inner p-3 rounded small mb-3">
            <div><i class="fa-solid fa-phone text-success me-1"></i> <b>Direct Support:</b> <a href="tel:+919307145593" class="text-white text-decoration-none">9307145593</a></div>
            <div><i class="fa-solid fa-envelope text-primary me-1"></i> <b>Email:</b> support@flyease.aero</div>
            <div><i class="fa-solid fa-location-dot text-danger me-1"></i> <b>HQ:</b> Chhatrapati Shivaji Maharaj Airport, Terminal 2, Mumbai</div>
            <div><i class="fa-solid fa-clock text-warning me-1"></i> <b>Hours:</b> 24 Hours / 7 Days</div>
          </div>
        `
      },
      help: {
        title: 'Help Center & Support',
        icon: '<i class="fa-solid fa-circle-question text-primary"></i>',
        content: `
          <p>Find quick solutions for booking, baggage allowances, check-in schedules, and fare rules.</p>
          <div class="glass-inner p-3 rounded mb-2">
            <h5 class="m-0 mb-1 text-primary">Quick Actions</h5>
            <div class="small muted">· Web check-in opens 24 hours prior to scheduled departure.</div>
            <div class="small muted mt-1">· Download or print your verified E-Ticket with PNR anytime from <a href="/dashboard/" class="text-primary underline">My Trips</a>.</div>
          </div>
        `
      },
      faqs: {
        title: 'Frequently Asked Questions',
        icon: '<i class="fa-solid fa-comments text-warning"></i>',
        content: `
          <div class="faq-item glass-inner p-3 rounded mb-2 small">
            <b>Q: How does Dynamic Pricing work on FlyEase?</b>
            <p class="muted mb-0 mt-1">Fares fluctuate in real-time based on seat demand, remaining cabin inventory, peak travel hours, and flight departure proximity.</p>
          </div>
          <div class="faq-item glass-inner p-3 rounded mb-2 small">
            <b>Q: What is the baggage allowance?</b>
            <p class="muted mb-0 mt-1">Standard Economy includes 7 kg Cabin Baggage + 15 kg Check-in. Extra baggage up to 15 kg can be added during booking.</p>
          </div>
          <div class="faq-item glass-inner p-3 rounded small">
            <b>Q: Can I select specific seats?</b>
            <p class="muted mb-0 mt-1">Yes! Use our 3D interactive cabin map to choose Window, Aisle, Extra Legroom, or Premium seats with instant undo capability.</p>
          </div>
        `
      },
      booking_support: {
        title: 'Booking & Reservation Support',
        icon: '<i class="fa-solid fa-ticket-simple text-primary"></i>',
        content: `
          <p>Manage existing bookings, request flight modifications, or resend confirmed E-Tickets to your email.</p>
          <div class="glass-inner p-3 rounded small mb-3">
            <div><i class="fa-solid fa-circle-check text-success me-1"></i> Instant PNR confirmation & PDF generation</div>
            <div class="mt-1"><i class="fa-solid fa-circle-check text-success me-1"></i> Multi-passenger and round-trip support</div>
            <div class="mt-1"><i class="fa-solid fa-circle-check text-success me-1"></i> Secure checkout with Cards, UPI, Net Banking, and Wallets</div>
          </div>
        `
      },
      baggage: {
        title: 'Baggage Information & Guidelines',
        icon: '<i class="fa-solid fa-suitcase-rolling text-secondary"></i>',
        content: `
          <div class="grid-2 gap-2 glass-inner p-3 rounded small mb-3">
            <div>
              <b class="text-primary"><i class="fa-solid fa-bag-shopping me-1"></i> Cabin Baggage:</b>
              <p class="muted mb-0 mt-1">1 piece up to 7 kg (55 × 35 × 25 cm) + 1 small laptop bag/purse.</p>
            </div>
            <div>
              <b class="text-primary"><i class="fa-solid fa-suitcase me-1"></i> Check-in Baggage:</b>
              <p class="muted mb-0 mt-1">1 piece up to 15 kg for Domestic (25 kg for International).</p>
            </div>
          </div>
          <p class="small muted mb-0"><i class="fa-solid fa-info-circle text-warning me-1"></i> Additional baggage can be selected under Add-on Services.</p>
        `
      },
      airlines: {
        title: 'Partner Airline Network',
        icon: '<i class="fa-solid fa-plane-up text-primary"></i>',
        content: `
          <p>FlyEase codeshares with premier international & domestic aviation carriers ensuring top-tier service standards:</p>
          <div class="grid-2 gap-2 glass-inner p-3 rounded small">
            <div>✈ <b>Air India (AI)</b> · Full Service</div>
            <div>✈ <b>IndiGo (6E)</b> · Express Low-Cost</div>
            <div>✈ <b>Emirates (EK)</b> · Luxury Global Hubs</div>
            <div>✈ <b>Singapore Airlines (SQ)</b> · Star Alliance</div>
            <div>✈ <b>SpiceJet (SG)</b> · Regional Domestic</div>
            <div>✈ <b>British Airways (BA)</b> · Transatlantic</div>
          </div>
        `
      },
      flight_status: {
        title: 'Live Flight Status Tracker',
        icon: '<i class="fa-solid fa-satellite-dish text-primary"></i>',
        content: `
          <p>Track real-time flight departures, gate numbers, and arrival estimations directly from our global airspace radar.</p>
          <div class="glass-inner p-3 rounded small text-center mb-3">
            <i class="fa-solid fa-circle-notch fa-spin text-primary me-2"></i> All simulated flights are currently <b>ON SCHEDULE</b>.
          </div>
          <p class="small muted text-center mb-0">Use the Flight Search bar on the homepage to view live dynamic schedules.</p>
        `
      },
      privacy: {
        title: 'FlyEase Privacy Policy',
        icon: '<i class="fa-solid fa-user-shield text-success"></i>',
        content: `
          <p>FlyEase values passenger privacy and implements stringent data protection standards.</p>
          <div class="glass-inner p-3 rounded small mb-2">
            <b>1. Data Collected:</b> Passenger names, contact information, date of birth, and travel document IDs solely for ticket generation.<br><br>
            <b>2. Security:</b> 256-bit SSL encryption across all transaction endpoints.<br><br>
            <b>3. Simulator Scope:</b> Mock payments do not store or process real banking credentials.
          </div>
        `
      },
      terms: {
        title: 'Terms of Service',
        icon: '<i class="fa-solid fa-file-contract text-primary"></i>',
        content: `
          <p>By using the FlyEase Flight Simulator, passengers agree to the following terms:</p>
          <div class="glass-inner p-3 rounded small mb-2">
            · Fares are determined by real-time demand-driven dynamic pricing algorithms.<br>
            · E-tickets issued with valid PNRs represent confirmed simulator bookings.<br>
            · All travelers must present valid Government-issued photo identification at airport security.
          </div>
        `
      },
      refund: {
        title: 'Cancellation & Refund Policy',
        icon: '<i class="fa-solid fa-hand-holding-dollar text-warning"></i>',
        content: `
          <p>Cancellations made via your FlyEase dashboard or booking lookup are handled swiftly:</p>
          <div class="glass-inner p-3 rounded small mb-2">
            · <b>Full Refund:</b> Cancellations made >24 hours prior to departure.<br>
            · <b>Standard Refund:</b> Cancellations within 24 hours subject to nominal airline fee.<br>
            · <b>Processing Time:</b> Simulated refunds reflect instantly in transaction ledger.
          </div>
        `
      },
      security: {
        title: 'Security & Trust Center',
        icon: '<i class="fa-solid fa-shield-halved text-success"></i>',
        content: `
          <p>Our infrastructure adheres to high cybersecurity and compliance benchmarks:</p>
          <div class="glass-inner p-3 rounded small mb-2">
            <div><i class="fa-solid fa-lock text-success me-1"></i> End-to-End SSL/TLS Encryption</div>
            <div class="mt-1"><i class="fa-solid fa-shield-virus text-primary me-1"></i> CSRF & Anti-Tamper Protected Endpoints</div>
            <div class="mt-1"><i class="fa-solid fa-database text-secondary me-1"></i> Secure Relational Booking Ledger with ACID Compliance</div>
          </div>
        `
      }
    };

    const item = data[type] || data.terms;
    titleEl.innerText = item.title;
    iconEl.innerHTML = item.icon || '<i class="fa-solid fa-circle-info text-primary"></i>';
    bodyEl.innerHTML = item.content;

    modal.classList.remove('hidden');
    modal.classList.add('is-open');
    document.body.style.overflow = 'hidden';
  }

  closeInfoModal() {
    const modal = document.getElementById('flyease-info-modal');
    if (!modal) return;
    modal.classList.remove('is-open');
    modal.classList.add('hidden');
    document.body.style.overflow = '';
  }

  showTermsModal(type) {
    this.openInfoModal(type);
  }

  /* ---- Calculate grand total ---- */
  calcGrandTotal() {
    const count = this.state.passengersCount;
    let total = 0;
    if (this.state.flight) total += (this.state.flight.pricing.total * count) + this.state.extraSeatFees;
    if (this.state.returnFlight) total += (this.state.returnFlight.pricing.total * count) + this.state.returnExtraSeatFees;
    total += (this.state.serviceFees || 0);
    const discount = (this.state.dealDiscountAmount || 0) + (this.state.couponDiscount || 0);
    return Math.max(0, total - discount);
  }

  /* ---- Update fare summary on passengers step ---- */
  updateFareSummary() {
    const count   = this.state.passengersCount;
    const pricing = this.state.flight?.pricing;
    if (!pricing) return;

    const base      = pricing.base_fare    * count;
    const dyn       = pricing.dynamic_fare * count;
    const tax       = pricing.taxes        * count;
    const seatFees  = this.state.extraSeatFees + this.state.returnExtraSeatFees;
    const srvFees   = this.state.serviceFees   || 0;
    const total     = this.calcGrandTotal();
    const discount  = (this.state.dealDiscountAmount || 0) + (this.state.couponDiscount || 0);

    const setEl = (id, v) => { const el = document.getElementById(id); if (el) el.innerText = v; };

    setEl('pax-side-route', `${this.state.origin} → ${this.state.dest}`);
    setEl('pax-side-date', this.state.date || '--');
    setEl('pax-side-count', `${count} Adult(s)`);
    setEl('pax-side-seats', [...this.state.seats, ...this.state.returnSeats].join(', ') || 'Unassigned');

    setEl('pax-side-base', `₹${base.toFixed(2)}`);
    setEl('pax-side-dynamic', `₹${dyn.toFixed(2)}`);
    setEl('pax-side-seatfees', `₹${seatFees.toFixed(2)}`);
    setEl('pax-side-services', `₹${srvFees.toFixed(2)}`);
    setEl('pax-side-taxes', `₹${tax.toFixed(2)}`);
    
    const row = document.getElementById('pax-side-discount-row');
    if (discount > 0) {
      if (row) row.classList.remove('hidden');
      const offerLabel = this.state.dealTitle ? `Offer: ${this.state.dealTitle}` : 'Promo Discount';
      const labelSpan = row ? row.querySelector('span') : null;
      if (labelSpan) labelSpan.innerText = offerLabel;
      setEl('pax-side-discount', `-₹${discount.toFixed(2)}`);
    } else if (row) {
      row.classList.add('hidden');
    }

    setEl('pax-side-total', `₹${total.toFixed(2)}`);
  }

  /* ---- Apply coupon or deal code ---- */
  async applyCoupon() {
    const code = document.getElementById('coupon-code').value.trim().toUpperCase();
    if (!code) return;

    const grossTotal = this.calcGrandTotal() + (this.state.dealDiscountAmount || 0) + (this.state.couponDiscount || 0);

    // First attempt to validate as a Deal
    try {
      const dealRes = await fetch('/flights/deals/validate/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': this.getCsrfToken() },
        body: JSON.stringify({
          code: code,
          passengers: this.state.passengersCount,
          class: this.state.cabinClass,
          amount: grossTotal,
          flight_id: this.state.flight ? this.state.flight.id : null
        })
      });
      const dealData = await dealRes.json();
      const msgDiv = document.getElementById('coupon-msg');
      if (msgDiv) msgDiv.classList.remove('hidden');

      if (dealData.success) {
        this.state.dealCode = code;
        this.state.dealTitle = dealData.deal_title;
        this.state.dealDiscountAmount = dealData.discount_amount;
        this.state.coupon = null;
        this.state.couponDiscount = 0;
        if (msgDiv) {
          msgDiv.className = 'text-success small mt-1';
          msgDiv.innerText = dealData.message || `✓ Deal ${dealData.deal_title} applied! -₹${dealData.discount_amount.toFixed(2)}`;
        }
        this.updateFareSummary();
        NotificationService.show(`Offer ${dealData.deal_title} applied successfully!`, 'success');
        return;
      }
    } catch (err) {
      // Continue to coupon check
    }

    // Attempt coupon validation fallback
    try {
      const res  = await fetch('/flights/apply_coupon/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': this.getCsrfToken() },
        body: JSON.stringify({ coupon_code: code, amount: grossTotal })
      });
      const data = await res.json();
      const msgDiv = document.getElementById('coupon-msg');
      if (msgDiv) msgDiv.classList.remove('hidden');

      if (data.success) {
        this.state.coupon         = code;
        this.state.couponDiscount = data.discount;
        this.state.dealCode       = null;
        this.state.dealTitle      = null;
        this.state.dealDiscountAmount = 0;
        if (msgDiv) {
          msgDiv.className = 'text-success small mt-1';
          msgDiv.innerText = `✓ Promo code applied! -₹${data.discount.toFixed(2)}`;
        }
      } else {
        this.state.coupon = null;
        this.state.couponDiscount = 0;
        this.state.dealCode = null;
        this.state.dealDiscountAmount = 0;
        if (msgDiv) {
          msgDiv.className = 'text-danger small mt-1';
          msgDiv.innerText = data.error || 'Invalid deal or coupon code';
        }
      }
      this.updateFareSummary();
    } catch (e) {
      NotificationService.show('Error applying promo code', 'error');
    }
  }

  /* ---- Validate passenger forms with smooth scroll to invalid field ---- */
  validatePassengerForms() {
    let isValid = true;
    let firstInvalidEl = null;

    // Reset old validation errors
    document.querySelectorAll('.form-control-custom').forEach(el => {
      el.classList.remove('is-invalid', 'is-valid');
    });
    document.querySelectorAll('.inline-error-msg').forEach(el => el.classList.add('hidden'));

    // 1. Validate Passenger Cards
    const container = document.getElementById('passenger-forms-container');
    const cards = container.children;

    for (let i = 0; i < cards.length; i++) {
      const fname = cards[i].querySelector('.pax-fname');
      const lname = cards[i].querySelector('.pax-lname');
      const dob   = cards[i].querySelector('.pax-dob');
      const nat   = cards[i].querySelector('.pax-nationality');

      if (!fname.value.trim()) {
        fname.classList.add('is-invalid');
        fname.parentNode.querySelector('.inline-error-msg')?.classList.remove('hidden');
        if (!firstInvalidEl) firstInvalidEl = fname;
        isValid = false;
      } else { fname.classList.add('is-valid'); }

      if (!lname.value.trim()) {
        lname.classList.add('is-invalid');
        lname.parentNode.querySelector('.inline-error-msg')?.classList.remove('hidden');
        if (!firstInvalidEl) firstInvalidEl = lname;
        isValid = false;
      } else { lname.classList.add('is-valid'); }

      if (!dob.value) {
        dob.classList.add('is-invalid');
        dob.parentNode.querySelector('.inline-error-msg')?.classList.remove('hidden');
        if (!firstInvalidEl) firstInvalidEl = dob;
        isValid = false;
      } else { dob.classList.add('is-valid'); }

      if (!nat.value.trim()) {
        nat.classList.add('is-invalid');
        nat.parentNode.querySelector('.inline-error-msg')?.classList.remove('hidden');
        if (!firstInvalidEl) firstInvalidEl = nat;
        isValid = false;
      } else { nat.classList.add('is-valid'); }
    }

    // 2. Validate Contact Information
    const emailEl = document.getElementById('contact-email');
    const phoneEl = document.getElementById('contact-phone');

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailEl.value.trim() || !emailRegex.test(emailEl.value.trim())) {
      emailEl.classList.add('is-invalid');
      document.getElementById('err-contact-email')?.classList.remove('hidden');
      if (!firstInvalidEl) firstInvalidEl = emailEl;
      isValid = false;
    } else { emailEl.classList.add('is-valid'); }

    if (!phoneEl.value.trim() || phoneEl.value.trim().length < 8) {
      phoneEl.classList.add('is-invalid');
      document.getElementById('err-contact-phone')?.classList.remove('hidden');
      if (!firstInvalidEl) firstInvalidEl = phoneEl;
      isValid = false;
    } else { phoneEl.classList.add('is-valid'); }

    // If invalid, scroll into view smooth and focus first error
    if (!isValid && firstInvalidEl) {
      firstInvalidEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
      firstInvalidEl.focus();
      NotificationService.show('Please fill out all required fields marked in red.', 'error');
    }

    return isValid;
  }

  /* ---- Collect passenger & document data ---- */
  collectPassengerData() {
    this.state.pax = [];
    const container = document.getElementById('passenger-forms-container');
    const cards = container.children;

    const emailContact = document.getElementById('contact-email')?.value.trim() || '';
    const phoneContact = document.getElementById('contact-phone')?.value.trim() || '';
    const passportNo   = document.getElementById('doc-passport-no')?.value.trim() || '';
    const govtId       = document.getElementById('doc-govt-id')?.value.trim() || '';
    const nationality  = document.getElementById('pax-nationality')?.value.trim() || 'Indian';

    for (let i = 0; i < cards.length; i++) {
      const fname = cards[i].querySelector('.pax-fname').value.trim();
      const lname = cards[i].querySelector('.pax-lname').value.trim();
      const dob   = cards[i].querySelector('.pax-dob').value;
      const gen   = cards[i].querySelector('.pax-gender').value;
      const nat   = cards[i].querySelector('.pax-nationality').value.trim() || nationality;

      this.state.pax.push({
        first_name:  fname,
        last_name:   lname,
        email:       i === 0 ? emailContact : '',
        phone:       i === 0 ? phoneContact : '',
        dob:         dob,
        gender:      gen,
        passport_id: passportNo || govtId,
        nationality: nat
      });
    }
  }

  /* ---- Confirm & Book (with payment validation, loading, premium confirmation population) ---- */
  async confirmBooking() {
    // 1. Validate current payment method
    const pv = this.validatePaymentDetails();
    if (!pv.valid) return;
    const paymentDetails = pv.paymentDetails;

    // 2. Show processing state
    const btn             = document.getElementById('confirm-booking-btn');
    const btnTextSpan     = document.getElementById('pay-btn-text');
    const btnLoadingSpan  = document.getElementById('pay-btn-loading');
    const overlay         = document.getElementById('pay-processing-overlay');
    const processingSub   = document.getElementById('pay-processing-subtitle');
    if (btn)             btn.disabled = true;
    if (btnTextSpan)     btnTextSpan.classList.add('hidden');
    if (btnLoadingSpan)  btnLoadingSpan.classList.remove('hidden');
    if (overlay)         overlay.classList.remove('hidden');

    const setProcessing = (msg) => {
      if (processingSub) processingSub.innerText = msg;
    };
    const methodLabel = this._humanPaymentMethod(paymentDetails.method);

    try {
      // Stage 1: build itinerary
      setProcessing(`Preparing itinerary and locking seats…`);
      const itinerary = [{
        flight_id:  this.state.flight.id,
        class:      this.state.cabinClass,
        extra_fees: this.state.extraSeatFees,
        seats_list: this.state.seats,
      }];
      if (this.state.returnFlight) {
        itinerary.push({
          flight_id:  this.state.returnFlight.id,
          class:      this.state.cabinClass,
          extra_fees: this.state.returnExtraSeatFees,
          seats_list: this.state.returnSeats,
        });
      }

      // Stage 2 (optional): validate payment separately if user chose non-counter method
      if (paymentDetails.method !== 'COUNTER') {
        setProcessing(`Connecting to ${methodLabel} gateway…`);
        await new Promise(r => setTimeout(r, 650));
        setProcessing(`Authorising payment of ₹${this.calcGrandTotal().toLocaleString()}…`);
        await new Promise(r => setTimeout(r, 700));
      } else {
        setProcessing(`Holding reservation for 48 hours at counter…`);
      }

      // Stage 3: send booking payload with payment_details to backend
      const payload = {
        itinerary,
        passengers: this.state.pax,
        services:   this.state.selectedServices,
        coupon:     this.state.coupon,
        deal_code:  this.state.dealCode,
        payment_details: paymentDetails,   // backend uses this to create Payment DB records
      };

      const res  = await fetch('/flights/book/confirm/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': this.getCsrfToken() },
        body: JSON.stringify(payload)
      });
      const data = await res.json();

      if (!data.success) {
        if (data.payment_status === 'FAILED' || res.status === 402) {
          throw new Error(data.error || `${methodLabel} payment was declined. Please try again or use a different method.`);
        }
        throw new Error(data.error || 'Booking failed — please try again.');
      }

      setProcessing(`Issuing ticket & generating PNR…`);
      await new Promise(r => setTimeout(r, 400));

      // Stage 4: populate and go to confirmation step
      this.populatePremiumConfirmation({
        pnrs: data.pnrs || (data.pnr ? [data.pnr] : []),
        ticketNumbers: data.ticket_numbers || [],
        payments: data.payments || [],
        paymentMethod: paymentDetails.method,
        transactionId: data.transaction_id || null,
        bookingStatus: data.booking_status || 'CONFIRMED',
        dealApplied: data.deal_applied || this.state.dealTitle,
        discountAmount: data.discount_amount || this.state.dealDiscountAmount || this.state.couponDiscount,
        itinerary,
      });

      await this.goToStep('confirmation', 'LANDING');

      // Trigger E-ticket scanner beam animation
      const ticketCard = document.querySelector('.ticket-card-premium');
      if (ticketCard) {
        const scanLine = document.createElement('div');
        scanLine.className = 'ticket-scan-line';
        ticketCard.style.position = 'relative';
        ticketCard.appendChild(scanLine);
        setTimeout(() => scanLine.remove(), 1300);
      }

      this.launchConfettiEffect();
      NotificationService.show('🎉 Booking Confirmed! Your E-Ticket is ready to download.', 'success');

    } catch (e) {
      if (overlay) overlay.classList.add('hidden');
      NotificationService.show(e.message || 'Payment failed.', 'error');
    } finally {
      if (btn)            btn.disabled = false;
      if (btnTextSpan)    btnTextSpan.classList.remove('hidden');
      if (btnLoadingSpan) btnLoadingSpan.classList.add('hidden');
      if (overlay)        setTimeout(() => overlay.classList.add('hidden'), 250);
    }
  }

  /* ---- Convert DB method choice → human-readable label ---- */
  _humanPaymentMethod(m) {
    switch (m) {
      case 'CARD':        return 'Credit/Debit Card';
      case 'UPI':         return 'UPI Payment';
      case 'NET_BANKING': return 'Net Banking';
      case 'WALLET':      return 'Digital Wallet';
      case 'COUNTER':     return 'Pay at Airport Counter';
      default:            return m || 'Card';
    }
  }
  _humanWallet(p) {
    return ({
      PAYTM: 'Paytm Wallet', PHONEPE: 'PhonePe', AMAZONPAY: 'Amazon Pay',
      MOBIKWIK: 'Mobikwik', FREECHARGE: 'Freecharge', OLA: 'Ola Money'
    })[p] || p;
  }
  _bankName(b) {
    return ({
      HDFC: 'HDFC Bank', ICICI: 'ICICI Bank', SBI: 'State Bank of India',
      AXIS: 'Axis Bank', KOTAK: 'Kotak Mahindra Bank', YES: 'Yes Bank',
      PNB: 'Punjab National Bank', BOB: 'Bank of Baroda',
      CANARA: 'Canara Bank', UNION: 'Union Bank of India',
      INDUSIND: 'IndusInd Bank', RBL: 'RBL Bank', OTHER: 'Other Bank'
    })[b] || b;
  }

  /* ---- Fill the NEW premium confirmation E-Ticket DOM ---- */
  populatePremiumConfirmation(ctx) {
    const setEl = (id, v) => { const el = document.getElementById(id); if (el != null) el.innerText = v; };

    // Main departure flight (primary info shown)
    const f = this.state.flight;
    const rf = this.state.returnFlight;
    const origAirport = this._findAirport(this.state.origin);
    const destAirport = this._findAirport(this.state.dest);
    const depTs = this._toLocal(f.departure_time || f.departure_at || f.scheduled_departure || this.state.date);
    const arrTs = this._toLocal(f.arrival_time   || f.arrival_at   || f.scheduled_arrival   || this.state.date);

    // --- Top badges ---
    const primaryPnr = (ctx.pnrs || [])[0] || '--------';
    const primaryTkt = (ctx.ticketNumbers || [])[0] || 'FE--------------';
    setEl('conf-pnr-main',    primaryPnr);
    setEl('conf-ticket-main', primaryTkt);
    setEl('conf-payment-status', (ctx.paymentStatus || (ctx.payments && ctx.payments[0]?.status) || 'SUCCESS').toUpperCase());

    // --- PNR strip (for multi-leg / round trip) ---
    const strip = document.getElementById('conf-pnr-strip-container');
    const inner = document.getElementById('conf-pnr');
    if (strip && inner && ctx.pnrs && ctx.pnrs.length > 1) {
      strip.classList.remove('d-none');
      inner.innerHTML = ctx.pnrs.map(p => `<span class="conf-badge conf-badge-pnr glass-inner" style="min-width:0;padding:0.4rem 0.8rem;"><span class="conf-badge-label">PNR</span> <span class="conf-badge-value" style="font-size:0.85rem;">${p}</span></span>`).join('');
    } else if (strip) {
      strip.classList.add('d-none');
    }

    // --- E-Ticket Header (issued date) ---
    setEl('conf-issued-date', new Date().toLocaleString(undefined, { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }));

    // --- E-Ticket Route timeline ---
    setEl('conf-orig-code', this.state.origin || '---');
    setEl('conf-orig-city', origAirport?.city || this.state.origin || '---');
    setEl('conf-dep-datetime', depTs);
    setEl('conf-dest-code', this.state.dest || '---');
    setEl('conf-dest-city', destAirport?.city || this.state.dest || '---');
    setEl('conf-arr-datetime', arrTs);
    setEl('conf-duration', f.duration_min ? this._fmtDuration(f.duration_min) : (rf && rf.duration_min ? this._fmtDuration(f.duration_min || rf.duration_min) : '--h --m'));

    // --- E-Ticket Details 4-col ---
    setEl('conf-flight-id',    `${f.airline?.code || 'FE'}-${f.flight_number || '----'}`);
    setEl('conf-airline-name', f.airline?.name || 'FlyEase Airlines');
    setEl('conf-aircraft',     f.aircraft?.model || f.aircraft_type || 'Boeing 737');
    setEl('conf-cabin',        (this.state.cabinClass || 'ECONOMY').charAt(0) + this.state.cabinClass.slice(1).toLowerCase());
    setEl('conf-seats',        [...this.state.seats, ...this.state.returnSeats].join(', ') || 'Unassigned');
    const n = this.state.passengersCount || 1;
    setEl('conf-pax-count',    `${n} Adult${n !== 1 ? 's' : ''}`);
    setEl('conf-total-paid-label', 'Total Paid');

    // --- E-Ticket Passenger rows ---
    const paxWrap = document.getElementById('conf-passengers-list');
    if (paxWrap) {
      const allSeats = [...this.state.seats, ...this.state.returnSeats];
      const cabin = (this.state.cabinClass || 'ECONOMY').charAt(0) + this.state.cabinClass.slice(1).toLowerCase();
      paxWrap.innerHTML = this.state.pax.map((px, idx) => {
        const seat = allSeats[idx % allSeats.length] || 'Unassigned';
        const dob = px.dob ? new Date(px.dob).toLocaleDateString() : '--';
        const gender = ({ M: 'Male', F: 'Female', O: 'Other' })[px.gender] || px.gender || '--';
        return `
          <div class="pax-row">
            <div class="pax-num">${idx + 1}</div>
            <div>
              <div class="pax-name">${(px.first_name || '').trim()} ${(px.last_name || '').trim()}</div>
              <div class="small muted">${px.email || this.state.pax[0]?.email || ''}</div>
            </div>
            <div><span class="pax-seat">${seat}</span></div>
            <div class="pax-class">${cabin}</div>
            <div class="pax-dob">${dob} · ${gender}</div>
          </div>
        `;
      }).join('');
    }

    // --- E-Ticket Fare breakdown ---
    const fareWrap = document.getElementById('conf-fare-breakdown');
    const p1 = f?.pricing || {};
    const p2 = rf?.pricing || {};
    const count = n;
    const baseFare   = ((p1.base_fare || 0)    + (p2.base_fare || 0))    * count;
    const dynFare    = ((p1.dynamic_fare || 0) + (p2.dynamic_fare || 0)) * count;
    const seatFees   = (this.state.extraSeatFees || 0) + (this.state.returnExtraSeatFees || 0);
    const srvFees    = this.state.serviceFees || 0;
    const taxes      = ((p1.taxes || 0) + (p2.taxes || 0)) * count;
    const discount   = (ctx.discountAmount || 0);
    const offerTitle = ctx.dealApplied || this.state.dealTitle || (this.state.coupon ? `Promo Code (${this.state.coupon})` : 'Offer Discount');
    const total      = this.calcGrandTotal();
    const fare = (label, val, cls='') =>
      `<div class="fare-row ${cls}"><span class="fare-label">${label}</span><span class="fare-val">${val}</span></div>`;
    if (fareWrap) {
      fareWrap.innerHTML =
        fare('Base Fare',            `₹${baseFare.toLocaleString(undefined, { maximumFractionDigits: 0 })}`) +
        fare('Dynamic Pricing',      `₹${dynFare.toLocaleString(undefined, { maximumFractionDigits: 0 })}`) +
        (seatFees > 0 ? fare('Seat Selection / Upgrades', `₹${seatFees.toLocaleString(undefined, { maximumFractionDigits: 0 })}`) : '') +
        (srvFees  > 0 ? fare('Add-on Services',         `₹${srvFees.toLocaleString(undefined, { maximumFractionDigits: 0 })}`)  : '') +
        fare('Taxes & Fees (incl. GST)', `₹${taxes.toLocaleString(undefined, { maximumFractionDigits: 0 })}`) +
        (discount > 0 ? fare(`Offer: ${offerTitle}`, `-₹${discount.toLocaleString(undefined, { maximumFractionDigits: 0 })}`, 'discount') : '') +
        fare('Total Amount Paid', `₹${total.toLocaleString(undefined, { maximumFractionDigits: 2 })}`, 'total');
    }
    setEl('conf-total', `₹${total.toLocaleString(undefined, { maximumFractionDigits: 2 })}`);

    // --- Payment method + TXN ID ---
    let methodHuman = this._humanPaymentMethod(ctx.paymentMethod);
    if (ctx.paymentMethod === 'WALLET' && ctx.payments?.length) {
      const provider = ctx.payments[0].wallet_provider || null;
      if (provider) methodHuman = `Wallet · ${this._humanWallet(provider)}`;
    }
    if (ctx.paymentMethod === 'NET_BANKING' && ctx.payments?.length) {
      const b = ctx.payments[0].bank_name || null;
      if (b) methodHuman = `Net Banking · ${this._bankName(b)}`;
    }
    if (ctx.paymentMethod === 'UPI' && ctx.payments?.length && ctx.payments[0].upi_id) {
      methodHuman = `UPI · ${ctx.payments[0].upi_id}`;
    }
    if (ctx.paymentMethod === 'CARD' && ctx.payments?.length && ctx.payments[0].card_last4) {
      methodHuman = `Card · •••• ${ctx.payments[0].card_last4}`;
    }
    setEl('conf-payment-method', methodHuman);
    const txnId = ctx.transactionId || (ctx.payments && ctx.payments[0]?.transaction_id) || (ctx.payments && ctx.payments[0]?.payment_id) || 'N/A';
    setEl('conf-txn-id', txnId);

    // --- QR / Verification URL ---
    const qrData = `${window.location.origin}/verify/${primaryPnr}/`;
    setEl('conf-qr-data', qrData);
    setEl('conf-booking-id', primaryPnr);

    // Remember primary and return PNRs/tickets for PDF downloads
    this._lastBooking = {
      pnr: primaryPnr,
      pnrs: ctx.pnrs || [primaryPnr],
      ticketNumbers: ctx.ticketNumbers || [primaryTkt],
      isRoundTrip: (ctx.pnrs && ctx.pnrs.length > 1)
    };

    // Update Action Buttons for Round-Trip vs One-Way
    const actionsContainer = document.querySelector('.confirmation-actions');
    if (actionsContainer && this._lastBooking.isRoundTrip) {
      const pnrOut = this._lastBooking.pnrs[0];
      const pnrRet = this._lastBooking.pnrs[1];
      actionsContainer.innerHTML = `
        <button type="button" class="btn btn-primary btn-large" onclick="app.downloadSingleETicket('${pnrOut}', 'Outbound')">
          <i class="fa-solid fa-plane-departure me-2"></i> Download Outbound PDF (${pnrOut})
        </button>
        <button type="button" class="btn btn-primary btn-large" onclick="app.downloadSingleETicket('${pnrRet}', 'Return')">
          <i class="fa-solid fa-plane-arrival me-2"></i> Download Return PDF (${pnrRet})
        </button>
        <button type="button" class="btn btn-outline btn-large" onclick="app.viewSingleETicket('${pnrOut}')">
          <i class="fa-solid fa-eye me-2"></i> View Outbound
        </button>
        <button type="button" class="btn btn-outline btn-large" onclick="app.viewSingleETicket('${pnrRet}')">
          <i class="fa-solid fa-eye me-2"></i> View Return
        </button>
        <button type="button" class="btn btn-outline btn-large" onclick="window.print()">
          <i class="fa-solid fa-print me-2"></i> Print
        </button>
        <button type="button" class="btn btn-ghost btn-large" onclick="location.href='/'">
          <i class="fa-solid fa-arrow-rotate-right me-2"></i> Book Another Flight
        </button>
      `;
    }
  }

  _findAirport(code) {
    if (!code || !Array.isArray(this.airports)) return null;
    return this.airports.find(a => (a.code || '').toUpperCase() === code.toUpperCase()) || null;
  }
  _toLocal(v) {
    if (!v) return '--';
    const d = v instanceof Date ? v : new Date(v);
    if (isNaN(d.getTime())) return String(v);
    return d.toLocaleString(undefined, {
      weekday: 'short', day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit'
    });
  }
  _fmtDuration(min) {
    if (!min) return '--';
    const h = Math.floor(min / 60), m = min % 60;
    return `${h}h ${String(m).padStart(2,'0')}m`;
  }

  /* ---- Download E-Ticket PDF ---- */
  downloadETicket() {
    const pnrs = this._lastBooking?.pnrs || (this._lastBooking?.pnr ? [this._lastBooking.pnr] : []);
    if (!pnrs.length) {
      NotificationService.show('No active booking to download.', 'warning');
      return;
    }
    pnrs.forEach((pnr, idx) => {
      setTimeout(() => {
        const link = document.createElement('a');
        link.href = `/flights/booking/${encodeURIComponent(pnr)}/eticket/`;
        link.download = `FlyEase_E-Ticket_${pnr}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }, idx * 600);
    });
    NotificationService.show(`Downloading E-Ticket PDF${pnrs.length > 1 ? 's' : ''}...`, 'success');
  }

  downloadSingleETicket(pnr, label = '') {
    if (!pnr) return;
    const link = document.createElement('a');
    link.href = `/flights/booking/${encodeURIComponent(pnr)}/eticket/`;
    link.download = `FlyEase_${label ? label + '_' : ''}E-Ticket_${pnr}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    NotificationService.show(`Downloading ${label || 'E-Ticket'} (PNR: ${pnr})...`, 'success');
  }

  /* ---- View Booking detail / PDF in new tab ---- */
  viewBookingDetail() {
    const pnr = this._lastBooking?.pnr;
    if (!pnr) {
      NotificationService.show('No active booking.', 'warning');
      return;
    }
    window.open(`/flights/booking/${encodeURIComponent(pnr)}/eticket/?view=1`, '_blank');
  }

  viewSingleETicket(pnr) {
    if (!pnr) return;
    window.open(`/flights/booking/${encodeURIComponent(pnr)}/eticket/?view=1`, '_blank');
  }

  /* ---- Confetti celebration effect ---- */
  launchConfettiEffect() {
    const colors = ['#6366f1', '#0ea5e9', '#f59e0b', '#10b981', '#ef4444', '#fff'];
    const container = document.body;
    for (let i = 0; i < 80; i++) {
      const dot = document.createElement('div');
      dot.style.cssText = `
        position:fixed;
        top:${Math.random() * 40}%;
        left:${Math.random() * 100}%;
        width:${6 + Math.random() * 8}px;
        height:${6 + Math.random() * 8}px;
        background:${colors[Math.floor(Math.random() * colors.length)]};
        border-radius:${Math.random() > 0.5 ? '50%' : '2px'};
        pointer-events:none;
        z-index:9999;
        animation:confettiFall ${1.5 + Math.random() * 2}s ease-in forwards;
        animation-delay:${Math.random() * 0.5}s;
      `;
      container.appendChild(dot);
      setTimeout(() => dot.remove(), 4000);
    }
  }

  /* ---- Auth & Dashboard ---- */
  bindAuthForms() {
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
      loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = Object.fromEntries(new FormData(loginForm).entries());
        try {
          const res = await fetch('/login/', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': this.getCsrfToken() }, body: JSON.stringify(data) });
          const js  = await res.json();
          if (js.success) window.location.href = js.redirect;
          else NotificationService.show(js.error, 'error');
        } catch { NotificationService.show('Login failed', 'error'); }
      });
    }

    const regForm = document.getElementById('register-form');
    if (regForm) {
      regForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = Object.fromEntries(new FormData(regForm).entries());
        try {
          const res = await fetch('/register/', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': this.getCsrfToken() }, body: JSON.stringify(data) });
          const js  = await res.json();
          if (js.success) window.location.href = js.redirect;
          else NotificationService.show(js.error, 'error');
        } catch { NotificationService.show('Registration failed', 'error'); }
      });
    }

    const dbList = document.getElementById('dashboard-bookings-list');
    if (dbList) this.loadDashboard();
  }

  /* ---- NOTIFICATION CENTER ---- */
  loadStoredNotifications() {
    try {
      const stored = localStorage.getItem('flyease_notifications');
      if (stored) return JSON.parse(stored);
    } catch(e) {}
    return [
      { id: 'notif-1', title: 'Welcome to FlyEase!', msg: 'Discover live flight simulator routing, dynamic pricing & digital boarding passes.', time: 'Just now', icon: 'fa-plane-departure', read: false, type: 'info' },
      { id: 'notif-2', title: 'Special Monsoon Deals Active', msg: 'Up to 30% OFF on select domestic & international routes. Use code MONSOON.', time: '1h ago', icon: 'fa-tag', read: false, type: 'deal' }
    ];
  }

  saveNotifications() {
    try {
      localStorage.setItem('flyease_notifications', JSON.stringify(this.notifications));
    } catch(e) {}
    this.updateNotificationBadge();
  }

  addNotification(title, msg, type = 'info', icon = 'fa-bell') {
    const notif = {
      id: `notif-${Date.now()}`,
      title,
      msg,
      time: 'Just now',
      icon,
      read: false,
      type
    };
    this.notifications.unshift(notif);
    this.saveNotifications();
    this.renderNotificationList();
    NotificationService.show(`${title}: ${msg}`, 'info');
  }

  initNotifications() {
    this.updateNotificationBadge();
    this.renderNotificationList();
  }

  updateNotificationBadge() {
    const badge = document.getElementById('notification-badge-count');
    if (!badge) return;
    const unreadCount = (this.notifications || []).filter(n => !n.read).length;
    if (unreadCount > 0) {
      badge.innerText = unreadCount > 9 ? '9+' : unreadCount;
      badge.classList.remove('hidden');
    } else {
      badge.classList.add('hidden');
    }
  }

  toggleNotificationDrawer() {
    const drawer = document.getElementById('notification-drawer-overlay');
    if (!drawer) return;
    drawer.classList.toggle('hidden');
    if (!drawer.classList.contains('hidden')) {
      this.renderNotificationList();
    }
  }

  renderNotificationList() {
    const list = document.getElementById('notification-items-list');
    if (!list) return;
    if (!this.notifications.length) {
      list.innerHTML = '<div class="text-center text-muted p-4"><i class="fa-regular fa-bell-slash fa-2x mb-2 d-block"></i>No notifications yet</div>';
      return;
    }
    list.innerHTML = this.notifications.map(n => `
      <div class="notification-item glass-inner p-3 mb-2 rounded ${n.read ? 'read' : 'unread'}" onclick="app.markNotificationRead('${n.id}')">
        <div class="flex gap-2 align-start">
          <div class="notif-icon-box flex align-center justify-center text-primary mt-1">
            <i class="fa-solid ${n.icon}"></i>
          </div>
          <div class="flex-1">
            <div class="flex justify-between align-center">
              <strong class="text-white small">${n.title}</strong>
              <span class="tiny muted">${n.time}</span>
            </div>
            <p class="muted small mb-0 mt-1">${n.msg}</p>
          </div>
          ${!n.read ? '<span class="unread-dot"></span>' : ''}
        </div>
      </div>
    `).join('');
  }

  markNotificationRead(id) {
    const n = this.notifications.find(x => x.id === id);
    if (n) {
      n.read = true;
      this.saveNotifications();
      this.renderNotificationList();
    }
  }

  markAllNotificationsRead() {
    this.notifications.forEach(n => n.read = true);
    this.saveNotifications();
    this.renderNotificationList();
  }

  clearAllNotifications() {
    this.notifications = [];
    this.saveNotifications();
    this.renderNotificationList();
    this.updateNotificationBadge();
  }

  /* ==========================================================
     CENTRAL FEATURE DISCOVERY HUB & AUTOMATIC REGISTRY ENGINE
     ========================================================== */
  initFeatureDiscoveryHub() {
    this.activeFeatureCategory = 'all';
    this.renderFeatureCategories();
    this.renderFeatureCards();
    this.initWhyFlyEaseSection();
    this.initScrollAirplaneTracker();
  }

  renderFeatureCategories() {
    const container = document.getElementById('feature-category-filters');
    if (!container) return;

    const categories = window.FLYEASE_FEATURE_CATEGORIES || [
      { key: "all", label: "✨ All Capabilities" }
    ];

    container.innerHTML = categories.map(cat => `
      <button type="button" class="feature-cat-pill ${cat.key === this.activeFeatureCategory ? 'active' : ''}" data-cat="${cat.key}" onclick="app.setFeatureCategory('${cat.key}')">
        ${cat.icon ? `<i class="${cat.icon} me-1"></i>` : ''} ${cat.label}
      </button>
    `).join('');

    const countBadge = document.getElementById('feature-count-badge');
    const totalFeatures = (window.FLYEASE_FEATURE_REGISTRY || []).length;
    if (countBadge) countBadge.innerText = `${totalFeatures} Active Capabilities`;
  }

  setFeatureCategory(catKey) {
    this.activeFeatureCategory = catKey;
    document.querySelectorAll('.feature-cat-pill').forEach(pill => {
      if (pill.dataset.cat === catKey) pill.classList.add('active');
      else pill.classList.remove('active');
    });
    this.renderFeatureCards();
  }

  filterFeatureCards() {
    this.renderFeatureCards();
  }

  renderFeatureCards() {
    const container = document.getElementById('feature-cards-grid');
    const noResultsEl = document.getElementById('no-features-found');
    const clearBtn = document.getElementById('clear-feature-search');
    const searchInput = document.getElementById('feature-search-input');
    if (!container) return;

    const query = (searchInput?.value || '').trim().toLowerCase();
    if (clearBtn) clearBtn.style.display = query ? 'inline-flex' : 'none';

    const registry = window.FLYEASE_FEATURE_REGISTRY || [];
    
    // Sort so '✨ NEW' / '🚀 JUST ADDED' appears first
    const sortedRegistry = [...registry].sort((a, b) => {
      const aIsNew = a.badgeType === 'new' ? 1 : 0;
      const bIsNew = b.badgeType === 'new' ? 1 : 0;
      return bIsNew - aIsNew;
    });

    const filtered = sortedRegistry.filter(f => {
      const matchesCategory = (this.activeFeatureCategory === 'all') || (f.categoryKey === this.activeFeatureCategory);
      if (!matchesCategory) return false;

      if (!query) return true;
      const titleMatch = f.title.toLowerCase().includes(query);
      const descMatch = f.description.toLowerCase().includes(query);
      const catMatch = f.category.toLowerCase().includes(query);
      const benMatch = f.benefits && f.benefits.some(b => b.toLowerCase().includes(query));
      return titleMatch || descMatch || catMatch || benMatch;
    });

    if (filtered.length === 0) {
      container.innerHTML = '';
      if (noResultsEl) noResultsEl.classList.remove('hidden');
      return;
    }

    if (noResultsEl) noResultsEl.classList.add('hidden');

    container.innerHTML = filtered.map(f => `
      <div class="flyease-feature-card reveal active" data-feature-id="${f.id}">
        <div>
          <div class="feat-card-top">
            <div class="feat-icon-box" style="background: ${f.iconBg || 'linear-gradient(135deg,#0284c7,#6366f1)'};">
              <i class="${f.icon}"></i>
            </div>
            ${f.badge ? `<span class="feat-badge-pill ${f.badgeType || 'hot'}">${f.badge}</span>` : ''}
          </div>

          <h3 class="feat-card-title">${f.title}</h3>
          <p class="feat-card-desc">${f.description}</p>

          <ul class="feat-benefits-list">
            ${(f.benefits || []).map(b => `
              <li class="feat-benefit-item"><i class="fa-solid fa-check"></i> ${b}</li>
            `).join('')}
          </ul>
        </div>

        <div class="feat-card-footer">
          <span class="feat-stat-tag"><i class="fa-solid fa-microchip text-secondary me-1"></i> ${f.stats || 'Active'}</span>
          <button type="button" class="feat-cta-btn" onclick="app.executeFeatureAction('${f.id}')">
            ${f.ctaText || 'Explore'} <i class="fa-solid fa-arrow-right"></i>
          </button>
        </div>
      </div>
    `).join('');

    // Attach subtle 3D tilt interaction
    this.attachCardTiltHandlers();
  }

  attachCardTiltHandlers() {
    document.querySelectorAll('.flyease-feature-card').forEach(card => {
      card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        const rotateX = ((y - centerY) / centerY) * -6;
        const rotateY = ((x - centerX) / centerX) * 6;
        card.style.transform = `perspective(1000px) rotateX(${rotateX.toFixed(2)}deg) rotateY(${rotateY.toFixed(2)}deg) translateY(-6px)`;
      });
      card.addEventListener('mouseleave', () => {
        card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0)';
      });
    });
  }

  executeFeatureAction(featureId) {
    const feature = (window.FLYEASE_FEATURE_REGISTRY || []).find(f => f.id === featureId);
    if (!feature) return;

    if (feature.actionType === 'js' && feature.actionTarget) {
      try {
        eval(feature.actionTarget);
      } catch (e) {
        console.warn('Feature action evaluation error:', e);
      }
    } else if (feature.actionType === 'scroll' && feature.actionTarget) {
      const el = document.getElementById(feature.actionTarget);
      if (el) el.scrollIntoView({ behavior: 'smooth' });
    } else if (feature.actionType === 'link' && feature.actionTarget) {
      if (feature.actionTarget.startsWith('/#')) {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        const orig = document.getElementById('origin');
        if (orig) orig.focus();
      } else {
        window.location.href = feature.actionTarget;
      }
    }
  }

  initWhyFlyEaseSection() {
    const tabsContainer = document.getElementById('why-tabs-container');
    const displayPanel = document.getElementById('why-display-panel');
    if (!tabsContainer || !displayPanel) return;

    let coreHighlights = (window.FLYEASE_FEATURE_REGISTRY || []).slice(0, 5);
    if (!coreHighlights.length) {
      coreHighlights = [
        {
          id: "ai-assistant",
          title: "FlyEase AI Assistant",
          category: "AI & Smart Travel",
          icon: "fa-solid fa-wand-magic-sparkles",
          iconBg: "linear-gradient(135deg, #0284c7, #6366f1)",
          badge: "✨ NEW",
          stats: "Llama 3.3 70B Grounded",
          highlightTitle: "Conversational Travel Intelligence",
          highlightDesc: "Natural-language aviation intelligence with real-time database flight grounding, baggage rules, and instant booking.",
          benefits: ["Real-time flight database grounding", "Instant visa & baggage answers", "One-click flight checkout"],
          ctaText: "Ask FlyEase AI",
          actionType: "js",
          actionTarget: "app.toggleAIChat()"
        },
        {
          id: "dynamic-pricing",
          title: "Dynamic Pricing",
          category: "Deals & Pricing",
          icon: "fa-solid fa-chart-line",
          iconBg: "linear-gradient(135deg, #4f46e5, #818cf8)",
          badge: "⚡ LIVE ALGO",
          stats: "100% Deterministic",
          highlightTitle: "Airline-Grade Dynamic Pricing",
          highlightDesc: "Live demand, seat load-factor calculations and departure countdown pricing algorithms.",
          benefits: ["Load factor multipliers", "Transparent fee breakdown", "Fare trajectory graph"],
          ctaText: "Explore Fare Engine",
          actionType: "scroll",
          actionTarget: "pricing-chart"
        },
        {
          id: "seat-selection-3d",
          title: "3D Seat Selection",
          category: "Booking",
          icon: "fa-solid fa-couch",
          iconBg: "linear-gradient(135deg, #0ea5e9, #38bdf8)",
          badge: "💺 3D CABIN",
          stats: "WebGL Spatial Orbit",
          highlightTitle: "Spatial 3D Cabin Visualizer",
          highlightDesc: "Interactive 3D aircraft cabin visualizer with emergency exit upgrades and live seat map locks.",
          benefits: ["Interactive 3D orbit & zoom", "Window/aisle tagging", "Live seat locking"],
          ctaText: "Choose Your Seat",
          actionType: "link",
          actionTarget: "/#step-search"
        },
        {
          id: "flight-comparison",
          title: "Flight Comparison",
          category: "AI & Smart Travel",
          icon: "fa-solid fa-code-compare",
          iconBg: "linear-gradient(135deg, #06b6d4, #3b82f6)",
          badge: "🚀 JUST ADDED",
          stats: "Up to 4 Flights",
          highlightTitle: "Multi-Factor Comparison Matrix",
          highlightDesc: "Compare up to 4 flights side-by-side on duration, dynamic fares, baggage allowance, and carbon footprint.",
          benefits: ["Cheapest & Best Value badges", "Carbon footprint estimates", "Direct booking from matrix"],
          ctaText: "Compare Flights",
          actionType: "link",
          actionTarget: "/#step-search"
        },
        {
          id: "live-radar",
          title: "Live Flight Radar",
          category: "Trips & Radar",
          icon: "fa-solid fa-satellite-dish",
          iconBg: "linear-gradient(135deg, #10b981, #059669)",
          badge: "📡 REAL-TIME",
          stats: "Live Coordinates",
          highlightTitle: "Live GPS Flight Tracker",
          highlightDesc: "Interactive airway radar map tracking aircraft latitude, longitude, altitude, speed, and remaining flight time.",
          benefits: ["Real-time aircraft coordinates", "Weather overlay along route", "Live takeoff & landing telemetry"],
          ctaText: "Track Live Flight",
          actionType: "link",
          actionTarget: "/#step-search"
        }
      ];
    }

    tabsContainer.innerHTML = coreHighlights.map((feat, idx) => `
      <button type="button" class="why-tab-btn ${idx === 0 ? 'active' : ''}" data-why-id="${feat.id}" onclick="app.selectWhyHighlight('${feat.id}')">
        <div class="why-tab-icon" style="background: ${feat.iconBg};">
          <i class="${feat.icon}"></i>
        </div>
        <div>
          <strong class="d-block text-white small">${feat.title}</strong>
          <span class="tiny text-muted">${feat.category}</span>
        </div>
      </button>
    `).join('');

    this._coreWhyHighlights = coreHighlights;
    this.selectWhyHighlight(coreHighlights[0].id);
  }

  selectWhyHighlight(featureId) {
    const displayPanel = document.getElementById('why-display-panel');
    const registry = window.FLYEASE_FEATURE_REGISTRY || this._coreWhyHighlights || [];
    const feature = registry.find(f => f.id === featureId);
    if (!displayPanel || !feature) return;

    document.querySelectorAll('.why-tab-btn').forEach(btn => {
      if (btn.dataset.whyId === featureId) btn.classList.add('active');
      else btn.classList.remove('active');
    });

    displayPanel.innerHTML = `
      <div class="why-highlight-content">
        <div class="flex justify-between align-center mb-3">
          <span class="badge badge-primary font-mono">${feature.badge || '✨ FEATURED'}</span>
          <span class="text-secondary small font-mono">${feature.stats || 'FlyEase Core'}</span>
        </div>
        <h3 class="text-white font-display mb-2" style="font-size: 1.5rem;">${feature.highlightTitle || feature.title}</h3>
        <p class="text-muted mb-4" style="line-height: 1.6;">${feature.highlightDesc || feature.description}</p>
        
        <div class="glass p-3 mb-4 rounded-lg border border-secondary">
          <strong class="text-cyan small d-block mb-2"><i class="fa-solid fa-sparkles me-1"></i> Key Technical Capabilities:</strong>
          <div class="grid gap-2" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));">
            ${(feature.benefits || []).map(b => `
              <div class="flex align-center gap-2 small text-white">
                <i class="fa-solid fa-circle-check text-success"></i> ${b}
              </div>
            `).join('')}
          </div>
        </div>

        <div class="flex justify-between align-center flex-wrap gap-3">
          <span class="text-muted tiny"><i class="fa-solid fa-shield-halved text-success me-1"></i> Tested & Concurrency Protected</span>
          <button type="button" class="btn btn-primary btn-md glow-btn" onclick="app.executeFeatureAction('${feature.id}')">
            ${feature.ctaText || 'Launch Capability'} <i class="fa-solid fa-arrow-right ms-2"></i>
          </button>
        </div>
      </div>
    `;
  }

  initScrollAirplaneTracker() {
    const journeyContainer = document.querySelector('.flyease-journey-section');
    const airplaneTracker = document.getElementById('journey-airplane-tracker');
    if (!journeyContainer || !airplaneTracker) return;

    window.addEventListener('scroll', () => {
      const rect = journeyContainer.getBoundingClientRect();
      const windowHeight = window.innerHeight;
      if (rect.top < windowHeight && rect.bottom > 0) {
        const progress = Math.min(Math.max((windowHeight - rect.top) / (windowHeight + rect.height), 0), 1);
        const steps = document.querySelectorAll('.journey-step-card');
        const activeStepIdx = Math.min(Math.floor(progress * steps.length), steps.length - 1);
        steps.forEach((s, idx) => {
          if (idx <= activeStepIdx) s.classList.add('active');
          else s.classList.remove('active');
        });
      }
    });
  }
  toggleFlightForComparison(flightId) {
    const flight = this.state.depOffers.find(f => f.id === flightId) || this.state.retOffers.find(f => f.id === flightId);
    if (!flight) return;

    const idx = this.comparisonList.findIndex(f => f.id === flightId);
    if (idx > -1) {
      this.comparisonList.splice(idx, 1);
      NotificationService.show(`Removed ${flight.airline.code}-${flight.flight_number} from comparison`, 'info');
    } else {
      if (this.comparisonList.length >= 4) {
        NotificationService.show('You can compare up to 4 flights at once.', 'warning');
        return;
      }
      this.comparisonList.push(flight);
      NotificationService.show(`Added ${flight.airline.code}-${flight.flight_number} to comparison`, 'success');
    }

    this.updateComparisonTray();
    this.updateCompareCheckboxes();
  }

  updateComparisonTray() {
    const tray = document.getElementById('flight-compare-tray');
    const countEl = document.getElementById('compare-count');
    const thumbWrap = document.getElementById('compare-thumbnails');
    if (!tray || !countEl || !thumbWrap) return;

    countEl.innerText = this.comparisonList.length;
    if (this.comparisonList.length >= 1) {
      tray.classList.remove('hidden');
      thumbWrap.innerHTML = this.comparisonList.map(f => `
        <span class="badge badge-outline flex align-center gap-1 font-mono">
          <b>${f.airline.code}-${f.flight_number}</b> (₹${f.pricing.total.toFixed(0)})
          <i class="fa-solid fa-xmark cursor-pointer text-danger ms-1" onclick="app.toggleFlightForComparison(${f.id})"></i>
        </span>
      `).join('');
    } else {
      tray.classList.add('hidden');
    }
  }

  updateCompareCheckboxes() {
    document.querySelectorAll('.compare-check-btn').forEach(btn => {
      const id = parseInt(btn.dataset.id);
      const isSelected = this.comparisonList.some(f => f.id === id);
      if (isSelected) {
        btn.classList.add('active');
        btn.innerHTML = '<i class="fa-solid fa-check text-cyan me-1"></i> Comparing';
      } else {
        btn.classList.remove('active');
        btn.innerHTML = '<i class="fa-solid fa-code-compare me-1"></i> Compare';
      }
    });
  }

  clearComparison() {
    this.comparisonList = [];
    this.updateComparisonTray();
    this.updateCompareCheckboxes();
  }

  openFlightComparison() {
    if (this.comparisonList.length < 2) {
      NotificationService.show('Please select at least 2 flights to compare side by side.', 'warning');
      return;
    }
    const modal = document.getElementById('flight-compare-modal');
    const matrix = document.getElementById('compare-matrix-container');
    if (!modal || !matrix) return;

    // Calculate Best Value, Cheapest, Fastest, Lowest Emissions
    const sortedByPrice = [...this.comparisonList].sort((a,b) => a.pricing.total - b.pricing.total);
    const cheapestId = sortedByPrice[0].id;

    const sortedBySpeed = [...this.comparisonList].sort((a,b) => a.duration_hours - b.duration_hours);
    const fastestId = sortedBySpeed[0].id;

    // Lowest emissions calculation (turboprop / neo ~105g CO2, standard jet ~140g CO2)
    const sortedByEmissions = [...this.comparisonList].sort((a,b) => {
      const emA = a.duration_hours * 110;
      const emB = b.duration_hours * 110;
      return emA - emB;
    });
    const lowestEmissionsId = sortedByEmissions[0].id;

    // Multi-factor Best Value Score
    let bestValueId = cheapestId;
    let minScore = Infinity;
    this.comparisonList.forEach(f => {
      const priceNorm = f.pricing.total / (sortedByPrice[0].pricing.total || 1);
      const durationNorm = f.duration_hours / (sortedBySpeed[0].duration_hours || 1);
      const score = (priceNorm * 0.55) + (durationNorm * 0.45);
      if (score < minScore) {
        minScore = score;
        bestValueId = f.id;
      }
    });

    let matrixHtml = `
      <table class="compare-table w-100 font-sans">
        <thead>
          <tr>
            <th class="compare-feature-col">Parameters</th>
            ${this.comparisonList.map(f => {
              const badges = [];
              if (f.id === bestValueId) badges.push('<span class="badge badge-success mb-1 d-block"><i class="fa-solid fa-trophy me-1"></i> BEST VALUE</span>');
              if (f.id === cheapestId) badges.push('<span class="badge badge-warning mb-1 d-block"><i class="fa-solid fa-coins me-1"></i> CHEAPEST</span>');
              if (f.id === fastestId) badges.push('<span class="badge badge-primary mb-1 d-block"><i class="fa-solid fa-bolt me-1"></i> FASTEST</span>');
              if (f.id === lowestEmissionsId) badges.push('<span class="badge badge-cyan mb-1 d-block"><i class="fa-solid fa-leaf me-1"></i> LOWEST EMISSIONS</span>');

              return `
                <th class="text-center compare-flight-th">
                  ${badges.join('')}
                  <div class="h4 m-0 text-white font-display">${f.airline.name}</div>
                  <div class="text-cyan font-mono small mb-2">${f.airline.code}-${f.flight_number}</div>
                  <div class="h3 text-gradient m-0 font-mono">₹${f.pricing.total.toFixed(2)}</div>
                  <button type="button" class="btn btn-primary btn-sm w-100 mt-2 glow-btn" onclick="app.selectFlightFromCompare(${f.id})">
                    Select Flight <i class="fa-solid fa-arrow-right ms-1"></i>
                  </button>
                </th>
              `;
            }).join('')}
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="font-weight-bold text-muted"><i class="fa-solid fa-plane-departure me-2"></i> Route & Flight</td>
            ${this.comparisonList.map(f => `<td>${f.origin} → ${f.destination} (${f.airline.code}-${f.flight_number})</td>`).join('')}
          </tr>
          <tr>
            <td class="font-weight-bold text-muted"><i class="fa-regular fa-clock me-2"></i> Departure & Arrival</td>
            ${this.comparisonList.map(f => {
              const dep = new Date(f.departure_time).toLocaleTimeString([], { hour:'2-digit', minute:'2-digit' });
              const arr = new Date(f.arrival_time).toLocaleTimeString([], { hour:'2-digit', minute:'2-digit' });
              return `<td><b>${dep}</b> → <b>${arr}</b></td>`;
            }).join('')}
          </tr>
          <tr>
            <td class="font-weight-bold text-muted"><i class="fa-solid fa-hourglass-half me-2"></i> Duration & Stops</td>
            ${this.comparisonList.map(f => `<td><b>${f.duration_hours}h 00m</b> · Non-stop</td>`).join('')}
          </tr>
          <tr>
            <td class="font-weight-bold text-muted"><i class="fa-solid fa-suitcase-rolling me-2"></i> Baggage Allowance</td>
            ${this.comparisonList.map(f => `<td>Cabin: 7kg · Check-in: 15kg (Included)</td>`).join('')}
          </tr>
          <tr>
            <td class="font-weight-bold text-muted"><i class="fa-solid fa-chair me-2"></i> Seat Availability</td>
            ${this.comparisonList.map(f => `<td class="text-success font-weight-bold"><i class="fa-solid fa-circle-check me-1"></i> ${f.available_seats || 45} Seats Left</td>`).join('')}
          </tr>
          <tr>
            <td class="font-weight-bold text-muted"><i class="fa-solid fa-leaf text-success me-2"></i> Carbon Footprint</td>
            ${this.comparisonList.map(f => `<td>~${Math.round(f.duration_hours * 115)} kg CO₂ <span class="tiny text-muted">/ passenger</span></td>`).join('')}
          </tr>
          <tr>
            <td class="font-weight-bold text-muted"><i class="fa-solid fa-wifi me-2"></i> In-Flight Amenities</td>
            ${this.comparisonList.map(f => `<td><i class="fa-solid fa-wifi text-primary me-1"></i> USB Port · <i class="fa-solid fa-utensils text-warning me-1"></i> Snacks · Stream TV</td>`).join('')}
          </tr>
          <tr>
            <td class="font-weight-bold text-muted"><i class="fa-solid fa-rotate-left me-2"></i> Refundability</td>
            ${this.comparisonList.map(f => `<td class="text-cyan"><i class="fa-solid fa-shield-check me-1"></i> Refundable (Subject to airline policy)</td>`).join('')}
          </tr>
          <tr>
            <td class="font-weight-bold text-muted"><i class="fa-solid fa-plane me-2"></i> Aircraft Model</td>
            ${this.comparisonList.map(f => `<td>${f.aircraft || 'Airbus A320neo'}</td>`).join('')}
          </tr>
        </tbody>
      </table>
    `;

    matrix.innerHTML = matrixHtml;
    modal.classList.add('is-open');
    modal.classList.remove('hidden');
  }

  closeFlightComparison() {
    const modal = document.getElementById('flight-compare-modal');
    if (modal) {
      modal.classList.remove('is-open');
      modal.classList.add('hidden');
    }
  }

  selectFlightFromCompare(flightId) {
    this.closeFlightComparison();
    const flight = this.state.depOffers.find(f => f.id === flightId) || this.state.retOffers.find(f => f.id === flightId);
    if (flight) this.selectFlight(flight);
  }

  /* ---- 2. 3D / 2D SEAT MAP ENGINE ---- */
  setSeatViewMode(mode) {
    this.seatViewMode = mode;
    const btn3d = document.getElementById('seat-view-3d-btn');
    const btn2d = document.getElementById('seat-view-2d-btn');
    const container = document.getElementById('aircraft-3d-container');
    const toolbar = document.getElementById('cabin-3d-toolbar');

    if (mode === '3d') {
      if (btn3d) btn3d.classList.add('active');
      if (btn2d) btn2d.classList.remove('active');
      if (container) container.classList.remove('view-2d-mode');
      if (toolbar) toolbar.classList.remove('hidden');
      this.updateCabinTransform();
    } else {
      if (btn2d) btn2d.classList.add('active');
      if (btn3d) btn3d.classList.remove('active');
      if (container) container.classList.add('view-2d-mode');
      if (toolbar) toolbar.classList.add('hidden');
      const fuselage = document.getElementById('aircraft-fuselage');
      if (fuselage) fuselage.style.transform = 'none';
    }
  }

  rotateCabin(deg) {
    if (this.seatViewMode !== '3d') return;
    this.cabinRotation += deg;
    this.updateCabinTransform();
  }

  zoomCabin(delta) {
    if (this.seatViewMode !== '3d') return;
    this.cabinZoom = Math.min(1.4, Math.max(0.7, this.cabinZoom + delta));
    this.updateCabinTransform();
  }

  resetCabinCamera() {
    this.cabinRotation = 0;
    this.cabinZoom = 1.0;
    this.updateCabinTransform();
  }

  updateCabinTransform() {
    const fuselage = document.getElementById('aircraft-fuselage');
    if (!fuselage || this.seatViewMode !== '3d') return;
    fuselage.style.transform = `rotateY(${this.cabinRotation}deg) scale(${this.cabinZoom})`;
  }

  /* ---- 3. EXPLORE WITHOUT DESTINATION ---- */
  initExploreSection() {
    this.exploreDateWindow = 'this-weekend';
    this.exploreDestinationsList = [];
    this.exploreVisibleCount = 6;
    this.exploreBudgetTimeout = null;
    const slider = document.getElementById('explore-budget-slider');
    const initialBudget = slider ? slider.value : 18500;
    const el = document.getElementById('explore-budget-val');
    if (el) el.innerText = `₹${parseInt(initialBudget).toLocaleString()}`;
    this.loadExploreDestinations('all', initialBudget, this.exploreDateWindow);
  }

  updateExploreBudget(val) {
    const el = document.getElementById('explore-budget-val');
    if (el) el.innerText = `₹${parseInt(val).toLocaleString()}`;
    
    // Real-time debounce for fast slider sliding without thrashing network
    if (this.exploreBudgetTimeout) clearTimeout(this.exploreBudgetTimeout);
    this.exploreBudgetTimeout = setTimeout(() => {
      const activeCat = document.querySelector('.explore-cat-btn.active')?.dataset.cat || 'all';
      const dateWin = this.exploreDateWindow || 'this-weekend';
      this.loadExploreDestinations(activeCat, val, dateWin);
    }, 60);
  }

  setExploreCategory(btn, cat) {
    document.querySelectorAll('.explore-cat-btn').forEach(b => b.classList.remove('active'));
    if (btn) btn.classList.add('active');
    const budget = document.getElementById('explore-budget-slider')?.value || 18500;
    const dateWin = this.exploreDateWindow || 'this-weekend';
    this.loadExploreDestinations(cat, budget, dateWin);
  }

  setExploreDate(btn, dateType) {
    document.querySelectorAll('.explore-date-btn').forEach(b => b.classList.remove('active'));
    if (btn) btn.classList.add('active');
    this.exploreDateWindow = dateType;
    const activeCat = document.querySelector('.explore-cat-btn.active')?.dataset.cat || 'all';
    const budget = document.getElementById('explore-budget-slider')?.value || 18500;
    this.loadExploreDestinations(activeCat, budget, dateType);
  }

  async loadExploreDestinations(category = 'all', budget = 18500, dateWindow = 'this-weekend') {
    const grid = document.getElementById('explore-results-grid');
    const loadMoreContainer = document.getElementById('explore-load-more-container');
    if (!grid) return;

    try {
      const res = await fetch(`/flights/explore/?category=${encodeURIComponent(category)}&max_budget=${budget}&date_window=${encodeURIComponent(dateWindow)}`);
      const data = await res.json();
      if (!data.destinations || !data.destinations.length) {
        this.exploreDestinationsList = [];
        grid.innerHTML = '<div class="glass p-5 text-center muted col-span-3"><i class="fa-solid fa-compass-drafting fa-2x mb-2 d-block text-cyan"></i><p class="text-white font-weight-bold mb-1">No destinations found under ₹' + parseInt(budget).toLocaleString() + '</p><p class="small text-muted mb-0">Try dragging the budget slider to the right or selecting "All Destinations".</p></div>';
        if (loadMoreContainer) loadMoreContainer.style.display = 'none';
        return;
      }

      this.exploreDestinationsList = data.destinations;
      this.exploreVisibleCount = 6;
      this.renderExploreGrid();
    } catch(e) {
      grid.innerHTML = '<p class="text-danger text-center">Unable to load explore destinations.</p>';
      if (loadMoreContainer) loadMoreContainer.style.display = 'none';
    }
  }

  renderExploreGrid() {
    const grid = document.getElementById('explore-results-grid');
    const loadMoreContainer = document.getElementById('explore-load-more-container');
    const remainingSpan = document.getElementById('explore-remaining-count');
    if (!grid) return;

    const visibleItems = this.exploreDestinationsList.slice(0, this.exploreVisibleCount);
    grid.innerHTML = visibleItems.map(d => `
      <div class="dest-card explore-interactive-card glass fade-in" onclick="app.bookExploreDestination('${d.code}', '${d.target_date || ''}')">
        <img src="${d.image}" referrerpolicy="no-referrer" loading="lazy" class="dest-img" alt="${d.city}">
        <div class="dest-overlay">
          <div class="flex justify-between align-center mb-1">
            <div class="dest-badge ${d.is_international ? 'dest-badge-purple' : ''}">
              <i class="fa-solid ${d.is_international ? 'fa-earth-americas' : 'fa-plane'}"></i> ${d.is_international ? 'International' : 'Domestic'}
            </div>
            ${d.travel_window_tag ? `<span class="badge badge-outline tiny font-mono text-cyan">${d.travel_window_tag}</span>` : ''}
          </div>
          <h3 class="m-0">${d.city} (${d.code})</h3>
          <p class="text-secondary small mb-1">${d.country} · ${d.duration} · ${d.season}</p>
          <div class="flex justify-between align-center mt-2">
            <span class="text-gradient font-mono font-large font-weight-bold">From ₹${d.starting_price.toLocaleString()}</span>
            <span class="btn btn-primary btn-xs">Book Flight <i class="fa-solid fa-arrow-right ms-1"></i></span>
          </div>
        </div>
      </div>
    `).join('');

    const remaining = this.exploreDestinationsList.length - this.exploreVisibleCount;
    if (loadMoreContainer) {
      if (remaining > 0) {
        loadMoreContainer.style.display = 'block';
        if (remainingSpan) remainingSpan.innerText = remaining;
      } else {
        loadMoreContainer.style.display = 'none';
      }
    }
  }

  loadMoreExploreDestinations() {
    this.exploreVisibleCount += 6;
    this.renderExploreGrid();
  }

  bookExploreDestination(destCode, travelDate = null) {
    const orig = document.getElementById('origin');
    const dest = document.getElementById('destination');
    const depInput = document.getElementById('depart-date') || document.getElementById('dep-date');
    if (orig && !orig.value) orig.value = 'BOM';
    if (dest) dest.value = destCode;
    if (depInput) {
      if (travelDate) {
        depInput.value = travelDate;
      } else if (!depInput.value) {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        depInput.value = tomorrow.toISOString().split('T')[0];
      }
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
    setTimeout(() => {
      const searchBtn = document.getElementById('search-btn') || document.getElementById('search-flights-btn');
      if (searchBtn) searchBtn.click();
    }, 350);
  }

  /* ---- 4. REALISTIC 3D VIDEO EARTH GLOBE CONTROLLER ---- */
  initInteractiveGlobe() {
    const canvas = document.getElementById('interactive-globe-canvas');
    const video = document.getElementById('earth-bg-video');
    if (!canvas) return;

    if (video) {
      video.play().catch(() => {});
    }

    const ctx = canvas.getContext('2d');
    const sphereSize = 360;
    canvas.width = sphereSize;
    canvas.height = sphereSize;

    const HUBS = [
      { code: 'BOM', city: 'Mumbai', country: 'India', lat: 19.08, lon: 72.87, fare: 2800, season: 'Oct – Mar' },
      { code: 'DEL', city: 'Delhi', country: 'India', lat: 28.55, lon: 77.10, fare: 3200, season: 'Oct – Mar' },
      { code: 'BLR', city: 'Bengaluru', country: 'India', lat: 12.97, lon: 77.59, fare: 2900, season: 'Sep – Mar' },
      { code: 'GOI', city: 'Goa', country: 'India', lat: 15.38, lon: 73.83, fare: 3100, season: 'Nov – Mar' },
      { code: 'DXB', city: 'Dubai', country: 'UAE', lat: 25.25, lon: 55.36, fare: 7999, season: 'Nov – Mar' },
      { code: 'SIN', city: 'Singapore', country: 'Singapore', lat: 1.36, lon: 103.99, fare: 12499, season: 'All Year' },
      { code: 'BKK', city: 'Bangkok', country: 'Thailand', lat: 13.69, lon: 100.75, fare: 8999, season: 'Nov – Feb' },
      { code: 'MLE', city: 'Maldives', country: 'Maldives', lat: 4.17, lon: 73.50, fare: 14500, season: 'Dec – Apr' },
      { code: 'LHR', city: 'London', country: 'UK', lat: 51.47, lon: -0.45, fare: 28999, season: 'May – Sep' },
      { code: 'CDG', city: 'Paris', country: 'France', lat: 49.00, lon: 2.55, fare: 32500, season: 'Apr – Oct' },
      { code: 'FRA', city: 'Frankfurt', country: 'Germany', lat: 50.03, lon: 8.57, fare: 31000, season: 'May – Sep' },
      { code: 'HND', city: 'Tokyo', country: 'Japan', lat: 35.54, lon: 139.77, fare: 35000, season: 'Mar – May' },
      { code: 'JFK', city: 'New York', country: 'USA', lat: 40.64, lon: -73.77, fare: 42500, season: 'May – Oct' },
      { code: 'SFO', city: 'San Francisco', country: 'USA', lat: 37.62, lon: -122.37, fare: 45000, season: 'Sep – Nov' },
      { code: 'SYD', city: 'Sydney', country: 'Australia', lat: -33.93, lon: 151.17, fare: 46000, season: 'Sep – Apr' },
      { code: 'DPS', city: 'Bali', country: 'Indonesia', lat: -8.74, lon: 115.16, fare: 16500, season: 'Apr – Oct' }
    ];

    let rot = 0;
    let isDragging = false;
    let startX = 0;

    canvas.onmousedown = (e) => {
      isDragging = true;
      startX = e.clientX;
      this.globeAutoSpin = false;
      const spinBtn = document.getElementById('globe-spin-btn');
      if (spinBtn) spinBtn.innerHTML = '<i class="fa-solid fa-play"></i>';
    };

    window.addEventListener('mouseup', () => { isDragging = false; });
    window.addEventListener('mousemove', (e) => {
      if (!isDragging) return;
      const dx = e.clientX - startX;
      rot += dx * 0.5;
      startX = e.clientX;
    });

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const cx = canvas.width / 2;
      const cy = canvas.height / 2;
      const r = (sphereSize / 2) - 6; // Fits directly on the globe sphere

      // Clip all route lines and effects directly to the circular earth sphere
      ctx.save();
      ctx.beginPath();
      ctx.arc(cx, cy, r + 2, 0, Math.PI * 2);
      ctx.clip();

      // Calculate projected 3D coordinates on the sphere
      const projectPoint = (lat, lon, rotation) => {
        const radLon = (lon + rotation) * Math.PI / 180;
        const radLat = lat * Math.PI / 180;
        const x = cx + r * Math.cos(radLat) * Math.sin(radLon);
        const y = cy - r * Math.sin(radLat);
        const z = Math.cos(radLon) * Math.cos(radLat);
        return { x, y, z, visible: z > 0.05 };
      };

      const projectedHubs = HUBS.map(h => ({
        ...h,
        ...projectPoint(h.lat, h.lon, rot)
      }));

      // Draw Great Circle curved arcs along Earth surface between BOM and other hubs
      const bom = HUBS.find(h => h.code === 'BOM');
      const bomProj = projectedHubs.find(h => h.code === 'BOM');

      if (bom && bomProj && bomProj.visible) {
        HUBS.forEach((h, idx) => {
          if (h.code === 'BOM') return;
          const targetProj = projectedHubs[idx];
          if (!targetProj.visible) return;

          // Draw spherical interpolated route curve
          ctx.beginPath();
          const steps = 24;
          let firstPoint = true;

          for (let s = 0; s <= steps; s++) {
            const t = s / steps;
            // Linear spherical interpolation of lat/lon
            const curLat = bom.lat + (h.lat - bom.lat) * t;
            const curLon = bom.lon + (h.lon - bom.lon) * t;
            const pt = projectPoint(curLat, curLon, rot);

            // Add altitude curvature above surface
            const altitude = Math.sin(t * Math.PI) * 18;
            const dirX = (pt.x - cx) / r;
            const dirY = (pt.y - cy) / r;
            const arcX = pt.x + dirX * altitude;
            const arcY = pt.y + dirY * altitude;

            if (pt.z > -0.1) {
              if (firstPoint) {
                ctx.moveTo(arcX, arcY);
                firstPoint = false;
              } else {
                ctx.lineTo(arcX, arcY);
              }
            }
          }

          const routeGrad = ctx.createLinearGradient(bomProj.x, bomProj.y, targetProj.x, targetProj.y);
          routeGrad.addColorStop(0, 'rgba(56, 189, 248, 0.9)');
          routeGrad.addColorStop(0.5, 'rgba(129, 140, 248, 0.85)');
          routeGrad.addColorStop(1, 'rgba(236, 72, 153, 0.9)');
          ctx.strokeStyle = routeGrad;
          ctx.lineWidth = 2.2;
          ctx.stroke();

          // Animated airplane / signal pulse along the curve
          const progress = ((Date.now() / 1500) + (idx * 0.15)) % 1;
          const pLat = bom.lat + (h.lat - bom.lat) * progress;
          const pLon = bom.lon + (h.lon - bom.lon) * progress;
          const ptProg = projectPoint(pLat, pLon, rot);
          if (ptProg.visible) {
            const alt = Math.sin(progress * Math.PI) * 18;
            const dirX = (ptProg.x - cx) / r;
            const dirY = (ptProg.y - cy) / r;
            const beaconX = ptProg.x + dirX * alt;
            const beaconY = ptProg.y + dirY * alt;

            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.arc(beaconX, beaconY, 3, 0, Math.PI * 2);
            ctx.shadowColor = '#38bdf8';
            ctx.shadowBlur = 10;
            ctx.fill();
            ctx.shadowBlur = 0;
          }
        });
      }

      // Draw Airport Hub Beacons & Tags
      projectedHubs.forEach(h => {
        if (!h.visible) return;
        const isSelected = h.code === this.activeGlobeHub;

        // Hub Beacon Point
        ctx.beginPath();
        ctx.arc(h.x, h.y, isSelected ? 6.5 : 4.5, 0, Math.PI * 2);
        ctx.fillStyle = isSelected ? '#38bdf8' : (h.country === 'India' ? '#34d399' : '#c084fc');
        ctx.shadowColor = isSelected ? '#38bdf8' : '#818cf8';
        ctx.shadowBlur = isSelected ? 16 : 8;
        ctx.fill();
        ctx.shadowBlur = 0;

        // Outer beacon ring
        ctx.beginPath();
        ctx.arc(h.x, h.y, isSelected ? 11 : 7.5, 0, Math.PI * 2);
        ctx.strokeStyle = isSelected ? 'rgba(56, 189, 248, 0.9)' : 'rgba(255, 255, 255, 0.5)';
        ctx.lineWidth = 1.2;
        ctx.stroke();

        // Hub Code Label with background pill
        const text = h.code;
        ctx.font = isSelected ? 'bold 11px Inter, sans-serif' : '10px Inter, sans-serif';
        const metrics = ctx.measureText(text);
        const tagX = h.x + 8;
        const tagY = h.y - 6;

        ctx.fillStyle = 'rgba(15, 23, 42, 0.75)';
        ctx.beginPath();
        ctx.roundRect ? ctx.roundRect(tagX - 3, tagY - 9, metrics.width + 6, 14, 4) : ctx.rect(tagX - 3, tagY - 9, metrics.width + 6, 14);
        ctx.fill();

        ctx.fillStyle = isSelected ? '#38bdf8' : '#f8fafc';
        ctx.fillText(text, tagX, tagY + 2);
      });

      ctx.restore(); // Restore clipping

      if (this.globeAutoSpin) {
        rot = (rot + 0.3) % 360;
      }
      this.globeAngle = rot;
      this.globeAnimFrame = requestAnimationFrame(draw);
    };

    if (this.globeAnimFrame) cancelAnimationFrame(this.globeAnimFrame);
    this.globeAnimFrame = requestAnimationFrame(draw);

    canvas.onclick = (e) => {
      const rect = canvas.getBoundingClientRect();
      const clickX = (e.clientX - rect.left) * (canvas.width / rect.width);
      const clickY = (e.clientY - rect.top) * (canvas.height / rect.height);
      const cx = canvas.width / 2;
      const cy = canvas.height / 2;
      const r = (sphereSize / 2) - 6;

      HUBS.forEach(h => {
        const radLon = (h.lon + this.globeAngle) * Math.PI / 180;
        const radLat = h.lat * Math.PI / 180;
        const x = cx + r * Math.cos(radLat) * Math.sin(radLon);
        const y = cy - r * Math.sin(radLat);
        const z = Math.cos(radLon) * Math.cos(radLat);
        if (z > 0) {
          const dist = Math.hypot(clickX - x, clickY - y);
          if (dist < 22) {
            this.selectGlobeHub(h);
          }
        }
      });
    };
  }

  rotateGlobe(deg) {
    this.globeAngle = (this.globeAngle + deg) % 360;
  }

  toggleGlobeAutoSpin() {
    this.globeAutoSpin = !this.globeAutoSpin;
    const btn = document.getElementById('globe-spin-btn');
    if (btn) {
      btn.innerHTML = this.globeAutoSpin ? '<i class="fa-solid fa-pause"></i>' : '<i class="fa-solid fa-play"></i>';
    }
  }

  resetGlobeView() {
    this.globeAngle = 0;
    this.selectGlobeHub({ code: 'BOM', city: 'Mumbai', country: 'India', fare: 2800, season: 'Oct – Mar' });
  }

  selectGlobeHub(hub) {
    this.activeGlobeHub = hub.code;
    const countryCrumb = document.getElementById('globe-country-crumb');
    const hubCrumb = document.getElementById('globe-hub-crumb');
    const drawerCode = document.getElementById('drawer-hub-code');
    const drawerCity = document.getElementById('drawer-hub-city');
    const drawerPrice = document.getElementById('drawer-hub-price');
    const drawerSeason = document.getElementById('drawer-hub-season');

    if (countryCrumb) countryCrumb.innerText = `${hub.country}`;
    if (hubCrumb) hubCrumb.innerText = `${hub.city} (${hub.code})`;
    if (drawerCode) drawerCode.innerText = hub.code;
    if (drawerCity) drawerCity.innerText = `${hub.city}, ${hub.country}`;
    if (drawerPrice) drawerPrice.innerText = `₹${hub.fare.toLocaleString()}`;
    if (drawerSeason) drawerSeason.innerText = hub.season;
  }

  bookFromGlobeHub() {
    window.location.href = `/?origin=BOM&dest=${this.activeGlobeHub}&autosearch=1`;
  }

  /* ---- 5. DIGITAL BOARDING PASS MODAL ---- */
  openBoardingPassModal(pnr = null) {
    const targetPnr = pnr || this._lastBooking?.pnr;
    const modal = document.getElementById('boarding-pass-modal');
    const content = document.getElementById('boarding-pass-modal-content');
    if (!modal || !content) return;

    modal.classList.add('is-open');
    modal.classList.remove('hidden');
    content.innerHTML = '<div class="loading-spinner p-4"><i class="fa-solid fa-circle-notch fa-spin text-primary me-2"></i> Generating Boarding Pass...</div>';

    fetch(`/flights/booking/${targetPnr}/`)
      .then(r => r.json())
      .then(data => {
        if (!data.success) {
          content.innerHTML = `<p class="text-danger">${data.error || 'Failed to load boarding pass'}</p>`;
          return;
        }
        const f = data.flight;
        const pax = data.passengers[0] || {};
        const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(`${window.location.origin}/verify/${data.pnr}/`)}`;

        content.innerHTML = `
          <div class="boarding-pass-ticket glass-inner p-4 rounded-xl">
            <div class="flex justify-between align-center border-bottom border-secondary pb-3 mb-3">
              <div class="flex align-center gap-2">
                <i class="fa-solid fa-plane-up text-primary font-large"></i>
                <h3 class="m-0 font-display text-white">FlyEase Priority Pass</h3>
              </div>
              <span class="badge badge-success font-mono"><i class="fa-solid fa-circle-check me-1"></i> VERIFIED CONFIRMED</span>
            </div>

            <div class="grid grid-2 gap-4 align-center mb-3">
              <div>
                <div class="muted tiny">PASSENGER NAME</div>
                <h4 class="text-white m-0">${(pax.first_name || 'TRAVELER').toUpperCase()} ${(pax.last_name || '').toUpperCase()}</h4>
                <div class="small muted mt-1">PNR: <b class="font-mono text-cyan">${data.pnr}</b> · Ticket: <span class="font-mono">${data.ticket_number || 'FE-TKT'}</span></div>
              </div>
              <div class="text-right">
                <div class="muted tiny">CABIN CLASS</div>
                <h4 class="text-gradient m-0">${pax.seat_class || 'ECONOMY'}</h4>
                <div class="small muted mt-1">Flight: <b class="font-mono text-white">${f.airline.code}-${f.flight_number}</b></div>
              </div>
            </div>

            <!-- Route Banner -->
            <div class="pass-route-row p-3 rounded glass my-3 flex justify-between align-center text-center">
              <div class="text-left">
                <div class="h2 text-cyan font-display m-0">${f.origin.code}</div>
                <div class="small muted">${f.origin.city}</div>
                <div class="font-mono text-white font-weight-bold mt-1">${new Date(f.departure_time).toLocaleTimeString([], { hour:'2-digit', minute:'2-digit' })}</div>
              </div>
              <div class="flex-1 mx-3 position-relative">
                <div class="small text-muted font-mono mb-1">${f.duration_min} mins · Non-stop</div>
                <div class="pass-plane-track"></div>
                <i class="fa-solid fa-plane text-primary"></i>
              </div>
              <div class="text-right">
                <div class="h2 text-cyan font-display m-0">${f.destination.code}</div>
                <div class="small muted">${f.destination.city}</div>
                <div class="font-mono text-white font-weight-bold mt-1">${new Date(f.arrival_time).toLocaleTimeString([], { hour:'2-digit', minute:'2-digit' })}</div>
              </div>
            </div>

            <!-- Gate, Seat, Terminal & QR Code -->
            <div class="grid grid-4 gap-2 text-center p-3 glass-inner rounded mb-3">
              <div>
                <div class="muted tiny">GATE</div>
                <div class="h3 text-warning font-mono m-0">${data.gate || 'B24'}</div>
              </div>
              <div>
                <div class="muted tiny">SEAT</div>
                <div class="h3 text-cyan font-mono m-0">${pax.seat || '12A'}</div>
              </div>
              <div>
                <div class="muted tiny">TERMINAL</div>
                <div class="h3 text-white font-mono m-0">${data.terminal || 'T2'}</div>
              </div>
              <div>
                <div class="muted tiny">BOARDING</div>
                <div class="h3 text-success font-mono m-0">${new Date(new Date(f.departure_time).getTime() - 40*60000).toLocaleTimeString([], { hour:'2-digit', minute:'2-digit' })}</div>
              </div>
            </div>

            <div class="flex justify-between align-center p-3 border-top border-secondary flex-wrap gap-2">
              <div>
                <div class="small text-muted font-mono"><i class="fa-solid fa-shield-halved text-success me-1"></i> Security Cleared · Priority Boarding Zone 1</div>
                <div class="tiny text-muted mt-1">Baggage: 15kg Check-in + 7kg Cabin allowed</div>
              </div>
              <div class="pass-qr-box">
                <img src="${qrUrl}" alt="Boarding QR" width="65" height="65" class="rounded">
              </div>
            </div>
          </div>
        `;

        const pdfBtn = document.getElementById('modal-pass-download-pdf');
        if (pdfBtn) {
          pdfBtn.onclick = () => window.open(`/flights/booking/${data.pnr}/eticket/`, '_blank');
        }
      });
  }

  closeBoardingPassModal() {
    const modal = document.getElementById('boarding-pass-modal');
    if (modal) {
      modal.classList.remove('is-open');
      modal.classList.add('hidden');
    }
  }

  /* ---- 6 & 7. LIVE FLIGHT STATUS TIMELINE & AIRPORT MODE ---- */
  openAirportMode(pnr) {
    const modal = document.getElementById('airport-mode-modal');
    const content = document.getElementById('airport-mode-content');
    if (!modal || !content) return;

    modal.classList.add('is-open');
    modal.classList.remove('hidden');
    content.innerHTML = '<div class="loading-spinner p-4"><i class="fa-solid fa-circle-notch fa-spin text-primary me-2"></i> Connecting to Airport Terminal HUD...</div>';

    fetch(`/flights/booking/${pnr}/`)
      .then(r => r.json())
      .then(data => {
        if (!data.success) {
          content.innerHTML = `<p class="text-danger">${data.error || 'Failed to load airport mode'}</p>`;
          return;
        }
        const f = data.flight;
        const dep = new Date(f.departure_time);
        const boardingStart = new Date(dep.getTime() - 40 * 60000);

        content.innerHTML = `
          <div class="airport-mode-hud p-4 glass-inner rounded-xl">
            <!-- Terminal Header -->
            <div class="flex justify-between align-center mb-3">
              <div>
                <span class="badge badge-warning font-mono mb-1"><i class="fa-solid fa-plane-departure me-1"></i> AIRPORT MODE ACTIVE</span>
                <h2 class="text-white m-0 font-display">${f.origin.city} · ${data.terminal || 'TERMINAL 2'}</h2>
              </div>
              <div class="text-right font-mono">
                <div class="text-cyan font-large font-weight-bold">${dep.toLocaleTimeString([], { hour:'2-digit', minute:'2-digit' })} DEPARTURE</div>
                <div class="small text-muted">Flight ${f.airline.code}-${f.flight_number}</div>
              </div>
            </div>

            <!-- Terminal Navigation Cards -->
            <div class="grid grid-3 gap-3 my-4">
              <div class="glass p-3 rounded text-center border border-primary">
                <div class="muted tiny mb-1">DEPARTURE GATE</div>
                <div class="h2 text-warning font-display m-0">${data.gate || 'B24'}</div>
                <div class="tiny text-success mt-1"><i class="fa-solid fa-person-walking me-1"></i> 8 min walk</div>
              </div>
              <div class="glass p-3 rounded text-center">
                <div class="muted tiny mb-1">BOARDING STARTS</div>
                <div class="h3 text-success font-mono m-0">${boardingStart.toLocaleTimeString([], { hour:'2-digit', minute:'2-digit' })}</div>
                <div class="tiny text-cyan mt-1">Zone 1 Priority</div>
              </div>
              <div class="glass p-3 rounded text-center">
                <div class="muted tiny mb-1">ESTIMATED SECURITY</div>
                <div class="h3 text-white font-mono m-0">12 – 15 min</div>
                <div class="tiny text-success mt-1"><i class="fa-solid fa-check me-1"></i> Fast Track Open</div>
              </div>
            </div>

            <!-- Split-flap Airport Departure Board View -->
            <div class="trans-departure-board w-100 my-3">
              <div class="departure-board-header">
                <span>TERMINAL GATEWAY</span>
                <span><i class="fa-regular fa-clock me-1"></i> LIVE RADAR</span>
              </div>
              <div class="departure-board-row highlight">
                <span class="board-flip-text">${f.origin.code} → ${f.destination.code}</span>
                <span class="font-mono">${f.airline.code} ${f.flight_number}</span>
                <span class="text-success font-weight-bold">${data.live_flight_status || 'BOARDING'}</span>
                <span class="text-right text-warning font-weight-bold">${data.gate || 'GATE B24'}</span>
              </div>
            </div>

            <div class="flex justify-between align-center mt-3 pt-3 border-top border-secondary">
              <span class="small text-muted font-mono"><i class="fa-solid fa-location-dot text-primary me-1"></i> Turn right past Duty-Free toward Gates B20–B32</span>
              <button type="button" class="btn btn-primary btn-sm" onclick="app.openBoardingPassModal('${data.pnr}')"><i class="fa-solid fa-qrcode me-1"></i> Show Gate Pass</button>
            </div>
          </div>
        `;
      });
  }

  closeAirportMode() {
    const modal = document.getElementById('airport-mode-modal');
    if (modal) {
      modal.classList.remove('is-open');
      modal.classList.add('hidden');
    }
  }

  /* ---- 8. CANCELLATION & REFUND FLOW ---- */
  openCancelModal(pnr, pricePaid) {
    const modal = document.getElementById('cancellation-modal');
    const content = document.getElementById('cancellation-modal-content');
    if (!modal || !content) return;

    modal.classList.add('is-open');
    modal.classList.remove('hidden');

    const fee = Math.min(pricePaid, 500);
    const refund = Math.max(0, pricePaid - fee);

    content.innerHTML = `
      <div class="cancellation-policy-card p-3 glass-inner rounded mb-3">
        <h4 class="text-white mb-2">Cancellation & Refund Breakdown</h4>
        <p class="muted small">According to FlyEase Fare Rules, you are eligible for an instant automated refund.</p>
        
        <div class="fare-list my-3">
          <div class="fare-row"><span class="fare-label">Ticket Total Paid:</span><span class="fare-val font-mono">₹${pricePaid.toFixed(2)}</span></div>
          <div class="fare-row"><span class="fare-label">Cancellation Fee:</span><span class="fare-val text-warning font-mono">-₹${fee.toFixed(2)}</span></div>
          <hr class="glass-divider my-2">
          <div class="fare-row total"><span class="fare-label text-success">Total Refund Amount:</span><span class="fare-val text-success font-mono font-large">₹${refund.toFixed(2)}</span></div>
        </div>

        <div class="small text-muted p-2 rounded glass font-mono">
          <i class="fa-solid fa-clock-rotate-left text-cyan me-1"></i> Refund will be credited back to your original payment method.
        </div>
      </div>

      <div class="flex justify-between align-center mt-4">
        <button type="button" class="btn btn-outline btn-sm" onclick="app.closeCancelModal()">Keep My Booking</button>
        <button type="button" class="btn btn-primary btn-sm bg-danger" onclick="app.confirmCancellation('${pnr}')">
          <i class="fa-solid fa-ban me-1"></i> Confirm Cancellation
        </button>
      </div>
    `;
  }

  closeCancelModal() {
    const modal = document.getElementById('cancellation-modal');
    if (modal) {
      modal.classList.remove('is-open');
      modal.classList.add('hidden');
    }
  }

  async confirmCancellation(pnr) {
    const content = document.getElementById('cancellation-modal-content');
    if (content) content.innerHTML = '<div class="loading-spinner p-4"><i class="fa-solid fa-circle-notch fa-spin text-danger me-2"></i> Processing cancellation & refund...</div>';

    try {
      const res = await fetch(`/flights/booking/${pnr}/cancel/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': this.getCsrfToken() }
      });
      const data = await res.json();
      if (!data.success) {
        if (content) content.innerHTML = `<p class="text-danger p-3">${data.error || 'Failed to cancel booking'}</p>`;
        return;
      }

      this.addNotification('Booking Cancelled', `Refund of ₹${data.refund_amount.toFixed(2)} processed for PNR ${pnr}.`, 'refund', 'fa-rotate-left');
      NotificationService.show(data.message, 'success');
      this.closeCancelModal();
      this.loadDashboard();
    } catch(e) {
      if (content) content.innerHTML = '<p class="text-danger p-3">Server error during cancellation. Please try again.</p>';
    }
  }

  /* ---- 10. FLYEASE PASSPORT & GAMIFICATION ---- */
  switchDashTab(tab) {
    const tripsPane = document.getElementById('dash-tab-trips');
    const passPane = document.getElementById('dash-tab-passport');
    document.querySelectorAll('.dashboard-nav li').forEach(li => li.classList.remove('active'));

    if (tab === 'passport') {
      if (tripsPane) tripsPane.classList.add('hidden');
      if (passPane) passPane.classList.remove('hidden');
      const activeLink = document.querySelector('a[href="#passport"]')?.parentNode;
      if (activeLink) activeLink.classList.add('active');
      this.renderPassportGamification();
    } else {
      if (passPane) passPane.classList.add('hidden');
      if (tripsPane) tripsPane.classList.remove('hidden');
      const activeLink = document.querySelector('a[href="#my-trips"]')?.parentNode;
      if (activeLink) activeLink.classList.add('active');
    }
  }

  renderPassportGamification() {
    const countriesEl = document.getElementById('passport-country-count');
    const flightsEl = document.getElementById('passport-flight-count');
    const distEl = document.getElementById('passport-distance-km');
    const stampsContainer = document.getElementById('passport-stamps-container');
    const achContainer = document.getElementById('passport-achievements-list');

    fetch('/flights/bookings/')
      .then(r => r.json())
      .then(data => {
        const validBookings = (data.bookings || []).filter(b => b.status === 'CONFIRMED' || b.status === 'COMPLETED');
        const count = validBookings.length;
        const totalDist = count * 1450;

        const visitedCodes = new Set();
        validBookings.forEach(b => {
          if (b.origin_code) visitedCodes.add(b.origin_code);
          if (b.dest_code) visitedCodes.add(b.dest_code);
        });

        if (countriesEl) countriesEl.innerText = visitedCodes.size > 2 ? '2+' : (visitedCodes.size ? '1' : '0');
        if (flightsEl) flightsEl.innerText = count;
        if (distEl) distEl.innerText = `${totalDist.toLocaleString()} km`;

        const statStamps = document.getElementById('stat-passport-stamps');
        if (statStamps) statStamps.innerText = visitedCodes.size;
        const statTrips = document.getElementById('stat-active-trips');
        if (statTrips) statTrips.innerText = validBookings.length;

        // Achievements
        const achievements = [
          { id: 'first_flight', title: 'First Flight', desc: 'Completed your first booking', unlocked: count >= 1, icon: 'fa-plane-departure' },
          { id: 'frequent_flyer', title: 'Frequent Flyer', desc: 'Booked 3 or more flights', unlocked: count >= 3, icon: 'fa-award' },
          { id: 'globe_explorer', title: 'World Explorer', desc: 'Visited multiple destinations', unlocked: visitedCodes.size >= 2, icon: 'fa-earth-americas' },
          { id: 'international', title: 'International Traveler', desc: 'Booked global routes', unlocked: count >= 2, icon: 'fa-passport' },
          { id: 'master_voyager', title: 'Master Voyager', desc: 'Accumulated over 5,000 km', unlocked: totalDist >= 5000, icon: 'fa-crown' },
        ];

        if (achContainer) {
          achContainer.innerHTML = achievements.map(a => `
            <div class="achievement-badge-card glass-inner p-3 rounded text-center ${a.unlocked ? 'unlocked' : 'locked'}">
              <div class="ach-icon-circle flex align-center justify-center mx-auto mb-2 text-warning">
                <i class="fa-solid ${a.icon} font-large"></i>
              </div>
              <h5 class="text-white m-0">${a.title}</h5>
              <p class="muted tiny m-0 mt-1">${a.desc}</p>
              <span class="badge ${a.unlocked ? 'badge-success' : 'badge-outline'} mt-2 tiny">
                ${a.unlocked ? '✓ UNLOCKED' : 'LOCKED'}
              </span>
            </div>
          `).join('');
        }

        // Stamps
        const STAMP_DATA = [
          { code: 'BOM', city: 'Mumbai', country: '🇮🇳 India' },
          { code: 'DEL', city: 'Delhi', country: '🇮🇳 India' },
          { code: 'DXB', city: 'Dubai', country: '🇦🇪 UAE' },
          { code: 'LHR', city: 'London', country: '🇬🇧 UK' },
          { code: 'SIN', city: 'Singapore', country: '🇸🇬 Singapore' },
          { code: 'HND', city: 'Tokyo', country: '🇯🇵 Japan' },
          { code: 'JFK', city: 'New York', country: '🇺🇸 USA' },
        ];

        if (stampsContainer) {
          stampsContainer.innerHTML = STAMP_DATA.map(st => {
            const hasStamp = visitedCodes.has(st.code);
            return `
              <div class="passport-stamp-chip glass p-3 rounded text-center ${hasStamp ? 'stamp-active' : 'stamp-faded'}" style="width:140px;">
                <div class="stamp-circle-border p-2">
                  <div class="font-display font-weight-bold text-cyan" style="font-size:1.4rem;">${st.code}</div>
                  <div class="small text-white font-weight-bold mt-1">${st.city}</div>
                  <div class="tiny text-muted">${st.country}</div>
                  <span class="badge ${hasStamp ? 'badge-success' : 'badge-outline'} mt-2 tiny">
                    ${hasStamp ? '✓ STAMPED' : 'UNVISITED'}
                  </span>
                </div>
              </div>
            `;
          }).join('');
        }
      });
  }

  /* ---- Dashboard Bookings List with Live Flight Status & Cancellation ---- */
  async loadDashboard() {
    this.loadDashboardBookings();
    this.renderPassportGamification();
  }

  async loadDashboardBookings() {
    const dbList = document.getElementById('dashboard-bookings-list');
    if (!dbList) return;

    try {
      const res = await fetch('/flights/bookings/');
      const data = await res.json();
      if (data.bookings && data.bookings.length > 0) {
        dbList.innerHTML = data.bookings.map(b => {
          const parts = (b.flight || '').split(' to ');
          const orig = b.origin_code || parts[0] || 'DEP';
          const dest = b.dest_code || parts[1] || 'ARR';
          const isCancelled = b.status === 'CANCELLED';

          // Timeline active steps (1..5)
          const step = b.timeline_step || 1;
          const statusLabels = ['Scheduled', 'Check-in Open', 'Boarding', 'In Flight', 'Arrived'];

          return `
          <div class="glass p-4 mb-4 rounded-xl dashboard-trip-card ${isCancelled ? 'trip-cancelled' : ''}">
            <div class="flex justify-between align-center flex-wrap gap-3 mb-3">
              <div class="flex align-center gap-2">
                <h3 class="m-0 text-gradient font-mono">${b.pnr}</h3>
                <span class="badge ${isCancelled ? 'badge-danger' : 'badge-success'}">${b.status}</span>
                ${b.deal_applied ? `<span class="badge badge-warning"><i class="fa-solid fa-tag me-1"></i>${b.deal_applied}</span>` : ''}
              </div>
              <div class="text-right">
                ${b.discount_amount > 0 ? `<div class="tiny muted" style="text-decoration:line-through;">₹${(b.original_fare || (b.price_paid + b.discount_amount)).toFixed(2)}</div>` : ''}
                <div class="font-large font-weight-bold text-gradient">₹${b.price_paid.toFixed(2)}</div>
                ${isCancelled && b.refund_amount > 0 ? `<div class="tiny text-success font-mono">Refund: ₹${b.refund_amount.toFixed(2)} (${b.refund_status})</div>` : ''}
              </div>
            </div>

            <!-- Animated Flight Route Path -->
            <div class="trip-route-display glass-inner p-3 my-3 flex justify-between align-center">
              <div class="trip-airport text-left">
                <span class="trip-iata font-display">${orig}</span>
                <span class="small muted d-block">${b.origin_city || 'Origin'}</span>
              </div>
              <div class="trip-path-line flex-1 mx-3 text-center position-relative">
                <div class="trip-progress-glow"></div>
                <i class="fa-solid fa-plane text-primary trip-plane-icon"></i>
              </div>
              <div class="trip-airport text-right">
                <span class="trip-iata font-display">${dest}</span>
                <span class="small muted d-block">${b.dest_city || 'Destination'}</span>
              </div>
            </div>

            <!-- Live Flight Status Timeline (simulator engine) -->
            ${!isCancelled ? `
            <div class="flight-timeline-card glass-inner p-3 my-3 rounded">
              <div class="flex justify-between align-center mb-2">
                <span class="small text-cyan font-mono font-weight-bold"><i class="fa-solid fa-satellite me-1"></i> LIVE RADAR TIMELINE</span>
                <span class="badge badge-outline tiny">${b.live_flight_status || 'SCHEDULED'}</span>
              </div>
              <div class="timeline-nodes-bar flex justify-between align-center position-relative">
                ${statusLabels.map((lbl, idx) => `
                  <div class="timeline-node text-center ${step >= idx + 1 ? 'active' : ''}">
                    <div class="node-bullet flex align-center justify-center mx-auto">${step >= idx + 1 ? '✓' : idx + 1}</div>
                    <span class="tiny muted mt-1 d-block">${lbl}</span>
                  </div>
                `).join('')}
              </div>
            </div>
            ` : `
            <div class="cancelled-notice-card p-2 rounded glass-inner text-center text-danger small font-mono my-2">
              <i class="fa-solid fa-ban me-1"></i> Booking Cancelled on ${b.cancelled_at ? new Date(b.cancelled_at).toLocaleDateString() : 'N/A'}. Refund processed.
            </div>
            `}

            <!-- Trip Meta & Action Bar -->
            <div class="flex justify-between align-center flex-wrap gap-3 mt-3">
              <div class="small muted">
                <i class="fa-solid fa-calendar-days me-1 text-primary"></i> ${new Date(b.date).toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' })} • <i class="fa-solid fa-user me-1 text-secondary"></i> ${b.seats} Seat(s) (${b.seats_list?.join(', ') || 'Assigned'})
              </div>
              <div class="flex gap-2 flex-wrap">
                <button type="button" class="btn btn-outline btn-sm" onclick="app.openLiveFlightTracker('${b.flight_number || b.pnr}')" title="Track live aircraft radar and telemetry">
                  <i class="fa-solid fa-satellite-dish text-cyan me-1"></i> Live Radar
                </button>
                <button type="button" class="btn btn-outline btn-sm" onclick="app.openBoardingPassModal('${b.pnr}')">
                  <i class="fa-solid fa-ticket me-1"></i> Boarding Pass
                </button>
                ${!isCancelled ? `
                <button type="button" class="btn btn-outline btn-sm" onclick="app.openAirportMode('${b.pnr}')">
                  <i class="fa-solid fa-plane-departure text-warning me-1"></i> Airport Mode
                </button>
                <button type="button" class="btn btn-outline btn-sm text-danger" onclick="app.openCancelModal('${b.pnr}', ${b.price_paid})">
                  <i class="fa-solid fa-ban me-1"></i> Cancel
                </button>
                ` : ''}
                <a href="/flights/booking/${b.pnr}/eticket/" class="btn btn-primary btn-sm">
                  <i class="fa-solid fa-file-pdf me-1"></i> PDF
                </a>
              </div>
            </div>
          </div>`;
        }).join('');
      } else {
        dbList.innerHTML = '<div class="glass p-4 text-center muted"><i class="fa-solid fa-ticket-simple fa-2x mb-2" style="display:block;"></i>No flight bookings found yet. Explore flights to earn your first Passport stamp!</div>';
      }
    } catch(e) {
      dbList.innerHTML = '<p class="text-danger">Failed to load bookings.</p>';
    }
  }

  /* ---- URL Query Parameter Handler (Landing page pre-fill & booking) ---- */
  handleUrlParams() {
    const params = new URLSearchParams(window.location.search);
    const origin = params.get('origin');
    const dest = params.get('dest') || params.get('destination');
    const deal = params.get('deal') || params.get('deal_code');
    const pax = params.get('passengers') || params.get('pax');
    const cls = params.get('class');
    const dateParam = params.get('date');
    const autoSearch = params.get('autosearch');

    if (origin) {
      const origInput = document.getElementById('origin');
      if (origInput) origInput.value = origin.toUpperCase();
      this.state.origin = origin.toUpperCase();
    }
    if (dest) {
      const destInput = document.getElementById('destination');
      if (destInput) destInput.value = dest.toUpperCase();
      this.state.dest = dest.toUpperCase();
    }
    if (dateParam) {
      const dateInput = document.getElementById('depart-date') || document.getElementById('dep-date');
      if (dateInput) dateInput.value = dateParam;
      this.state.date = dateParam;
    } else {
      const dateInput = document.getElementById('depart-date') || document.getElementById('dep-date');
      if (dateInput && !dateInput.value) {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 2);
        dateInput.value = tomorrow.toISOString().split('T')[0];
        this.state.date = dateInput.value;
      }
    }
    if (pax) {
      const paxSelect = document.getElementById('passengers') || document.getElementById('passengers-count');
      if (paxSelect) paxSelect.value = pax;
      this.state.passengersCount = parseInt(pax) || 1;
    }
    if (cls) {
      const clsSelect = document.getElementById('cabin-class');
      if (clsSelect) clsSelect.value = cls.toUpperCase();
      this.state.cabinClass = cls.toUpperCase();
    }
    if (deal) {
      this.state.dealCode = deal.toUpperCase();
      const couponInput = document.getElementById('coupon-code');
      if (couponInput) couponInput.value = deal.toUpperCase();
    }

    // If auto search triggered from Destination / Deals page
    if (autoSearch === '1' && origin && dest) {
      setTimeout(() => {
        const searchBtn = document.getElementById('search-btn') || document.getElementById('search-flights-btn');
        if (searchBtn) searchBtn.click();
      }, 300);
    }
  }

  /* ---- Direct booking trigger from Deals page ---- */
  async bookDealFromPage(dealCode, originCode, destCode, minPax, reqClass, discountPercent, dealTitle) {
    const today = new Date();
    today.setDate(today.getDate() + 3);
    const depDate = today.toISOString().split('T')[0];
    const orig = originCode || 'BOM';
    const dest = destCode || 'DEL';
    const pax = minPax || '1';
    const cls = reqClass || 'ECONOMY';

    const targetUrl = `/?origin=${encodeURIComponent(orig)}&dest=${encodeURIComponent(dest)}&deal=${encodeURIComponent(dealCode || '')}&passengers=${pax}&class=${cls}&date=${depDate}&autosearch=1`;
    window.location.href = targetUrl;
  }

  /* ---- Direct booking trigger from Destinations page ---- */
  async bookDestinationFromPage(destCode) {
    const orig = destCode.toUpperCase() === 'BOM' ? 'DEL' : 'BOM';
    const today = new Date();
    today.setDate(today.getDate() + 3);
    const depDate = today.toISOString().split('T')[0];

    const targetUrl = `/?origin=${encodeURIComponent(orig)}&dest=${encodeURIComponent(destCode)}&date=${depDate}&autosearch=1`;
    window.location.href = targetUrl;
  }

  /* ---- Initialize Destinations Page Cards & Filters ---- */
  initDestinationsPage() {
    const grid = document.getElementById('destinations-grid');
    if (!grid) return;

    const destinationsData = (window.GLOBAL_DESTINATIONS_DATA && window.GLOBAL_DESTINATIONS_DATA.length) 
      ? window.GLOBAL_DESTINATIONS_DATA 
      : [
          {
            city: 'Mumbai', code: 'BOM', country: 'India', type: 'domestic',
            price: 3499, popularity: 99,
            image: 'https://images.unsplash.com/photo-1570168007204-dfb528c6958f?w=800&auto=format&fit=crop&q=80',
            attractions: ['Gateway of India', 'Marine Drive', 'Bandra-Worli Sea Link'],
            bestTime: 'Oct - Mar'
          },
          {
            city: 'Delhi', code: 'DEL', country: 'India', type: 'domestic',
            price: 3299, popularity: 98,
            image: 'https://images.unsplash.com/photo-1587474260584-136574528ed5?w=800&auto=format&fit=crop&q=80',
            attractions: ['India Gate', 'Red Fort', 'Qutub Minar'],
            bestTime: 'Oct - Mar'
          }
        ];

    const renderDestinations = (items) => {
      grid.innerHTML = items.map(d => `
        <div class="destination-card-premium glass reveal">
          <div class="dest-card-img-wrap">
            <img src="${d.image}" alt="${d.city}" loading="lazy">
            <span class="dest-img-badge ${d.type === 'domestic' ? 'dest-badge-dom' : 'dest-badge-intl'}">
              ${d.type === 'domestic' ? '🇮🇳 Domestic' : '🌎 International'}
            </span>
          </div>
          <div class="dest-card-content">
            <div class="dest-card-header flex justify-between align-center">
              <div>
                <h3 class="m-0">${d.city}</h3>
                <span class="small muted">${d.country}</span>
              </div>
              <span class="dest-airport-tag">${d.code}</span>
            </div>

            <div class="dest-features-box p-3 my-3">
              <div class="tiny muted mb-1"><i class="fa-solid fa-sun text-warning me-1"></i> Best time: <b>${d.bestTime}</b></div>
              <div class="dest-attractions-list">
                ${d.attractions.map(a => `<span class="attraction-tag"><i class="fa-solid fa-location-dot me-1"></i>${a}</span>`).join('')}
              </div>
            </div>

            <div class="dest-card-footer mt-auto flex justify-between align-center">
              <div>
                <div class="tiny muted">STARTING FARE</div>
                <div class="dest-price-val text-gradient">₹${d.price.toLocaleString()}</div>
              </div>
              <button type="button" class="btn btn-primary btn-book-dest" onclick="app.bookDestinationFromPage('${d.code}')">
                <i class="fa-solid fa-plane-departure me-1"></i> Book Flight
              </button>
            </div>
          </div>
        </div>
      `).join('');
    };

    renderDestinations(destinationsData);

    // Filters and search logic
    const searchInput = document.getElementById('dest-search-input');
    const filterBtns = document.querySelectorAll('.dest-tab-btn');
    const sortSelect = document.getElementById('dest-sort-select');

    let currentFilter = 'all';
    let currentSearch = '';

    const filterAndSort = () => {
      let result = destinationsData.filter(d => {
        const matchesFilter = currentFilter === 'all' || d.type === currentFilter;
        const q = currentSearch.toLowerCase();
        const matchesSearch = !q || d.city.toLowerCase().includes(q) || d.code.toLowerCase().includes(q) || d.country.toLowerCase().includes(q);
        return matchesFilter && matchesSearch;
      });

      const sortVal = sortSelect ? sortSelect.value : 'popular';
      if (sortVal === 'price-low') result.sort((a,b) => a.price - b.price);
      else if (sortVal === 'price-high') result.sort((a,b) => b.price - a.price);
      else if (sortVal === 'name') result.sort((a,b) => a.city.localeCompare(b.city));
      else result.sort((a,b) => b.popularity - a.popularity);

      renderDestinations(result);
    };

    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        currentSearch = e.target.value.trim();
        filterAndSort();
      });
    }

    filterBtns.forEach(b => {
      b.addEventListener('click', () => {
        filterBtns.forEach(x => x.classList.remove('active'));
        b.classList.add('active');
        currentFilter = b.getAttribute('data-filter');
        filterAndSort();
      });
    });

    if (sortSelect) {
      sortSelect.addEventListener('change', filterAndSort);
    }
  }

  /* ---- Initialize Deals Page category tabs & countdowns ---- */
  initDealsPage() {
    const catBtns = document.querySelectorAll('.deal-cat-btn');
    const dealCards = document.querySelectorAll('.deal-card');

    if (!catBtns.length || !dealCards.length) return;

    catBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        catBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const cat = btn.getAttribute('data-category');

        let delayIdx = 0;
        dealCards.forEach(card => {
          const cardCat = card.getAttribute('data-category');
          if (cat === 'ALL' || cardCat === cat) {
            card.style.display = 'flex';
            card.style.opacity = '0';
            card.style.transform = 'translateY(18px) scale(0.96)';
            setTimeout(() => {
              card.style.transition = 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
              card.style.opacity = '1';
              card.style.transform = 'translateY(0) scale(1)';
            }, delayIdx * 45);
            delayIdx++;
          } else {
            card.style.display = 'none';
          }
        });
      });
    });

    // Start live countdown ticking for deals & featured banner
    const countdownElements = document.querySelectorAll('.deal-countdown, .deal-countdown-mini');
    if (countdownElements.length > 0) {
      setInterval(() => {
        countdownElements.forEach(el => {
          const hours = parseInt(el.getAttribute('data-hours')) || 24;
          const timerSpan = el.querySelector('.countdown-timer') || el;
          if (timerSpan) {
            const now = new Date();
            const minutesLeft = 59 - now.getMinutes();
            const secondsLeft = 59 - now.getSeconds();
            
            // Urgency styling if under 8 hours
            if (hours <= 8) {
              el.style.borderColor = 'rgba(239, 68, 68, 0.6)';
              el.style.color = '#fca5a5';
            }
            
            timerSpan.innerHTML = `<i class="fa-regular fa-clock me-1 text-warning"></i> Ends in ${hours}h ${String(minutesLeft).padStart(2,'0')}m ${String(secondsLeft).padStart(2,'0')}s`;
          }
        });
      }, 1000);
    }

    // Auto-cycling 5-Second Hot Deals Spotlight Carousel
    this.initFeaturedDealsCarousel();
  }

  /* ---- Auto-cycling 5-Second Hot Deals Spotlight Carousel ---- */
  initFeaturedDealsCarousel() {
    const slides = document.querySelectorAll('.featured-carousel-slide');
    const dots = document.querySelectorAll('.carousel-dot-btn');
    if (!slides.length) return;

    this._currentFeaturedIndex = 0;
    this._featuredTimer = setInterval(() => {
      this.nextFeaturedSlide();
    }, 5000);
  }

  setFeaturedSlide(index) {
    const slides = document.querySelectorAll('.featured-carousel-slide');
    const dots = document.querySelectorAll('.carousel-dot-btn');
    if (!slides.length || index < 0 || index >= slides.length) return;

    // Reset automatic interval when user clicks a dot
    if (this._featuredTimer) {
      clearInterval(this._featuredTimer);
      this._featuredTimer = setInterval(() => this.nextFeaturedSlide(), 5000);
    }

    slides.forEach((s, idx) => {
      if (idx === index) {
        s.classList.remove('hidden-slide');
        s.classList.add('active-slide');
      } else {
        s.classList.remove('active-slide');
        s.classList.add('hidden-slide');
      }
    });

    dots.forEach((d, idx) => {
      if (idx === index) d.classList.add('active');
      else d.classList.remove('active');
    });

    this._currentFeaturedIndex = index;
  }

  nextFeaturedSlide() {
    const slides = document.querySelectorAll('.featured-carousel-slide');
    if (!slides.length) return;
    const nextIdx = (this._currentFeaturedIndex + 1) % slides.length;
    this.setFeaturedSlide(nextIdx);
  }

  /* ---- 10. Deal Details Modal Interaction ---- */
  openDealModalFromElement(el) {
    const modal = document.getElementById('deal-details-modal');
    if (!modal) return;

    const data = el.dataset;
    const title = data.title || 'Exclusive Flight Deal';
    const orig = data.origin || 'BOM';
    const dest = data.destination || 'DEL';
    const discount = parseFloat(data.discount) || 15;
    const price = parseFloat(data.price) || 2999;
    const origPrice = parseFloat(data.origPrice) || Math.round(price / (1 - (discount / 100)));
    const code = data.dealCode || 'FLYEASE';
    const hours = data.hours || '24';
    const reqClass = data.class || 'ECONOMY';
    const minPax = data.passengers || '1';
    const desc = data.desc || '';
    const terms = data.terms || 'Subject to seat availability and standard airline rules.';
    const img = data.image || '';

    // Populate Modal Elements
    const heroCover = document.getElementById('modal-hero-cover');
    if (heroCover && img) {
      heroCover.style.backgroundImage = `linear-gradient(180deg, rgba(15,23,42,0.3) 0%, rgba(15,23,42,0.95) 100%), url('${img}')`;
    }
    const titleEl = document.getElementById('modal-deal-title');
    if (titleEl) titleEl.innerText = title;

    const routeEl = document.getElementById('modal-deal-route');
    if (routeEl) routeEl.innerText = `${orig} → ${dest}`;

    const descEl = document.getElementById('modal-deal-desc');
    if (descEl) descEl.innerText = desc;

    const cabinEl = document.getElementById('modal-cabin');
    if (cabinEl) cabinEl.innerText = reqClass.charAt(0).toUpperCase() + reqClass.slice(1).toLowerCase();

    const paxEl = document.getElementById('modal-pax');
    if (paxEl) paxEl.innerText = `Min ${minPax} Passenger(s)`;

    const validityEl = document.getElementById('modal-validity');
    if (validityEl) validityEl.innerText = `Ends in ${hours} hours`;

    const promoEl = document.getElementById('modal-promo-code');
    if (promoEl) promoEl.innerText = code;

    const termsEl = document.getElementById('modal-terms-text');
    if (termsEl) termsEl.innerText = terms;

    const origPriceEl = document.getElementById('modal-orig-price');
    if (origPriceEl) origPriceEl.innerText = `₹${origPrice.toLocaleString()}`;

    const discountValEl = document.getElementById('modal-discount-val');
    if (discountValEl) discountValEl.innerText = `-${discount.toFixed(0)}% OFF`;

    // 12. Animated Price Counter
    const finalPriceEl = document.getElementById('modal-final-price');
    if (finalPriceEl) {
      this.animatePriceCounter(finalPriceEl, origPrice, price, 600);
    }

    // Modal CTA Button
    const applyBtn = document.getElementById('modal-apply-btn');
    if (applyBtn) {
      applyBtn.onclick = () => {
        this.closeDealModal();
        this.bookDealFromPage(code, orig, dest, minPax, reqClass, discount, title);
      };
    }

    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
  }

  closeDealModal() {
    const modal = document.getElementById('deal-details-modal');
    if (!modal) return;
    modal.classList.add('hidden');
    document.body.style.overflow = '';
  }

  /* ---- 12. Smooth Price Counter Animation ---- */
  animatePriceCounter(element, start, end, duration = 600) {
    const startTime = performance.now();
    const step = (currentTime) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease out cubic
      const ease = 1 - Math.pow(1 - progress, 3);
      const current = Math.round(start - (start - end) * ease);
      element.innerText = `₹${current.toLocaleString()}`;
      if (progress < 1) {
        requestAnimationFrame(step);
      } else {
        element.innerText = `₹${end.toLocaleString()}`;
      }
    };
    requestAnimationFrame(step);
  }

  /* ---- 19. Micro-interaction: Copy Promo Code with Toast ---- */
  copyPromoCode(el, code) {
    if (!code) return;
    navigator.clipboard.writeText(code).then(() => {
      const origHtml = el.innerHTML;
      el.innerHTML = `<span class="text-success"><i class="fa-solid fa-check me-1"></i> Copied!</span>`;
      NotificationService.show(`Promo code "${code}" copied to clipboard!`, 'success');
      setTimeout(() => {
        el.innerHTML = origHtml;
      }, 2000);
    }).catch(() => {
      NotificationService.show(`Promo code: ${code}`, 'info');
    });
  }

  /* ---- 19. Micro-interaction: Toggle Favorite Deal ---- */
  toggleFavoriteDeal(btn, dealCode) {
    const isFav = btn.classList.toggle('is-favorite');
    const icon = btn.querySelector('i');
    if (icon) {
      icon.className = isFav ? 'fa-solid fa-heart' : 'fa-regular fa-heart';
    }
    NotificationService.show(isFav ? `Deal ${dealCode} added to your favorites! ❤️` : `Removed from favorites`, 'info');
  }

  /* ================================================================
     ✈️ FLYEASE AI CHAT ASSISTANT
     ================================================================ */
  toggleAIChat() {
    const win = document.getElementById('flyease-ai-chat-window');
    if (!win) return;
    win.classList.toggle('hidden');
    if (!win.classList.contains('hidden')) {
      const input = document.getElementById('flyease-ai-input');
      if (input) input.focus();
    }
  }

  clearAIChat() {
    const list = document.getElementById('flyease-ai-messages-list');
    if (list) {
      list.innerHTML = `
        <div class="ai-message-bubble bot-message">
          <div class="bot-msg-content">
            <p class="m-0">Hello! I am <strong>FlyEase AI</strong> ✈️. I can search real-time flight fares, predict price trends, check visa & document requirements, and explain baggage rules. How can I help your journey today?</p>
          </div>
        </div>
      `;
    }
    this.aiHistory = [];
  }

  sendQuickAIPrompt(text) {
    const input = document.getElementById('flyease-ai-input');
    if (input) {
      input.value = text;
      this.handleAISubmit(new Event('submit'));
    }
  }

  async handleAISubmit(e) {
    if (e && e.preventDefault) e.preventDefault();
    const input = document.getElementById('flyease-ai-input');
    const list = document.getElementById('flyease-ai-messages-list');
    if (!input || !list) return;

    const message = input.value.trim();
    if (!message) return;

    // Append User Bubble
    const userBubble = document.createElement('div');
    userBubble.className = 'ai-message-bubble user-message';
    userBubble.innerHTML = `<p class="m-0">${this.escapeHtml(message)}</p>`;
    list.appendChild(userBubble);
    input.value = '';
    list.scrollTop = list.scrollHeight;

    // Append Typing Indicator
    const typingBubble = document.createElement('div');
    typingBubble.className = 'ai-message-bubble bot-message typing-bubble';
    typingBubble.innerHTML = `<span class="muted small"><i class="fa-solid fa-circle-notch fa-spin text-primary me-2"></i> FlyEase AI is analyzing live schedules...</span>`;
    list.appendChild(typingBubble);
    list.scrollTop = list.scrollHeight;

    if (!this.aiHistory) this.aiHistory = [];
    this.aiHistory.push({ role: 'user', content: message });

    try {
      const headers = { 'Content-Type': 'application/json' };
      const csrf = this.getCsrfToken();
      if (csrf) headers['X-CSRFToken'] = csrf;

      const res = await fetch('/flights/ai/chat/', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({ message, history: this.aiHistory })
      });
      const data = await res.json();
      typingBubble.remove();

      const botBubble = document.createElement('div');
      botBubble.className = 'ai-message-bubble bot-message';
      
      let replyHtml = `<div class="bot-msg-content">${this.formatMarkdownText(data.reply || 'Here is what I found.')}</div>`;

      // Render interactive flight cards if returned
      if (data.flights && data.flights.length > 0) {
        replyHtml += `<div class="mt-2 pt-2 border-top border-secondary">`;
        data.flights.slice(0, 3).forEach(f => {
          replyHtml += `
            <div class="ai-card-offer flex justify-between align-center my-1">
              <div>
                <strong>${f.airline_code}-${f.flight_number}</strong> (${f.origin} → ${f.destination})
                <div class="tiny text-muted">${f.baggage}</div>
              </div>
              <div class="text-right">
                <span class="text-primary font-weight-bold">₹${parseFloat(f.price).toLocaleString()}</span>
                <button type="button" class="btn btn-primary btn-xs ms-2" onclick="app.quickBookAIFlight('${f.origin}', '${f.destination}')">Book</button>
              </div>
            </div>
          `;
        });
        replyHtml += `</div>`;
      }

      botBubble.innerHTML = replyHtml;
      list.appendChild(botBubble);
      list.scrollTop = list.scrollHeight;

      if (data.reply) {
        this.aiHistory.push({ role: 'assistant', content: data.reply });
      }
    } catch (err) {
      typingBubble.remove();
      const errBubble = document.createElement('div');
      errBubble.className = 'ai-message-bubble bot-message text-danger';
      errBubble.innerHTML = `<p class="m-0">⚠️ Connection error. Please verify your query or try again.</p>`;
      list.appendChild(errBubble);
      list.scrollTop = list.scrollHeight;
    }
  }

  quickBookAIFlight(origin, destination) {
    this.toggleAIChat();
    const origInput = document.getElementById('origin');
    const destInput = document.getElementById('destination');
    if (origInput) origInput.value = origin;
    if (destInput) destInput.value = destination;
    this.handleSearch();
  }

  escapeHtml(str) {
    const p = document.createElement('p');
    p.textContent = str;
    return p.innerHTML;
  }

  formatMarkdownText(str) {
    if (!str) return '';
    return str
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`([^`]+)`/g, '<code style="background:rgba(255,255,255,0.1);padding:2px 4px;border-radius:4px;color:#38bdf8;">$1</code>')
      .replace(/\n/g, '<br/>');
  }

  /* ================================================================
     🔔 PRICE DROP ALERTS MODAL
     ================================================================ */
  openPriceAlertModal(flightId = null) {
    const modal = document.getElementById('price-alert-modal');
    if (!modal) return;

    const origInput = document.getElementById('origin')?.value.trim().toUpperCase();
    const destInput = document.getElementById('destination')?.value.trim().toUpperCase();
    const dateInput = document.getElementById('depart-date')?.value;

    const orig = this.state.origin || origInput || 'BOM';
    const dest = this.state.dest || destInput || 'DEL';
    const date = this.state.date || dateInput || new Date().toISOString().split('T')[0];
    const flight = this.state.flight || (this.state.depOffers && this.state.depOffers[0]);
    const currentPrice = flight ? flight.pricing.total : 4850;

    const idEl = document.getElementById('alert_flight_id'); if (idEl) idEl.value = flight ? flight.id : '';
    const origEl = document.getElementById('alert_origin'); if (origEl) origEl.value = orig;
    const destEl = document.getElementById('alert_destination'); if (destEl) destEl.value = dest;
    const dateEl = document.getElementById('alert_date'); if (dateEl) dateEl.value = date;
    const classEl = document.getElementById('alert_class'); if (classEl) classEl.value = this.state.cabinClass || 'ECONOMY';
    const curEl = document.getElementById('alert_current_price'); if (curEl) curEl.value = currentPrice;

    const routeTxt = document.getElementById('alert-route-text'); if (routeTxt) routeTxt.innerText = `${orig} → ${dest}`;
    const dateTxt = document.getElementById('alert-date-text'); if (dateTxt) dateTxt.innerText = `Departure Date: ${date}`;
    const priceTxt = document.getElementById('alert-current-price-text'); if (priceTxt) priceTxt.innerText = `₹${parseFloat(currentPrice).toLocaleString()}`;
    const targetEl = document.getElementById('alert_target_price'); if (targetEl) targetEl.value = Math.max(1000, Math.round(currentPrice * 0.88));

    modal.classList.remove('hidden');
  }

  closePriceAlertModal() {
    const modal = document.getElementById('price-alert-modal');
    if (modal) modal.classList.add('hidden');
  }

  async handleCreatePriceAlert(e) {
    e.preventDefault();
    const payload = {
      flight_id: document.getElementById('alert_flight_id')?.value || null,
      origin: document.getElementById('alert_origin')?.value || this.state.origin || 'BOM',
      destination: document.getElementById('alert_destination')?.value || this.state.dest || 'DEL',
      travel_date: document.getElementById('alert_date')?.value || this.state.date || new Date().toISOString().split('T')[0],
      class: document.getElementById('alert_class')?.value || this.state.cabinClass || 'ECONOMY',
      current_price: parseFloat(document.getElementById('alert_current_price')?.value || '4850'),
      target_price: parseFloat(document.getElementById('alert_target_price')?.value || '4200'),
      email: document.getElementById('alert_email')?.value || ''
    };

    try {
      const res = await fetch('/flights/price-alert/create/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.success) {
        this.closePriceAlertModal();
        NotificationService.show(`🔔 ${data.message}`, 'success');
      } else {
        NotificationService.show(data.error || 'Failed to create price alert', 'error');
      }
    } catch (err) {
      NotificationService.show('Error activating price alert.', 'error');
    }
  }

  /* ================================================================
     🛂 DESTINATION VISA & TRAVEL REQUIREMENTS MODAL
     ================================================================ */
  async openTravelRequirementsModal() {
    const modal = document.getElementById('travel-requirements-modal');
    const loading = document.getElementById('req-modal-loading');
    const content = document.getElementById('req-modal-content');
    if (!modal) return;

    modal.classList.remove('hidden');
    if (loading) loading.classList.remove('hidden');
    if (content) content.classList.add('hidden');

    const origInput = document.getElementById('origin')?.value.trim();
    const destInput = document.getElementById('destination')?.value.trim();

    const orig = this.state.origin || origInput || 'BOM';
    const dest = this.state.dest || destInput || 'DEL';

    try {
      const res = await fetch(`/flights/requirements/?origin=${encodeURIComponent(orig)}&destination=${encodeURIComponent(dest)}`);
      const data = await res.json();

      if (loading) loading.classList.add('hidden');
      if (content) {
        content.classList.remove('hidden');
        content.innerHTML = `
          <div class="glass-inner p-3 rounded mb-3 flex justify-between align-center">
            <div>
              <strong class="text-white" style="font-size:1.1rem;">${data.origin_country} → ${data.destination_country}</strong>
              <div class="text-muted small">${data.origin_code} to ${data.destination_code}</div>
            </div>
            <span class="badge ${data.is_domestic ? 'badge-success' : 'badge-primary'}">${data.visa_required}</span>
          </div>

          <div class="mb-3">
            <label class="text-muted small d-block mb-1">Visa Category & Entry Policy</label>
            <div class="text-white font-weight-bold">${data.visa_type}</div>
          </div>

          <div class="mb-3">
            <label class="text-muted small d-block mb-1">Passport / Identification Validity</label>
            <div class="text-cyan">${data.passport_validity}</div>
          </div>

          <div class="mb-3">
            <label class="text-muted small d-block mb-1">Required Travel Documents Checklist</label>
            <div class="glass-inner p-3 rounded small text-white" style="white-space:pre-line;line-height:1.6;">
              ${data.documents_required}
            </div>
          </div>

          <div class="mb-3">
            <label class="text-muted small d-block mb-1">Transit Requirements</label>
            <p class="text-muted small m-0">${data.transit_requirements}</p>
          </div>

          <div class="p-3 rounded mb-3" style="background:rgba(245,158,11,0.1);border-left:4px solid #f59e0b;">
            <p class="text-warning small m-0"><strong>Disclaimer:</strong> ${data.disclaimer}</p>
          </div>

          ${data.official_source_url ? `
            <div class="text-center mt-3">
              <a href="${data.official_source_url}" target="_blank" class="btn btn-outline btn-sm">
                <i class="fa-solid fa-arrow-up-right-from-square me-1"></i> Official Government Visa Portal
              </a>
            </div>
          ` : ''}
        `;
      }
    } catch (e) {
      if (loading) loading.classList.add('hidden');
      if (content) {
        content.classList.remove('hidden');
        content.innerHTML = `<p class="text-danger">Unable to load travel requirements.</p>`;
      }
    }
  }

  closeRequirementsModal() {
    const modal = document.getElementById('travel-requirements-modal');
    if (modal) modal.classList.add('hidden');
  }

  closeTravelRequirementsModal() {
    this.closeRequirementsModal();
  }

  /* ================================================================
     ⛅ DESTINATION WEATHER MODAL
     ================================================================ */
  async openDestinationWeatherModal() {
    const modal = document.getElementById('destination-weather-modal');
    const body = document.getElementById('weather-modal-body');
    if (!modal || !body) return;

    modal.classList.remove('hidden');
    body.innerHTML = `
      <div class="text-center p-4">
        <i class="fa-solid fa-circle-notch fa-spin text-warning fa-2x"></i>
        <p class="text-muted small mt-2">Connecting to live meteorological service...</p>
      </div>
    `;

    const destInput = document.getElementById('destination')?.value.trim();
    const dest = this.state.dest || destInput || 'DEL';

    try {
      const res = await fetch(`/flights/weather/${encodeURIComponent(dest)}/`);
      const w = await res.json();

      let forecastHtml = '';
      if (w.forecast && w.forecast.length > 0) {
        forecastHtml = `
          <div class="mt-3 pt-3 border-top border-secondary">
            <h5 class="text-white small mb-2">5-Day Meteorological Forecast</h5>
            <div class="flex gap-2 justify-between overflow-x-auto pb-2">
              ${w.forecast.map(f => `
                <div class="glass-inner p-2 rounded text-center" style="min-width:80px;">
                  <div class="text-muted tiny">${f.date}</div>
                  <div style="font-size:1.4rem;margin:4px 0;">${f.icon_symbol || '☀️'}</div>
                  <div class="font-weight-bold text-white small">${f.temp_max}°</div>
                  <div class="text-muted tiny">${f.temp_min}°</div>
                </div>
              `).join('')}
            </div>
          </div>
        `;
      }

      body.innerHTML = `
        <div class="glass-inner p-4 rounded mb-3 flex justify-between align-center">
          <div>
            <h3 class="m-0 text-white">${w.city} (${w.code})</h3>
            <span class="text-muted small">${w.country}</span>
            <div class="text-cyan font-weight-bold mt-2">${w.condition}</div>
          </div>
          <div class="text-right">
            <div style="font-size:2.4rem;font-weight:800;color:#38bdf8;">${w.temp}°C</div>
            <span class="text-muted tiny">Feels like ${w.feels_like}°C</span>
          </div>
        </div>

        <div class="grid grid-2 gap-2 mb-3">
          <div class="glass-inner p-2 rounded flex align-center gap-2">
            <i class="fa-solid fa-droplet text-cyan"></i>
            <div>
              <span class="text-muted tiny d-block">Humidity</span>
              <strong class="text-white small">${w.humidity}%</strong>
            </div>
          </div>
          <div class="glass-inner p-2 rounded flex align-center gap-2">
            <i class="fa-solid fa-wind text-warning"></i>
            <div>
              <span class="text-muted tiny d-block">Wind Speed</span>
              <strong class="text-white small">${w.wind_speed_kmh} km/h</strong>
            </div>
          </div>
        </div>

        <div class="glass-inner p-3 rounded">
          <span class="text-muted tiny d-block">🌟 Recommended Best Season to Visit</span>
          <strong class="text-emerald">${w.best_season || 'Oct – Apr'}</strong>
        </div>

        ${forecastHtml}
      `;
    } catch (e) {
      body.innerHTML = `<p class="text-danger">Could not retrieve live destination weather.</p>`;
    }
  }

  closeWeatherModal() {
    const modal = document.getElementById('destination-weather-modal');
    if (modal) modal.classList.add('hidden');
  }

  /* ================================================================
     🌍 3D FLIGHT ROUTE & EARTH VISUALIZER
     ================================================================ */
  openRoute3DModal(orig, dest, duration = '2.5') {
    const modal = document.getElementById('route-3d-modal');
    if (!modal) return;

    modal.classList.remove('hidden');
    document.getElementById('route3d-title').innerText = `3D Flight Route: ${orig} → ${dest}`;
    document.getElementById('route-stat-duration').innerHTML = `Duration: <strong>${duration}h</strong>`;

    this.initThreeDRouteCanvas(orig, dest);
  }

  closeRoute3DModal() {
    const modal = document.getElementById('route-3d-modal');
    if (modal) modal.classList.add('hidden');
    if (this._threeAnimationId) {
      cancelAnimationFrame(this._threeAnimationId);
    }
  }

  initThreeDRouteCanvas(orig, dest) {
    const container = document.getElementById('route-3d-canvas-container');
    if (!container) return;

    // Clear previous canvases if any
    const existingCanvas = container.querySelector('canvas');
    if (existingCanvas) existingCanvas.remove();

    if (typeof THREE === 'undefined') {
      // 2D Canvas Fallback
      container.innerHTML = `
        <div class="text-center p-5 text-white">
          <i class="fa-solid fa-plane fa-2x text-cyan mb-2"></i>
          <h4>Great Circle Flight Path: ${orig} → ${dest}</h4>
          <p class="text-muted small">Simulated non-stop airway corridor.</p>
        </div>
      `;
      return;
    }

    const width = container.clientWidth || 680;
    const height = container.clientHeight || 360;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x030814);

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.z = 2.8;

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // Globe Sphere
    const globeGeo = new THREE.SphereGeometry(1, 32, 32);
    const globeMat = new THREE.MeshBasicMaterial({
      color: 0x091e3a,
      wireframe: true,
      transparent: true,
      opacity: 0.35
    });
    const globe = new THREE.Mesh(globeGeo, globeMat);
    scene.add(globe);

    // Inner Glow
    const innerGeo = new THREE.SphereGeometry(0.98, 32, 32);
    const innerMat = new THREE.MeshBasicMaterial({ color: 0x0284c7, transparent: true, opacity: 0.15 });
    const innerMesh = new THREE.Mesh(innerGeo, innerMat);
    scene.add(innerMesh);

    // Create Curved Flight Route Arc
    const p1 = new THREE.Vector3(-0.6, 0.4, 0.7);
    const p2 = new THREE.Vector3(0.6, 0.2, 0.7);
    const midPoint = new THREE.Vector3(0, 0.75, 1.1);

    const curve = new THREE.QuadraticBezierCurve3(p1, midPoint, p2);
    const points = curve.getPoints(50);
    const lineGeo = new THREE.BufferGeometry().setFromPoints(points);
    const lineMat = new THREE.LineBasicMaterial({ color: 0x38bdf8, linewidth: 2 });
    const routeLine = new THREE.Line(lineGeo, lineMat);
    scene.add(routeLine);

    // Animated Airplane Particle
    const planeGeo = new THREE.SphereGeometry(0.035, 12, 12);
    const planeMat = new THREE.MeshBasicMaterial({ color: 0x10b981 });
    const planeMesh = new THREE.Mesh(planeGeo, planeMat);
    scene.add(planeMesh);

    let progress = 0;
    const animate = () => {
      this._threeAnimationId = requestAnimationFrame(animate);
      globe.rotation.y += 0.002;
      
      progress += 0.006;
      if (progress > 1) progress = 0;

      const pos = curve.getPoint(progress);
      planeMesh.position.copy(pos);

      renderer.render(scene, camera);
    };

    animate();
  }

  /* ================================================================
     📡 LIVE FLIGHT RADAR & TELEMETRY ON MY TRIPS
     ================================================================ */
  async openLiveFlightTracker(flightIdentifier) {
    try {
      const res = await fetch(`/flights/tracker/${flightIdentifier}/`);
      const data = await res.json();
      if (!data.success) {
        NotificationService.show(data.status_message || 'Telemetry currently offline.', 'info');
        return;
      }

      this.showInfoModal({
        icon: 'fa-solid fa-satellite-dish text-primary',
        title: `Live Radar Telemetry: ${data.airline_code}-${data.flight_number}`,
        body: `
          <div class="radar-telemetry-card">
            <div class="flex justify-between align-center">
              <div>
                <strong class="text-white" style="font-size:1.1rem;">${data.origin} → ${data.destination}</strong>
                <div class="text-muted small">${data.airline} • ${data.aircraft || 'Aircraft'}</div>
              </div>
              <span class="badge ${data.status === 'IN_FLIGHT' ? 'badge-success' : 'badge-primary'}">${data.status_label || data.status}</span>
            </div>

            <div class="telemetry-grid">
              <div class="telemetry-item">
                <div class="telemetry-label">Altitude</div>
                <div class="telemetry-val">${(data.altitude_ft || 0).toLocaleString()} FT</div>
              </div>
              <div class="telemetry-item">
                <div class="telemetry-label">Airspeed</div>
                <div class="telemetry-val">${data.speed_kmh || 0} KM/H</div>
              </div>
              <div class="telemetry-item">
                <div class="telemetry-label">Distance Left</div>
                <div class="telemetry-val">${(data.distance_remaining_km || 0).toLocaleString()} KM</div>
              </div>
              <div class="telemetry-item">
                <div class="telemetry-label">Terminal / Gate</div>
                <div class="telemetry-val">${data.terminal} / ${data.gate}</div>
              </div>
            </div>

            <div class="mt-3">
              <div class="flex justify-between text-muted tiny mb-1">
                <span>Flight Progress</span>
                <span>${data.progress_pct || 0}%</span>
              </div>
              <div style="width:100%;height:6px;background:rgba(255,255,255,0.1);border-radius:3px;overflow:hidden;">
                <div style="width:${data.progress_pct || 0}%;height:100%;background:linear-gradient(90deg,#0ea5e9,#10b981);"></div>
              </div>
            </div>
          </div>
        `
      });
    } catch (e) {
      NotificationService.show('Failed to connect to flight radar.', 'error');
    }
  }

  showInfoModal(opt) {
    const modal = document.getElementById('flyease-info-modal');
    const title = document.getElementById('info-modal-title');
    const body = document.getElementById('info-modal-body');
    const icon = document.getElementById('info-modal-icon');
    if (!modal) return;

    if (title) title.innerText = opt.title || 'Information';
    if (body) body.innerHTML = opt.body || '';
    if (icon && opt.icon) icon.innerHTML = `<i class="${opt.icon}"></i>`;

    modal.classList.remove('hidden');
  }

  closeInfoModal() {
    const modal = document.getElementById('flyease-info-modal');
    if (modal) modal.classList.add('hidden');
  }

  sortFlightOffers(sortBy) {
    const offers = this.state.currentLeg === 'return' ? this.state.retOffers : this.state.depOffers;
    if (sortBy === 'cheapest') {
      offers.sort((a,b) => a.pricing.total - b.pricing.total);
    } else if (sortBy === 'fastest') {
      offers.sort((a,b) => a.duration_hours - b.duration_hours);
    } else if (sortBy === 'best_value') {
      offers.sort((a,b) => (b.recommendation_score || 0) - (a.recommendation_score || 0));
    }
    this.renderFlightList();
  }
}


/* =============================================
   INITIALIZATION
   ============================================= */
document.addEventListener('DOMContentLoaded', () => {
  window.app = new FlightApp();

  // Mobile menu toggle
  const mobileToggle = document.getElementById('nav-mobile-toggle');
  const navLinks = document.getElementById('nav-links');
  if (mobileToggle && navLinks) {
    mobileToggle.addEventListener('click', () => {
      navLinks.classList.toggle('show-mobile');
    });
  }

  // Universal Modal Dismiss Handler (Clicks on close buttons, overlays, and Escape key)
  document.addEventListener('click', (e) => {
    const closeBtn = e.target.closest('.btn-close-modal, [data-close-modal], .modal-close-btn');
    if (closeBtn) {
      e.preventDefault();
      e.stopPropagation();
      const modal = closeBtn.closest('.global-modal-overlay, #flyease-info-modal, .flyease-modal-backdrop');
      if (modal) {
        modal.classList.add('hidden');
      } else {
        document.querySelectorAll('.global-modal-overlay:not(.hidden), #flyease-info-modal:not(.hidden)').forEach(m => m.classList.add('hidden'));
      }
      return;
    }

    const overlay = e.target;
    if (overlay.classList && (overlay.classList.contains('global-modal-overlay') || overlay.classList.contains('flyease-modal-backdrop')) && e.target === overlay) {
      overlay.classList.add('hidden');
    }
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      document.querySelectorAll('.global-modal-overlay:not(.hidden), #flyease-info-modal:not(.hidden)').forEach(m => {
        m.classList.add('hidden');
      });
    }
  });

  // Inject confetti keyframes
  const style = document.createElement('style');
  style.textContent = `
    @keyframes confettiFall {
      0%   { transform: translateY(0) rotate(0deg); opacity:1; }
      100% { transform: translateY(120vh) rotate(720deg); opacity:0; }
    }
    @keyframes fadeSlideIn {
      from { opacity:0; transform: translateY(20px); }
      to   { opacity:1; transform: translateY(0); }
    }
    .card-selected {
      border: 2px solid var(--primary) !important;
      box-shadow: 0 0 20px rgba(99,102,241,0.4) !important;
    }
    .btn-select-flight { transition: all 0.2s ease; }
    .btn-select-flight:hover { transform: scale(1.05); }
    .flight-card { animation: fadeSlideIn 0.4s ease both; }
    .seat-item { transition: transform 0.2s ease, background 0.2s ease, box-shadow 0.2s ease; }
    .seat-item.available:hover { transform: scale(1.15); box-shadow: 0 0 10px rgba(99,102,241,0.5); }
  `;
  document.head.appendChild(style);



  // Navbar scroll effect
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    window.addEventListener('scroll', () => {
      navbar.classList.toggle('scrolled', window.scrollY > 50);
    });
  }

  // Intersection Observer for scroll animations
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('active');
        const statItems = entry.target.querySelectorAll ? entry.target.querySelectorAll('.stat-item, .stat-item-new') : [];
        if (entry.target.classList.contains('stat-item') || entry.target.classList.contains('stat-item-new')) {
          triggerStatCounter(entry.target);
        }
        statItems.forEach(s => triggerStatCounter(s));
      }
    });
  }, { threshold: 0.05, rootMargin: '0px 0px 50px 0px' });

  function triggerStatCounter(el) {
    if (el && !el.dataset.counted) {
      el.dataset.counted = 'true';
      const numberEl = el.querySelector('.stat-number');
      if (numberEl && numberEl.dataset.target) {
        animateValue(numberEl, 0, parseFloat(numberEl.dataset.target), 1800);
      }
    }
  }

  document.querySelectorAll('.reveal, .reveal-left, .reveal-right, .stat-item-new, .stats-belt, #pricing-chart').forEach(el => {
    observer.observe(el);
    // Instant fallback check for elements already in viewport or immediate load
    const rect = el.getBoundingClientRect();
    if (rect.top < window.innerHeight + 100 && rect.bottom > -100) {
      el.classList.add('active');
      if (el.classList.contains('stat-item-new') || el.classList.contains('stat-item')) {
        triggerStatCounter(el);
      }
      el.querySelectorAll?.('.stat-item, .stat-item-new').forEach(s => triggerStatCounter(s));
    }
  });

  function animateValue(obj, start, end, duration) {
    let startTimestamp = null;
    const isFloat = end % 1 !== 0;
    const step = (timestamp) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const currentVal = start + eased * (end - start);
      obj.innerHTML = isFloat ? currentVal.toFixed(1) : Math.floor(currentVal).toLocaleString();
      if (progress < 1) requestAnimationFrame(step);
      else obj.innerHTML = isFloat ? end.toFixed(1) : Math.floor(end).toLocaleString();
    };
    requestAnimationFrame(step);
  }
});

/* ================================================================
   FLYEASE — LANDING PAGE VIDEO BACKGROUND PLAYER
   - Discovered airport videos from /video/*.mp4
   - Double-buffered (two <video> layers) for seamless crossfade
   - Advances via video.onended (NOT fixed timers)
   - Preloads next video during current playback
   - Respects prefers-reduced-motion
   - Graceful static fallback for mobile/autoplay-failure
   ================================================================ */
(function () {
  'use strict';

  // Playlist — dynamic cinematic airport & flight sequence.
  // Files discovered from: frontend/public/video/
  const AIRPORT_VIDEOS = [
    '/video/v1.mp4',
    '/video/v2.mp4',
    '/video/v3.mp4',
    '/video/v4.mp4',
    '/video/v5.mp4',
    '/video/Create_a_cinematic_ultra_real (1).mp4',
    '/video/add_a_night_view_also_just_lik.mp4',
    '/video/another_part_of_this.mp4',
    '/video/make_different_diferent_aircra.mp4',
    '/video/make_more_another_part_various.mp4',
    '/video/the_video_now_you_made_just_ma.mp4'
  ];

  if (!AIRPORT_VIDEOS || AIRPORT_VIDEOS.length === 0) return;

  const prefersReducedMotion = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const isLowPowerMobile = () => {
    const w = window.innerWidth;
    return w <= 560 ||
      (navigator && navigator.connection && navigator.connection.saveData === true);
  };

  const crossfadeMs = prefersReducedMotion ? 0 : 1100;

  function buildProgressDots(activeIndex, total) {
    const container = document.getElementById('video-progress-dots');
    if (!container) return;
    container.innerHTML = '';
    for (let i = 0; i < total; i++) {
      const d = document.createElement('span');
      d.className = 'video-dot' + (i === activeIndex ? ' active' : '');
      d.setAttribute('aria-hidden', 'true');
      container.appendChild(d);
    }
  }

  function setActiveDot(index) {
    const dots = document.querySelectorAll('#video-progress-dots .video-dot');
    dots.forEach((d, i) => {
      if (i === index) d.classList.add('active');
      else d.classList.remove('active');
    });
  }

  function applyRevealDelays() {
    const items = document.querySelectorAll('.hero-content .reveal');
    items.forEach(el => {
      const raw = el.getAttribute('data-reveal-delay');
      if (raw == null) return;
      const sec = parseFloat(raw);
      if (!isNaN(sec)) {
        el.style.setProperty('--reveal-delay', sec + 's');
        el.style.animationDelay = sec + 's';
      }
    });
    // Hero CTA buttons are also reveal items
    const ctas = document.querySelectorAll('.hero-actions .btn');
    ctas.forEach(b => {
      if (!b.classList.contains('reveal')) b.classList.add('reveal');
    });
  }

  class VideoBackgroundPlayer {
    constructor(playlist) {
      this.playlist = playlist.slice();
      this.total = playlist.length;
      this.activeIndex = 0;
      this.layers = {
        A: document.getElementById('video-layer-a'),
        B: document.getElementById('video-layer-b')
      };
      this.bgWrap = document.querySelector('.video-background');
      this.activeLabel = 'A';   // which layer is currently playing/visible
      this.fallback = false;
      this._initialized = false;
    }

    getLayer(label) { return this.layers[label]; }
    otherLabel(label) { return label === 'A' ? 'B' : 'A'; }

    getNextIndex(i) { return (i + 1) % this.total; }
    getPrevIndex(i) { return (i - 1 + this.total) % this.total; }

    async start() {
      if (!this.layers.A || !this.layers.B) return;
      if (isLowPowerMobile()) { this.setFallback(); return; }
      applyRevealDelays();
      buildProgressDots(0, this.total);

      // Reset layer state
      Object.values(this.layers).forEach(v => {
        v.loop = false;
        v.controls = false;
        v.muted = true;
        v.setAttribute('muted', '');
        v.setAttribute('playsinline', '');
        v.playsInline = true;
        v.removeAttribute('controls');
      });

      // Prime: layer A loads 0, layer B preloads 1
      this.activeIndex = 0;
      this.activeLabel = 'A';
      this.loadIndexInto(0, 'A', true);
      this.loadIndexInto(this.getNextIndex(0), 'B', false);

      // Attempt to play active layer
      try {
        const active = this.getLayer(this.activeLabel);
        const p = active.play();
        if (p && typeof p.catch === 'function') {
          await p.catch(err => {
            // Autoplay blocked by browser
            console.warn('[FlyEase VideoBG] Autoplay blocked, falling back to static background:', err && err.message);
            this.setFallback();
          });
        }
      } catch (e) {
        console.warn('[FlyEase VideoBG] Play failed, fallback:', e);
        this.setFallback();
      }

      if (this.fallback) return;

      // Wire ended listener on both layers
      Object.entries(this.layers).forEach(([label, el]) => {
        el.addEventListener('ended', () => this.onLayerEnded(label));
        el.addEventListener('error', (e) => {
          // Skip bad video: advance but don't stall forever
          console.warn('[FlyEase VideoBG] Video load error for index, skipping:', label, e);
        });
      });

      // Mark currently-active layer as visible
      this.getLayer(this.activeLabel).classList.add('is-active');
      setActiveDot(0);
      this._initialized = true;
    }

    setFallback() {
      this.fallback = true;
      if (this.bgWrap) this.bgWrap.classList.add('is-fallback');
      applyRevealDelays();
    }

    loadIndexInto(index, label, isActive) {
      const el = this.getLayer(label);
      if (!el) return;
      const url = this.playlist[index];
      if (!url) return;
      // Only reload if source is different
      if (el.dataset.srcIndex != index) {
        el.src = url;
        el.dataset.srcIndex = index;
        // Start preloading metadata
        try { el.load(); } catch (_) { /* noop */ }
      }
      if (prefersReducedMotion) {
        el.style.transition = 'none';
      }
    }

    onLayerEnded(endedLabel) {
      if (this.fallback) return;
      // The ended layer is the current one; advance to next index on the OTHER layer
      const nextLabel = this.otherLabel(endedLabel);
      const endedLayer = this.getLayer(endedLabel);
      const nextLayer = this.getLayer(nextLabel);

      this.activeIndex = this.getNextIndex(this.activeIndex);
      setActiveDot(this.activeIndex);

      // Preload the one AFTER next onto the just-ended layer (soon to be background)
      const preloadIndex = this.getNextIndex(this.activeIndex);

      // Crossfade: bring next layer to opacity 1
      nextLayer.classList.add('is-active');
      // Immediately play next layer (it was preloaded, should be ready)
      try {
        const p = nextLayer.play();
        if (p && typeof p.catch === 'function') p.catch(() => { /* ignore */ });
      } catch (_) { /* noop */ }

      // After crossfade, retire the ended layer and load next+1 onto it
      setTimeout(() => {
        endedLayer.classList.remove('is-active');
        try { endedLayer.pause(); } catch (_) { /* noop */ }
        // Reset playback position
        try { endedLayer.currentTime = 0; } catch (_) { /* noop */ }
        // Load the upcoming video onto the now-idle layer
        this.loadIndexInto(preloadIndex, endedLabel, false);
      }, crossfadeMs);

      this.activeLabel = nextLabel;
    }
  }

  function init() {
    const player = new VideoBackgroundPlayer(AIRPORT_VIDEOS);
    player.start();
    // Expose for troubleshooting in console (optional)
    window.__flyeaseVideoBG = player;
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
