import { useEffect, useRef } from "react";
import type { CalculationRequest } from "../types";

interface UseDebouncedCalculationProps {
	parameters: CalculationRequest;
	onCalculate: () => void;
	delay?: number;
	enabled?: boolean;
}

export const useDebouncedCalculation = ({
	parameters: _parameters,
	onCalculate,
	delay = 500,
	enabled = true,
}: UseDebouncedCalculationProps) => {
	const timeoutRef = useRef<NodeJS.Timeout | null>(null);
	const isFirstRender = useRef(true);
	const wasEnabledRef = useRef(enabled);

	useEffect(() => {
		// Skip the first render to avoid immediate calculation on mount
		if (isFirstRender.current) {
			isFirstRender.current = false;
			wasEnabledRef.current = enabled;
			return;
		}

		// Skip calculation when transitioning from disabled to enabled
		if (!wasEnabledRef.current && enabled) {
			wasEnabledRef.current = enabled;
			return;
		}

		wasEnabledRef.current = enabled;

		if (!enabled) return;

		// Clear existing timeout
		if (timeoutRef.current) {
			clearTimeout(timeoutRef.current);
		}

		// Set new timeout for calculation
		timeoutRef.current = setTimeout(() => {
			onCalculate();
		}, delay);

		// Cleanup
		return () => {
			if (timeoutRef.current) {
				clearTimeout(timeoutRef.current);
			}
		};
	}, [onCalculate, delay, enabled]);
};
