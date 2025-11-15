'use client'

import { useQuery } from '@tanstack/react-query'
import { queriesApi, assignmentApi } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Inbox,
  Clock,
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  Users,
} from 'lucide-react'

export default function DashboardPage() {
  // Fetch dashboard stats
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: queriesApi.getStats,
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  const { data: assignmentStats, isLoading: assignmentLoading } = useQuery({
    queryKey: ['assignment-stats'],
    queryFn: assignmentApi.getStats,
    refetchInterval: 30000,
  })

  if (statsLoading || assignmentLoading) {
    return <DashboardSkeleton />
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 mt-1">
          Real-time overview of your query management system
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Queries"
          value={stats?.total_queries || 0}
          icon={<Inbox className="h-5 w-5" />}
          trend="+12% from last week"
          color="blue"
        />
        <StatCard
          title="Urgent"
          value={stats?.urgent || 0}
          icon={<AlertTriangle className="h-5 w-5" />}
          trend="Requires immediate attention"
          color="red"
        />
        <StatCard
          title="Unassigned"
          value={stats?.unassigned || 0}
          icon={<Users className="h-5 w-5" />}
          trend="Awaiting assignment"
          color="orange"
        />
        <StatCard
          title="Avg Response Time"
          value={`${(stats?.avg_response_time || 0).toFixed(1)}h`}
          icon={<Clock className="h-5 w-5" />}
          trend="-15% from last week"
          color="green"
        />
      </div>

      {/* Today's Activity */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Today's Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Queries Received</span>
                <span className="text-2xl font-bold text-gray-900">
                  {stats?.queries_today || 0}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">This Week</span>
                <span className="text-2xl font-bold text-gray-900">
                  {stats?.queries_this_week || 0}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Team Workload</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {assignmentStats?.by_team && Object.entries(assignmentStats.by_team).map(([team, count]) => (
                <div key={team} className="flex items-center justify-between">
                  <span className="text-sm capitalize text-gray-600">{team}</span>
                  <span className="text-lg font-semibold text-gray-900">{count}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Agent Workloads */}
      <Card>
        <CardHeader>
          <CardTitle>Agent Performance</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {assignmentStats?.agent_workloads?.map((agent) => (
              <div key={agent.agent_id} className="flex items-center gap-4">
                <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-semibold">
                  {agent.agent_name.charAt(0)}
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">
                    {agent.agent_name}
                  </p>
                  <p className="text-xs text-gray-500 capitalize">{agent.team}</p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-semibold text-gray-900">
                    {agent.active_tickets}
                  </p>
                  <p className="text-xs text-gray-500">active tickets</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Stat Card Component
function StatCard({
  title,
  value,
  icon,
  trend,
  color,
}: {
  title: string
  value: string | number
  icon: React.ReactNode
  trend: string
  color: 'blue' | 'red' | 'orange' | 'green'
}) {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    red: 'bg-red-100 text-red-600',
    orange: 'bg-orange-100 text-orange-600',
    green: 'bg-green-100 text-green-600',
  }

  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
            <p className="text-xs text-gray-500 mt-2">{trend}</p>
          </div>
          <div className={`p-3 rounded-full ${colorClasses[color]}`}>
            {icon}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

// Loading skeleton
function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      <Skeleton className="h-10 w-64" />
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <Skeleton key={i} className="h-32" />
        ))}
      </div>
    </div>
  )
}
