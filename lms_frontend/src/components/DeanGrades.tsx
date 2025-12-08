import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Search, GraduationCap, Edit2 } from 'lucide-react';

interface ClassItem {
    id: number;
    code: string;
    course?: {
        name: string;
    }
}

interface GradeItem {
    id: number;
    grade_type: string;
    score: number;
    weight: number;
}

interface StudentGrade {
    student_id: number;
    student_code: string;
    full_name: string;
    grades: GradeItem[];
}

const DeanGrades: React.FC = () => {
    const [classes, setClasses] = useState<ClassItem[]>([]);
    const [selectedClass, setSelectedClass] = useState<number | null>(null);
    const [grades, setGrades] = useState<StudentGrade[]>([]);
    const [loading, setLoading] = useState(false);

    // Edit Grade State
    const [editingGrade, setEditingGrade] = useState<GradeItem | null>(null);
    const [showEditModal, setShowEditModal] = useState(false);
    const [formData, setFormData] = useState({ score: 0 });

    useEffect(() => {
        api.get('/deans/classes').then(res => setClasses(res.data));
    }, []);

    useEffect(() => {
        if (selectedClass) {
            setLoading(true);
            api.get(`/deans/classes/${selectedClass}/grades`)
                .then(res => setGrades(res.data))
                .catch(err => {
                    console.error(err);
                    setGrades([]);
                })
                .finally(() => setLoading(false));
        } else {
            setGrades([]);
        }
    }, [selectedClass]);

    const openEditModal = (grade: GradeItem) => {
        setEditingGrade(grade);
        setFormData({ score: grade.score });
        setShowEditModal(true);
    };

    const handleUpdateGrade = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!editingGrade) return;

        try {
            await api.put(`/deans/grades/${editingGrade.id}`, { ...editingGrade, score: parseFloat(formData.score as any) });
            // Refresh grades
            const res = await api.get(`/deans/classes/${selectedClass}/grades`);
            setGrades(res.data);
            setShowEditModal(false);
            setEditingGrade(null);
        } catch (err) {
            alert("Không thể cập nhật điểm");
        }
    };

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <div>
                <h2 className="text-2xl font-bold text-gray-900">Quản Lý Điểm Số</h2>
                <p className="text-gray-500 text-sm">Xem và quản lý bảng điểm theo lớp học</p>
            </div>

            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                <div className="max-w-md">
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Chọn Lớp Học</label>
                    <select
                        className="w-full border border-gray-200 p-3 rounded-xl focus:ring-2 focus:ring-purple-500/20 focus:border-purple-500 outline-none transition-all cursor-pointer"
                        onChange={e => setSelectedClass(parseInt(e.target.value))}
                        value={selectedClass || ''}
                    >
                        <option value="">-- Chọn lớp để xem điểm --</option>
                        {classes.map(c => (
                            <option key={c.id} value={c.id}>{c.code} - {c.course?.name || 'Học phần'}</option>
                        ))}
                    </select>
                </div>
            </div>

            {selectedClass && (
                <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                    <div className="p-6 border-b border-gray-50 bg-gray-50/50">
                        <h3 className="font-bold text-gray-800">Danh Sách Bảng Điểm</h3>
                    </div>
                    {loading ? (
                        <div className="flex justify-center p-12">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
                        </div>
                    ) : (
                        <table className="w-full text-left text-sm text-gray-600">
                            <thead className="bg-gray-50/50 text-gray-800 font-semibold uppercase text-xs">
                                <tr>
                                    <th className="px-6 py-4">MSSV</th>
                                    <th className="px-6 py-4">Họ và Tên</th>
                                    <th className="px-6 py-4 text-center">Đầu Điểm</th>
                                    <th className="px-6 py-4 text-center">Trọng Số</th>
                                    <th className="px-6 py-4 text-center">Điểm Số</th>
                                    <th className="px-6 py-4 text-right">Thao Tác</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100">
                                {grades.flatMap(student =>
                                    student.grades.map((grade: GradeItem) => (
                                        <tr key={grade.id} className="hover:bg-purple-50/30 transition-colors">
                                            <td className="px-6 py-4 font-medium text-gray-900">{student.student_code}</td>
                                            <td className="px-6 py-4">{student.full_name}</td>
                                            <td className="px-6 py-4 text-center bg-gray-50/50 text-gray-700 font-medium">{grade.grade_type}</td>
                                            <td className="px-6 py-4 text-center">{grade.weight}</td>
                                            <td className="px-6 py-4 text-center">
                                                <span className={`px-2.5 py-1 rounded-md font-bold text-xs ${grade.score >= 5 ? 'bg-green-50 text-green-700 border border-green-100' : 'bg-red-50 text-red-700 border border-red-100'}`}>
                                                    {grade.score}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 text-right">
                                                <button
                                                    onClick={() => openEditModal(grade)}
                                                    className="text-gray-400 hover:text-purple-600 hover:bg-purple-50 transition-colors p-2 rounded-lg"
                                                >
                                                    <Edit2 className="h-4 w-4" />
                                                </button>
                                            </td>
                                        </tr>
                                    ))
                                )}
                                {grades.length === 0 && (
                                    <tr>
                                        <td colSpan={6} className="px-6 py-12 text-center text-gray-400 italic">Chưa có dữ liệu điểm</td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    )}
                </div>
            )}

            {/* Edit Modal */}
            {showEditModal && (
                <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
                    <div className="bg-white p-6 rounded-2xl w-full max-w-sm shadow-xl animate-in zoom-in-95 duration-200">
                        <h3 className="text-lg font-bold text-gray-900 mb-4">Cập Nhật Điểm</h3>
                        <form onSubmit={handleUpdateGrade} className="space-y-4">
                            <div>
                                <label className="block text-sm font-semibold text-gray-700 mb-1">Điểm Số</label>
                                <input
                                    type="number" step="0.1" min="0" max="10"
                                    className="w-full border border-gray-200 p-3 rounded-xl focus:ring-2 focus:ring-purple-500/20 focus:border-purple-500 outline-none transition-all"
                                    value={formData.score}
                                    onChange={e => setFormData({ score: parseFloat(e.target.value) })}
                                    required
                                />
                            </div>
                            <div className="flex justify-end gap-3 pt-2">
                                <button
                                    type="button"
                                    onClick={() => setShowEditModal(false)}
                                    className="text-gray-600 px-4 py-2 hover:bg-gray-100 rounded-lg font-medium transition-colors"
                                >
                                    Hủy
                                </button>
                                <button
                                    type="submit"
                                    className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 font-medium shadow-sm transition-all"
                                >
                                    Lưu
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default DeanGrades;
