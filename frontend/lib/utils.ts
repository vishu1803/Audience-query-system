import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Format date helper
export function formatDate(date: string | Date): string {
  return new Date(date).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// Format relative time
export function formatRelativeTime(date: string | Date): string {
  const now = new Date()
  const then = new Date(date)
  const diffMs = now.getTime() - then.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  return `${diffDays}d ago`
}

// Priority colors
export function getPriorityColor(priority: string): string {
  const colors: Record<string, string> = {
    urgent: 'bg-red-500',
    high: 'bg-orange-500',
    medium: 'bg-blue-500',
    low: 'bg-gray-500',
  }
  return colors[priority.toLowerCase()] || 'bg-gray-500'
}

// Status colors
export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    new: 'bg-purple-500',
    assigned: 'bg-blue-500',
    in_progress: 'bg-yellow-500',
    resolved: 'bg-green-500',
    closed: 'bg-gray-500',
  }
  return colors[status.toLowerCase()] || 'bg-gray-500'
}

// Category colors
export function getCategoryColor(category: string): string {
  const colors: Record<string, string> = {
    question: 'bg-purple-500',
    request: 'bg-blue-500',
    complaint: 'bg-red-500',
    feedback: 'bg-green-500',
    bug_report: 'bg-orange-500',
    general: 'bg-gray-500',
  }
  return colors[category.toLowerCase()] || 'bg-gray-500'
}
