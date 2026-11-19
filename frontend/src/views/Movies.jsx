import { useRef, useState } from 'react'
import { listMovies, saveMovie } from '../api.js'
import { CatalogStatus, useCatalog } from '../useCatalog.jsx'

const blank = { title: '', release_year: '', runtime_minutes: '', prerequisite_ids: [] }

export default function Movies() {
  const { items: movies, setItems, error, retry } = useCatalog(listMovies)
  const [editing, setEditing] = useState(null)
  const [draft, setDraft] = useState(blank)
  const [saving, setSaving] = useState(false)
  const [toggling, setToggling] = useState(null)
  const [formError, setFormError] = useState('')
  const [listError, setListError] = useState('')
  const [notice, setNotice] = useState('')
  const titleInput = useRef(null)

  function update(key, value) {
    setDraft(draft => ({ ...draft, [key]: value }))
  }

  function startEdit(movie) {
    setEditing(movie.id)
    setDraft(movie)
    setFormError('')
    titleInput.current.focus()
  }

  function clearForm() {
    setEditing(null)
    setDraft(blank)
    setFormError('')
  }

  async function submit(event) {
    event.preventDefault()
    setSaving(true)
    setFormError('')
    setNotice('')
    try {
      const { title, release_year, runtime_minutes, prerequisite_ids } = draft
      const saved = await saveMovie({
        title, release_year: Number(release_year), runtime_minutes: Number(runtime_minutes), prerequisite_ids,
      }, editing)
      setItems(items => editing ? items.map(item => item.id === saved.id ? saved : item) : [...items, saved])
      setNotice(editing ? 'Movie updated.' : 'Movie added.')
      clearForm()
    } catch (error) {
      setFormError(error.message)
    } finally {
      setSaving(false)
    }
  }

  async function markWatched(movie, watched) {
    setToggling(movie.id)
    setListError('')
    try {
      const saved = await saveMovie({ watched }, movie.id)
      setItems(items => items.map(item => item.id === saved.id ? saved : item))
    } catch (error) {
      setListError(error.message)
    } finally {
      setToggling(null)
    }
  }

  const busy = saving || toggling !== null
  return (
    <>
      <div className="page-heading"><h1>Movies</h1><p>Build your MCU watchlist and set what comes first.</p></div>
      {movies === null ? <CatalogStatus error={error} retry={retry} label="movies" /> : (
        <div className="layout movies-layout">
          <section aria-labelledby="watchlist-title">
            <div className="section-heading"><h2 id="watchlist-title">Watchlist</h2><span>{movies.length} {movies.length === 1 ? 'movie' : 'movies'}</span></div>
            {listError && <p role="alert" className="message error">{listError}</p>}
            {movies.length === 0 ? <p className="empty">Your watchlist is empty. Add a movie to get started.</p> : (
              <ul className="records">
                {movies.map(movie => (
                  <li className="record movie-record" key={movie.id}>
                    <div className="record-copy">
                      <strong>{movie.title}</strong>
                      <small>{movie.release_year} · {movie.runtime_minutes} min · {movie.prerequisite_ids.length} {movie.prerequisite_ids.length === 1 ? 'prerequisite' : 'prerequisites'}</small>
                    </div>
                    <div className="row-actions">
                      <label className="check"><input type="checkbox" checked={movie.watched}
                        aria-label={'Watched: ' + movie.title} disabled={busy}
                        onChange={event => markWatched(movie, event.target.checked)} /> Watched</label>
                      <button type="button" className="quiet" onClick={() => startEdit(movie)} disabled={busy}
                        aria-label={'Edit ' + movie.title}>Edit</button>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </section>
          <section className="panel" aria-labelledby="movie-form-title">
            <h2 id="movie-form-title">{editing ? 'Edit movie' : 'Add movie'}</h2>
            <form onSubmit={submit}>
              <fieldset disabled={busy}>
                <label>Title<input ref={titleInput} required value={draft.title} onChange={event => update('title', event.target.value)} /></label>
                <div className="field-pair">
                  <label>Release year<input type="number" required min="1000" max="9999" value={draft.release_year} onChange={event => update('release_year', event.target.value)} /></label>
                  <label>Runtime (min)<input type="number" required min="1" max="300" value={draft.runtime_minutes} onChange={event => update('runtime_minutes', event.target.value)} /></label>
                </div>
                <fieldset className="prerequisites">
                  <legend>Prerequisites</legend>
                  {movies.filter(movie => movie.id !== editing).length ? (
                    <div className="checklist">{movies.filter(movie => movie.id !== editing).map(movie => (
                      <label className="check" key={movie.id}>
                        <input type="checkbox" checked={draft.prerequisite_ids.includes(movie.id)}
                          onChange={event => update('prerequisite_ids', event.target.checked
                            ? [...draft.prerequisite_ids, movie.id]
                            : draft.prerequisite_ids.filter(id => id !== movie.id))} />
                        <span>{movie.title}</span>
                      </label>
                    ))}</div>
                  ) : <p className="muted">Other movies will appear here.</p>}
                </fieldset>
                {formError && <p className="message error" role="alert">{formError}</p>}
                <div className="form-actions">
                  <button className="primary">{saving ? 'Saving…' : editing ? 'Save changes' : 'Add movie'}</button>
                  {editing && <button type="button" onClick={clearForm}>Cancel</button>}
                </div>
              </fieldset>
            </form>
            {notice && <p role="status" className="notice">{notice}</p>}
          </section>
        </div>
      )}
    </>
  )
}
