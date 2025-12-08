import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { Clock, AlertCircle, Activity, ShieldCheck, FileText } from 'lucide-react';

interface AuditLog {
    id: number;
    action: string;
    details: string;
    timestamp: string;
    user: string;
}

const Dashboard: React.FC = () => {
    const [logs, setLogs] = useState<AuditLog[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchLogs();
    }, []);

    const fetchLogs = async () => {
        try {
            const response = await api.get('/deans/audit-logs');
            setLogs(response.data);
        } catch (err) {
            setError('Không thể tải nhật ký hệ thống');
        } finally {
            setLoading(false);
        }
    };

    const StatCard = ({ title, value, icon: Icon, color }: { title: string, value: string | number, icon: any, color: string }) => (
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start">
                <div>
                    <p className="text-gray-500 text-sm font-medium mb-1">{title}</p>
                    <h3 className="text-3xl font-bold text-gray-900">{value}</h3>
                </div>
                <div className={`p-3 rounded-xl ${color}`}>
                    <Icon className="h-6 w-6 text-white" />
                </div>
            </div>
        </div>
    );

    if (loading) return (
        <div className="flex items-center justify-center p-10">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-3 text-gray-500 font-medium">Đang tải dữ liệu...</span>
        </div>
    );

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <StatCard
                    title="Tổng Hoạt Động"
                    value={logs.length}
                    icon={Activity}
                    color="bg-blue-500"
                />
                <StatCard
                    title="Bảo Mật"
                    value="An toàn"
                    icon={ShieldCheck}
                    color="bg-green-500"
                />
                <StatCard
                    title="Báo Cáo Mới"
                    value="0"
                    icon={FileText}
                    color="bg-orange-500"
                />
            </div>

            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                <div className="p-6 border-b border-gray-50 flex justify-between items-center bg-gray-50/50">
                    <div>
                        <h3 className="font-bold text-gray-900 text-lg">Nhật Ký Hệ Thống</h3>
                        <p className="text-gray-500 text-sm">Theo dõi các hoạt động gần đây của Dean</p>
                    </div>
                    <button
                        onClick={fetchLogs}
                        className="px-4 py-2 bg-white border border-gray-200 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50 hover:border-gray-300 transition-colors shadow-sm"
                    >
                        Làm mới
                    </button>
                </div>

                {error ? (
                    <div className="p-8 text-red-600 flex items-center justify-center gap-2 bg-red-50/50">
                        <AlertCircle className="h-5 w-5" /> {error}
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-sm text-gray-600">
                            <thead className="bg-gray-50/80 text-gray-700 font-semibold uppercase text-xs tracking-wider">
                                <tr>
                                    <th className="px-6 py-4">Hành Động</th>
                                    <th className="px-6 py-4">Người Dùng</th>
                                    <th className="px-6 py-4">Chi Tiết</th>
                                    <th className="px-6 py-4">Thời Gian</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100">
                                {logs.map((log) => (
                                    <tr key={log.id} className="hover:bg-gray-50/80 transition-colors">
                                        <td className="px-6 py-4 font-medium text-blue-600">
                                            <span className="bg-blue-50 text-blue-700 px-2 py-1 rounded-md text-xs font-semibold border border-blue-100">
                                                {log.action}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-gray-900 font-medium">{log.user}</td>
                                        <td className="px-6 py-4 max-w-xs truncate" title={log.details}>{log.details || '-'}</td>
                                        <td className="px-6 py-4 flex items-center gap-2 text-gray-500">
                                            <Clock className="h-3.5 w-3.5" />
                                            {new Date(log.timestamp).toLocaleString('vi-VN')}
                                        </td>
                                    </tr>
                                ))}
                                {logs.length === 0 && (
                                    <tr>
                                        <td colSpan={4} className="px-6 py-12 text-center text-gray-400 flex flex-col items-center gap-2">
                                            <FileText className="h-8 w-8 text-gray-300" />
                                            <span>Chưa có nhật ký nào được ghi lại</span>
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Dashboard;
