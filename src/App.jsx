import { Routes, Route } from 'react-router-dom'
import { lazy, Suspense } from 'react'
import Nav from './components/Nav'
import Footer from './components/Footer'

// Critical pages - load immediately
import Home from './pages/Home'
import ArticlePage from './pages/ArticlePage'

// Non-critical pages - lazy load
const ArticlesPage = lazy(() => import('./pages/ArticlesPage'))
const HizmetlerimizPage = lazy(() => import('./pages/HizmetlerimizPage'))
const EkibimizPage = lazy(() => import('./pages/EkibimizPage'))
const HesaplamaAraclariPage = lazy(() => import('./pages/HesaplamaAraclariPage'))
const InfazYatarPage = lazy(() => import('./pages/InfazYatarPage'))
const TazminatHesaplamaPage = lazy(() => import('./pages/TazminatHesaplamaPage'))
const MakalelerPage = lazy(() => import('./pages/MakalelerPage'))
const IletisimPage = lazy(() => import('./pages/IletisimPage'))
const MuvekkilPaneliPage = lazy(() => import('./pages/MuvekkilPaneliPage'))
const LogoShowcasePage = lazy(() => import('./pages/LogoShowcasePage'))

// Loading component
const PageLoader = () => (
  <div className="min-h-screen flex items-center justify-center">
    <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600"></div>
  </div>
)

function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <Nav />
      <main className="flex-grow">
        <Suspense fallback={<PageLoader />}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/hizmetlerimiz" element={<HizmetlerimizPage />} />
            <Route path="/ekibimiz" element={<EkibimizPage />} />
            <Route path="/hesaplama-araclari" element={<HesaplamaAraclariPage />} />
            <Route path="/hesaplama-araclari/infaz-yatar" element={<InfazYatarPage />} />
            <Route path="/hesaplama-araclari/tazminat-hesaplama" element={<TazminatHesaplamaPage />} />
            <Route path="/makaleler" element={<ArticlesPage />} />
            <Route path="/makaleler/:slug" element={<ArticlePage />} />
            <Route path="/makale/:slug" element={<ArticlePage />} />
            <Route path="/iletisim" element={<IletisimPage />} />
            <Route path="/muvekkil-paneli" element={<MuvekkilPaneliPage />} />
            <Route path="/logo-showcase" element={<LogoShowcasePage />} />
          </Routes>
        </Suspense>
      </main>
      <Footer />
    </div>
  )
}

export default App