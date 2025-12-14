import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  LayoutDashboard,
  Users,
  Briefcase,
  Calendar,
  FileText,
  LogOut,
  Home,
  UserCircle,
} from 'lucide-react';

const Layout = ({ children }) => {
  const { user, logout, isCoach } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const coachNav = [
    { path: '/coach/dashboard', label: 'ダッシュボード', icon: LayoutDashboard },
    { path: '/coach/profile', label: 'プロフィール', icon: UserCircle },
    { path: '/coach/clients', label: '顧客管理', icon: Users },
    { path: '/applications', label: '応募管理', icon: Briefcase },
    { path: '/coach/availability', label: '空き枠管理', icon: Calendar },
    { path: '/appointments', label: '面談予約', icon: Calendar },
    { path: '/coach/resumes/pending', label: '職務経歴書添削', icon: FileText },
  ];

  const clientNav = [
    { path: '/client/dashboard', label: 'ダッシュボード', icon: LayoutDashboard },
    { path: '/client/profile', label: 'プロフィール', icon: UserCircle },
    { path: '/applications', label: '応募管理', icon: Briefcase },
    { path: '/appointments', label: '面談予約', icon: Calendar },
    { path: '/client/resume', label: '職務経歴書', icon: FileText },
  ];

  const navItems = isCoach ? coachNav : clientNav;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-xl font-bold text-gray-900">
              medcareercoach
            </h1>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                {user?.email} ({isCoach ? 'コーチ' : '利用者'})
              </span>
              <button
                onClick={handleLogout}
                className="btn btn-secondary flex items-center space-x-2"
              >
                <LogOut size={16} />
                <span>ログアウト</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className="w-64 bg-white min-h-screen shadow-sm">
          <nav className="mt-4 px-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;

              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-3 px-4 py-3 rounded-md mb-1 transition-colors ${
                    isActive
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <Icon size={20} />
                  <span className="font-medium">{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-8">
          <div className="max-w-7xl mx-auto">{children}</div>
        </main>
      </div>
    </div>
  );
};

export default Layout;
