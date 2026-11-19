import { useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import Movies from './views/Movies.jsx'
import RewatchPlan from './views/RewatchPlan.jsx'
import Booking from './views/Booking.jsx'
import './styles.css'

const views = { movies: ['Movies', Movies], rewatch: ['Rewatch Plan', RewatchPlan], booking: ['Booking', Booking] }
const currentView = () => {
  const key = location.hash.slice(1)
  return Object.hasOwn(views, key) ? key : 'movies'
}

function App() {
  const [active, setActive] = useState(currentView)

  useEffect(() => {
    const update = () => setActive(currentView())
    window.addEventListener('hashchange', update)
    return () => window.removeEventListener('hashchange', update)
  }, [])

  const [, View] = views[active]
  return (
    <>
      <header className="site-header">
        <div className="shell header-inner">
          <a className="brand" href="#movies">Doomsday <span>Ready</span></a>
          <nav aria-label="Main navigation">
            {Object.entries(views).map(([key, [label]]) => (
              <a key={key} href={'#' + key} aria-current={active === key ? 'page' : undefined}>{label}</a>
            ))}
          </nav>
        </div>
      </header>
      <main className="shell"><View /></main>
    </>
  )
}

createRoot(document.getElementById('root')).render(<App />)
