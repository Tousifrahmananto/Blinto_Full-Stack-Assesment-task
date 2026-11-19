import { useEffect, useState } from 'react'

export function useCatalog(load) {
  const [items, setItems] = useState(null)
  const [error, setError] = useState('')
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    const controller = new AbortController()
    load(controller.signal).then(setItems).catch(error => {
      if (!controller.signal.aborted) setError(error.message)
    })
    return () => controller.abort()
  }, [load, attempt])

  function retry() {
    setError('')
    setAttempt(attempt => attempt + 1)
  }

  return { items, setItems, error, retry }
}

export function CatalogStatus({ error, retry, label }) {
  return error
    ? <div className="message error"><p role="alert">{error}</p><button onClick={retry}>Try again</button></div>
    : <p role="status">Loading {label}…</p>
}
