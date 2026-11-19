import { useState } from 'react'
import { getPlan, listMovies } from '../api.js'
import { CatalogStatus, useCatalog } from '../useCatalog.jsx'

export default function RewatchPlan() {
  const { items: movies, error, retry } = useCatalog(listMovies)
  const [target, setTarget] = useState('')
  const [plan, setPlan] = useState(null)
  const [busy, setBusy] = useState(false)
  const [quoteError, setQuoteError] = useState('')

  async function submit(event) {
    event.preventDefault()
    setBusy(true)
    setQuoteError('')
    setPlan(null)
    try {
      setPlan(await getPlan(target))
    } catch (error) {
      setQuoteError(error.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <>
      <div className="page-heading"><h1>Rewatch Plan</h1><p>Choose a target movie to see what to watch, in order.</p></div>
      {movies === null ? <CatalogStatus error={error} retry={retry} label="movies" /> :
        movies.length === 0 ? <p className="empty">Your watchlist is empty. <a href="#movies">Add a movie</a> to make a plan.</p> : (
          <div className="layout">
            <section className="panel" aria-labelledby="target-heading">
              <h2 id="target-heading">Build a plan</h2>
              <form onSubmit={submit}>
                <fieldset disabled={busy}>
                  <div className="field"><label htmlFor="target">Target movie</label><select id="target" required value={target} onChange={event => {
                    setTarget(event.target.value)
                    setPlan(null)
                    setQuoteError('')
                  }}>
                    <option value="">Select a movie</option>
                    {movies.map(movie => <option key={movie.id} value={movie.id}>{movie.title}</option>)}
                  </select></div>
                  <button className="primary" disabled={!target}>{busy ? 'Building…' : 'Show rewatch order'}</button>
                </fieldset>
              </form>
              {quoteError && <p className="message error" role="alert">{quoteError}</p>}
            </section>
            <section aria-labelledby="order-heading">
              <div className="section-heading"><h2 id="order-heading">Viewing order</h2></div>
              {busy ? <p className="empty" role="status">Building your rewatch plan…</p> : !plan ? (
                <p className="empty">Your ordered list will appear here.</p>
              ) : (
                <>
                  <div className="progress-summary" role="status">
                    <div><strong>{plan.watched_count} of {plan.movies.length} watched</strong><span>{plan.remaining_runtime_minutes} min remaining</span></div>
                    {plan.movies.length > 0 && <progress aria-label="Movies watched" value={plan.watched_count} max={plan.movies.length} />}
                  </div>
                  {plan.movies.length === 0 ? <p className="empty">This movie has no prerequisites.</p> : (
                    <ol className="records ordered">{plan.movies.map((movie, index) => (
                      <li className="record" key={movie.id}>
                        <span className="order" aria-hidden="true">{index + 1}</span>
                        <div className="record-copy"><strong>{movie.title}</strong><small>{movie.release_year} · {movie.runtime_minutes} min</small></div>
                        <span className={movie.watched ? 'watched' : 'muted'}>{movie.watched ? 'Watched' : 'Unwatched'}</span>
                      </li>
                    ))}</ol>
                  )}
                </>
              )}
            </section>
          </div>
        )}
    </>
  )
}
