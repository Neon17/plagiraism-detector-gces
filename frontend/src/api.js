// One place that talks to the Django backend.
const BASE = '/api'

async function post(path, body, isForm) {
  const opts = { method: 'POST' }
  if (isForm) {
    opts.body = body
  } else {
    opts.headers = { 'Content-Type': 'application/json' }
    opts.body = JSON.stringify(body)
  }
  const res = await fetch(`${BASE}${path}`, opts)
  if (!res.ok) {
    let detail = 'Request failed'
    try {
      detail = (await res.json()).detail || detail
    } catch {
      /* ignore */
    }
    throw new Error(detail)
  }
  return res.json()
}

export async function compareDocuments(files, method = 'sbert') {
  const form = new FormData()
  for (const file of files) form.append('files', file)
  form.append('method', method)
  return post('/compare/', form, true)
}

// Check one document against the web. Accepts pasted text and optional URLs.
export async function checkWeb({ text, file, urls }) {
  if (file) {
    const form = new FormData()
    form.append('files', file)
    if (urls?.length) urls.forEach((u) => form.append('urls', u))
    return post('/check-web/', form, true)
  }
  return post('/check-web/', { texts: [{ name: 'pasted', text }], urls }, false)
}
