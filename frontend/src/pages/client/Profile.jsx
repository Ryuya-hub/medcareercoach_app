import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Layout from '../../components/common/Layout';
import { clientsAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import toast from 'react-hot-toast';
import { User, Mail, Phone, Building } from 'lucide-react';

const ClientProfile = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const [formData, setFormData] = useState({
    last_name: '',
    first_name: '',
    last_name_kana: '',
    first_name_kana: '',
    email: '',
    phone: '',
    company_name: '',
    occupation: '',
  });

  // 利用者情報取得
  const { data: clientData } = useQuery({
    queryKey: ['client-profile', user?.user_id],
    queryFn: () => clientsAPI.getMe().then(res => res.data),
    enabled: !!user?.user_id,
  });

  // クライアントデータが取得されたらフォームに設定
  useEffect(() => {
    if (clientData) {
      setFormData({
        last_name: clientData.last_name || '',
        first_name: clientData.first_name || '',
        last_name_kana: clientData.last_name_kana || '',
        first_name_kana: clientData.first_name_kana || '',
        email: clientData.email || '',
        phone: clientData.phone || '',
        company_name: clientData.company_name || '',
        occupation: clientData.occupation || '',
      });
    }
  }, [clientData]);


  const updateMutation = useMutation({
    mutationFn: (data) => clientsAPI.update(clientData.client_id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['client-profile', user?.user_id]);
      toast.success('プロフィールを更新しました');
    },
    onError: (error) => {
      console.error('更新エラー:', error);
      toast.error(error.response?.data?.detail || '更新に失敗しました');
    },
  });

  const handleChange = (e) => {
    const { name, value } = e.target;

    // 電話番号の場合、ハイフンを自動削除
    if (name === 'phone') {
      const cleanedPhone = value.replace(/[^0-9]/g, '');
      setFormData({
        ...formData,
        [name]: cleanedPhone,
      });
    } else {
      setFormData({
        ...formData,
        [name]: value,
      });
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    updateMutation.mutate(formData);
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold">プロフィール設定</h2>
          <p className="text-gray-600">アカウント情報の確認・変更</p>
        </div>

        <div className="card">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label flex items-center space-x-2">
                  <User size={16} />
                  <span>姓（苗字） *</span>
                </label>
                <input
                  type="text"
                  name="last_name"
                  className="input"
                  value={formData.last_name}
                  onChange={handleChange}
                  placeholder="山田"
                  required
                />
              </div>

              <div>
                <label className="label">名 *</label>
                <input
                  type="text"
                  name="first_name"
                  className="input"
                  value={formData.first_name}
                  onChange={handleChange}
                  placeholder="太郎"
                  required
                />
              </div>

              <div>
                <label className="label">姓（ふりがな）</label>
                <input
                  type="text"
                  name="last_name_kana"
                  className="input"
                  value={formData.last_name_kana}
                  onChange={handleChange}
                  placeholder="やまだ"
                />
              </div>

              <div>
                <label className="label">名（ふりがな）</label>
                <input
                  type="text"
                  name="first_name_kana"
                  className="input"
                  value={formData.first_name_kana}
                  onChange={handleChange}
                  placeholder="たろう"
                />
              </div>

              <div>
                <label className="label flex items-center space-x-2">
                  <Mail size={16} />
                  <span>メールアドレス</span>
                </label>
                <input
                  type="email"
                  name="email"
                  className="input"
                  value={formData.email}
                  onChange={handleChange}
                  required
                />
              </div>

              <div>
                <label className="label flex items-center space-x-2">
                  <Phone size={16} />
                  <span>電話番号</span>
                </label>
                <input
                  type="tel"
                  name="phone"
                  className="input"
                  value={formData.phone}
                  onChange={handleChange}
                  placeholder="09012345678"
                  pattern="[0-9]*"
                  inputMode="numeric"
                />
                <p className="text-xs text-gray-500 mt-1">
                  ハイフンなしの数字のみで入力してください（自動的にハイフンは削除されます）
                </p>
              </div>

              <div>
                <label className="label flex items-center space-x-2">
                  <Building size={16} />
                  <span>現在の会社名</span>
                </label>
                <input
                  type="text"
                  name="company_name"
                  className="input"
                  value={formData.company_name}
                  onChange={handleChange}
                />
              </div>

              <div>
                <label className="label">職種</label>
                <input
                  type="text"
                  name="occupation"
                  className="input"
                  value={formData.occupation}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="flex justify-end">
              <button
                type="submit"
                className="btn btn-primary"
                disabled={updateMutation.isLoading}
              >
                {updateMutation.isLoading ? '更新中...' : '保存'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Layout>
  );
};

export default ClientProfile;
