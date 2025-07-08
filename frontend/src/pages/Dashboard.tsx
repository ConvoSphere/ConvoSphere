import { useGetDashboardStatsQuery } from '../services/apiSlice'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { useAppSelector } from '../hooks'

const DashboardPage = () => {
  const { data: stats, isLoading, error } = useGetDashboardStatsQuery()
  const { user } = useAppSelector((state) => state.auth)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-500">Failed to load dashboard data</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
        <p className="text-gray-600 dark:text-gray-300">
          Welcome back, {user?.username || 'User'}!
        </p>
      </div>

      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Total Conversations</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-indigo">{stats.total_conversations}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Total Messages</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-indigo">{stats.total_messages}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Active Assistants</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-indigo">{stats.active_assistants}</p>
            </CardContent>
          </Card>
        </div>
      )}

      {stats?.recent_activity && stats.recent_activity.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {stats.recent_activity.map((activity) => (
                <div key={activity.id} className="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-800 last:border-b-0">
                  <div>
                    <p className="font-medium">{activity.description}</p>
                    <p className="text-sm text-gray-500">{activity.type}</p>
                  </div>
                  <span className="text-sm text-gray-400">
                    {new Date(activity.created_at).toLocaleDateString()}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default DashboardPage
