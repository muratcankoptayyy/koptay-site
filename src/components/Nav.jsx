import { useState, useEffect } from "react"
import { Link, useLocation } from "react-router-dom"
import { Menu, X } from "lucide-react"
import KoptayLogoExecutive from "../assets/logos/KoptayLogo6-Executive"

const Nav = () => {
  const [isOpen, setIsOpen] = useState(false)
  const [isScrolled, setIsScrolled] = useState(false)
  const location = useLocation()

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50)
    }
    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  const toggleMenu = () => {
    setIsOpen(!isOpen)
  }

  const closeMenu = () => {
    setIsOpen(false)
  }

  const navLinks = [
    { name: "Ana Sayfa", href: "/" },
    { name: "Hizmetler", href: "/hizmetlerimiz" },
    { name: "Ekibimiz", href: "/ekibimiz" },
    { name: "Hesaplama Araçları", href: "/hesaplama-araclari" },
    { name: "Makaleler", href: "/makaleler" },
    { name: "Müvekkil Paneli", href: "/muvekkil-paneli" },
    { name: "İletişim", href: "/iletisim" }
  ]

  // Hesaplama araçları sayfalarında her zaman dark mode
  const isCalculatorPage = location.pathname.startsWith('/hesaplama-araclari')
  const shouldUseDarkMode = isScrolled || isCalculatorPage

  return (
    <header className={`fixed w-full z-50 transition-all duration-300 ${
      shouldUseDarkMode 
        ? "bg-white border-b-2 border-lawSecondary py-2" 
        : "bg-transparent py-4"
    }`}>
      <div className="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center gap-4">
          <Link 
            to="/" 
            className="flex items-center"
            onClick={closeMenu}
          >
            <KoptayLogoExecutive className="h-12 md:h-14 w-auto" />
          </Link>

          <nav className="hidden lg:flex space-x-4 xl:space-x-6">
            {navLinks.map((link) => (
              <Link
                key={link.name}
                to={link.href}
                className={`text-sm xl:text-base font-medium uppercase tracking-wide transition-colors duration-300 whitespace-nowrap ${
                  shouldUseDarkMode 
                    ? "text-lawDark hover:text-lawSecondary" 
                    : "text-white/80 hover:text-white"
                } ${
                  location.pathname === link.href ? "text-lawSecondary" : ""
                }`}
                onClick={closeMenu}
              >
                {link.name}
              </Link>
            ))}
          </nav>

          <Link 
            to="/iletisim"
            className={`hidden lg:block px-4 xl:px-6 py-3 text-sm xl:text-base font-medium uppercase transition-all duration-300 whitespace-nowrap ${
              shouldUseDarkMode 
                ? "bg-lawPrimary text-white hover:bg-lawSecondary" 
                : "bg-lawSecondary text-white hover:bg-lawPrimary"
            }`}
          >
            Ücretsiz Görüşme
          </Link>

          <button
            onClick={toggleMenu}
            className={`lg:hidden p-2 border-2 transition-colors duration-300 ${
              shouldUseDarkMode 
                ? "border-lawDark text-lawDark hover:bg-lawDark hover:text-white" 
                : "border-white text-white hover:bg-white hover:text-lawPrimary"
            }`}
          >
            {isOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {isOpen && (
          <div className="lg:hidden mt-4">
            <div className="bg-lawDark/95 backdrop-blur-sm rounded-lg p-6">
              {navLinks.map((link) => (
                <Link
                  key={link.name}
                  to={link.href}
                  onClick={closeMenu}
                  className={`block w-full text-left py-3 px-4 text-lg font-medium uppercase tracking-wide hover:text-lawSecondary transition-colors duration-300 border-b border-white/20 last:border-b-0 ${
                    location.pathname === link.href ? "text-lawSecondary" : "text-white"
                  }`}
                >
                  {link.name}
                </Link>
              ))}
              <Link 
                to="/iletisim"
                onClick={closeMenu}
                className="block w-full text-center bg-lawSecondary text-white px-6 py-3 font-medium uppercase transition-colors duration-300 hover:bg-lawPrimary mt-4 rounded"
              >
                Ücretsiz Görüşme
              </Link>
            </div>
          </div>
        )}
      </div>
    </header>
  )
}

export default Nav
