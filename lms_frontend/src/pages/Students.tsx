import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Plus, User, Mail, Phone, Trash2, Search, GraduationCap } from 'lucide-react';

interface UserData {
    id: number;
    username: string;
    email: string;
    full_name: string;
    phone_number: string;
    is_active: boolean;
}

const Students: React.FC = () => {
    const [students, setStudents] = useState<UserData[]>([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [formData, setFormData] = useState({
        username: '', email: '', password: '', full_name: '', phone_number: ''
    });
    const [error, setError] = useState('');

    useEffect(() => {
        fetchStudents();
    }, []);

    const fetchStudents = async () => {
        try {
            const response = await api.get('/deans/students');
            setStudents(response.data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await api.post('/deans/students', { ...formData, role: 'student' });
            setShowModal(false);
            setFormData({ username: '', email: '', password: '', full_name: '', phone_number: '' });
            fetchStudents();
        } catch (err) {
            setError('Không thể tạo sinh viên');
        }
    };

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h2 className="text-2xl font-bold text-gray-900">Quản Lý Sinh Viên</h2>
                    <p className="text-gray-500 text-sm">Danh sách sinh viên toàn trường</p>
                </div>
                <button
                    onClick={() => setShowModal(true)}
                    className="bg-green-600 text-white px-5 py-2.5 rounded-xl flex items-center gap-2 hover:bg-green-700 shadow-lg shadow-green-500/20 transition-all active:scale-95 font-medium"
                >
                    <Plus className="h-5 w-5" /> Thêm Sinh Viên
                </button>
            </div>

            {showModal && (
                <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
                    <div className="bg-white p-8 rounded-2xl w-full max-w-md shadow-2xl animate-in zoom-in-95 duration-200 max-h-[90vh] overflow-y-auto">
                        <div className="flex justify-between items-center mb-6">
                            <h3 className="text-xl font-bold text-gray-900">Thêm Sinh Viên Mới</h3>
                            <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-gray-600">✕</button>
                        </div>

                        {error && <p className="bg-red-50 text-red-600 p-3 rounded-lg text-sm mb-4 border border-red-100">{error}</p>}

                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <label className="block text-sm font-semibold text-gray-700 mb-1">Tên đăng nhập (MSSV)</label>
                                <input
                                    className="w-full border border-gray-200 p-3 rounded-xl focus:ring-2 focus:ring-green-500/20 focus:border-green-500 outline-none transition-all"
                                    value={formData.username}
                                    onChange={e => setFormData({ ...formData, username: e.target.value })}
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-semibold text-gray-700 mb-1">Email</label>
                                <input
                                    type="email"
                                    className="w-full border border-gray-200 p-3 rounded-xl focus:ring-2 focus:ring-green-500/20 focus:border-green-500 outline-none transition-all"
                                    value={formData.email}
                                    onChange={e => setFormData({ ...formData, email: e.target.value })}
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-semibold text-gray-700 mb-1">Mật khẩu</label>
                                <input
                                    type="password"
                                    className="w-full border border-gray-200 p-3 rounded-xl focus:ring-2 focus:ring-green-500/20 focus:border-green-500 outline-none transition-all"
                                    value={formData.password}
                                    onChange={e => setFormData({ ...formData, password: e.target.value })}
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-semibold text-gray-700 mb-1">Họ và tên</label>
                                <input
                                    className="w-full border border-gray-200 p-3 rounded-xl focus:ring-2 focus:ring-green-500/20 focus:border-green-500 outline-none transition-all"
                                    value={formData.full_name}
                                    onChange={e => setFormData({ ...formData, full_name: e.target.value })}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-semibold text-gray-700 mb-1">Số điện thoại</label>
                                <input
                                    className="w-full border border-gray-200 p-3 rounded-xl focus:ring-2 focus:ring-green-500/20 focus:border-green-500 outline-none transition-all"
                                    value={formData.phone_number}
                                    onChange={e => setFormData({ ...formData, phone_number: e.target.value })}
                                />
                            </div>

                            <div className="flex justify-end gap-3 pt-4">
                                <button
                                    type="button"
                                    onClick={() => setShowModal(false)}
                                    className="text-gray-600 px-5 py-2.5 hover:bg-gray-100 rounded-xl font-medium transition-colors"
                                >
                                    Hủy
                                </button>
                                <button
                                    type="submit"
                                    className="bg-green-600 text-white px-5 py-2.5 rounded-xl hover:bg-green-700 font-medium shadow-lg shadow-green-500/30 transition-all"
                                >
                                    Tạo Mới
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {loading ? (
                <div className="flex justify-center p-12">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
                </div>
            ) : (
                <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                    <table className="w-full text-left text-sm text-gray-600">
                        <thead className="bg-gray-50/50 text-gray-800 font-semibold uppercase text-xs">
                            <tr>
                                <th className="px-6 py-4">Sinh Viên</th>
                                <th className="px-6 py-4">Liên Hệ</th>
                                <th className="px-6 py-4">Trạng Thái</th>
                                <th className="px-6 py-4 text-right">Thao Tác</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {students.map(student => (
                                <tr key={student.id} className="hover:bg-green-50/30 transition-colors group">
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-4">
                                            <div className="bg-green-100 p-3 rounded-xl shadow-sm">
                                                <User className="h-5 w-5 text-green-600" />
                                            </div>
                                            <div>
                                                <div className="font-bold text-gray-900 text-base">{student.full_name || 'Chưa cập nhật tên'}</div>
                                                <div className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full w-fit mt-1">@{student.username}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="space-y-1.5">
                                            <div className="flex items-center gap-2 text-gray-600">
                                                <Mail className="h-3.5 w-3.5 text-gray-400" /> {student.email}
                                            </div>
                                            {student.phone_number && (
                                                <div className="flex items-center gap-2 text-gray-600">
                                                    <Phone className="h-3.5 w-3.5 text-gray-400" /> {student.phone_number}
                                                </div>
                                            )}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${student.is_active ? 'bg-green-100 text-green-700 border border-green-200' : 'bg-red-100 text-red-700 border border-red-200'}`}>
                                            {student.is_active ? 'Hoạt động' : 'Đã khóa'}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-right">
                                        <button className="text-gray-400 hover:text-red-500 transition-colors p-2 hover:bg-red-50 rounded-lg">
                                            <Trash2 className="h-4.5 w-4.5" />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                            {students.length === 0 && (
                                <tr>
                                    <td colSpan={4} className="px-6 py-10 text-center text-gray-400 italic">Chưa có sinh viên nào</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

export default Students;
