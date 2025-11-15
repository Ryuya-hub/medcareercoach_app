import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import Layout from '../../components/common/Layout';
import { clientsAPI, applicationsAPI, appointmentsAPI, resumesAPI } from '../../services/api';
import { Users, Briefcase, Calendar, FileText } from 'lucide-react';

const CoachDashboard = () => {
  const { data: clients } = useQuery({
    queryKey: ['clients'],
    queryFn: () => clientsAPI.getAll().then((res) => res.data),
  });

  const { data: applications } = useQuery({
    queryKey: ['applications'],
    queryFn: () => applicationsAPI.getAll().then((res) => res.data),
  });

  const { data: appointments } = useQuery({
    queryKey: ['appointments'],
    queryFn: () => appointmentsAPI.getAll().then((res) => res.data),
  });

  const { data: pendingResumes } = useQuery({
    queryKey: ['pendingResumes'],
    queryFn: () => resumesAPI.getPendingResumes().then((res) => res.data),
  });

  const stats = [
    {
      label: '総顧客数',
      value: clients?.length || 0,
      icon: Users,
      color: 'bg-blue-500',
      link: '/coach/clients',
    },
    {
      label: '応募中企業',
      value: applications?.filter((a) => a.status === '選考中').length || 0,
      icon: Briefcase,
      color: 'bg-green-500',
      link: '/applications',
    },
    {
      label: '今週の面談',
      value: appointments?.filter((a) => a.status !== 'キャンセル').length || 0,
      icon: Calendar,
      color: 'bg-purple-500',
      link: '/appointments',
    },
    {
      label: '添削待ち',
      value: pendingResumes?.length || 0,
      icon: FileText,
      color: 'bg-orange-500',
      link: '/coach/resumes/pending',
    },
  ];

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">ダッシュボード</h2>
          <p className="text-gray-600">コーチ管理画面</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat) => {
            const Icon = stat.icon;
            return (
              <Link
                key={stat.label}
                to={stat.link}
                className="card hover:shadow-md transition-shadow cursor-pointer"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">{stat.label}</p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">{stat.value}</p>
                  </div>
                  <div className={`${stat.color} p-3 rounded-lg`}>
                    <Icon className="text-white" size={24} />
                  </div>
                </div>
              </Link>
            );
          })}
        </div>

        {/* Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Upcoming Appointments */}
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">今週の面談予定</h3>
            <div className="space-y-3">
              {appointments?.slice(0, 5).map((appointment) => (
                <div
                  key={appointment.appointment_id}
                  className="p-3 bg-gray-50 rounded-md"
                >
                  <p className="font-medium">{appointment.client_name}</p>
                  <p className="text-sm text-gray-600">
                    {new Date(appointment.appointment_date).toLocaleString('ja-JP')}
                  </p>
                </div>
              ))}
              {!appointments || appointments.length === 0 && (
                <p className="text-gray-500 text-center py-4">面談予定はありません</p>
              )}
            </div>
          </div>

          {/* Pending Resumes */}
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">添削待ち職務経歴書</h3>
            <div className="space-y-3">
              {pendingResumes?.slice(0, 5).map((resume) => (
                <div
                  key={resume.resume_id}
                  className="p-3 bg-gray-50 rounded-md flex justify-between items-center"
                >
                  <div>
                    <p className="font-medium">{resume.full_name}</p>
                    <p className="text-sm text-gray-600">
                      提出日: {new Date(resume.submitted_at).toLocaleDateString('ja-JP')}
                    </p>
                  </div>
                  <Link
                    to={`/coach/resumes/pending`}
                    className="btn btn-primary text-sm"
                  >
                    添削する
                  </Link>
                </div>
              ))}
              {!pendingResumes || pendingResumes.length === 0 && (
                <p className="text-gray-500 text-center py-4">添削待ちはありません</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default CoachDashboard;
