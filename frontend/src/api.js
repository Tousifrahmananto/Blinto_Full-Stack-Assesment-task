async function request(path, { method = 'GET', data, signal } = {}) {
  const response = await fetch('/api' + path, {
    method, signal,
    ...(data && { headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }),
  })
  const body = await response.json().catch(() => null)
  if (!response.ok) {
    throw new Error(body?.message ?? (Array.isArray(body?.detail) ? body.detail[0]?.msg : body?.detail)
      ?? 'The server could not complete the request. Please try again.')
  }
  return body
}

export const listMovies = signal => request('/movies', { signal })
export const saveMovie = (data, id) => id
  ? request('/movies/' + id, { method: 'PATCH', data })
  : request('/movies', { method: 'POST', data })
export const getPlan = id => request('/movies/' + id + '/rewatch-order')
export const listCinemas = signal => request('/cinemas', { signal })
export const createCinema = data => request('/cinemas', { method: 'POST', data })
export const getQuote = (id, groupSize) => request('/cinemas/' + id + '/booking?' + new URLSearchParams({ groupSize }))
