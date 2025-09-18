// API Base URL - adjust according to your environment
const API_BASE = 'http://localhost:8000/api/v1';
let authToken = localStorage.getItem('authToken');

// DOM Elements
const pages = document.querySelectorAll('.page');
const navLinks = document.querySelectorAll('.nav-link');
const messageArea = document.getElementById('message-area');
const loginBtn = document.getElementById('login-btn');
const registerBtn = document.getElementById('register-btn');
const logoutBtn = document.getElementById('logout-btn');

// Check if user is logged in
if (authToken) {
  updateAuthUI(true);
}

// Navigation
navLinks.forEach((link) => {
  link.addEventListener('click', (e) => {
    e.preventDefault();
    const pageId = `${e.target.dataset.page}-page`;
    showPage(pageId);

    // Load data for the page
    if (pageId === 'products-page') {
      loadProducts();
    } else if (pageId === 'categories-page') {
      loadCategories();
    } else if (pageId === 'users-page') {
      loadUsers();
    } else if (pageId === 'home-page') {
      loadDashboard();
    }
  });
});

// Auth buttons
loginBtn.addEventListener('click', () => showPage('login-form'));
registerBtn.addEventListener('click', () => showPage('register-form'));
logoutBtn.addEventListener('click', logout);

// Cancel buttons
document
  .getElementById('cancel-login')
  .addEventListener('click', () => showPage('home-page'));
document
  .getElementById('cancel-register')
  .addEventListener('click', () => showPage('home-page'));

// Form submissions
document.getElementById('login-form-data').addEventListener('submit', login);
document
  .getElementById('register-form-data')
  .addEventListener('submit', register);

// Show a specific page
function showPage(pageId) {
  pages.forEach((page) => {
    page.classList.remove('active');
  });
  document.getElementById(pageId).classList.add('active');
}

// Show message
function showMessage(message, type = 'success') {
  messageArea.innerHTML = `
        <div class="alert alert-${type}">
            ${message}
        </div>
    `;

  // Auto hide after 5 seconds
  setTimeout(() => {
    messageArea.innerHTML = '';
  }, 5000);
}

// Update UI based on auth status
function updateAuthUI(isLoggedIn) {
  if (isLoggedIn) {
    loginBtn.style.display = 'none';
    registerBtn.style.display = 'none';
    logoutBtn.style.display = 'block';
  } else {
    loginBtn.style.display = 'block';
    registerBtn.style.display = 'block';
    logoutBtn.style.display = 'none';
  }
}

// API Functions
async function login(e) {
  e.preventDefault();
  const username = document.getElementById('login-username').value;
  const password = document.getElementById('login-password').value;

  try {
    const response = await fetch(`${API_BASE}/auth/login/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    const data = await response.json();

    if (response.ok) {
      authToken = data.data.tokens.access;
      localStorage.setItem('authToken', authToken);
      updateAuthUI(true);
      showPage('home-page');
      showMessage('Login successful!');
      loadDashboard();
    } else {
      showMessage(data.message || 'Login failed', 'error');
    }
  } catch (error) {
    showMessage('An error occurred during login', 'error');
  }
}

async function register(e) {
  e.preventDefault();
  const username = document.getElementById('register-username').value;
  const email = document.getElementById('register-email').value;
  const password = document.getElementById('register-password').value;
  const first_name = document.getElementById('register-firstname').value;
  const last_name = document.getElementById('register-lastname').value;

  try {
    const response = await fetch(`${API_BASE}/auth/register/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username,
        email,
        password,
        first_name,
        last_name,
      }),
    });

    const data = await response.json();

    if (response.ok) {
      showMessage('Registration successful! Please login.');
      showPage('login-form');
    } else {
      showMessage(data.message || 'Registration failed', 'error');
    }
  } catch (error) {
    showMessage('An error occurred during registration', 'error');
  }
}

function logout() {
  authToken = null;
  localStorage.removeItem('authToken');
  updateAuthUI(false);
  showMessage('Logged out successfully');
}

async function loadDashboard() {
  try {
    // Load products count
    const productsResponse = await fetch(`${API_BASE}/products/`);
    if (productsResponse.ok) {
      const productsData = await productsResponse.json();
      document.getElementById('products-count').textContent =
        productsData.meta.pagination.total || 0;
    }

    // Load categories count
    const categoriesResponse = await fetch(`${API_BASE}/categories/`);
    if (categoriesResponse.ok) {
      const categoriesData = await categoriesResponse.json();
      document.getElementById('categories-count').textContent =
        categoriesData.meta.pagination.total || 0;
    }

    // Load users count (requires auth)
    if (authToken) {
      const usersResponse = await fetch(`${API_BASE}/users/`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      if (usersResponse.ok) {
        const usersData = await usersResponse.json();
        document.getElementById('users-count').textContent =
          usersData.meta.pagination.total || 0;
      }
    }
  } catch (error) {
    console.error('Error loading dashboard:', error);
  }
}

async function loadProducts() {
  try {
    const response = await fetch(`${API_BASE}/products/`);
    const data = await response.json();

    if (response.ok) {
      const productsTable = document
        .getElementById('products-table')
        .querySelector('tbody');
      productsTable.innerHTML = '';

      data.data.forEach((product) => {
        const row = document.createElement('tr');
        row.innerHTML = `
                    <td>${product.id}</td>
                    <td>${product.name}</td>
                    <td>$${product.price}</td>
                    <td>${product.category ? product.category.name : 'N/A'}</td>
                    <td>${product.stock_quantity}</td>
                    <td>
                        <button class="btn btn-outline">Edit</button>
                        <button class="btn btn-danger">Delete</button>
                    </td>
                `;
        productsTable.appendChild(row);
      });
    } else {
      showMessage('Failed to load products', 'error');
    }
  } catch (error) {
    showMessage('Error loading products', 'error');
  }
}

async function loadCategories() {
  try {
    const response = await fetch(`${API_BASE}/categories/`);
    const data = await response.json();

    if (response.ok) {
      const categoriesTable = document
        .getElementById('categories-table')
        .querySelector('tbody');
      categoriesTable.innerHTML = '';

      data.data.forEach((category) => {
        const row = document.createElement('tr');
        row.innerHTML = `
                    <td>${category.id}</td>
                    <td>${category.name}</td>
                    <td>${category.description || 'N/A'}</td>
                    <td>${category.product_count || 0}</td>
                    <td>
                        <button class="btn btn-outline">Edit</button>
                        <button class="btn btn-danger">Delete</button>
                    </td>
                `;
        categoriesTable.appendChild(row);
      });
    } else {
      showMessage('Failed to load categories', 'error');
    }
  } catch (error) {
    showMessage('Error loading categories', 'error');
  }
}

async function loadUsers() {
  if (!authToken) {
    showMessage('Please login to view users', 'error');
    return;
  }

  try {
    const response = await fetch(`${API_BASE}/users/`, {
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
    });

    const data = await response.json();

    if (response.ok) {
      const usersTable = document
        .getElementById('users-table')
        .querySelector('tbody');
      usersTable.innerHTML = '';

      data.data.forEach((user) => {
        const row = document.createElement('tr');
        row.innerHTML = `
                    <td>${user.id}</td>
                    <td>${user.username}</td>
                    <td>${user.email}</td>
                    <td>${user.first_name} ${user.last_name}</td>
                    <td>${user.is_active ? 'Active' : 'Inactive'}</td>
                    <td>
                        <button class="btn btn-outline">Edit</button>
                        <button class="btn btn-danger">Delete</button>
                    </td>
                `;
        usersTable.appendChild(row);
      });
    } else {
      showMessage('Failed to load users', 'error');
    }
  } catch (error) {
    showMessage('Error loading users', 'error');
  }
}

// Initialize the dashboard
loadDashboard();
