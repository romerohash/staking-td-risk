import axios from "axios";
import type { CalculationRequest, CalculationResponse } from "./types";

// Always use '/api' - in development vite will proxy to localhost:8000
// In production, the backend serves both API and static files
const API_BASE_URL = "/api";

const api = axios.create({
	baseURL: API_BASE_URL,
	headers: {
		"Content-Type": "application/json",
	},
});

export const calculateTrackingError = async (
	request: CalculationRequest,
): Promise<CalculationResponse> => {
	const response = await api.post<CalculationResponse>("/calculate", request);
	return response.data;
};
