import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { MessageSquare, Zap, BarChart3, Shield } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Hero Section */}
      <div className="container mx-auto px-6 py-20">
        <div className="text-center max-w-4xl mx-auto">
          <div className="flex items-center justify-center gap-2 mb-6">
            <MessageSquare className="h-12 w-12 text-blue-600" />
            <h1 className="text-5xl font-bold text-gray-900">QueryHub</h1>
          </div>
          
          <p className="text-2xl text-gray-600 mb-4">
            Unified Audience Query Management System
          </p>
          
          <p className="text-lg text-gray-500 mb-8 max-w-2xl mx-auto">
            Centralize all customer queries from email, social media, and chat.
            Powered by AI for intelligent categorization and routing.
          </p>
          
          <Link href="/dashboard">
            <Button size="lg" className="text-lg px-8 py-6">
              Go to Dashboard →
            </Button>
          </Link>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-4 gap-8 mt-20">
          <FeatureCard
            icon={<MessageSquare className="h-8 w-8" />}
            title="Multi-Channel Inbox"
            description="Email, chat, social media - all in one place"
          />
          <FeatureCard
            icon={<Zap className="h-8 w-8" />}
            title="AI Categorization"
            description="Automatic priority and category detection"
          />
          <FeatureCard
            icon={<BarChart3 className="h-8 w-8" />}
            title="Smart Routing"
            description="Load-balanced team assignment"
          />
          <FeatureCard
            icon={<Shield className="h-8 w-8" />}
            title="SLA Monitoring"
            description="Automatic escalation and alerts"
          />
        </div>

        {/* Stats */}
        <div className="mt-20 bg-white rounded-2xl shadow-xl p-12">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            Built for Hackathon Excellence
          </h2>
          <div className="grid md:grid-cols-3 gap-8 text-center">
            <div>
              <p className="text-4xl font-bold text-blue-600">4</p>
              <p className="text-gray-600 mt-2">Channels Unified</p>
            </div>
            <div>
              <p className="text-4xl font-bold text-blue-600">AI-Powered</p>
              <p className="text-gray-600 mt-2">Smart Categorization</p>
            </div>
            <div>
              <p className="text-4xl font-bold text-blue-600">Real-Time</p>
              <p className="text-gray-600 mt-2">Live Updates</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode
  title: string
  description: string
}) {
  return (
    <div className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow">
      <div className="text-blue-600 mb-4">{icon}</div>
      <h3 className="text-xl font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  )
}
