import { Sidebar } from '@/components/layout/sidebar'
import { Header } from '@/components/layout/header'
import { NotificationProvider } from '@/components/notification-provider'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <NotificationProvider>
      <div className="flex h-screen bg-gray-50">
        <Sidebar />
        <div className="flex flex-1 flex-col overflow-hidden">
          <Header />
          <main className="flex-1 overflow-auto p-6">
            {children}
          </main>
        </div>
      </div>
    </NotificationProvider>
  )
}
