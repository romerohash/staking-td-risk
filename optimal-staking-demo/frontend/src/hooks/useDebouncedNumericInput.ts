import { useState, useEffect, useCallback } from 'react';

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
  const formatValue = (num: number): string => {
    return decimalPlaces !== undefined ? num.toFixed(decimalPlaces) : num.toString();
  };

  const [localValue, setLocalValue] = useState(formatValue(value));
  const [timeoutId, setTimeoutId] = useState<NodeJS.Timeout | null>(null);

  // Update local value when prop changes from external source
  useEffect(() => {
    setLocalValue(formatValue(value));
  }, [value, decimalPlaces]);

  const handleChange = useCallback((inputValue: string) => {
    setLocalValue(inputValue);

    // Clear existing timeout
    if (timeoutId) {
      clearTimeout(timeoutId);
    }

    // Set new timeout
    const newTimeoutId = setTimeout(() => {
      const numValue = parseFloat(inputValue);
      
      if (!isNaN(numValue)) {
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
    }, delay);

    setTimeoutId(newTimeoutId);
  }, [onChange, delay, min, max, decimalPlaces]);

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