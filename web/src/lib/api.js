const API_BASE = import.meta.env.VITE_API_URL || '/api';

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  if (!response.ok) {
    let detail = `Erreur serveur (${response.status}).`;
    try {
      const body = await response.json();
      if (body.detail) {
        detail = typeof body.detail === 'string'
          ? body.detail
          : JSON.stringify(body.detail);
      }
    } catch {
      // Corps illisible : on garde le message par défaut
    }
    throw new Error(detail);
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
