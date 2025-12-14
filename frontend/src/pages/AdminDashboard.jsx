import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const AdminDashboard = () => {
  const { user, isSuperAdmin } = useAuth();
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newUser, setNewUser] = useState({
    email: '',
    password: '',
    user_type: 'client',
    last_name: '',
    first_name: '',
    last_name_kana: '',
    first_name_kana: '',
    phone: ''
  });

  // 統括管理者でない場合はリダイレクト
  useEffect(() => {
    if (!isSuperAdmin) {
      toast.error('アクセス権限がありません');
      navigate('/dashboard');
    }
  }, [isSuperAdmin, navigate]);

  // ユーザーリスト取得
  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API_URL}/api/admin/users`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUsers(response.data);
    } catch (error) {
      toast.error('ユーザーリストの取得に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (userId, newStatus) => {
    try {
      const token = localStorage.getItem('access_token');
      await axios.patch(
        `${API_URL}/api/admin/users/${userId}/status`,
        { status: newStatus },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success('ステータスを変更しました');
      fetchUsers();
    } catch (error) {
      toast.error('ステータスの変更に失敗しました');
    }
  };

  const handleDeleteUser = async (userId, email) => {
    if (!window.confirm(`本当に ${email} を削除しますか？この操作は取り消せません。`)) {
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      await axios.delete(`${API_URL}/api/admin/users/${userId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('ユーザーを削除しました');
      fetchUsers();
    } catch (error) {
      toast.error('ユーザーの削除に失敗しました');
    }
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('access_token');
      await axios.post(
        `${API_URL}/api/admin/users`,
        newUser,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success('ユーザーを作成しました');
      setShowCreateModal(false);
      setNewUser({
        email: '',
        password: '',
        user_type: 'client',
        last_name: '',
        first_name: '',
        last_name_kana: '',
        first_name_kana: '',
        phone: ''
      });
      fetchUsers();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'ユーザーの作成に失敗しました');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">読み込み中...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white rounded-lg shadow p-4 md:p-6 mb-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
            <h1 className="text-2xl md:text-3xl font-bold mb-4 md:mb-0">ユーザー管理</h1>
            <button
              onClick={() => setShowCreateModal(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 w-full md:w-auto"
            >
              新規ユーザー作成
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">名前</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">メール</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">タイプ</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">ロール</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">ステータス</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {users.map((userItem) => (
                  <tr key={userItem.user_id}>
                    <td className="px-4 py-4 whitespace-nowrap text-sm">{userItem.name || '-'}</td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm">{userItem.email}</td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm">
                      <span className={`px-2 py-1 rounded text-xs ${
                        userItem.user_type === 'coach' ? 'bg-purple-100 text-purple-800' : 'bg-green-100 text-green-800'
                      }`}>
                        {userItem.user_type === 'coach' ? 'コーチ' : '利用者'}
                      </span>
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm">
                      <span className={`px-2 py-1 rounded text-xs ${
                        userItem.role === 'super_admin' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'
                      }`}>
                        {userItem.role === 'super_admin' ? '統括管理者' : userItem.role}
                      </span>
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm">
                      <select
                        value={userItem.status}
                        onChange={(e) => handleStatusChange(userItem.user_id, e.target.value)}
                        className="border rounded px-2 py-1 text-xs"
                        disabled={userItem.user_id === user.user_id}
                      >
                        <option value="active">有効</option>
                        <option value="inactive">無効</option>
                        <option value="suspended">停止</option>
                      </select>
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm">
                      <button
                        onClick={() => handleDeleteUser(userItem.user_id, userItem.email)}
                        disabled={userItem.user_id === user.user_id}
                        className="text-red-600 hover:text-red-800 disabled:text-gray-400 disabled:cursor-not-allowed"
                      >
                        削除
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* 新規ユーザー作成モーダル */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold mb-4">新規ユーザー作成</h2>
            <form onSubmit={handleCreateUser} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">メールアドレス *</label>
                <input
                  type="email"
                  required
                  value={newUser.email}
                  onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">パスワード *</label>
                <input
                  type="password"
                  required
                  value={newUser.password}
                  onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">ユーザータイプ *</label>
                <select
                  value={newUser.user_type}
                  onChange={(e) => setNewUser({ ...newUser, user_type: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                >
                  <option value="client">利用者</option>
                  <option value="coach">コーチ</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">姓 *</label>
                <input
                  type="text"
                  required
                  value={newUser.last_name}
                  onChange={(e) => setNewUser({ ...newUser, last_name: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">名 *</label>
                <input
                  type="text"
                  required
                  value={newUser.first_name}
                  onChange={(e) => setNewUser({ ...newUser, first_name: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">姓（カナ）</label>
                <input
                  type="text"
                  value={newUser.last_name_kana}
                  onChange={(e) => setNewUser({ ...newUser, last_name_kana: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">名（カナ）</label>
                <input
                  type="text"
                  value={newUser.first_name_kana}
                  onChange={(e) => setNewUser({ ...newUser, first_name_kana: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">電話番号</label>
                <input
                  type="tel"
                  value={newUser.phone}
                  onChange={(e) => setNewUser({ ...newUser, phone: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                />
              </div>
              <div className="flex gap-2 pt-4">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                >
                  作成
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 bg-gray-200 text-gray-800 px-4 py-2 rounded hover:bg-gray-300"
                >
                  キャンセル
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;
