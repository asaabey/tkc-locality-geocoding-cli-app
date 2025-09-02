import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { geocodeApi } from '../lib/api'
import type { LocationResult, SingleLocationResponse, BatchLocationResponse } from '../types/api'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Textarea } from './ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'

interface LocationFormProps {
  onResult: (result: LocationResult) => void
  onBatchResult: (results: LocationResult[]) => void
}

export function LocationForm({ onResult, onBatchResult }: LocationFormProps) {
  const [singleLocation, setSingleLocation] = useState('')
  const [batchLocations, setBatchLocations] = useState('')
  const [mode, setMode] = useState<'single' | 'batch'>('single')

  const singleMutation = useMutation<SingleLocationResponse, Error, string>({
    mutationFn: (location: string) => geocodeApi.geocodeSingle(location),
    onSuccess: (data: SingleLocationResponse) => {
      onResult(data.result)
      setSingleLocation('')
    },
  })

  const batchMutation = useMutation<BatchLocationResponse, Error, string[]>({
    mutationFn: (locations: string[]) => geocodeApi.geocodeBatch(locations),
    onSuccess: (data: BatchLocationResponse) => {
      onBatchResult(data.results)
      setBatchLocations('')
    },
  })

  const handleSingleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (singleLocation.trim()) {
      singleMutation.mutate(singleLocation.trim())
    }
  }

  const handleBatchSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (batchLocations.trim()) {
      const locations = batchLocations
        .split('\n')
        .map(loc => loc.trim())
        .filter(loc => loc.length > 0)

      if (locations.length > 0) {
        batchMutation.mutate(locations)
      }
    }
  }

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>CHC Location Geocoder</CardTitle>
        <CardDescription>
          Enter location(s) to get coordinates and ABS statistical area classifications
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex space-x-2">
          <Button
            type="button"
            onClick={() => setMode('single')}
            variant={mode === 'single' ? 'default' : 'outline'}
            size="sm"
          >
            Single Location
          </Button>
          <Button
            type="button"
            onClick={() => setMode('batch')}
            variant={mode === 'batch' ? 'default' : 'outline'}
            size="sm"
          >
            Multiple Locations
          </Button>
        </div>

        {mode === 'single' ? (
          <form onSubmit={handleSingleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="location" className="text-sm font-medium">
                Location
              </label>
              <Input
                type="text"
                id="location"
                value={singleLocation}
                onChange={(e) => setSingleLocation(e.target.value)}
                placeholder="e.g., Alice Springs Hospital, NT"
                disabled={singleMutation.isPending}
              />
            </div>
            <Button
              type="submit"
              disabled={!singleLocation.trim() || singleMutation.isPending}
              className="w-full"
            >
              {singleMutation.isPending ? 'Geocoding...' : 'Geocode Location'}
            </Button>
          </form>
        ) : (
          <form onSubmit={handleBatchSubmit} className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="locations" className="text-sm font-medium">
                Locations (one per line)
              </label>
              <Textarea
                id="locations"
                value={batchLocations}
                onChange={(e) => setBatchLocations(e.target.value)}
                placeholder="Alice Springs Hospital, NT&#10;Darwin Hospital, NT&#10;Katherine Hospital, NT"
                rows={6}
                disabled={batchMutation.isPending}
              />
            </div>
            <Button
              type="submit"
              disabled={!batchLocations.trim() || batchMutation.isPending}
              className="w-full"
            >
              {batchMutation.isPending ? 'Processing...' : 'Geocode Locations'}
            </Button>
          </form>
        )}

        {(singleMutation.error || batchMutation.error) && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-600 text-sm">
              Error: {singleMutation.error?.message || batchMutation.error?.message}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}