import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import Layout from '../../components/common/Layout';
import { applicationsAPI, appointmentsAPI, resumesAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { Briefcase, Calendar, FileText, TrendingUp } from 'lucide-react';

const ClientDashboard = () => {
  const { user } = useAuth();

  const { data: applications } = useQuery({
    queryKey: ['applications'],
    queryFn: () => applicationsAPI.getAll().then((res) => res.data),
  });

  const { data: appointments } = useQuery({
    queryKey: ['appointments'],
    queryFn: () => appointmentsAPI.getAll().then((res) => res.data),
  });

  const { data: resumes } = useQuery({
    queryKey: ['client-resumes'],
    queryFn: () => resumesAPI.getMe().then((res) => res.data),
    enabled: !!user,
  });

  const stats = [
    {
      label: '応募中',
      value: applications?.filter((a) => a.status === '選考中').length || 0,
      icon: Briefcase,
      color: 'bg-blue-500',
    },
    {
      label: '内定',
      value: applications?.filter((a) => a.status === '内定').length || 0,
      icon: TrendingUp,
      color: 'bg-green-500',
    },
    {
      label: '今週の面談',
      value: appointments?.filter((a) => a.status !== 'キャンセル').length || 0,
      icon: Calendar,
      color: 'bg-purple-500',
    },
    {
      label: '職務経歴書',
      value: resumes && resumes.length > 0 ? '作成済み' : '未作成',
      icon: FileText,
      color: 'bg-orange-500',
    },
  ];

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">ダッシュボード</h2>
          <p className="text-gray-600">利用者ホーム画面</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat) => {
            const Icon = stat.icon;
            return (
              <div key={stat.label} className="card">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">{stat.label}</p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">{stat.value}</p>
                  </div>
                  <div className={`${stat.color} p-3 rounded-lg`}>
                    <Icon className="text-white" size={24} />
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Quick Actions */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">クイックアクション</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link
              to="/applications"
              className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors text-center"
            >
              <Briefcase className="mx-auto mb-2 text-gray-600" size={24} />
              <p className="font-medium">新規応募登録</p>
            </Link>
            <Link
              to="/appointments"
              className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors text-center"
            >
              <Calendar className="mx-auto mb-2 text-gray-600" size={24} />
              <p className="font-medium">面談予約</p>
            </Link>
            <Link
              to="/client/resume"
              className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors text-center"
            >
              <FileText className="mx-auto mb-2 text-gray-600" size={24} />
              <p className="font-medium">職務経歴書編集</p>
            </Link>
          </div>
        </div>

        {/* Recent Applications */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">最近の応募状況</h3>
          <div className="space-y-3">
            {applications?.slice(0, 5).map((app) => (
              <div
                key={app.application_id}
                className="p-3 bg-gray-50 rounded-md flex justify-between items-center"
              >
                <div>
                  <p className="font-medium">{app.company_name}</p>
                  <p className="text-sm text-gray-600">{app.selection_stage}</p>
                </div>
                <span
                  className={`badge ${
                    app.status === '選考中'
                      ? 'badge-primary'
                      : app.status === '内定'
                      ? 'badge-success'
                      : 'badge-danger'
                  }`}
                >
                  {app.status}
                </span>
              </div>
            ))}
            {!applications || applications.length === 0 && (
              <p className="text-gray-500 text-center py-4">応募企業はありません</p>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default ClientDashboard;
