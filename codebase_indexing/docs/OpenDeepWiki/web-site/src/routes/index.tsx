
import { lazy, Suspense } from 'react'
import { Loader2 } from 'lucide-react'

// 懒加载页面组件
const HomePage = lazy(() => import('@/pages/home/index'))
const LoginPage = lazy(() => import('@/pages/auth/Login'))
const RegisterPage = lazy(() => import('@/pages/auth/RegisterPage'))
const SettingsPage = lazy(() => import('@/pages/SettingsPage'))
const AboutPage = lazy(() => import('@/pages/about/index'))
const ProfilePage = lazy(() => import('@/pages/profile/index'))
const RepositoryLayout = lazy(() => import('@/components/layout/RepositoryLayout/index'))
const RepositoryDetailPage = lazy(() => import('@/pages/repository/RepositoryDetailPage/index'))
const DocumentPage = lazy(() => import('@/pages/repository/DocumentPage/index'))
const MindMapPage = lazy(() => import('@/pages/repository/MindMapPage/index'))

// 管理员控制台组件
const AdminLayout = lazy(() => import('@/components/layout/AdminLayout/index'))
const AdminDashboard = lazy(() => import('@/pages/admin/index'))
const AdminUsers = lazy(() => import('@/pages/admin/UsersPage/index'))
const AdminRoles = lazy(() => import('@/pages/admin/RolesPage/index'))
const AdminRepositories = lazy(() => import('@/pages/admin/RepositoriesPage/index'))
const AdminRepositoryDetail = lazy(() => import('@/pages/admin/RepositoryDetailPage/index'))
const AdminSystemSettings = lazy(() => import('@/pages/admin/SystemSettingsPage/index'))

// 加载组件
const Loading = () => (
  <div className="flex items-center justify-center h-screen">
    <Loader2 className="h-8 w-8 animate-spin text-primary" />
  </div>
)

const routes = [
  {
    path: "/",
    element: (
      <Suspense fallback={<Loading />}>
        <HomePage />
      </Suspense>
    ),
  },
  {
    path: "/login",
    element: (
      <Suspense fallback={<Loading />}>
        <LoginPage />
      </Suspense>
    ),
  },
  {
    path: "/register",
    element: (
      <Suspense fallback={<Loading />}>
        <RegisterPage />
      </Suspense>
    ),
  },
  {
    path: "/settings",
    element: (
      <Suspense fallback={<Loading />}>
        <SettingsPage />
      </Suspense>
    ),
  },
  {
    path: "/about",
    element: (
      <Suspense fallback={<Loading />}>
        <AboutPage />
      </Suspense>
    ),
  },
  {
    path: "/profile",
    element: (
      <Suspense fallback={<Loading />}>
        <ProfilePage />
      </Suspense>
    ),
  },
  {
    path: "/:owner/:name",
    element: (
      <Suspense fallback={<Loading />}>
        <RepositoryLayout />
      </Suspense>
    ),
    children: [
      {
        index: true,
        element: (
          <Suspense fallback={<Loading />}>
            <RepositoryDetailPage />
          </Suspense>
        ),
      },
      {
        path: "mindmap",
        element: (
          <Suspense fallback={<Loading />}>
            <MindMapPage />
          </Suspense>
        ),
      },
      {
        path: "*",
        element: (
          <Suspense fallback={<Loading />}>
            <DocumentPage />
          </Suspense>
        ),
      },
    ]
  },
  {
    path: "/admin",
    element: (
      <Suspense fallback={<Loading />}>
        <AdminLayout />
      </Suspense>
    ),
    children: [
      {
        index: true,
        element: (
          <Suspense fallback={<Loading />}>
            <AdminDashboard />
          </Suspense>
        ),
      },
      {
        path: "users",
        element: (
          <Suspense fallback={<Loading />}>
            <AdminUsers />
          </Suspense>
        ),
      },
      {
        path: "roles",
        element: (
          <Suspense fallback={<Loading />}>
            <AdminRoles />
          </Suspense>
        ),
      },
      {
        path: "repositories",
        element: (
          <Suspense fallback={<Loading />}>
            <AdminRepositories />
          </Suspense>
        ),
      },
      {
        path: "repositories/:id",
        element: (
          <Suspense fallback={<Loading />}>
            <AdminRepositoryDetail />
          </Suspense>
        ),
      },
      {
        path: "settings",
        element: (
          <Suspense fallback={<Loading />}>
            <AdminSystemSettings />
          </Suspense>
        ),
      },
    ]
  },
]

export default routes