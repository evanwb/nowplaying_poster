const IMDB_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwZWNlMmQzM2RlOGQzY2U2MGEwMDI2YjcxOTQ1Zjk5NSIsIm5iZiI6MTczNjY0ODU5Ni43Nywic3ViIjoiNjc4MzI3OTQxMzZlMTU3Y2YyN2IxY2U5Iiwic2NvcGVzIjpbImFwaV9yZWFkIl0sInZlcnNpb24iOjF9.2saEcfF4A0bx80s11Pcze88F50-Icaogp_badqPrX_8";

const posterElement = document.getElementById("poster");
const titleElement = document.getElementById("title");

function splitTitleAndYear(input) {
    const match = input.match(/^(.*?)\s*\((\d{4})\)?$/);
    return match ? [match[1].trim(), match[2]] : [input.trim(), null];
}

function updateNowPlaying(hasData, posterUrl) {
    if (hasData && posterUrl) {
        // Show the elements and update their content
        titleElement.classList.remove("hidden");
        posterElement.classList.remove("hidden");

        // Update the poster image source
        posterElement.src = posterUrl;
        posterElement.alt = "Now Playing Poster";
    } else {
        // Hide the elements if no data is available
        titleElement.classList.add("hidden");
        posterElement.classList.add("hidden");
    }
}


async function fetchPoster(title) {
    const [name, year] = splitTitleAndYear(title);
    const query = encodeURIComponent(name);
    const yearFilter = year ? `&primary_release_year=${year}` : "";
    const url = `https://api.themoviedb.org/3/search/multi?query=${query}&include_adult=false&language=en-US${yearFilter}`;

    const response = await fetch(url, {
        headers: {
            accept: "application/json",
            Authorization: `Bearer ${IMDB_KEY}`,
        },
    });

    const data = await response.json();
    if (data.results && data.results.length > 0) {
        return `https://image.tmdb.org/t/p/w500/${data.results[0].poster_path}`;
    } else {
        return null; // No poster found
    }
}

// MQTT Client Setup
const client = mqtt.connect("ws://10.6.0.19:1884", {
    username: "mqtt_user",
    password: "mqtt_pass",
});

client.on("connect", () => {
    console.log("Connected to MQTT broker");
    client.subscribe("current/movie");
});

client.on("message", async (topic, message) => {
    if (topic === "current/movie") {
        const title = message.toString();
        console.log("Received title:", title);


        const posterUrl = await fetchPoster(title);
        if (posterUrl) {
            //alert(posterUrl);
            posterElement.src = posterUrl;
            updateNowPlaying(Boolean(title && posterUrl), posterUrl);
            client.publish("current/url", posterUrl);
        } else {
            posterElement.src = "";
            client.publish("current/url", "");
            updateNowPlaying(false, null);
        }
    }
});

// Fullscreen Toggle
window.addEventListener("click", () => {
    document.documentElement.requestFullscreen();
});
