'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { queriesApi, Query } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import { use } from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Mail,
  MessageSquare,
  Clock,
  User,
  Tag,
  ArrowLeft,
} from 'lucide-react'
import { formatDate, formatRelativeTime, getPriorityColor, getStatusColor, getCategoryColor } from '@/lib/utils'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

export default function QueryDetailPage({ params }: { params:Promise<{ id: string }>}) {
  const { id } = use(params)
  const queryId = parseInt(id)
  const router = useRouter()
  const queryClient = useQueryClient()
  const [response, setResponse] = useState('')

  // Fetch query details
  const { data: query, isLoading } = useQuery({
    queryKey: ['query', queryId],
    queryFn: () => queriesApi.getQuery(queryId),
    refetchInterval: 5000, // Refresh every 5 seconds
  })

  // Update status mutation
  const updateStatusMutation = useMutation({
    mutationFn: ({ status }: { status: string }) =>
      queriesApi.updateStatus(queryId, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['query', queryId] })
      queryClient.invalidateQueries({ queryKey: ['queries'] })
    },
  })

  const handleStatusChange = (status: string) => {
    updateStatusMutation.mutate({ status })
  }

  if (isLoading) {
    return <DetailSkeleton />
  }

  if (!query) {
    return (
      <div className="flex flex-col items-center justify-center h-full">
        <p className="text-gray-500">Query not found</p>
        <Button className="mt-4" onClick={() => router.back()}>
          Go Back
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Back button */}
      <Button variant="ghost" onClick={() => router.back()}>
        <ArrowLeft className="h-4 w-4 mr-2" />
        Back to Inbox
      </Button>

      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold text-gray-900">{query.subject}</h1>
          <div className="flex items-center gap-2">
            <Badge className={getPriorityColor(query.priority)}>
              {query.priority}
            </Badge>
            <Badge className={getCategoryColor(query.category || 'general')}>
              {query.category}
            </Badge>
            {query.tags.map((tag) => (
              <Badge key={tag} variant="outline">
                {tag}
              </Badge>
            ))}
          </div>
        </div>

        {/* Status selector */}
        <Select value={query.status} onValueChange={handleStatusChange}>
          <SelectTrigger className="w-[200px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="new">New</SelectItem>
            <SelectItem value="assigned">Assigned</SelectItem>
            <SelectItem value="in_progress">In Progress</SelectItem>
            <SelectItem value="resolved">Resolved</SelectItem>
            <SelectItem value="closed">Closed</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Main content - 2 columns */}
        <div className="col-span-2 space-y-6">
          {/* Query content */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center">
                    <User className="h-6 w-6 text-blue-600" />
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900">
                      {query.sender_name || 'Unknown Sender'}
                    </p>
                    <p className="text-sm text-gray-500">{query.sender_email}</p>
                  </div>
                </div>
                <div className="text-right text-sm text-gray-500">
                  {formatDate(query.received_at)}
                  <p className="text-xs">{formatRelativeTime(query.received_at)}</p>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="prose max-w-none">
                <p className="text-gray-700 whitespace-pre-wrap">{query.content}</p>
              </div>
            </CardContent>
          </Card>

          {/* Response section */}
          <Card>
            <CardHeader>
              <CardTitle>Send Response</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Textarea
                placeholder="Type your response here..."
                value={response}
                onChange={(e) => setResponse(e.target.value)}
                rows={6}
                className="resize-none"
              />
              <div className="flex gap-2">
                <Button 
                  onClick={() => {
                    // Handle send response
                    handleStatusChange('in_progress')
                    setResponse('')
                  }}
                  disabled={!response.trim()}
                >
                  Send Response
                </Button>
                <Button variant="outline">
                  Save as Draft
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar - 1 column */}
        <div className="space-y-6">
          {/* Query info */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Query Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm">
                  <MessageSquare className="h-4 w-4 text-gray-400" />
                  <span className="text-gray-600">Channel:</span>
                  <span className="font-medium capitalize">{query.channel}</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Clock className="h-4 w-4 text-gray-400" />
                  <span className="text-gray-600">Received:</span>
                  <span className="font-medium">
                    {formatRelativeTime(query.received_at)}
                  </span>
                </div>
                {query.assigned_at && (
                  <div className="flex items-center gap-2 text-sm">
                    <User className="h-4 w-4 text-gray-400" />
                    <span className="text-gray-600">Assigned:</span>
                    <span className="font-medium">
                      {formatRelativeTime(query.assigned_at)}
                    </span>
                  </div>
                )}
              </div>

              <div className="border-t pt-4">
                <p className="text-sm font-medium text-gray-600 mb-2">Status</p>
                <Badge className={getStatusColor(query.status)}>
                  {query.status.replace('_', ' ')}
                </Badge>
              </div>

              {query.response_time && (
                <div className="border-t pt-4">
                  <p className="text-sm font-medium text-gray-600 mb-1">
                    Response Time
                  </p>
                  <p className="text-2xl font-bold text-gray-900">
                    {query.response_time.toFixed(1)}h
                  </p>
                </div>
              )}

              {query.resolution_time && (
                <div className="border-t pt-4">
                  <p className="text-sm font-medium text-gray-600 mb-1">
                    Resolution Time
                  </p>
                  <p className="text-2xl font-bold text-gray-900">
                    {query.resolution_time.toFixed(1)}h
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button variant="outline" className="w-full justify-start">
                Reassign
              </Button>
              <Button variant="outline" className="w-full justify-start">
                Escalate
              </Button>
              <Button variant="outline" className="w-full justify-start">
                Add to Favorites
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

function DetailSkeleton() {
  return (
    <div className="space-y-6">
      <Skeleton className="h-10 w-32" />
      <Skeleton className="h-16 w-full" />
      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 space-y-6">
          <Skeleton className="h-64" />
          <Skeleton className="h-48" />
        </div>
        <div className="space-y-6">
          <Skeleton className="h-64" />
          <Skeleton className="h-32" />
        </div>
      </div>
    </div>
  )
}
