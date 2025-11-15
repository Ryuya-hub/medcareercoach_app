import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Layout from '../../components/common/Layout';
import { appointmentsAPI, coachesAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import Calendar from 'react-calendar';
import 'react-calendar/dist/Calendar.css';
import toast from 'react-hot-toast';
import { Calendar as CalendarIcon, Clock, Plus, Trash2, List } from 'lucide-react';

const AvailabilityManagement = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [showModal, setShowModal] = useState(false);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [viewMode, setViewMode] = useState('calendar'); // 'calendar' or 'list'
  const [newSlot, setNewSlot] = useState({
    date: '',
    start_time: '',
    end_time: '',
  });

  // コーチ情報取得
  const { data: coachData } = useQuery({
    queryKey: ['coach-profile'],
    queryFn: () => coachesAPI.getMe().then(res => res.data),
    enabled: !!user,
  });

  // 空き枠一覧取得
  const { data: availabilities, isLoading } = useQuery({
    queryKey: ['coach-availability', coachData?.coach_id],
    queryFn: () => {
      if (!coachData?.coach_id) return [];
      return appointmentsAPI.getCoachAvailability(coachData.coach_id).then(res => res.data);
    },
    enabled: !!coachData?.coach_id,
  });

  // 空き枠作成
  const createMutation = useMutation({
    mutationFn: appointmentsAPI.createAvailability,
    onSuccess: () => {
      queryClient.invalidateQueries(['coach-availability']);
      toast.success('空き枠を登録しました');
      setShowModal(false);
      setNewSlot({
        date: '',
        start_time: '',
        end_time: '',
      });
    },
    onError: (error) => {
      console.error('登録エラー:', error);
      toast.error(error.response?.data?.detail || '登録に失敗しました');
    },
  });

  // 空き枠削除
  const deleteMutation = useMutation({
    mutationFn: (availabilityId) => appointmentsAPI.deleteAvailability(availabilityId),
    onSuccess: () => {
      queryClient.invalidateQueries(['coach-availability']);
      toast.success('空き枠を削除しました');
    },
    onError: (error) => {
      toast.error('削除に失敗しました');
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!coachData?.coach_id) {
      toast.error('コーチ情報が取得できません');
      return;
    }

    // ローカルタイムゾーン(JST)でDateオブジェクトを作成し、ISO文字列に変換
    const startDate = new Date(`${newSlot.date}T${newSlot.start_time}:00`);
    const endDate = new Date(`${newSlot.date}T${newSlot.end_time}:00`);

    const dataToSend = {
      coach_id: coachData.coach_id,
      available_start: startDate.toISOString(),
      available_end: endDate.toISOString(),
      is_booked: false,
    };

    createMutation.mutate(dataToSend);
  };

  const handleDelete = (availabilityId, isBooked) => {
    if (isBooked) {
      toast.error('予約済みの空き枠は削除できません');
      return;
    }
    if (window.confirm('この空き枠を削除しますか？')) {
      deleteMutation.mutate(availabilityId);
    }
  };

  // 空き枠を日付ごとにグループ化
  const groupedAvailabilities = availabilities?.reduce((acc, slot) => {
    const date = new Date(slot.available_start).toLocaleDateString('ja-JP');
    if (!acc[date]) {
      acc[date] = [];
    }
    acc[date].push(slot);
    return acc;
  }, {}) || {};

  // カレンダーのタイルコンテンツ（空き枠がある日にマークを表示）
  const tileContent = ({ date, view }) => {
    if (view === 'month' && availabilities) {
      const daySlots = availabilities.filter(slot => {
        const slotDate = new Date(slot.available_start);
        return slotDate.toDateString() === date.toDateString();
      });

      if (daySlots.length > 0) {
        const hasAvailable = daySlots.some(slot => !slot.is_booked);
        return (
          <div className="flex justify-center">
            <div className={`w-1 h-1 rounded-full mt-1 ${
              hasAvailable ? 'bg-green-500' : 'bg-gray-400'
            }`}></div>
          </div>
        );
      }
    }
    return null;
  };

  // 選択した日付の空き枠を取得
  const selectedDateSlots = availabilities?.filter(slot => {
    const slotDate = new Date(slot.available_start);
    return slotDate.toDateString() === selectedDate.toDateString();
  }) || [];

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
          <div>
            <h2 className="text-2xl font-bold">空き枠管理</h2>
            <p className="text-gray-600">面談可能な日時を登録・管理します</p>
          </div>
          <div className="flex space-x-3">
            <button
              className={`btn ${viewMode === 'calendar' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setViewMode('calendar')}
            >
              <CalendarIcon size={20} />
              <span className="ml-2">カレンダー</span>
            </button>
            <button
              className={`btn ${viewMode === 'list' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setViewMode('list')}
            >
              <List size={20} />
              <span className="ml-2">リスト</span>
            </button>
            <button
              className="btn btn-primary flex items-center space-x-2"
              onClick={() => setShowModal(true)}
            >
              <Plus size={20} />
              <span>空き枠を追加</span>
            </button>
          </div>
        </div>

        {viewMode === 'calendar' ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* カレンダー */}
            <div className="lg:col-span-2 card">
              <Calendar
                onChange={setSelectedDate}
                value={selectedDate}
                tileContent={tileContent}
                locale="ja-JP"
                className="w-full border-none"
              />
            </div>

            {/* 選択した日の空き枠 */}
            <div className="card">
              <h3 className="text-lg font-semibold mb-4">
                {selectedDate.toLocaleDateString('ja-JP', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                })}
              </h3>
              <div className="space-y-3">
                {selectedDateSlots.length > 0 ? (
                  selectedDateSlots
                    .sort((a, b) => new Date(a.available_start) - new Date(b.available_start))
                    .map((slot) => (
                      <div
                        key={slot.availability_id}
                        className={`p-3 rounded-md border ${
                          slot.is_booked
                            ? 'bg-gray-100 border-gray-300'
                            : 'bg-green-50 border-green-200'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <Clock size={16} className="text-gray-600" />
                            <span className="font-medium">
                              {new Date(slot.available_start).toLocaleTimeString('ja-JP', {
                                hour: '2-digit',
                                minute: '2-digit',
                              })}
                              {' - '}
                              {new Date(slot.available_end).toLocaleTimeString('ja-JP', {
                                hour: '2-digit',
                                minute: '2-digit',
                              })}
                            </span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <span
                              className={`badge text-xs ${
                                slot.is_booked ? 'badge-secondary' : 'badge-success'
                              }`}
                            >
                              {slot.is_booked ? '予約済' : '空き'}
                            </span>
                            {!slot.is_booked && (
                              <button
                                onClick={() => handleDelete(slot.availability_id, slot.is_booked)}
                                className="text-red-500 hover:text-red-700"
                              >
                                <Trash2 size={16} />
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    ))
                ) : (
                  <p className="text-gray-500 text-center py-4 text-sm">空き枠はありません</p>
                )}
              </div>
            </div>
          </div>
        ) : (
          /* リスト表示 */
          <div className="space-y-4">
            {Object.keys(groupedAvailabilities).length > 0 ? (
              Object.entries(groupedAvailabilities)
                .sort(([dateA], [dateB]) => new Date(dateA) - new Date(dateB))
                .map(([date, slots]) => (
                  <div key={date} className="card">
                    <h3 className="text-lg font-semibold mb-3 flex items-center space-x-2">
                      <CalendarIcon size={20} className="text-primary-600" />
                      <span>{date}</span>
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                      {slots
                        .sort((a, b) => new Date(a.available_start) - new Date(b.available_start))
                        .map((slot) => (
                          <div
                            key={slot.availability_id}
                            className={`p-3 rounded-md border ${
                              slot.is_booked
                                ? 'bg-gray-100 border-gray-300'
                                : 'bg-green-50 border-green-200'
                            }`}
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex items-center space-x-2">
                                <Clock size={16} className="text-gray-600" />
                                <span className="font-medium">
                                  {new Date(slot.available_start).toLocaleTimeString('ja-JP', {
                                    hour: '2-digit',
                                    minute: '2-digit',
                                  })}
                                  {' - '}
                                  {new Date(slot.available_end).toLocaleTimeString('ja-JP', {
                                    hour: '2-digit',
                                    minute: '2-digit',
                                  })}
                                </span>
                              </div>
                              <div className="flex items-center space-x-2">
                                <span
                                  className={`badge text-xs ${
                                    slot.is_booked ? 'badge-secondary' : 'badge-success'
                                  }`}
                                >
                                  {slot.is_booked ? '予約済' : '空き'}
                                </span>
                                {!slot.is_booked && (
                                  <button
                                    onClick={() => handleDelete(slot.availability_id, slot.is_booked)}
                                    className="text-red-500 hover:text-red-700"
                                  >
                                    <Trash2 size={16} />
                                  </button>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                    </div>
                  </div>
                ))
            ) : (
              <div className="card text-center py-12">
                <p className="text-gray-500">空き枠が登録されていません</p>
                <p className="text-sm text-gray-400 mt-2">
                  「空き枠を追加」ボタンから面談可能な日時を登録してください
                </p>
              </div>
            )}
          </div>
        )}

        {/* 空き枠追加モーダル */}
        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-bold">空き枠を追加</h3>
                <button
                  onClick={() => setShowModal(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <Plus size={24} className="transform rotate-45" />
                </button>
              </div>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="label">日付</label>
                  <input
                    type="date"
                    className="input"
                    value={newSlot.date}
                    onChange={(e) => setNewSlot({ ...newSlot, date: e.target.value })}
                    required
                    min={new Date().toISOString().split('T')[0]}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="label">開始時刻</label>
                    <select
                      className="input"
                      value={newSlot.start_time}
                      onChange={(e) => setNewSlot({ ...newSlot, start_time: e.target.value })}
                      required
                    >
                      <option value="">選択してください</option>
                      {Array.from({ length: 28 }, (_, i) => {
                        const hour = Math.floor(i / 2) + 9;
                        const minute = (i % 2) * 30;
                        const timeStr = `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`;
                        return (
                          <option key={timeStr} value={timeStr}>
                            {timeStr}
                          </option>
                        );
                      })}
                    </select>
                  </div>
                  <div>
                    <label className="label">終了時刻</label>
                    <select
                      className="input"
                      value={newSlot.end_time}
                      onChange={(e) => setNewSlot({ ...newSlot, end_time: e.target.value })}
                      required
                    >
                      <option value="">選択してください</option>
                      {Array.from({ length: 28 }, (_, i) => {
                        const hour = Math.floor(i / 2) + 9;
                        const minute = (i % 2) * 30;
                        const timeStr = `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`;
                        return (
                          <option key={timeStr} value={timeStr}>
                            {timeStr}
                          </option>
                        );
                      })}
                    </select>
                  </div>
                </div>
                <div className="flex justify-end space-x-3 mt-6">
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => setShowModal(false)}
                  >
                    キャンセル
                  </button>
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={createMutation.isLoading}
                  >
                    {createMutation.isLoading ? '登録中...' : '登録'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default AvailabilityManagement;
