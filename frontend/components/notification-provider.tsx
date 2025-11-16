'use client'

import { useEffect, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { queriesApi } from '@/lib/api'
import { notificationService } from '@/lib/notifications'
import { Toaster } from 'sonner'

export function NotificationProvider({ children }: { children: React.ReactNode }) {
  const previousStatsRef = useRef<{ total: number; urgent: number } | null>(null)

  // Poll for stats every 10 seconds
  const { data: stats } = useQuery({
    queryKey: ['notification-stats'],
    queryFn: queriesApi.getStats,
    refetchInterval: 10000, // Check every 10 seconds
  })

  useEffect(() => {
    if (stats && previousStatsRef.current) {
      // Check for new queries
      notificationService.checkNewQueries(
        stats.total_queries,
        previousStatsRef.current.total
      )

      // Check for new urgent queries
      notificationService.checkUrgentQueries(
        stats.urgent,
        previousStatsRef.current.urgent
      )
    }

    if (stats) {
      previousStatsRef.current = {
        total: stats.total_queries,
        urgent: stats.urgent,
      }
    }
  }, [stats])

  return (
    <>
      <Toaster 
        position="top-right" 
        richColors 
        closeButton
        toastOptions={{
          style: {
            background: 'white',
          },
        }}
      />
      {children}
    </>
  )
}
