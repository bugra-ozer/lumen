let token = null;
const genres = ["action", "adventure", "animation", "biography", "comedy", "crime", "documentary", "drama", "family", "fantasy", "film-noir", "history", "horror", "music", "musical", "mystery", "romance", "sci-fi", "sport", "thriller", "war", "western"]
const container = document.getElementById('genre-container');

for (const genre of genres) {
    const box = document.createElement('div');
    box.className = 'genre-pill';
    box.addEventListener('click', function(){
        box.classList.toggle('selected');
    });
    box.textContent = genre;
    container.appendChild(box);
}

document.getElementById('login-btn').addEventListener('click', function() {
    const username = document.getElementById('username').value;
    const pw = document.getElementById('pw').value;

    fetch('/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username: username, pw: pw})
    })
    .then(response => response.json())
    .then(data => {
        token=data.access_token;
        document.getElementById('auth-section').classList.add('hidden');
        document.getElementById('filter-section').classList.remove('hidden');
    });
});

document.getElementById('pw').addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        document.getElementById('login-btn').click();
    }
});

document.getElementById('register-btn').addEventListener('click', function(){
    const username = document.getElementById('username').value;
    const pw = document.getElementById('pw').value;

    fetch('/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username: username, pw: pw})
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
    });
})

/** RECOMMENDATION */
document.getElementById('recommend-btn').addEventListener('click', function() {
    const selectedGenres = Array.from(document.querySelectorAll('.selected')).map(box => box.textContent);
    const ratingFrom = parseFloat(document.getElementById('rating-from').value);
    const ratingTo = parseFloat(document.getElementById('rating-to').value);

    const filterTools = {
        genre: { value: selectedGenres }
        };
        
        const hasFrom = !isNaN(ratingFrom);
        const hasTo = !isNaN(ratingTo);

        if (hasFrom && hasTo) {
            filterTools.rating = { value: [ratingFrom, ratingTo], operator: 'between' };
        } else if (hasFrom) {
            filterTools.rating = { value: [ratingFrom], operator: '>' };
        } else if (hasTo) {
            filterTools.rating = { value: [ratingTo], operator: '<' };
}

    fetch('/recommendations', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        },
        body: JSON.stringify({ filter_tools: filterTools })
    })
    .then(response => response.json())
    .then(data => {
        const resultsSection = document.getElementById('results-section');
        resultsSection.innerHTML = '';
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