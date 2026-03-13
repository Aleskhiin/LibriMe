import './App.css'

function App() {
  return (
      <main className="min-h-screen p-8 bg-gray-50">
          <div className="mx-auto max-w-3xl">
              <h1 className="text-3xl font-bold tracking-tight">librime</h1>
              <p className="mt-2 text-gray-700">
                  React + TypeScript + Vite + Tailwind – Grundsetup steht.
              </p>
              <div className="mt-6 rounded-xl border bg-white p-6 shadow">
                  <img
                      src="/logoBig.png"
                      alt="librime Logo groß"
                      className="mx-auto h-40 w-auto"
                  />
                  <p className="text-sm text-gray-600">Hier entsteht dein Frontend.</p>
              </div>
          </div>
      </main>
  )
}

export default App
