import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Layout from '../../components/common/Layout';
import { appointmentsAPI, coachesAPI, clientsAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import Calendar from 'react-calendar';
import 'react-calendar/dist/Calendar.css';
import toast from 'react-hot-toast';
import { Calendar as CalendarIcon, Clock, X, Check, XCircle, Plus } from 'lucide-react';

const AppointmentList = () => {
  const { user, isCoach } = useAuth();
  const queryClient = useQueryClient();
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [showModal, setShowModal] = useState(false);
  const [showAvailabilityModal, setShowAvailabilityModal] = useState(false);
  const [viewMode, setViewMode] = useState('calendar'); // 'calendar' or 'list'

  const [newAppointment, setNewAppointment] = useState({
    appointment_date: '',
    appointment_time: '',
    appointment_type: '定期面談',
    notes: '',
  });

  // 複数コーチ選択用の状態
  const [selectedCoaches, setSelectedCoaches] = useState([]);
  const [selectedCoachForNewAppointment, setSelectedCoachForNewAppointment] = useState('');

  // 利用者情報取得
  const { data: clientData } = useQuery({
    queryKey: ['client-me'],
    queryFn: () => clientsAPI.getMe().then(res => res.data),
    enabled: !isCoach && !!user,
  });

  // コーチ一覧取得
  const { data: coaches } = useQuery({
    queryKey: ['coaches'],
    queryFn: () => coachesAPI.getAll().then(res => res.data),
    enabled: !isCoach && !!user,
  });

  // 全コーチの空き枠取得（利用者の場合のみ）
  const { data: availabilities, isLoading: availabilitiesLoading, error: availabilitiesError } = useQuery({
    queryKey: ['all-coach-availability'],
    queryFn: () => appointmentsAPI.getAllCoachAvailability().then(res => {
      console.log('[DEBUG] getAllCoachAvailability response:', res.data);
      return res.data;
    }).catch(err => {
      console.error('[ERROR] getAllCoachAvailability failed:', err.response?.data || err.message);
      throw err;
    }),
    enabled: !isCoach && !!user,
    retry: false,
  });

  const { data: appointments, isLoading } = useQuery({
    queryKey: ['appointments'],
    queryFn: () => appointmentsAPI.getAll().then((res) => res.data),
  });

  const createMutation = useMutation({
    mutationFn: appointmentsAPI.create,
    onSuccess: () => {
      queryClient.invalidateQueries(['appointments']);
      queryClient.invalidateQueries(['all-coach-availability']);
      toast.success('面談予約を申請しました');
      setShowModal(false);
      setShowAvailabilityModal(false);
      setNewAppointment({
        appointment_date: '',
        appointment_time: '',
        appointment_type: '定期面談',
        notes: '',
      });
      setSelectedCoachForNewAppointment('');
      setSelectedCoaches([]);
    },
    onError: (error) => {
      console.error('予約エラー:', error);
      toast.error(error.response?.data?.detail || '予約に失敗しました');
    },
  });

  const cancelMutation = useMutation({
    mutationFn: appointmentsAPI.cancel,
    onSuccess: () => {
      queryClient.invalidateQueries(['appointments']);
      toast.success('予約をキャンセルしました');
    },
    onError: (error) => {
      toast.error('キャンセルに失敗しました');
    },
  });

  const approveMutation = useMutation({
    mutationFn: appointmentsAPI.approve,
    onSuccess: () => {
      queryClient.invalidateQueries(['appointments']);
      toast.success('予約を承認しました');
    },
    onError: (error) => {
      toast.error('承認に失敗しました');
    },
  });

  const rejectMutation = useMutation({
    mutationFn: appointmentsAPI.reject,
    onSuccess: () => {
      queryClient.invalidateQueries(['appointments']);
      toast.success('予約を拒否しました');
    },
    onError: (error) => {
      toast.error('拒否に失敗しました');
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!selectedCoachForNewAppointment) {
      toast.error('コーチを選択してください');
      return;
    }

    // 日付と時刻を結合し、ローカルタイムゾーン(JST)でDateオブジェクトを作成
    const appointmentDate = new Date(`${newAppointment.appointment_date}T${newAppointment.appointment_time}:00`);

    const dataToSend = {
      appointment_date: appointmentDate.toISOString(),
      appointment_type: newAppointment.appointment_type,
      notes: newAppointment.notes,
      status: '予約申請中',
      coach_id: selectedCoachForNewAppointment,
    };

    createMutation.mutate(dataToSend);
  };

  const handleCancel = (appointmentId) => {
    if (window.confirm('この予約をキャンセルしますか？')) {
      cancelMutation.mutate(appointmentId);
    }
  };

  // 時間帯でグループ化した空き枠を取得
  const groupedByTime = React.useMemo(() => {
    if (!availabilities) return [];

    const groups = {};
    availabilities.forEach(slot => {
      const key = `${slot.available_start}-${slot.available_end}`;
      if (!groups[key]) {
        groups[key] = {
          available_start: slot.available_start,
          available_end: slot.available_end,
          coaches: []
        };
      }
      groups[key].coaches.push({
        coach_id: slot.coach_id,
        coach_name: slot.coach?.name || 'コーチ',
        availability_id: slot.availability_id
      });
    });

    return Object.values(groups).sort((a, b) =>
      new Date(a.available_start) - new Date(b.available_start)
    );
  }, [availabilities]);

  const handleBookAvailability = (timeSlot) => {
    // 選択されたコーチがいない場合は、その時間帯の全コーチを選択
    const coachIds = selectedCoaches.length > 0
      ? selectedCoaches
      : timeSlot.coaches.map(c => c.coach_id);

    const dataToSend = {
      appointment_date: timeSlot.available_start,
      appointment_type: '定期面談',
      notes: '',
      status: '予約申請中',
      coach_ids: coachIds,
    };
    createMutation.mutate(dataToSend);
    setShowAvailabilityModal(false);
    setSelectedCoaches([]);
  };

  const toggleCoachSelection = (coachId) => {
    setSelectedCoaches(prev => {
      if (prev.includes(coachId)) {
        return prev.filter(id => id !== coachId);
      } else {
        return [...prev, coachId];
      }
    });
  };

  // カレンダーの日付にマークをつける
  const tileContent = ({ date, view }) => {
    if (view === 'month' && appointments) {
      const dayAppointments = appointments.filter(app => {
        const appDate = new Date(app.appointment_date);
        return appDate.toDateString() === date.toDateString();
      });

      if (dayAppointments.length > 0) {
        return (
          <div className="flex justify-center">
            <div className="w-1 h-1 bg-primary-600 rounded-full mt-1"></div>
          </div>
        );
      }
    }
    return null;
  };

  // 選択した日付の予約を取得
  const selectedDateAppointments = appointments?.filter(app => {
    const appDate = new Date(app.appointment_date);
    return appDate.toDateString() === selectedDate.toDateString();
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
          <h2 className="text-2xl font-bold">面談予約管理</h2>
          <div className="flex space-x-3">
            <button
              className={`btn ${viewMode === 'calendar' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setViewMode('calendar')}
            >
              カレンダー表示
            </button>
            <button
              className={`btn ${viewMode === 'list' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setViewMode('list')}
            >
              リスト表示
            </button>
            {!isCoach && (
              <button
                className="btn btn-success flex items-center space-x-2"
                onClick={() => setShowAvailabilityModal(true)}
              >
                <Clock size={20} />
                <span>空き枠から予約</span>
              </button>
            )}
            <button className="btn btn-primary" onClick={() => setShowModal(true)}>
              新規予約
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

            {/* 選択した日の予約 */}
            <div className="card">
              <h3 className="text-lg font-semibold mb-4">
                {selectedDate.toLocaleDateString('ja-JP', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                })}
              </h3>
              <div className="space-y-3">
                {selectedDateAppointments.length > 0 ? (
                  selectedDateAppointments.map((appointment) => (
                    <div key={appointment.appointment_id} className="p-3 bg-gray-50 rounded-md">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2">
                            <Clock size={16} className="text-gray-600" />
                            <p className="font-medium">
                              {new Date(appointment.appointment_date).toLocaleTimeString('ja-JP', {
                                hour: '2-digit',
                                minute: '2-digit'
                              })}
                            </p>
                          </div>
                          <p className="text-sm text-gray-600 mt-1">
                            {appointment.appointment_type}
                          </p>
                          {appointment.coaches && appointment.coaches.length > 0 && (
                            <p className="text-xs text-primary-700 mt-1">
                              コーチ: {appointment.coaches.map(c => c.name).join(', ')}
                              {appointment.coaches.length > 1 && (
                                <span className="ml-2 badge badge-info text-xs">複数人MTG</span>
                              )}
                            </p>
                          )}
                          {appointment.notes && (
                            <p className="text-xs text-gray-500 mt-1">{appointment.notes}</p>
                          )}
                        </div>
                        <div className="flex flex-col items-end space-y-2">
                          <span className={`badge text-xs ${
                            appointment.status === '確定' ? 'badge-success' :
                            appointment.status === 'キャンセル' ? 'badge-danger' :
                            'badge-warning'
                          }`}>
                            {appointment.status}
                          </span>
                          {appointment.status === '予約申請中' && (
                            <>
                              {isCoach ? (
                                <div className="flex space-x-2">
                                  <button
                                    onClick={() => approveMutation.mutate(appointment.appointment_id)}
                                    className="text-green-500 hover:text-green-700 text-xs flex items-center space-x-1"
                                  >
                                    <Check size={14} />
                                    <span>承認</span>
                                  </button>
                                  <button
                                    onClick={() => rejectMutation.mutate(appointment.appointment_id)}
                                    className="text-red-500 hover:text-red-700 text-xs flex items-center space-x-1"
                                  >
                                    <XCircle size={14} />
                                    <span>拒否</span>
                                  </button>
                                </div>
                              ) : (
                                <button
                                  onClick={() => handleCancel(appointment.appointment_id)}
                                  className="text-red-500 hover:text-red-700 text-xs"
                                >
                                  キャンセル
                                </button>
                              )}
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-500 text-center py-4 text-sm">予約はありません</p>
                )}
              </div>
            </div>
          </div>
        ) : (
          /* リスト表示 */
          <div className="grid grid-cols-1 gap-4">
            {appointments?.map((appointment) => (
              <div key={appointment.appointment_id} className="card">
                <div className="flex items-start space-x-4">
                  <CalendarIcon className="text-primary-600 mt-1" size={24} />
                  <div className="flex-1">
                    <p className="font-semibold">
                      {new Date(appointment.appointment_date).toLocaleString('ja-JP', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                    <p className="text-sm text-gray-600 mt-1">
                      タイプ: {appointment.appointment_type}
                    </p>
                    {appointment.coaches && appointment.coaches.length > 0 && (
                      <p className="text-sm text-primary-700 mt-1">
                        コーチ: {appointment.coaches.map(c => c.name).join(', ')}
                        {appointment.coaches.length > 1 && (
                          <span className="ml-2 badge badge-info text-xs">複数人MTG</span>
                        )}
                      </p>
                    )}
                    {appointment.notes && (
                      <p className="text-sm text-gray-600 mt-1">{appointment.notes}</p>
                    )}
                  </div>
                  <div className="flex flex-col items-end space-y-2">
                    <span className={`badge ${
                      appointment.status === '確定' ? 'badge-success' :
                      appointment.status === 'キャンセル' ? 'badge-danger' :
                      'badge-warning'
                    }`}>
                      {appointment.status}
                    </span>
                    {appointment.status === '予約申請中' && (
                      <>
                        {isCoach ? (
                          <div className="flex space-x-2">
                            <button
                              onClick={() => approveMutation.mutate(appointment.appointment_id)}
                              className="btn btn-sm bg-green-500 hover:bg-green-600 text-white flex items-center space-x-1"
                            >
                              <Check size={16} />
                              <span>承認</span>
                            </button>
                            <button
                              onClick={() => rejectMutation.mutate(appointment.appointment_id)}
                              className="btn btn-sm bg-red-500 hover:bg-red-600 text-white flex items-center space-x-1"
                            >
                              <XCircle size={16} />
                              <span>拒否</span>
                            </button>
                          </div>
                        ) : (
                          <button
                            onClick={() => handleCancel(appointment.appointment_id)}
                            className="text-red-500 hover:text-red-700 text-sm"
                          >
                            キャンセル
                          </button>
                        )}
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))}
            {!appointments || appointments.length === 0 && (
              <p className="text-gray-500 text-center py-12">面談予約はありません</p>
            )}
          </div>
        )}

        {/* 新規予約モーダル */}
        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-bold">新規予約申請</h3>
                <button onClick={() => setShowModal(false)} className="text-gray-500 hover:text-gray-700">
                  <X size={24} />
                </button>
              </div>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="label">日付</label>
                  <input
                    type="date"
                    className="input"
                    value={newAppointment.appointment_date}
                    onChange={(e) => setNewAppointment({...newAppointment, appointment_date: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <label className="label">時刻</label>
                  <select
                    className="input"
                    value={newAppointment.appointment_time}
                    onChange={(e) => setNewAppointment({...newAppointment, appointment_time: e.target.value})}
                    required
                  >
                    <option value="">時刻を選択</option>
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
                  <label className="label">面談タイプ</label>
                  <select
                    className="input"
                    value={newAppointment.appointment_type}
                    onChange={(e) => setNewAppointment({...newAppointment, appointment_type: e.target.value})}
                  >
                    <option>定期面談</option>
                    <option>書類添削</option>
                    <option>面接対策</option>
                    <option>その他</option>
                  </select>
                </div>
                <div>
                  <label className="label">コーチ *</label>
                  <select
                    className="input"
                    value={selectedCoachForNewAppointment}
                    onChange={(e) => setSelectedCoachForNewAppointment(e.target.value)}
                    required
                  >
                    <option value="">コーチを選択</option>
                    {coaches?.map((coach) => (
                      <option key={coach.coach_id} value={coach.coach_id}>
                        {coach.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="label">備考</label>
                  <textarea
                    className="input"
                    rows={3}
                    value={newAppointment.notes}
                    onChange={(e) => setNewAppointment({...newAppointment, notes: e.target.value})}
                    placeholder="相談したい内容など"
                  />
                </div>
                <div className="flex justify-end space-x-3">
                  <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                    キャンセル
                  </button>
                  <button type="submit" className="btn btn-primary" disabled={createMutation.isLoading}>
                    {createMutation.isLoading ? '申請中...' : '予約申請'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* 空き枠から予約モーダル */}
        {showAvailabilityModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-bold">空き枠から予約</h3>
                <button onClick={() => setShowAvailabilityModal(false)} className="text-gray-500 hover:text-gray-700">
                  <X size={24} />
                </button>
              </div>
              {availabilitiesLoading ? (
                <div className="text-center py-8">読み込み中...</div>
              ) : groupedByTime && groupedByTime.length > 0 ? (
                <div className="space-y-4">
                  {groupedByTime.map((timeSlot, idx) => (
                    <div
                      key={idx}
                      className="p-4 bg-green-50 border border-green-200 rounded-md"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <p className="font-semibold text-lg">
                            {new Date(timeSlot.available_start).toLocaleString('ja-JP', {
                              year: 'numeric',
                              month: 'long',
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit',
                            })}
                            {' - '}
                            {new Date(timeSlot.available_end).toLocaleTimeString('ja-JP', {
                              hour: '2-digit',
                              minute: '2-digit',
                            })}
                          </p>
                          <p className="text-sm text-gray-600 mt-1">
                            {Math.round((new Date(timeSlot.available_end) - new Date(timeSlot.available_start)) / 60000)}分
                          </p>
                        </div>
                        {timeSlot.coaches.length > 1 && (
                          <span className="badge badge-info text-xs">複数人対応可</span>
                        )}
                      </div>

                      <div className="space-y-2 mb-3">
                        <p className="text-sm font-medium text-gray-700">対応可能なコーチ:</p>
                        {timeSlot.coaches.map(coach => (
                          <label
                            key={coach.coach_id}
                            className="flex items-center space-x-2 p-2 bg-white rounded border border-gray-200 hover:bg-gray-50 cursor-pointer"
                          >
                            <input
                              type="checkbox"
                              checked={selectedCoaches.includes(coach.coach_id)}
                              onChange={() => toggleCoachSelection(coach.coach_id)}
                              className="form-checkbox h-4 w-4 text-primary-600"
                            />
                            <span className="text-sm font-medium text-primary-700">
                              {coach.coach_name}
                            </span>
                          </label>
                        ))}
                      </div>

                      <button
                        onClick={() => handleBookAvailability(timeSlot)}
                        className="btn btn-primary btn-sm w-full"
                        disabled={createMutation.isLoading}
                      >
                        {selectedCoaches.length > 0
                          ? `選択したコーチ（${selectedCoaches.length}人）で予約`
                          : timeSlot.coaches.length > 1
                          ? `全員（${timeSlot.coaches.length}人）で予約`
                          : '予約する'}
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <p className="text-gray-500">空き枠がありません</p>
                  <p className="text-sm text-gray-400 mt-2">コーチが空き枠を登録するまでお待ちください</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default AppointmentList;
