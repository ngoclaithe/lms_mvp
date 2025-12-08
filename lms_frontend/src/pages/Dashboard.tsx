import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Users, GraduationCap, BookOpen, School } from 'lucide-react';

interface Statistics {
    total_students: number;
    total_lecturers: number;
    total_courses: number;
    total_classes: number;
    total_departments: number;
}

const Dashboard: React.FC = () => {
    const [stats, setStats] = useState<Statistics | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchStatistics();
    }, []);

    const fetchStatistics = async () => {
        try {
            const response = await api.get('/deans/statistics');
            setStats(response.data);
        } catch (err) {
            console.error('Failed to fetch statistics:', err);
        } finally {
            setLoading(false);
        }
    };

    const StatCard = ({
        title,
        value,
        icon: Icon,
        bgColor,
        iconColor
    }: {
        title: string;
        value: number;
        icon: any;
        bgColor: string;
        iconColor: string;
    }) => (
        <div className={`${bgColor} p-6 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1`}>
            <div className="flex justify-between items-start">
                <div>
                    <p className="text-white/80 text-sm font-medium mb-2">{title}</p>
                    <h3 className="text-4xl font-bold text-white">{value}</h3>
                </div>
                <div className={`${iconColor} p-4 rounded-xl bg-white/20 backdrop-blur-sm`}>
                    <Icon className="h-8 w-8 text-white" />
                </div>
            </div>
        </div>
    );

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                    title="Tổng Sinh Viên"
                    value={stats?.total_students || 0}
                    icon={Users}
                    bgColor="bg-gradient-to-br from-green-500 to-green-600"
                    iconColor="text-green-600"
                />
                <StatCard
                    title="Tổng Giảng Viên"
                    value={stats?.total_lecturers || 0}
                    icon={GraduationCap}
                    bgColor="bg-gradient-to-br from-indigo-500 to-indigo-600"
                    iconColor="text-indigo-600"
                />
                <StatCard
                    title="Tổng Môn Học"
                    value={stats?.total_courses || 0}
                    icon={BookOpen}
                    bgColor="bg-gradient-to-br from-blue-500 to-blue-600"
                    iconColor="text-blue-600"
                />
                <StatCard
                    title="Tổng Lớp Học"
                    value={stats?.total_classes || 0}
                    icon={School}
                    bgColor="bg-gradient-to-br from-purple-500 to-purple-600"
                    iconColor="text-purple-600"
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                    <h3 className="text-lg font-bold text-gray-800 mb-4">Thống Kê Nhanh</h3>
                    <div className="space-y-3">
                        <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                            <span className="text-gray-600">Tổng Khoa/Viện</span>
                            <span className="font-bold text-gray-900">{stats?.total_departments || 0}</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                            <span className="text-gray-600">Trung bình SV/Lớp</span>
                            <span className="font-bold text-gray-900">
                                {stats?.total_classes ? Math.round((stats.total_students / stats.total_classes) * 10) / 10 : 0}
                            </span>
                        </div>
                    </div>
                </div>

                <div className="bg-gradient-to-br from-gray-50 to-gray-100 p-6 rounded-2xl border border-gray-200">
                    <h3 className="text-lg font-bold text-gray-800 mb-2">Hệ Thống Quản Lý</h3>
                    <p className="text-gray-600 text-sm mb-4">Khoa Công Nghệ Thông Tin</p>
                    <div className="flex items-center gap-2 text-sm text-gray-500">
                        <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
                        <span>Hệ thống đang hoạt động</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
