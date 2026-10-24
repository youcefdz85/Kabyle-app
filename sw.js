// Offline support.
// - App files: network first (so content updates show up right away), cache as fallback.
// - Audio: cache first; each recording is saved the first time it's played.
const CACHE = "awal-v3";
const SHELL = [
  "./", "index.html", "app.js", "styles.css", "data/lessons.js",
  "manifest.webmanifest", "icons/logo-32.png", "icons/logo-96.png", "icons/app-192.png",
  "fonts/nunito-latin.woff2", "fonts/nunito-latin-ext.woff2"
];

self.addEventListener("install", event => {
  event.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", event => {
  const req = event.request;
  const url = new URL(req.url);
  if (req.method !== "GET" || url.origin !== location.origin) return;
  if (url.pathname.includes("/audio/")) event.respondWith(audio(req));
  else event.respondWith(shell(req));
});

async function shell(req) {
  const cache = await caches.open(CACHE);
  try {
    const res = await fetch(req);
    if (res.ok) cache.put(req, res.clone());
    return res;
  } catch (err) {
    const cached = await cache.match(req, { ignoreSearch: true });
    if (cached) return cached;
    throw err;
  }
}

async function audio(req) {
  const cache = await caches.open(CACHE);
  const key = req.url; // ignore the Range header for caching
  let res = await cache.match(key);
  if (!res) {
    res = await fetch(key);
    if (!res.ok) return res; // 404 = no recording yet; lets the player try the next format
    await cache.put(key, res.clone());
  }
  return withRange(req, res);
}

// Media players (especially Safari) ask for byte ranges; answer from the cached file.
async function withRange(req, res) {
  const range = req.headers.get("range");
  const m = range && /bytes=(\d*)-(\d*)/.exec(range);
  if (!m) return res;
  const buf = await res.arrayBuffer();
  const start = m[1] ? Number(m[1]) : 0;
  const end = m[2] ? Math.min(Number(m[2]), buf.byteLength - 1) : buf.byteLength - 1;
  return new Response(buf.slice(start, end + 1), {
    status: 206,
    headers: {
      "Content-Type": res.headers.get("Content-Type") || "application/octet-stream",
      "Content-Range": `bytes ${start}-${end}/${buf.byteLength}`,
      "Content-Length": String(end - start + 1),
      "Accept-Ranges": "bytes"
    }
  });
}
