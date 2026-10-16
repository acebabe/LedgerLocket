// Cloudflare Pages Function: VNS API (production-ready template)
// Features:
// - Bearer-token auth via API_KEYS KV binding (store token -> JSON metadata)
// - Per-user / admin authorization (role in key metadata)
// - KV-backed data: TRIALS and NUMBERS KV bindings
// - Strict validation for inputs
// - Idempotency support using IDEMPOTENCY KV binding for retry-safe writes
//
// Bindings required (configure in your Pages project or wrangler):
// - env.API_KEYS (KV namespace): token -> JSON metadata { role: 'user'|'admin', permissions: [...] }
// - env.TRIALS (KV namespace): keys like 'trial:<id>' -> JSON trial object
// - env.NUMBERS (KV namespace): single key 'numbers' -> JSON array of number objects
// - env.IDEMPOTENCY (KV namespace): 'ide:<key>' -> trialId
//
// NOTE: KV is eventually consistent and has limits. For higher write-safety and
// consistency consider Durable Objects. This template uses idempotency keys to
// make POST /api/trial retry-safe.

export const onRequest = async ({ request, env }) => {
  const url = new URL(request.url)
  const rawPath = url.pathname.replace(/\/+/g, '/')
  const path = rawPath.replace(/\/+$|^\/+/, '') // trim trailing and leading slashes
  const method = request.method.toUpperCase()

  const CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, Idempotency-Key'
  }

  const json = (obj, status = 200) => {
    return new Response(JSON.stringify(obj), {
      status,
      headers: Object.assign({ 'Content-Type': 'application/json' }, CORS_HEADERS)
    })
  }

  // Handle CORS preflight
  if (method === 'OPTIONS') return new Response(null, { status: 204, headers: CORS_HEADERS })

  // Helper: require KV bindings
  const requireBinding = (name) => {
    if (!env || !env[name]) {
      throw new Error(`Missing KV binding: ${name}. Configure it in your Pages project.`)
    }
  }

  try {
    // Validate configuration early
    requireBinding('API_KEYS')
    requireBinding('TRIALS')
    requireBinding('NUMBERS')
    requireBinding('IDEMPOTENCY')
  } catch (err) {
    console.error(err)
    return json({ error: 'server_misconfigured', message: String(err) }, 500)
  }

  // Auth: lookup token in API_KEYS KV
  const getAuth = async (req) => {
    const authHeader = req.headers.get('Authorization') || req.headers.get('authorization')
    if (!authHeader) return null
    const parts = authHeader.split(' ')
    if (parts.length !== 2 || parts[0].toLowerCase() !== 'bearer') return null
    const token = parts[1]
    try {
      const raw = await env.API_KEYS.get(token)
      if (!raw) return null
      return JSON.parse(raw)
    } catch (e) {
      console.error('API_KEYS.get error', e)
      return null
    }
  }

  const requireAuth = async (req) => {
    const user = await getAuth(req)
    if (!user) throw { status: 401, body: { error: 'unauthorized' } }
    return user
  }

  const requireAdmin = async (req) => {
    const user = await requireAuth(req)
    if (!user.role || user.role !== 'admin') throw { status: 403, body: { error: 'forbidden' } }
    return user
  }

  // Utility: simple email validation
  const isValidEmail = (s) => {
    if (!s || typeof s !== 'string') return false
    // basic RFC5322-ish check
    return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(s)
  }

  // Utility: seed numbers into NUMBERS KV if missing
  const ensureNumbersSeeded = async () => {
    try {
      const raw = await env.NUMBERS.get('numbers')
      if (raw) return JSON.parse(raw)
      const initial = [
        { id: 'US-1', country: 'US', number: '+1-555-0100', region: 'CA' },
        { id: 'US-2', country: 'US', number: '+1-555-0101', region: 'NY' },
        { id: 'GB-1', country: 'GB', number: '+44-20-5555-0100', region: 'London' },
        { id: 'DE-1', country: 'DE', number: '+49-30-5555-0100', region: 'Berlin' }
      ]
      await env.NUMBERS.put('numbers', JSON.stringify(initial))
      return initial
    } catch (e) {
      console.error('ensureNumbersSeeded error', e)
      throw e
    }
  }

  // Utility: generate UUID v4
  const uuidv4 = () => {
    // simple UUID generator for Workers
    const bytes = crypto.getRandomValues(new Uint8Array(16))
    bytes[6] = (bytes[6] & 0x0f) | 0x40
    bytes[8] = (bytes[8] & 0x3f) | 0x80
    const hex = [...bytes].map(b => b.toString(16).padStart(2, '0')).join('')
    return `${hex.slice(0,8)}-${hex.slice(8,12)}-${hex.slice(12,16)}-${hex.slice(16,20)}-${hex.slice(20)}`
  }

  try {
    // GET /api/numbers  (public)
    if (path === 'api/numbers' && method === 'GET') {
      try {
        const nums = await ensureNumbersSeeded()
        return json({ numbers: nums })
      } catch (e) {
        console.error('GET /api/numbers failed', e)
        return json({ error: 'internal' }, 500)
      }
    }

    // POST /api/trial  (authenticated users)
    if (path === 'api/trial' && method === 'POST') {
      let payload = {}
      try {
        payload = await request.json()
      } catch (e) {
        return json({ error: 'invalid_json' }, 400)
      }

      // Auth
      let user
      try {
        user = await requireAuth(request)
      } catch (authErr) {
        return json(authErr.body || { error: 'unauthorized' }, authErr.status || 401)
      }

      const { name, email, numberId } = payload || {}
      if (!name || typeof name !== 'string' || name.length > 200) {
        return json({ error: 'invalid_name' }, 400)
      }
      if (!isValidEmail(email) || email.length > 320) {
        return json({ error: 'invalid_email' }, 400)
      }
      if (!numberId || typeof numberId !== 'string') {
        return json({ error: 'invalid_numberId' }, 400)
      }

      // Verify number exists
      const numbersRaw = await env.NUMBERS.get('numbers')
      const numbers = numbersRaw ? JSON.parse(numbersRaw) : await ensureNumbersSeeded()
      const exists = numbers.some(n => n.id === numberId)
      if (!exists) return json({ error: 'number_not_found' }, 404)

      // Idempotency handling
      const ideKey = request.headers.get('Idempotency-Key') || request.headers.get('idempotency-key')
      if (ideKey) {
        try {
          const existing = await env.IDEMPOTENCY.get(`ide:${ideKey}`)
          if (existing) {
            const trialRaw = await env.TRIALS.get(`trial:${existing}`)
            if (trialRaw) return json({ trial: JSON.parse(trialRaw) }, 200)
            // If mapping exists but trial missing, continue to create new and overwrite mapping
          }
        } catch (e) {
          console.error('idempotency check failed', e)
          // continue; idempotency is best-effort
        }
      }

      // Create trial
      const id = uuidv4()
      const now = new Date().toISOString()
      const trial = {
        id,
        name,
        email,
        numberId,
        createdAt: now,
        approved: false,
        createdBy: user?.sub || user?.id || null
      }

      try {
        // Write trial
        await env.TRIALS.put(`trial:${id}`, JSON.stringify(trial))
        if (ideKey) {
          try {
            await env.IDEMPOTENCY.put(`ide:${ideKey}`, id)
          } catch (e) {
            console.error('idempotency put failed', e)
            // not fatal
          }
        }
      } catch (e) {
        console.error('writing trial failed', e)
        return json({ error: 'internal' }, 500)
      }

      return json({ trial }, 201)
    }

    // GET /api/admin/trials  (admin only)
    if (path === 'api/admin/trials' && method === 'GET') {
      try {
        await requireAdmin(request)
      } catch (authErr) {
        return json(authErr.body || { error: 'unauthorized' }, authErr.status || 401)
      }

      try {
        const list = await env.TRIALS.list({ prefix: 'trial:' })
        const keys = list.keys || []
        const values = await Promise.all(keys.map(k => env.TRIALS.get(k.name)))
        const trials = values.filter(Boolean).map(v => JSON.parse(v))
        return json({ trials })
      } catch (e) {
        console.error('listing trials failed', e)
        return json({ error: 'internal' }, 500)
      }
    }

    // POST /api/admin/approve  (admin only)
    if (path === 'api/admin/approve' && method === 'POST') {
      try {
        await requireAdmin(request)
      } catch (authErr) {
        return json(authErr.body || { error: 'unauthorized' }, authErr.status || 401)
      }

      let body = {}
      try {
        body = await request.json()
      } catch (e) {
        return json({ error: 'invalid_json' }, 400)
      }

      const { id } = body || {}
      if (!id || typeof id !== 'string') return json({ error: 'invalid_id' }, 400)

      try {
        const trialRaw = await env.TRIALS.get(`trial:${id}`)
        if (!trialRaw) return json({ error: 'not_found' }, 404)
        const trial = JSON.parse(trialRaw)
        if (trial.approved) return json({ trial }, 200)
        trial.approved = true
        trial.approvedAt = new Date().toISOString()
        await env.TRIALS.put(`trial:${id}`, JSON.stringify(trial))
        return json({ trial }, 200)
      } catch (e) {
        console.error('approving trial failed', e)
        return json({ error: 'internal' }, 500)
      }
    }

    // Unknown route
    return json({ error: 'not_found' }, 404)
  } catch (err) {
    console.error('Unhandled error', err)
    // If err is a controlled throw with shape {status, body}
    if (err && err.status && err.body) return json(err.body, err.status)
    return json({ error: 'internal', details: String(err) }, 500)
  }
}
