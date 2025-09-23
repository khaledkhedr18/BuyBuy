document.addEventListener('DOMContentLoaded', () => {
  // ---------------- LOGIN ----------------
  const loginForm = document.getElementById('login-form-data');
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const username = document.getElementById('login-username').value;
      const password = document.getElementById('login-password').value;

      try {
        const res = await fetch('/api/login/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password }),
        });

        if (res.ok) {
          window.location.href = 'index.html';
        } else {
          alert('Invalid credentials');
        }
      } catch (err) {
        console.error('Login error:', err);
      }
    });
  }

  // ---------------- REGISTER ----------------
  const registerForm = document.getElementById('register-form-data');
  if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const userData = {
        username: document.getElementById('register-username').value,
        email: document.getElementById('register-email').value,
        password: document.getElementById('register-password').value,
        first_name: document.getElementById('register-firstname').value,
        last_name: document.getElementById('register-lastname').value,
      };

      try {
        const res = await fetch('/api/register/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(userData),
        });

        if (res.ok) {
          window.location.href = 'login.html';
        } else {
          alert('Registration failed');
        }
      } catch (err) {
        console.error('Register error:', err);
      }
    });
  }

  // ---------------- FETCH COUNTS ----------------
  const productsCount = document.getElementById('products-count');
  const categoriesCount = document.getElementById('categories-count');
  const usersCount = document.getElementById('users-count');

  if (productsCount || categoriesCount || usersCount) {
    fetch('/api/dashboard/')
      .then((res) => res.json())
      .then((data) => {
        if (productsCount) productsCount.textContent = data.products || 0;
        if (categoriesCount) categoriesCount.textContent = data.categories || 0;
        if (usersCount) usersCount.textContent = data.users || 0;
      })
      .catch((err) => console.error('Dashboard error:', err));
  }

  // ---------------- LOAD TABLES ----------------
  const productsTable = document.querySelector('#products-table tbody');
  if (productsTable) {
    fetch('/api/products/')
      .then((res) => res.json())
      .then((data) => {
        productsTable.innerHTML = data
          .map(
            (p) => `
          <tr>
            <td>${p.id}</td>
            <td>${p.name}</td>
            <td>${p.price}</td>
            <td>${p.category}</td>
            <td>${p.stock}</td>
            <td><button class="btn btn-danger">Delete</button></td>
          </tr>`,
          )
          .join('');
      });
  }

  const categoriesTable = document.querySelector('#categories-table tbody');
  if (categoriesTable) {
    fetch('/api/categories/')
      .then((res) => res.json())
      .then((data) => {
        categoriesTable.innerHTML = data
          .map(
            (c) => `
          <tr>
            <td>${c.id}</td>
            <td>${c.name}</td>
            <td>${c.description}</td>
            <td>${c.products_count}</td>
            <td><button class="btn btn-danger">Delete</button></td>
          </tr>`,
          )
          .join('');
      });
  }

  const usersTable = document.querySelector('#users-table tbody');
  if (usersTable) {
    fetch('/api/users/')
      .then((res) => res.json())
      .then((data) => {
        usersTable.innerHTML = data
          .map(
            (u) => `
          <tr>
            <td>${u.id}</td>
            <td>${u.username}</td>
            <td>${u.email}</td>
            <td>${u.first_name} ${u.last_name}</td>
            <td>${u.is_active ? 'Active' : 'Inactive'}</td>
            <td><button class="btn btn-danger">Delete</button></td>
          </tr>`,
          )
          .join('');
      });
  }
});
