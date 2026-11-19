import { useState } from 'react'
import { createCinema, getQuote, listCinemas } from '../api.js'
import { CatalogStatus, useCatalog } from '../useCatalog.jsx'

export default function Booking() {
  const { items: cinemas, setItems, error, retry } = useCatalog(listCinemas)
  const [cinemaId, setCinemaId] = useState('')
  const [groupSize, setGroupSize] = useState('')
  const [quote, setQuote] = useState(null)
  const [busy, setBusy] = useState(false)
  const [quoteError, setQuoteError] = useState('')
  const [saving, setSaving] = useState(false)
  const [cinemaError, setCinemaError] = useState('')
  const [added, setAdded] = useState('')
  const selected = cinemas?.find(cinema => String(cinema.id) === cinemaId)

  function clearResult() {
    setQuote(null)
    setQuoteError('')
  }

  async function submitQuote(event) {
    event.preventDefault()
    clearResult()
    setBusy(true)
    try {
      setQuote(await getQuote(cinemaId, groupSize))
    } catch (error) {
      setQuoteError(error.message)
    } finally {
      setBusy(false)
    }
  }

  async function submitCinema(event) {
    event.preventDefault()
    setCinemaError('')
    setAdded('')
    const form = event.currentTarget
    const data = new FormData(form)
    const sizes = data.get('sizes').split(',').map(size => size.trim())
    if (sizes.some(size => !/^\d+$/.test(size))) {
      setCinemaError('Enter whole numbers separated by commas.')
      return
    }
    setSaving(true)
    try {
      const saved = await createCinema({ name: data.get('name'), bundle_sizes: sizes.map(Number) })
      setItems(items => [...items, saved])
      setCinemaId(String(saved.id))
      clearResult()
      form.reset()
      setAdded(saved.name + ' added.')
    } catch (error) {
      setCinemaError(error.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <>
      <div className="page-heading"><h1>Booking</h1><p>Find the fewest seat bundles that fit your watch party exactly.</p></div>
      {cinemas === null ? <CatalogStatus error={error} retry={retry} label="cinemas" /> : (
        <div className="layout booking-layout">
          <section className="panel" aria-labelledby="quote-form-heading">
            <h2 id="quote-form-heading">Get a quote</h2>
            {cinemas.length === 0 ? <p className="muted">Add a cinema below to get started.</p> :
              <form onSubmit={submitQuote}>
                <fieldset disabled={busy || saving}>
                  <div className="field"><label htmlFor="cinema">Cinema</label><select id="cinema" value={cinemaId} required onChange={event => {
                    setCinemaId(event.target.value)
                    clearResult()
                  }}>
                    <option value="">Select a cinema</option>
                    {cinemas.map(cinema => <option value={cinema.id} key={cinema.id}>{cinema.name}</option>)}
                  </select></div>
                  {selected && <p className="muted">Bundle sizes: {selected.bundle_sizes.join(', ')} seats</p>}
                  <label>Group size<input type="number" min="1" max="10000" required value={groupSize}
                    onChange={event => { setGroupSize(event.target.value); clearResult() }} /></label>
                  <button className="primary" disabled={!cinemaId || !groupSize}>{busy ? 'Calculating…' : 'Calculate bundles'}</button>
                </fieldset>
              </form>}
            {quoteError && <p className="message error" role="alert">{quoteError}</p>}
          </section>
          <section className="booking-result" aria-labelledby="result-heading">
            <div className="section-heading"><h2 id="result-heading">Quote result</h2></div>
            {busy ? <p className="empty" role="status">Calculating bundles…</p> : !quote ? (
              <p className="empty">Enter a group size to see your quote.</p>
            ) : !quote.possible ? (
              <div className="empty" role="status"><strong>Not possible</strong><p>These bundles can’t seat {groupSize} people exactly. Try a different group size or cinema.</p></div>
            ) : (
              <>
                <div className="progress-summary" role="status"><div>
                  <strong>{quote.bundle_count} {quote.bundle_count === 1 ? 'bundle' : 'bundles'}</strong><span>{groupSize} seats total</span>
                </div></div>
                <ul className="records">{quote.bundles.map(bundle => (
                  <li className="record" key={bundle.size}><strong>{bundle.size}-seat bundle</strong>
                    <span>Quantity {bundle.quantity}</span></li>
                ))}</ul>
              </>
            )}
          </section>
          <details className="panel" open={cinemas.length === 0 ? true : undefined}>
            <summary>Add a cinema</summary>
            <form onSubmit={submitCinema}>
              <fieldset disabled={saving || busy}>
                <label>Cinema name<input name="name" required /></label>
                <label>Bundle sizes<input name="sizes" placeholder="1, 3, 4" required aria-describedby="bundle-hint" /></label>
                <p className="muted" id="bundle-hint">Enter 1–10 different sizes, separated by commas.</p>
                {cinemaError && <p className="message error" role="alert">{cinemaError}</p>}
                <button className="primary">{saving ? 'Adding…' : 'Add cinema'}</button>
              </fieldset>
            </form>
            {added && <p className="notice" role="status">{added}</p>}
          </details>
        </div>
      )}
    </>
  )
}
