import { useCallback, useEffect, useState } from "react";

interface UseDebouncedNumericInputProps {
	value: number;
	onChange: (value: number) => void;
	delay?: number;
	min?: number;
	max?: number;
	decimalPlaces?: number;
}

export const useDebouncedNumericInput = ({
	value,
	onChange,
	delay = 300,
	min,
	max,
	decimalPlaces,
}: UseDebouncedNumericInputProps) => {
	// Format initial value with appropriate decimal places
	// Memoize this function to prevent unnecessary re-renders
	const formatValue = useCallback(
		(num: number): string => {
			return decimalPlaces !== undefined
				? num.toFixed(decimalPlaces)
				: num.toString();
		},
		[decimalPlaces],
	);

	const [localValue, setLocalValue] = useState(formatValue(value));
	const [timeoutId, setTimeoutId] = useState<NodeJS.Timeout | null>(null);
	const [isUserTyping, _setIsUserTyping] = useState(false);

	// Update local value when prop changes from external source
	// BUT only if the user is not currently typing
	useEffect(() => {
		if (!isUserTyping) {
			setLocalValue(formatValue(value));
		}
	}, [value, formatValue, isUserTyping]);

	const handleChange = useCallback(
		(inputValue: string) => {
			setLocalValue(inputValue);
			_setIsUserTyping(true);

			// Clear existing timeout
			if (timeoutId) {
				clearTimeout(timeoutId);
			}

			// Set new timeout
			const newTimeoutId = setTimeout(() => {
				const numValue = parseFloat(inputValue);

				if (!Number.isNaN(numValue)) {
					let finalValue = numValue;

					// Apply constraints
					if (min !== undefined && finalValue < min) finalValue = min;
					if (max !== undefined && finalValue > max) finalValue = max;

					// Apply decimal places rounding
					if (decimalPlaces !== undefined) {
						finalValue = parseFloat(finalValue.toFixed(decimalPlaces));
					}

					onChange(finalValue);
				}

				// Mark typing as complete after debounce
				_setIsUserTyping(false);
			}, delay);

			setTimeoutId(newTimeoutId);
		},
		[onChange, delay, min, max, decimalPlaces, timeoutId],
	);

	// Cleanup timeout on unmount
	useEffect(() => {
		return () => {
			if (timeoutId) {
				clearTimeout(timeoutId);
			}
		};
	}, [timeoutId]);

	return {
		value: localValue,
		onChange: handleChange,
	};
};
