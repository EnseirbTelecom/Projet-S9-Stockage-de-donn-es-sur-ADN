const API_BASE = import.meta.env.VITE_API_URL || '/api';

async function extractDetail(response) {
  try {
    const body = await response.json();
    if (body.detail) {
      return typeof body.detail === 'string'
        ? body.detail
        : JSON.stringify(body.detail);
    }
  } catch {
    // Corps illisible : on garde le message par défaut
  }
  return `Erreur serveur (${response.status}).`;
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  if (!response.ok) {
    throw new Error(await extractDetail(response));
  }

  return response.json();
}

export function fetchCatalog() {
  return request('/catalog');
}

export function runTransmission({
  message,
  useProtection,
  seed,
  encoder,
  decoder,
  channel,
  channelParameters = {},
  protection,
}) {
  const body = {
    message,
    use_protection: useProtection,
    ...channelParameters,
  };

  if (encoder) body.encoder = encoder;
  if (decoder) body.decoder = decoder;
  if (channel) body.channel = channel;
  if (useProtection && protection) body.protection = protection;

  if (seed !== '' && seed !== null && seed !== undefined && !Number.isNaN(Number(seed))) {
    body.seed = Number(seed);
  }

  return request('/communication/run', {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

// Import d'un fichier : le corps est un FormData (multipart), on laisse le
// navigateur générer l'en-tête Content-Type avec la boundary.
export async function importDnaFile(file, { encoder, protection, seed } = {}) {
  const form = new FormData();
  form.append('file', file);

  const params = new URLSearchParams();
  if (encoder) params.set('encoder', encoder);
  if (protection) params.set('protection', protection);
  if (seed !== '' && seed !== null && seed !== undefined && !Number.isNaN(Number(seed))) {
    params.set('seed', String(Number(seed)));
  }

  const query = params.toString() ? `?${params.toString()}` : '';
  const response = await fetch(`${API_BASE}/files/import${query}`, {
    method: 'POST',
    body: form,
  });

  if (!response.ok) {
    throw new Error(await extractDetail(response));
  }

  return response.json();
}

export function fetchDnaFiles() {
  return request('/files');
}

export function dnaFileDownloadUrl(id) {
  return `${API_BASE}/files/${id}/download`;
}
