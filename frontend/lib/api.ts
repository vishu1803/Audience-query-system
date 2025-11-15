import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Types matching your backend
export interface Query {
  id: number
  channel: string
  sender_email?: string
  sender_name?: string
  subject: string
  content: string
  category?: string
  priority: string
  status: string
  tags: string[]
  assigned_to?: number
  received_at: string
  assigned_at?: string
  first_response_at?: string
  resolved_at?: string
  response_time?: number
  resolution_time?: number
}

export interface PaginatedQueries {
  total: number
  page: number
  page_size: number
  queries: Query[]
}

export interface DashboardStats {
  total_queries: number
  queries_today: number
  queries_this_week: number
  unassigned: number
  urgent: number
  avg_response_time: number
}

export interface AssignmentStats {
  unassigned: number
  by_team: Record<string, number>
  agent_workloads: Array<{
    agent_id: number
    agent_name: string
    team: string
    active_tickets: number
  }>
}

export interface CategoryAnalytics {
  categories: Array<{ category: string; count: number }>
  priorities: Array<{ priority: string; count: number }>
  statuses: Array<{ status: string; count: number }>
  top_tags: Array<{ tag: string; count: number }>
  avg_response_by_priority: Array<{
    priority: string
    avg_hours: number
  }>
}

// API functions
export const queriesApi = {
  // Get paginated queries
  getQueries: async (params: {
    page?: number
    page_size?: number
    status?: string
    priority?: string
    channel?: string
  }): Promise<PaginatedQueries> => {
    const { data } = await api.get('/api/queries', { params })
    return data
  },

  // Get single query
  getQuery: async (id: number): Promise<Query> => {
    const { data } = await api.get(`/api/queries/${id}`)
    return data
  },

  // Update query status
  updateStatus: async (id: number, status: string): Promise<Query> => {
    const { data } = await api.put(`/api/queries/${id}/status`, { status })
    return data
  },

  // Assign query
  assignQuery: async (id: number, assignedTo: number): Promise<Query> => {
    const { data } = await api.put(`/api/queries/${id}/assign`, {
      assigned_to: assignedTo,
    })
    return data
  },

  // Get dashboard stats
  getStats: async (): Promise<DashboardStats> => {
    const { data } = await api.get('/api/queries/stats/dashboard')
    return data
  },

  // Get category analytics
  getAnalytics: async (): Promise<CategoryAnalytics> => {
    const { data } = await api.get('/api/queries/analytics/categories')
    return data
  },
}

export const assignmentApi = {
  // Get assignment stats
  getStats: async (): Promise<AssignmentStats> => {
    const { data } = await api.get('/api/assignment/stats')
    return data
  },

  // Auto-assign query
  autoAssign: async (queryId: number): Promise<Query> => {
    const { data } = await api.post(`/api/assignment/auto-assign/${queryId}`)
    return data
  },

  // Batch assign
  batchAssign: async (limit: number = 50) => {
    const { data } = await api.post(`/api/assignment/batch-assign?limit=${limit}`)
    return data
  },
}
