'use client'

import { useQuery } from '@tanstack/react-query'
import { usersApi } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Users, Mail, Briefcase, Activity } from 'lucide-react'
import { Progress } from '@/components/ui/progress'

export default function TeamPage() {
  const { data: users, isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: usersApi.getUsers,
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  if (isLoading) {
    return <TeamSkeleton />
  }

  // Group users by team
  const usersByTeam = users?.reduce((acc, user) => {
    if (!acc[user.team]) {
      acc[user.team] = []
    }
    acc[user.team].push(user)
    return acc
  }, {} as Record<string, typeof users>) || {}

  // Calculate team stats
  const totalUsers = users?.length || 0
  const totalActiveTickets = users?.reduce((sum, user) => sum + user.active_tickets, 0) || 0
  const avgTicketsPerAgent = totalUsers > 0 ? (totalActiveTickets / totalUsers).toFixed(1) : 0

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Team Management</h1>
        <p className="text-gray-500 mt-1">
          Manage your support team and monitor workload distribution
        </p>
      </div>

      {/* Team Stats */}
      <div className="grid gap-6 md:grid-cols-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-full bg-blue-100">
                <Users className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Total Agents</p>
                <p className="text-2xl font-bold text-gray-900">{totalUsers}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-full bg-green-100">
                <Activity className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Active Tickets</p>
                <p className="text-2xl font-bold text-gray-900">{totalActiveTickets}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-full bg-purple-100">
                <Briefcase className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Avg per Agent</p>
                <p className="text-2xl font-bold text-gray-900">{avgTicketsPerAgent}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-full bg-orange-100">
                <Users className="h-6 w-6 text-orange-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Teams</p>
                <p className="text-2xl font-bold text-gray-900">
                  {Object.keys(usersByTeam).length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Teams */}
      {Object.entries(usersByTeam).map(([team, teamUsers]) => (
        <Card key={team}>
          <CardHeader>
            <CardTitle className="capitalize">{team} Team</CardTitle>
            <p className="text-sm text-gray-500">
              {teamUsers.length} {teamUsers.length === 1 ? 'member' : 'members'} • {' '}
              {teamUsers.reduce((sum, u) => sum + u.active_tickets, 0)} active tickets
            </p>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {teamUsers.map((user) => (
                <AgentCard key={user.id} user={user} />
              ))}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

function AgentCard({ user }: { user: any }) {
  // Calculate workload percentage (max 15 tickets = 100%)
  const workloadPercent = Math.min((user.active_tickets / 15) * 100, 100)
  
  // Get initials
  const initials = user.name
    .split(' ')
    .map((n: string) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)

  // Workload color
  const getWorkloadColor = () => {
    if (workloadPercent >= 80) return 'text-red-600'
    if (workloadPercent >= 60) return 'text-orange-600'
    if (workloadPercent >= 40) return 'text-yellow-600'
    return 'text-green-600'
  }

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardContent className="p-6">
        <div className="flex items-start gap-4">
          <Avatar className="h-12 w-12">
            <AvatarFallback className="bg-blue-100 text-blue-700 font-semibold">
              {initials}
            </AvatarFallback>
          </Avatar>
          
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="font-semibold text-gray-900 truncate">{user.name}</h3>
              {user.role === 'admin' && (
                <Badge variant="secondary" className="text-xs">Admin</Badge>
              )}
            </div>
            
            <div className="flex items-center gap-1 text-sm text-gray-500 mb-3">
              <Mail className="h-3 w-3" />
              <span className="truncate">{user.email}</span>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Active Tickets</span>
                <span className={`font-semibold ${getWorkloadColor()}`}>
                  {user.active_tickets}
                </span>
              </div>
              
              <div className="space-y-1">
                <Progress value={workloadPercent} className="h-2" />
                <p className="text-xs text-gray-500">
                  {workloadPercent.toFixed(0)}% capacity
                </p>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

function TeamSkeleton() {
  return (
    <div className="space-y-6">
      <Skeleton className="h-10 w-64" />
      <div className="grid gap-6 md:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <Skeleton key={i} className="h-32" />
        ))}
      </div>
      <Skeleton className="h-96" />
    </div>
  )
}
