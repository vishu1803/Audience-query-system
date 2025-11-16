import { toast } from 'sonner'

export type NotificationType = 'new_query' | 'urgent_query' | 'assigned' | 'status_changed'

export interface Notification {
  id: string
  type: NotificationType
  title: string
  message: string
  timestamp: Date
  queryId?: number
}

class NotificationService {
  private lastCheckTime: Date = new Date()
  private seenQueryIds: Set<number> = new Set()

  async checkNewQueries(currentTotal: number, previousTotal: number) {
    if (currentTotal > previousTotal) {
      const diff = currentTotal - previousTotal
      toast.success(`${diff} new ${diff === 1 ? 'query' : 'queries'} received`, {
        description: 'Check your inbox for new items',
        duration: 5000,
      })
    }
  }

  async checkUrgentQueries(urgentCount: number, previousUrgent: number) {
    if (urgentCount > previousUrgent) {
      const diff = urgentCount - previousUrgent
      toast.error(`${diff} urgent ${diff === 1 ? 'query' : 'queries'} need attention!`, {
        description: 'These queries require immediate response',
        duration: 10000,
        action: {
          label: 'View',
          onClick: () => window.location.href = '/dashboard/inbox?priority=urgent',
        },
      })
    }
  }

  notifyQueryAssigned(queryId: number, agentName: string) {
    toast.info('Query assigned', {
      description: `Query #${queryId} assigned to ${agentName}`,
      duration: 5000,
    })
  }

  notifyStatusChanged(queryId: number, oldStatus: string, newStatus: string) {
    toast.success('Status updated', {
      description: `Query #${queryId}: ${oldStatus} → ${newStatus}`,
      duration: 5000,
    })
  }

  notifyError(message: string) {
    toast.error('Error', {
      description: message,
      duration: 5000,
    })
  }
}

export const notificationService = new NotificationService()
