export interface FeatureFlagsResponse {
  s3_enabled: boolean
  email_enabled: boolean
  cache_enabled: boolean
  scheduler_enabled: boolean
}

export interface S3ConfigResponse {
  enabled: boolean
  access_key_id?: string
  secret_access_key?: string
  bucket_name?: string
  region?: string
  endpoint_url?: string
}

export interface S3ConfigUpdate {
  enabled?: boolean
  access_key_id?: string
  secret_access_key?: string
  bucket_name?: string
  region?: string
  endpoint_url?: string
}

export interface EmailConfigResponse {
  enabled: boolean
  smtp_host?: string
  smtp_port?: number
  smtp_user?: string
  smtp_password?: string
  smtp_use_tls?: boolean
  from_address?: string
  to_addresses?: string[]
}

export interface EmailConfigUpdate {
  enabled?: boolean
  smtp_host?: string
  smtp_port?: number
  smtp_user?: string
  smtp_password?: string
  smtp_use_tls?: boolean
  from_address?: string
  to_addresses?: string[]
}

export interface TestResponse {
  success: boolean
  message: string
}

