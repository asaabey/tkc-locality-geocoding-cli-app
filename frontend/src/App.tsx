import { useState } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { LocationForm } from './components/LocationForm'
import { ResultsTable } from './components/ResultsTable'
import type { LocationResult } from './types/api'

const queryClient = new QueryClient()

function App() {
  const [results, setResults] = useState<LocationResult[]>([])

  const handleSingleResult = (result: LocationResult) => {
    setResults(prev => [result, ...prev])
  }

  const handleBatchResults = (newResults: LocationResult[]) => {
    setResults(prev => [...newResults, ...prev])
  }

  const handleClearResults = () => {
    setResults([])
  }

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="container mx-auto px-4 space-y-8">
          <LocationForm 
            onResult={handleSingleResult}
            onBatchResult={handleBatchResults}
          />
          <ResultsTable 
            results={results}
            onClear={handleClearResults}
          />
        </div>
      </div>
    </QueryClientProvider>
  )
}

export default App