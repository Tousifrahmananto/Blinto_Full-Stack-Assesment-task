import { useEffect, useState } from 'react'
import { listMovies } from '../api.js'

export default function Movies() {
  const [movies, setMovies] = useState(null)
  const [error, setError] = useState(false)

  useEffect(() => {
    const controller = new AbortController()
    listMovies(controller.signal).then(setMovies).catch(() => {
      if (!controller.signal.aborted) setError(true)
    })
    return () => controller.abort()
  }, [])

  return (
    <>
      <h1>Doomsday Ready</h1>
      <h2>Movies</h2>
      {error ? <p role="alert">Could not load movies.</p> :
        movies === null ? <p role="status">Loading movies…</p> :
        movies.length === 0 ? <p>No movies yet.</p> :
        <ul>{movies.map(movie => (
          <li key={movie.id}>{movie.title} ({movie.release_year})</li>
        ))}</ul>}
    </>
  )
}
