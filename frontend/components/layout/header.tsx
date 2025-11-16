'use client'

import { useState } from 'react'
import { Bell, Search } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Badge } from '@/components/ui/badge'
import { useQuery } from '@tanstack/react-query'
import { queriesApi } from '@/lib/api'
import { formatRelativeTime } from '@/lib/utils'
import Link from 'next/link'

export function Header() {
  const { data: stats } = useQuery({
    queryKey: ['header-stats'],
    queryFn: queriesApi.getStats,
    refetchInterval: 10000,
  })

  const urgentCount = stats?.urgent || 0
  const unassignedCount = stats?.unassigned || 0
  const totalNotifications = urgentCount + unassignedCount

  return (
    <header className="flex h-16 items-center justify-between border-b bg-white px-6">
      {/* Search */}
      <div className="flex flex-1 items-center gap-4">
        <div className="relative w-96">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <Input
            placeholder="Search queries..."
            className="pl-10"
          />
        </div>
      </div>

      {/* Notifications */}
      <div className="flex items-center gap-4">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="relative">
              <Bell className="h-5 w-5" />
              {totalNotifications > 0 && (
                <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-xs text-white">
                  {totalNotifications}
                </span>
              )}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-80">
            <div className="p-4 border-b">
              <h3 className="font-semibold text-gray-900">Notifications</h3>
              <p className="text-sm text-gray-500">
                {totalNotifications} items need attention
              </p>
            </div>

            {urgentCount > 0 && (
              <Link href="/dashboard/inbox?priority=urgent">
                <DropdownMenuItem className="p-4 cursor-pointer">
                  <div className="flex items-start gap-3 w-full">
                    <div className="p-2 rounded-full bg-red-100">
                      <Bell className="h-4 w-4 text-red-600" />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">
                        {urgentCount} Urgent {urgentCount === 1 ? 'Query' : 'Queries'}
                      </p>
                      <p className="text-sm text-gray-500">
                        Requires immediate attention
                      </p>
                    </div>
                    <Badge variant="destructive">{urgentCount}</Badge>
                  </div>
                </DropdownMenuItem>
              </Link>
            )}

            {unassignedCount > 0 && (
              <Link href="/dashboard/inbox?status=new">
                <DropdownMenuItem className="p-4 cursor-pointer">
                  <div className="flex items-start gap-3 w-full">
                    <div className="p-2 rounded-full bg-orange-100">
                      <Bell className="h-4 w-4 text-orange-600" />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">
                        {unassignedCount} Unassigned {unassignedCount === 1 ? 'Query' : 'Queries'}
                      </p>
                      <p className="text-sm text-gray-500">
                        Awaiting assignment
                      </p>
                    </div>
                    <Badge variant="secondary">{unassignedCount}</Badge>
                  </div>
                </DropdownMenuItem>
              </Link>
            )}

            {totalNotifications === 0 && (
              <div className="p-8 text-center text-gray-500">
                <Bell className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No new notifications</p>
              </div>
            )}

            <div className="p-2 border-t">
              <Link href="/dashboard/inbox">
                <Button variant="ghost" className="w-full">
                  View All Queries
                </Button>
              </Link>
            </div>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  )
}
