import React from 'react';
import { useQuery } from '@tanstack/react-query';
import Layout from '../../components/common/Layout';
import { clientsAPI } from '../../services/api';

const ClientList = () => {
  const { data: clients, isLoading } = useQuery({
    queryKey: ['clients'],
    queryFn: () => clientsAPI.getAll().then((res) => res.data),
  });

  if (isLoading) {
    return (
      <Layout>
        <div className="text-center py-12">読み込み中...</div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold">顧客管理</h2>
        </div>

        <div className="card">
          <table className="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  氏名
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  メールアドレス
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  職種
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  契約日
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  契約終了日
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  ステータス
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {clients?.map((client) => {
                const contractDate = new Date(client.created_at);
                const contractEndDate = new Date(contractDate);
                contractEndDate.setMonth(contractEndDate.getMonth() + 3);

                return (
                  <tr key={client.client_id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {client.last_name && client.first_name
                        ? `${client.last_name} ${client.first_name}`
                        : client.name || '名前未設定'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">{client.email}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{client.occupation || '-'}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {contractDate.toLocaleDateString('ja-JP')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {contractEndDate.toLocaleDateString('ja-JP')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`badge ${
                        client.status === 'active' ? 'badge-success' : 'badge-danger'
                      }`}>
                        {client.status}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </Layout>
  );
};

export default ClientList;
