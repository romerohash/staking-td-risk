import axios from 'axios';
import { CalculationRequest, CalculationResponse } from './types';

// In production, use the full API URL from environment variable
// In development, use the proxy path '/api' which vite will proxy to localhost:8000
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const calculateTrackingError = async (
  request: CalculationRequest
): Promise<CalculationResponse> => {
  const response = await api.post<CalculationResponse>('/calculate', request);
  return response.data;
};