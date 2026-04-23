import api from '../../services/api';

export const getReports = async (engineerId, sectorId) => {
    const params = {};
    if (engineerId) params.engineer = engineerId;
    if (sectorId) params.sector = sectorId;
    return (await api.get('reports/daily', { params })).data;
};

export const createReport = async (data) => (await api.post('reports/daily', data)).data;
