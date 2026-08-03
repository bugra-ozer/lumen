let token = null;
let refreshToken = null;
let currentUsername = null;
const genres = ["action", "adventure", "animation", "biography", "comedy", "crime", "documentary", "drama", "family", "fantasy", "film-noir", "history", "horror", "music", "musical", "mystery", "romance", "sci-fi", "sport", "thriller", "war", "western"]
const container = document.getElementById('genre-container');

for (const genre of genres) {
    const box = document.createElement('div');
    box.className = 'genre-pill';
    box.textContent = genre;
    box.dataset.genre = genre;
    box.addEventListener('click', function(){
        box.classList.toggle('selected');
    });
    box.textContent = genre;
    container.appendChild(box);
}

function performLogin(username, pw) {
    return fetch('/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username: username, pw: pw})
    })
    .then(response => response.json().then(data => ({status: response.status, body: data})))
    .then(result => {
        const errorEl = document.getElementById('auth-error');
        if (result.status === 200) {
            token = result.body.access_token;
            refreshToken = result.body.refresh_token;
            localStorage.setItem('refreshToken', refreshToken);
            localStorage.setItem('username', username);
            currentUsername = username;
            document.getElementById('user-bar').classList.remove('hidden');
            document.getElementById('username-display').textContent = 'Signed in as ' + currentUsername;
            document.getElementById('auth-section').classList.add('hidden');
            document.getElementById('filter-section').classList.remove('hidden');
        } else {
            errorEl.textContent = 'Invalid username or password.';
            errorEl.classList.remove('hidden');
        }
    });
}

document.getElementById('login-btn').addEventListener('click', function() {
    const username = document.getElementById('username').value.trim().toLowerCase();
    const pw = document.getElementById('pw').value.trim();
    const errorEl = document.getElementById('auth-error');
    const loginBtn = document.getElementById('login-btn');

    if (!username || !pw) {
        errorEl.textContent = 'Please enter both fields to login.';
        errorEl.classList.remove('hidden');
        return;
    }

    loginBtn.disabled = true;
    performLogin(username, pw)
        .then(() => { loginBtn.disabled = false; })
        .catch(() => {
            loginBtn.disabled = false;
            errorEl.textContent = 'Network error. Please try again.';
            errorEl.classList.remove('hidden');
        });
});

function authFetch(url, options) {
    options.headers = options.headers || {};
    options.headers['Authorization'] = 'Bearer ' + token;

    return fetch(url, options).then(response => {
        if (response.status !== 401) {
            return response;
        }
        return fetch('/refresh', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({refresh_token: refreshToken})
        })
        .then(refreshResponse => refreshResponse.json())
        .then(refreshData => {
            token = refreshData.access_token;
            options.headers['Authorization'] = 'Bearer ' + token;
            return fetch(url, options);
        });
    });
}

window.addEventListener('load', function() {
    const savedRefreshToken = localStorage.getItem('refreshToken');
    if (!savedRefreshToken) return;

    fetch('/refresh', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({refresh_token: savedRefreshToken})
    })
    .then(response => response.json())
    .then(data => {
        token = data.access_token;
        refreshToken = savedRefreshToken;
        currentUsername = localStorage.getItem('username');
        document.getElementById('user-bar').classList.remove('hidden');
        document.getElementById('username-display').textContent = 'Signed in as ' + currentUsername;
        document.getElementById('auth-section').classList.add('hidden');
        document.getElementById('filter-section').classList.remove('hidden');
    });
});

document.getElementById('logout-btn').addEventListener('click', function() {
    fetch('/logout', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({refresh_token: refreshToken})
    })
    .then(() => {
        token = null;
        refreshToken = null;
        currentUsername = localStorage.getItem('username');
        localStorage.removeItem('refreshToken');
        document.getElementById('user-bar').classList.add('hidden');
        document.getElementById('username-display').textContent = '';
        document.getElementById('filter-section').classList.add('hidden');
        document.getElementById('auth-section').classList.remove('hidden');
        document.getElementById('results-section').innerHTML = '<p class="empty-state">Your recommendations will appear here.</p>';
    });
});

document.getElementById('pw').addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        document.getElementById('login-btn').click();
    }
});

document.getElementById('register-btn').addEventListener('click', function(){
    const username = document.getElementById('username').value.trim().toLowerCase();
    const pw = document.getElementById('pw').value.trim();
    const errorEl = document.getElementById('auth-error');
    const registerBtn = document.getElementById('register-btn');

    if (!username || !pw) {
        errorEl.textContent = 'Please enter both fields to register.';
        errorEl.classList.remove('hidden');
        return;
    }

    registerBtn.disabled = true;

    fetch('/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username: username, pw: pw})
    })
    .then(response => response.json().then(data => ({status: response.status, body: data})))
    .then(result => {
        if (result.status >= 200 && result.status < 300) {
            errorEl.classList.add('hidden');
            errorEl.textContent = '';
            return performLogin(username, pw);
        } else {
            errorEl.textContent = result.body.status || 'Registration failed. Please check your input.';
            errorEl.classList.remove('hidden');
        }
    })
    .then(() => { registerBtn.disabled = false; })
    .catch(() => {
        registerBtn.disabled = false;
        errorEl.textContent = 'Network error. Please try again.';
        errorEl.classList.remove('hidden');
    });
})

/** RECOMMENDATION */
document.getElementById('recommend-btn').addEventListener('click', function() {
    const selectedGenres = Array.from(document.querySelectorAll('.selected')).map(box => box.dataset.genre);
    const ratingFrom = parseFloat(document.getElementById('rating-from').value);
    const ratingTo = parseFloat(document.getElementById('rating-to').value);

    const filterTools = {};

    if (selectedGenres.length > 0) {
        filterTools.genre = { value: selectedGenres };
    }

    const hasFrom = !isNaN(ratingFrom);
    const hasTo = !isNaN(ratingTo);

    if (hasFrom && hasTo) {
        filterTools.rating = { value: [ratingFrom, ratingTo], operator: 'between' };
    } else if (hasFrom) {
        filterTools.rating = { value: [ratingFrom], operator: '>' };
    } else if (hasTo) {
        filterTools.rating = { value: [ratingTo], operator: '<' };
    }

    authFetch('/recommendations', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ filter_tools: filterTools })
    })
    .then(response => response.json())
    .then(data => {
        const resultsSection = document.getElementById('results-section');
        resultsSection.innerHTML = '';

        if (data.length === 0) {
            resultsSection.innerHTML = '<p class="empty-state">No movies matched your filters. Try widening your search.</p>';
            return;
        }

        data.forEach(movie => {
            const card = document.createElement('div');
            card.className = 'movie-card';

            const img = document.createElement('img');
            img.src = movie.poster_path;
            img.alt = movie.primary_title;

            const title = document.createElement('p');
            title.textContent = movie.primary_title;

            const meta = document.createElement('p');
            meta.textContent = `${movie.published} · ⭐ ${movie.average_rating} · ${movie.genre}`;

            card.appendChild(img);
            card.appendChild(title);
            card.appendChild(meta);
            resultsSection.appendChild(card);
        });
    });
});