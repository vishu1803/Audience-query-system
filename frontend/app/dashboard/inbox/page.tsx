'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { queriesApi } from '@/lib/api'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Mail,
  MessageSquare,
  Twitter,
  Instagram,
  Facebook,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react'
import Link from 'next/link'
import {
  formatRelativeTime,
  getPriorityColor,
  getStatusColor,
  getCategoryColor,
} from '@/lib/utils'

const CHANNEL_ICONS = {
  email: Mail,
  chat: MessageSquare,
  twitter: Twitter,
  instagram: Instagram,
  facebook: Facebook,
}

export default function InboxPage() {
  const [page, setPage] = useState(1)
  const [filters, setFilters] = useState({
    status: 'all',
    priority: 'all',
    channel: 'all',
  })
  const [lastUpdated, setLastUpdated] = useState(new Date())

  const { data, isLoading, refetch, isFetching } = useQuery({
    queryKey: ['queries', page, filters],
    queryFn: () =>
      queriesApi.getQueries({
        page,
        page_size: 20,
        ...(filters.status !== 'all' && { status: filters.status }),
        ...(filters.priority !== 'all' && { priority: filters.priority }),
        ...(filters.channel !== 'all' && { channel: filters.channel }),
      }),
    refetchInterval: 10000,
    onSuccess: () => setLastUpdated(new Date()),
  })

  const totalPages = Math.ceil((data?.total || 0) / 20)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Unified Inbox</h1>
          <p className="text-gray-500 mt-1">
            {data?.total || 0} total queries
            {isFetching && (
              <span className="ml-2 text-sm text-blue-600">• Refreshing...</span>
            )}
          </p>
        </div>

        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-500">
            Last updated: {formatRelativeTime(lastUpdated.toISOString())}
          </span>

          <Button onClick={() => refetch()} disabled={isFetching}>
            {isFetching ? 'Refreshing...' : 'Refresh'}
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card className="p-4">
        <div className="flex gap-4 flex-wrap">

          {/* Status Filter */}
          <Select
            value={filters.status}
            onValueChange={(value) => setFilters({ ...filters, status: value })}
          >
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="All Statuses" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Statuses</SelectItem>
              <SelectItem value="new">New</SelectItem>
              <SelectItem value="assigned">Assigned</SelectItem>
              <SelectItem value="in_progress">In Progress</SelectItem>
              <SelectItem value="resolved">Resolved</SelectItem>
            </SelectContent>
          </Select>

          {/* Priority Filter */}
          <Select
            value={filters.priority}
            onValueChange={(value) => setFilters({ ...filters, priority: value })}
          >
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="All Priorities" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Priorities</SelectItem>
              <SelectItem value="urgent">Urgent</SelectItem>
              <SelectItem value="high">High</SelectItem>
              <SelectItem value="medium">Medium</SelectItem>
              <SelectItem value="low">Low</SelectItem>
            </SelectContent>
          </Select>

          {/* Channel Filter */}
          <Select
            value={filters.channel}
            onValueChange={(value) => setFilters({ ...filters, channel: value })}
          >
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="All Channels" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Channels</SelectItem>
              <SelectItem value="email">Email</SelectItem>
              <SelectItem value="chat">Chat</SelectItem>
              <SelectItem value="twitter">Twitter</SelectItem>
              <SelectItem value="instagram">Instagram</SelectItem>
              <SelectItem value="facebook">Facebook</SelectItem>
            </SelectContent>
          </Select>

          {(filters.status !== 'all' ||
            filters.priority !== 'all' ||
            filters.channel !== 'all') && (
            <Button
              variant="outline"
              onClick={() =>
                setFilters({ status: 'all', priority: 'all', channel: 'all' })
              }
            >
              Clear Filters
            </Button>
          )}
        </div>
      </Card>

      {/* Table */}
      {isLoading ? (
        <TableSkeleton />
      ) : (
        <Card>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Channel</TableHead>
                <TableHead>Subject</TableHead>
                <TableHead>From</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Priority</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Received</TableHead>
              </TableRow>
            </TableHeader>

            <TableBody>
              {data?.queries?.map((query: any) => (
                <TableRow key={query.id} className="cursor-pointer hover:bg-gray-50">
                  <TableCell>
                    <Link href={`/dashboard/inbox/${query.id}`}>
                      <ChannelIcon channel={query.channel} />
                    </Link>
                  </TableCell>

                  <TableCell>
                    <Link
                      href={`/dashboard/inbox/${query.id}`}
                      className="hover:underline"
                    >
                      <div className="font-medium text-gray-900">{query.subject}</div>
                      <div className="text-sm text-gray-500 truncate max-w-md">
                        {query.content?.substring(0, 100)}...
                      </div>
                    </Link>
                  </TableCell>

                  <TableCell>
                    <div className="text-sm">
                      <div className="font-medium">{query.sender_name}</div>
                      <div className="text-gray-500">{query.sender_email}</div>
                    </div>
                  </TableCell>

                  <TableCell>
                    <Badge className={getCategoryColor(query.category || 'general')}>
                      {query.category}
                    </Badge>
                  </TableCell>

                  <TableCell>
                    <Badge className={getPriorityColor(query.priority)}>
                      {query.priority}
                    </Badge>
                  </TableCell>

                  <TableCell>
                    <Badge className={getStatusColor(query.status)}>
                      {query.status.replace('_', ' ')}
                    </Badge>
                  </TableCell>

                  <TableCell className="text-sm text-gray-500">
                    {formatRelativeTime(query.received_at)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          {/* Pagination */}
          <div className="flex items-center justify-between border-t p-4">
            <div className="text-sm text-gray-500">
              Showing {(page - 1) * 20 + 1} to{' '}
              {Math.min(page * 20, data?.total || 0)} of {data?.total || 0}
            </div>

            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                <ChevronLeft className="h-4 w-4" /> Previous
              </Button>

              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
              >
                Next <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}

/* Channel Icon */
function ChannelIcon({ channel }: { channel: string }) {
  const Icon = CHANNEL_ICONS[channel as keyof typeof CHANNEL_ICONS] || Mail
  return (
    <div className="flex items-center justify-center h-8 w-8 rounded-full bg-gray-100">
      <Icon className="h-4 w-4 text-gray-600" />
    </div>
  )
}

/* Skeleton Loader */
function TableSkeleton() {
  return (
    <Card>
      <div className="p-4 space-y-3">
        {[...Array(10)].map((_, i) => (
          <Skeleton key={i} className="h-16 w-full" />
        ))}
      </div>
    </Card>
  )
}
