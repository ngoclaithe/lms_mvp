import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Plus, Trash2, Search, Book } from 'lucide-react';

interface Course {
    id: number;
    code: string;
    name: string;
    credits: number;
    department_id: number;
}

const Courses: React.FC = () => {
    const [courses, setCourses] = useState<Course[]>([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [formData, setFormData] = useState({ code: '', name: '', credits: 3, department_id: 1 });
    const [error, setError] = useState('');

    useEffect(() => {
        fetchCourses();
    }, []);

    const fetchCourses = async () => {
        try {
            const response = await api.get('/deans/courses');
            setCourses(response.data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await api.post('/deans/courses', formData);
            setShowModal(false);
            setFormData({ code: '', name: '', credits: 3, department_id: 1 });
            fetchCourses();
        } catch (err) {
            setError('Không thể tạo khóa học');
        }
    };

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h2 className="text-2xl font-bold text-gray-900">Quản Lý Khóa Học</h2>
                    <p className="text-gray-500 text-sm">Danh sách các môn học trong hệ thống</p>
                </div>
                <button
                    onClick={() => setShowModal(true)}
                    className="bg-blue-600 text-white px-5 py-2.5 rounded-xl flex items-center gap-2 hover:bg-blue-700 shadow-lg shadow-blue-500/20 transition-all active:scale-95 font-medium"
                >
                    <Plus className="h-5 w-5" /> Thêm Khóa Học
                </button>
            </div>

            {/* Search Placeholder */}
            <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center gap-3 max-w-md">
                <Search className="h-5 w-5 text-gray-400" />
                <input
                    type="text"
                    placeholder="Tìm kiếm khóa học..."
                    className="flex-1 outline-none text-gray-700 bg-transparent"
                />
            </div>

            {showModal && (
                <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
                    <div className="bg-white p-8 rounded-2xl w-full max-w-md shadow-2xl animate-in zoom-in-95 duration-200">
                        <div className="flex justify-between items-center mb-6">
                            <h3 className="text-xl font-bold text-gray-900">Thêm Môn Học Mới</h3>
                            <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-gray-600">✕</button>
                        </div>

                        {error && <p className="bg-red-50 text-red-600 p-3 rounded-lg text-sm mb-4 border border-red-100">{error}</p>}

                        <form onSubmit={handleSubmit} className="space-y-5">
                            <div>
                                <label className="block text-sm font-semibold text-gray-700 mb-1">Mã môn học</label>
                                <input
                                    className="w-full border border-gray-200 p-3 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
                                    value={formData.code}
                                    onChange={e => setFormData({ ...formData, code: e.target.value })}
                                    placeholder="VD: CS101"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-semibold text-gray-700 mb-1">Tên môn học</label>
                                <input
                                    className="w-full border border-gray-200 p-3 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
                                    value={formData.name}
                                    onChange={e => setFormData({ ...formData, name: e.target.value })}
                                    placeholder="VD: Nhập môn lập trình"
                                    required
                                />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-semibold text-gray-700 mb-1">Số tín chỉ</label>
                                    <input
                                        type="number"
                                        className="w-full border border-gray-200 p-3 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
                                        value={formData.credits}
                                        onChange={e => setFormData({ ...formData, credits: parseInt(e.target.value) })}
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-semibold text-gray-700 mb-1">ID Khoa</label>
                                    <input
                                        type="number"
                                        className="w-full border border-gray-200 p-3 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
                                        value={formData.department_id}
                                        onChange={e => setFormData({ ...formData, department_id: parseInt(e.target.value) })}
                                        required
                                    />
                                </div>
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
                                    className="bg-blue-600 text-white px-5 py-2.5 rounded-xl hover:bg-blue-700 font-medium shadow-lg shadow-blue-500/30 transition-all"
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
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                </div>
            ) : (
                <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                    <table className="w-full text-left text-sm text-gray-600">
                        <thead className="bg-gray-50/50 text-gray-800 font-semibold uppercase text-xs">
                            <tr>
                                <th className="px-6 py-4">Mã HP</th>
                                <th className="px-6 py-4">Tên Học Phần</th>
                                <th className="px-6 py-4 text-center">Tín Chỉ</th>
                                <th className="px-6 py-4 text-center">Khoa</th>
                                <th className="px-6 py-4 text-right">Thao Tác</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {courses.map(course => (
                                <tr key={course.id} className="hover:bg-blue-50/50 transition-colors group">
                                    <td className="px-6 py-4 font-bold text-blue-600">
                                        <div className="flex items-center gap-2">
                                            <Book className="h-4 w-4 text-blue-400" />
                                            {course.code}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 font-medium text-gray-900">{course.name}</td>
                                    <td className="px-6 py-4 text-center">
                                        <span className="bg-gray-100 px-2.5 py-1 rounded-md text-xs font-bold text-gray-600">{course.credits}</span>
                                    </td>
                                    <td className="px-6 py-4 text-center text-gray-500">ID: {course.department_id}</td>
                                    <td className="px-6 py-4 text-right">
                                        <button className="text-gray-400 hover:text-red-500 transition-colors p-2 hover:bg-red-50 rounded-lg">
                                            <Trash2 className="h-4.5 w-4.5" />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                            {courses.length === 0 && (
                                <tr>
                                    <td colSpan={5} className="px-6 py-10 text-center text-gray-400 italic">Chưa có khóa học nào</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

export default Courses;
