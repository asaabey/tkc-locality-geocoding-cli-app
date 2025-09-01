export interface LocationResult {
  location: string
  latitude: number | null
  longitude: number | null
  sa1_code: string | null
  sa1_name: string | null
  sa2_code: string | null
  sa2_name: string | null
  sa3_code: string | null
  sa3_name: string | null
  sa4_code: string | null
  sa4_name: string | null
  gccsa_code: string | null
  gccsa_name: string | null
  state_code: string | null
  state_name: string | null
  iare_code: string | null
  iare_name: string | null
  geocode_success: boolean
  error_message: string | null
}

export interface SingleLocationRequest {
  location: string
}

export interface BatchLocationRequest {
  locations: string[]
}

export interface SingleLocationResponse {
  result: LocationResult
}

export interface BatchLocationResponse {
  results: LocationResult[]
  total_processed: number
  successful_geocodes: number
  failed_geocodes: number
}

export interface HealthResponse {
  status: string
  version: string
  asgs_files_available: boolean
  nominatim_accessible: boolean
}