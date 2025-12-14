import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Layout from '../../components/common/Layout';
import { coachesAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import toast from 'react-hot-toast';
import { User, Mail, Phone, Video } from 'lucide-react';

const CoachProfile = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const [formData, setFormData] = useState({
    last_name: '',
    first_name: '',
    last_name_kana: '',
    first_name_kana: '',
    email: '',
    phone: '',
    mtg_url: '',
  });

  // コーチ情報取得
  const { data: coachData } = useQuery({
    queryKey: ['coach-profile'],
    queryFn: () => coachesAPI.getMe().then(res => res.data),
    enabled: !!user,
  });

  // コーチデータが取得されたらフォームに設定
  useEffect(() => {
    if (coachData) {
      setFormData({
        last_name: coachData.last_name || '',
        first_name: coachData.first_name || '',
        last_name_kana: coachData.last_name_kana || '',
        first_name_kana: coachData.first_name_kana || '',
        email: coachData.email || '',
        phone: coachData.phone || '',
        mtg_url: coachData.mtg_url || '',
      });
    }
  }, [coachData]);

  const updateMutation = useMutation({
    mutationFn: (data) => coachesAPI.update(coachData.coach_id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['coach-profile']);
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
          <p className="text-gray-600">コーチアカウント情報の確認・変更</p>
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
            </div>

            <div>
              <label className="label flex items-center space-x-2">
                <Video size={16} />
                <span>オンライン面談URL</span>
              </label>
              <input
                type="url"
                name="mtg_url"
                className="input"
                value={formData.mtg_url}
                onChange={handleChange}
                placeholder="https://zoom.us/j/..."
              />
              <p className="text-xs text-gray-500 mt-1">
                ZoomやGoogle Meetなどのオンライン面談用のURLを設定できます
              </p>
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

export default CoachProfile;
