import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import './index.css'
import App from './App.tsx'
import LandingPage from './pages/LandingPage.tsx'
import ImprintPage from './pages/ImprintPage.tsx'
import { LanguageProvider } from './i18n.tsx'

//router-configuration
const router = createBrowserRouter([
    {
        path: '/',
        element: <LandingPage />,
    },
    {
        path: '/app',
        element: <App />,
    },
    {
        path: '/impressum',
        element: <ImprintPage />,
    },
])

// root-rendering
createRoot(document.getElementById('root')!).render(
    <StrictMode>
        <LanguageProvider>
            <RouterProvider router={router} />
        </LanguageProvider>
    </StrictMode>,
)

