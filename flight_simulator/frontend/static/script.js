
document.addEventListener('DOMContentLoaded', () => {

	const searchForm = document.getElementById('search-form');
	const fromInput = document.getElementById('from');
	const toInput = document.getElementById('to');
	const dateInput = document.getElementById('date');
	const returnCol = document.getElementById('return-col');
	const returnInput = document.getElementById('return-date');
	const passengersInput = document.getElementById('passengers');
	
	const resultsSection = document.getElementById('results-section');
	const flightResults = document.getElementById('flight-results');
	const backToSearchBtn = document.getElementById('back-to-search');
	
	const selectSection = document.getElementById('select-section');
	const selectedFlightDiv = document.getElementById('selected-flight');
	const classForm = document.getElementById('class-form');
	const seatClassSelect = document.getElementById('seat-class');
	const classBack = document.getElementById('class-back');
	
	const passengerSection = document.getElementById('passenger-section');
	const passengerFormsContainer = document.getElementById('passenger-forms-container');
	const passengerForm = document.getElementById('passenger-form');
	const passengerBack = document.getElementById('passenger-back');
	
	const reviewSection = document.getElementById('review-section');
	const reviewSummary = document.getElementById('review-summary');
	const reviewBack = document.getElementById('review-back');
	
	const confirmationSection = document.getElementById('confirmation-section');
	const confirmationDetails = document.getElementById('confirmation-details');
	const confirmBookingBtn = document.getElementById('confirm-booking');
	const downloadJsonBtn = document.getElementById('download-json');
	const downloadPdfBtn = document.getElementById('download-pdf');
	const newSearchBtn = document.getElementById('new-search');
	
	const fromSuggestions = document.getElementById('from-suggestions');
	const toSuggestions = document.getElementById('to-suggestions');
	
	
	let searchState = {};
	let selectedFlightOffer = null;
	let chosenClass = 'Economy';
	let passengerList = [];
	let bookingInfo = null;
	
	
	const airports = [
	  { city: "Delhi", code: "DEL", country: "India" },
	  { city: "Mumbai", code: "BOM", country: "India" },
	  { city: "Bangalore", code: "BLR", country: "India" },
	  { city: "Chennai", code: "MAA", country: "India" },
	  { city: "Kolkata", code: "CCU", country: "India" },
	  { city: "London", code: "LHR", country: "UK" },
	  { city: "New York", code: "JFK", country: "USA" },
	  { city: "Paris", code: "CDG", country: "France" },
	  { city: "Dubai", code: "DXB", country: "UAE" },
	  { city: "Singapore", code: "SIN", country: "Singapore" }
	];
	
	function setupAutocomplete(inputEl, boxEl) {
	  inputEl.addEventListener('input', () => {
	    const q = inputEl.value.trim().toLowerCase();
	    boxEl.innerHTML = '';
	    if (!q) { boxEl.style.display = 'none'; return; }
	    const matches = airports.filter(a => a.city.toLowerCase().includes(q) || a.code.toLowerCase().includes(q));
	    matches.slice(0, 8).forEach(a => {
	      const div = document.createElement('div');
	      div.textContent = `${a.city} (${a.code}) — ${a.country}`;
	      div.addEventListener('click', () => {
	        inputEl.value = `${a.city} (${a.code})`;
	        boxEl.innerHTML = '';
	        boxEl.style.display = 'none';
	      });
	      boxEl.appendChild(div);
	    });
	    boxEl.style.display = matches.length ? 'block' : 'none';
	  });
	
	  document.addEventListener('click', (e) => {
	    if (!inputEl.contains(e.target) && !boxEl.contains(e.target)) boxEl.style.display = 'none';
	  });
	}
	
	setupAutocomplete(fromInput, fromSuggestions);
	setupAutocomplete(toInput, toSuggestions);
	
	
	document.querySelectorAll('input[name="trip-type"]').forEach(radio => {
	  radio.addEventListener('change', () => {
	    const val = document.querySelector('input[name="trip-type"]:checked').value;
	    if (val === 'roundtrip') {
	      returnCol.style.display = 'block';
	      returnInput.required = true;
	    } else {
	      returnCol.style.display = 'none';
	      returnInput.required = false;
	      returnInput.value = '';
	    }
	  });
	});
	

	searchForm.addEventListener('submit', async (e) => {
	  e.preventDefault();
	  const from = fromInput.value.trim();
	  const to = toInput.value.trim();
	  const departDate = dateInput.value;
	  const returnDate = returnInput.value;
	  const passengers = Math.max(1, Number(passengersInput.value || 1));
	  const tripType = document.querySelector('input[name="trip-type"]:checked').value;

	  if (!from || !to || !departDate) {
	    alert('Please fill origin, destination, and departure date.');
	    return;
	  }
	  if (tripType === 'roundtrip' && !returnDate) {
	    alert('Please select a return date for round-trip.');
	    return;
	  }

	  searchState = { from, to, departDate, returnDate: tripType === 'roundtrip' ? returnDate : null, passengers, tripType };

	  const originCode = extractCode(from);
	  const destinationCode = extractCode(to);

	  const params = new URLSearchParams({
	    origin: originCode,
	    destination: destinationCode,
	    departure_date: departDate
	  });
	  const query = `/flights/search/?${params.toString()}`;
	  console.info('Searching flights', { query, origin: originCode, destination: destinationCode, departDate });

	  flightResults.innerHTML = `<p>Loading flights...</p>`;

	  try {
	    const res = await fetch(query, { credentials: 'same-origin' });
	    const text = await res.text();

	    
	    let data = null;
	    try { data = text ? JSON.parse(text) : null; } catch (parseErr) { console.warn('Non-JSON server response', text); }

	    if (!res.ok) {
	      const serverMsg = (data && (data.error || data.message)) || text || res.statusText || `Server error ${res.status}`;
	      throw new Error(serverMsg);
	    }

	    const offers = Array.isArray(data) ? data : (data?.offers || data?.results || []);
	    flightResults.innerHTML = '';
	    if (!offers || offers.length === 0) {
	      flightResults.innerHTML = `<p>No flights found. (Query sent: origin=${originCode}, destination=${destinationCode})</p>`;
	      return;
	    }

	    offers.forEach(o => {
	      const card = document.createElement('div');
	      card.className = 'flight-card';
	      const price = o.dynamic_price_per_seat ?? o.price ?? 0;
	      const flightId = o.flight_id ?? o.id ?? '';
	      const airline = o.airline || "FlyEase Air";
	      const dep = o.departure_time ? new Date(o.departure_time).toLocaleString() : (o.departure || 'N/A');
	      const arr = o.arrival_time ? new Date(o.arrival_time).toLocaleString() : (o.arrival || 'N/A');
	      card.innerHTML = `
	        <div>
	          <h3>${airline} <span class="small">(${o.origin || originCode} → ${o.destination || destinationCode})</span></h3>
	          <div class="small">Departure: ${dep}</div>
	          <div class="small">Arrival: ${arr}</div>
	        </div>
	        <div style="text-align:right">
	          <div class="price">₹${price}</div>
	          <div style="margin-top:8px;"></div>
	        </div>
	      `;
	      const btn = document.createElement('button');
	      btn.className = 'btn';
	      btn.type = 'button';
	      btn.textContent = 'Select';
	      btn.addEventListener('click', () => selectOffer(flightId, price, airline));
	      const rightDiv = card.querySelector('div[style]');
	      if (rightDiv) rightDiv.appendChild(btn);
	      flightResults.appendChild(card);
	    });

	    show(resultsSection);
	    hide(selectSection); hide(passengerSection); hide(reviewSection); hide(confirmationSection);
	    window.scrollTo({ top: resultsSection.offsetTop - 20, behavior: 'smooth' });
	  } catch (err) {
	    console.error('Flight search error:', err);
	    flightResults.innerHTML = `<p class="error">Error fetching flights: ${err.message}</p>`;
	  }
	});
	
	backToSearchBtn.addEventListener('click', () => {
	  hide(resultsSection);
	  window.scrollTo({ top: document.getElementById('search-section').offsetTop - 20, behavior: 'smooth' });
	});
	
	
	window.selectOffer = (id, basePrice, airline) => {
	  selectedFlightOffer = {
	    id,
	    basePrice,
	    airline,
	    from: searchState.from,
	    to: searchState.to,
	    departDate: searchState.departDate,
	    returnDate: searchState.returnDate,
	    tripType: searchState.tripType
	  };
	
	  selectedFlightDiv.innerHTML = `
	    <div class="flight-card">
	      <div>
	        <h3>${airline}</h3>
	        <div class="small">${selectedFlightOffer.from} → ${selectedFlightOffer.to}</div>
	        <div class="small">Departure: ${selectedFlightOffer.departDate}</div>
	        ${selectedFlightOffer.tripType === 'roundtrip' ? `<div class="small">Return: ${selectedFlightOffer.returnDate}</div>` : ''}
	      </div>
	      <div style="text-align:right">
	        <div class="price">From ₹${basePrice}</div>
	      </div>
	    </div>
	  `;
	  seatClassSelect.value = 'Economy';
	  chosenClass = 'Economy';
	
	  hide(resultsSection);
	  show(selectSection);
	  window.scrollTo({ top: selectSection.offsetTop - 20, behavior: 'smooth' });
	};
	
	
	classForm.addEventListener('submit', (e) => {
	  e.preventDefault();
	  chosenClass = seatClassSelect.value;
	  preparePassengerForms();
	  hide(selectSection);
	  show(passengerSection);
	  window.scrollTo({ top: passengerSection.offsetTop - 20, behavior: 'smooth' });
	});
	
	classBack.addEventListener('click', () => {
	  hide(selectSection);
	  show(resultsSection);
	});
	
	function preparePassengerForms() {
	  passengerFormsContainer.innerHTML = '';
	  passengerList = [];
	  const count = Math.max(1, Number(searchState.passengers || 1));
	  for (let i = 0; i < count; i++) {
	    const idx = i + 1;
	    const wrapper = document.createElement('div');
	    wrapper.className = 'passenger-card';
	    wrapper.innerHTML = `
	      <h4>Passenger ${idx}</h4>
	      <label>Full name</label>
	      <input required name="p_name_${i}" type="text" placeholder="e.g. Rahul Kumar" />
	      <label>Age</label>
	      <input required name="p_age_${i}" type="number" min="0" />
	      <label>Gender</label>
	      <select required name="p_gender_${i}">
	        <option>Male</option><option>Female</option><option>Other</option>
	      </select>
	    `;
	    passengerFormsContainer.appendChild(wrapper);
	  }
	}
	
	passengerForm.addEventListener('submit', (e) => {
	  e.preventDefault();
	  const count = Math.max(1, Number(searchState.passengers || 1));
	  passengerList = [];
	  for (let i = 0; i < count; i++) {
	    const name = e.target.querySelector(`[name="p_name_${i}"]`).value.trim();
	    const age = e.target.querySelector(`[name="p_age_${i}"]`).value.trim();
	    const gender = e.target.querySelector(`[name="p_gender_${i}"]`).value;
	    passengerList.push({ name, age, gender });
	  }
	  buildReview();
	  hide(passengerSection);
	  show(reviewSection);
	});
	
	reviewBack.addEventListener('click', () => {
	  hide(reviewSection);
	  show(passengerSection);
	});
	
	
	function buildReview() {
	  const base = Number(selectedFlightOffer.basePrice || 0);
	  const total = base * passengerList.length;
	  searchState.totalPrice = total;
	  let html = `
	    <strong>Flight:</strong> ${selectedFlightOffer.from} → ${selectedFlightOffer.to}<br/>
	    <strong>Airline:</strong> ${selectedFlightOffer.airline}<br/>
	    <strong>Class:</strong> ${chosenClass}<br/>
	    <strong>Passengers:</strong> ${passengerList.length}<br/>
	    <strong>Total Price:</strong> ₹${total}
	  `;
	  reviewSummary.innerHTML = html;
	}
	
	
	confirmBookingBtn.addEventListener('click', () => {
	  const payload = {
	    flight_id: selectedFlightOffer.id,
	    seats: passengerList.length,
	    passenger: {
	      first_name: passengerList[0]?.name?.split(" ")[0] || "Guest",
	      last_name: passengerList[0]?.name?.split(" ")[1] || "",
	      email: "test@example.com",
	      phone: "9999999999"
	    }
	  };
	
	  fetch("/flights/book/confirm/", {
	    method: "POST",
	    headers: {
	      "Content-Type": "application/json",
	      "X-CSRFToken": getCookie('csrftoken') || ''
	    },
	    body: JSON.stringify(payload)
	  })
	  .then(res => {
	    if (!res.ok) return res.json().then(j => { throw new Error(j.error || 'Server error ' + res.status); });
	    return res.json();
	  })
	  .then(data => {
	    if (!data.success) throw new Error(data.error || "Unknown error");
	    bookingInfo = {
	      pnr: data.pnr,
	      flight: selectedFlightOffer,
	      class: chosenClass,
	      passengers: passengerList,
	      total: data.price_paid,
	      bookedAt: new Date().toLocaleString()
	    };
	
	    confirmationDetails.innerHTML = `
	      <p><strong>PNR:</strong> ${bookingInfo.pnr}</p>
	      <p><strong>Route:</strong> ${bookingInfo.flight.from} → ${bookingInfo.flight.to}</p>
	      <p><strong>Class:</strong> ${bookingInfo.class}</p>
	      <p><strong>Passengers:</strong> ${bookingInfo.passengers.length}</p>
	      <p><strong>Total Paid:</strong> ₹${bookingInfo.total}</p>
	      <p class="small muted">Booked at: ${bookingInfo.bookedAt}</p>
	    `;
	    hide(reviewSection);
	    show(confirmationSection);
	  })
	  .catch(err => {
	    alert("Booking failed: " + err.message);
	  });
	});
	

	downloadJsonBtn.addEventListener('click', () => {
	  if (!bookingInfo) return;
	  const blob = new Blob([JSON.stringify(bookingInfo, null, 2)], { type: 'application/json' });
	  const a = document.createElement('a');
	  a.href = URL.createObjectURL(blob);
	  a.download = `booking_${bookingInfo.pnr}.json`;
	  a.click();
	});
	
	newSearchBtn.addEventListener('click', () => {
	  searchState = {};
	  selectedFlightOffer = null;
	  passengerList = [];
	  bookingInfo = null;
	  searchForm.reset();
	  passengerFormsContainer.innerHTML = '';
	  reviewSummary.innerHTML = '';
	  confirmationDetails.innerHTML = '';
	  hide(resultsSection); hide(selectSection); hide(passengerSection); hide(reviewSection); hide(confirmationSection);
	  window.scrollTo({ top: 0, behavior: 'smooth' });
	});
	

	function extractCode(input) {
	  if (!input) return '';
	  const m = input.match(/\(([A-Z0-9]{2,4})\)/i);
	  if (m && m[1]) return m[1].toUpperCase();
	  return input.trim();
	}

	function show(el){ if(el) el.classList.remove('hidden'); }
	function hide(el){ if(el) el.classList.add('hidden'); }
	
	function getCookie(name) {
	  const cookies = document.cookie ? document.cookie.split('; ') : [];
	  for (let i = 0; i < cookies.length; i++) {
	    const parts = cookies[i].split('=');
	    const key = parts.shift();
	    const value = parts.join('=');
	    if (key === name) return decodeURIComponent(value);
	  }
	  return null;
	}
});
