'use client'

import { useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { AlertTriangle } from 'lucide-react'

export default function ErrorBoundary({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error('Error:', error)
  }, [error])

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <Card className="p-8 max-w-md">
        <div className="flex flex-col items-center text-center space-y-4">
          <AlertTriangle className="h-12 w-12 text-red-500" />
          <h2 className="text-2xl font-bold text-gray-900">
            Something went wrong!
          </h2>
          <p className="text-gray-600">
            {error.message || 'An unexpected error occurred'}
          </p>
          <Button onClick={reset}>Try Again</Button>
        </div>
      </Card>
    </div>
  )
}
