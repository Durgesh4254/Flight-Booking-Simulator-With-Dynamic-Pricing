/* 
  FlyEase Admin Dashboard Application Engine
  Handles real-time KPI counters, Chart.js integrations, search, pricing simulation, modals & filters
*/

window.AdminApp = {
  activeTab: 'dashboard',
  charts: {},

  init: function() {
    this.bindSidebar();
    this.loadTopStats();
  },

  // Toggle Sidebar
  bindSidebar: function() {
    const toggleBtn = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.admin-sidebar');
    const mainWrapper = document.querySelector('.admin-main-wrapper');
    const mobileBtn = document.getElementById('mobile-menu-btn');

    if (toggleBtn && sidebar && mainWrapper) {
      toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
        mainWrapper.classList.toggle('sidebar-collapsed');
      });
    }

    if (mobileBtn && sidebar) {
      mobileBtn.addEventListener('click', () => {
        sidebar.classList.toggle('mobile-open');
      });
    }
  },

  // Load KPI top header stats
  loadTopStats: function() {
    fetch('/admin-portal/api/kpis/')
      .then(res => res.json())
      .then(data => {
        const flightEl = document.getElementById('top-active-flights');
        const alertEl = document.getElementById('top-unread-alerts');
        if (flightEl) flightEl.textContent = data.active_flights;
        if (alertEl) {
          alertEl.textContent = data.unread_alerts;
          alertEl.style.display = data.unread_alerts > 0 ? 'flex' : 'none';
        }
      })
      .catch(err => console.error('Top stats error:', err));
  },

  // Format INR Currency
  formatINR: function(val) {
    return '₹' + parseFloat(val || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 });
  },

  // Show Toast Alert Notification
  showToast: function(message, type = 'success') {
    let container = document.getElementById('admin-toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'admin-toast-container';
      container.style.cssText = 'position:fixed;bottom:24px;right:24px;z-index:9999;display:flex;flex-direction:column;gap:10px;';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    const icon = type === 'success' ? 'fa-circle-check' : 'fa-circle-exclamation';
    const borderCol = type === 'success' ? '#10B981' : '#F43F5E';
    
    toast.style.cssText = `background:#0F172A;border:1px solid ${borderCol};color:#fff;padding:12px 20px;border-radius:10px;display:flex;align-items:center;gap:10px;box-shadow:0 10px 25px rgba(0,0,0,0.5);font-size:0.9rem;animation:modalEnter 0.2s;`;
    toast.innerHTML = `<i class="fa-solid ${icon}" style="color:${borderCol}"></i> <span>${message}</span>`;
    
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transition = 'opacity 0.3s';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  },

  // Open Modal Helper
  openModal: function(modalId) {
    const el = document.getElementById(modalId);
    if (el) el.classList.add('active');
  },

  closeModal: function(modalId) {
    const el = document.getElementById(modalId);
    if (el) el.classList.remove('active');
  }
};

document.addEventListener('DOMContentLoaded', () => {
  AdminApp.init();
});
