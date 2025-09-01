import type { LocationResult } from '../types/api'
import { CheckCircle, XCircle, Download } from 'lucide-react'
import { Button } from './ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'

interface ResultsTableProps {
  results: LocationResult[]
  onClear: () => void
}

export function ResultsTable({ results, onClear }: ResultsTableProps) {
  if (results.length === 0) return null

  const exportToCSV = () => {
    const headers = [
      'Location',
      'Latitude',
      'Longitude',
      'SA1_Code',
      'SA1_Name',
      'SA2_Code',
      'SA2_Name',
      'SA3_Code', 
      'SA3_Name',
      'SA4_Code',
      'SA4_Name',
      'GCCSA_Code',
      'GCCSA_Name',
      'State_Code',
      'State_Name',
      'IARE_Code',
      'IARE_Name',
      'Success',
      'Error'
    ]

    const csvContent = [
      headers.join(','),
      ...results.map(result => [
        `"${result.location}"`,
        result.latitude || '',
        result.longitude || '',
        result.sa1_code || '',
        `"${result.sa1_name || ''}"`,
        result.sa2_code || '',
        `"${result.sa2_name || ''}"`,
        result.sa3_code || '',
        `"${result.sa3_name || ''}"`,
        result.sa4_code || '',
        `"${result.sa4_name || ''}"`,
        result.gccsa_code || '',
        `"${result.gccsa_name || ''}"`,
        result.state_code || '',
        `"${result.state_name || ''}"`,
        result.iare_code || '',
        `"${result.iare_name || ''}"`,
        result.geocode_success,
        `"${result.error_message || ''}"`
      ].join(','))
    ].join('\\n')

    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `geocoding_results_${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    window.URL.revokeObjectURL(url)
  }

  const successCount = results.filter(r => r.geocode_success).length
  const failureCount = results.length - successCount

  return (
    <Card className="w-full max-w-7xl mx-auto">
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle>Geocoding Results</CardTitle>
            <CardDescription>
              {results.length} location(s) processed • 
              <span className="text-green-600 ml-1">{successCount} successful</span> • 
              <span className="text-red-600 ml-1">{failureCount} failed</span>
            </CardDescription>
          </div>
          <div className="flex space-x-2">
            <Button
              onClick={exportToCSV}
              variant="outline"
              size="sm"
              className="flex items-center"
            >
              <Download className="w-4 h-4 mr-1" />
              Export CSV
            </Button>
            <Button
              onClick={onClear}
              variant="outline"
              size="sm"
            >
              Clear Results
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>

        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr className="border-b">
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Location</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Latitude</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Longitude</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">SA1</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">SA2</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">SA3</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">SA4</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">IARE</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">State</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {results.map((result, index) => (
                <tr key={index} className={result.geocode_success ? '' : 'bg-red-50'}>
                  <td className="px-3 py-2 whitespace-nowrap">
                    {result.geocode_success ? (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    ) : (
                      <XCircle className="w-5 h-5 text-red-500" />
                    )}
                  </td>
                  <td className="px-3 py-2 text-sm font-medium max-w-xs truncate" title={result.location}>
                    {result.location}
                  </td>
                  <td className="px-3 py-2 text-sm text-gray-600">
                    {result.latitude?.toFixed(6) || '-'}
                  </td>
                  <td className="px-3 py-2 text-sm text-gray-600">
                    {result.longitude?.toFixed(6) || '-'}
                  </td>
                  <td className="px-3 py-2 text-sm text-gray-600" title={result.sa1_name || undefined}>
                    {result.sa1_code || '-'}
                  </td>
                  <td className="px-3 py-2 text-sm text-gray-600" title={result.sa2_name || undefined}>
                    {result.sa2_code || '-'}
                  </td>
                  <td className="px-3 py-2 text-sm text-gray-600" title={result.sa3_name || undefined}>
                    {result.sa3_code || '-'}
                  </td>
                  <td className="px-3 py-2 text-sm text-gray-600" title={result.sa4_name || undefined}>
                    {result.sa4_code || '-'}
                  </td>
                  <td className="px-3 py-2 text-sm text-gray-600" title={result.iare_name || undefined}>
                    {result.iare_code || '-'}
                  </td>
                  <td className="px-3 py-2 text-sm text-gray-600" title={result.state_name || undefined}>
                    {result.state_code || '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {results.some(r => r.error_message) && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
            <h3 className="text-lg font-medium text-red-600 mb-2">Errors</h3>
            <div className="space-y-1">
              {results
                .filter(r => r.error_message)
                .map((result, index) => (
                  <div key={index} className="text-sm text-red-600">
                    <strong>{result.location}:</strong> {result.error_message}
                  </div>
                ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}