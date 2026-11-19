export async function listMovies(signal) {
  const response = await fetch('/api/movies', { signal })
  if (!response.ok) throw new Error('Could not load movies.')
  return response.json()
}
